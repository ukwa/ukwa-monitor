import os
import json
import luigi
import luigi.contrib.esindex
import socket
import logging
import requests
import requests.adapters
import datetime
import lxml.etree as etree
from hapy import hapy
from multiprocessing import Pool, Process


logger = logging.getLogger('luigi-interface')

# Avoid hangs when systems are unreachable:
TIMEOUT = 10
socket.setdefaulttimeout(TIMEOUT)

# Set up a request session that does not retry:
s = requests.Session()
a = requests.adapters.HTTPAdapter(max_retries=1)
s.mount('http://', a)
s.mount('https://', a)


class CheckStatus(luigi.Task):
    """
    """
    task_namespace = 'monitor'
    date = luigi.DateMinuteParameter(default=datetime.datetime.today())

    servers = os.path.join(os.path.dirname(__file__), 'servers.json')
    services = os.path.join(os.path.dirname(__file__), 'services.json')

    def output(self):
        STATE_FOLDER = os.environ['LUIGI_STATE_FOLDER']
        return luigi.LocalTarget('%s/monitor/checkstatus.%s' % (STATE_FOLDER, self.date.strftime(luigi.DateMinuteParameter.date_format)))

    def run(self):
        services = self.load_as_json(self.services)
        services['timestamp'] = datetime.datetime.utcnow().isoformat()

        pool = Pool(20)

        # Parallel check for H3 job status:
        argsv = []
        for job in services.get('jobs', []):
            server = services['servers'][services['jobs'][job]['server']]
            server_url = server['url']
            server_user =  server['user']
            server_pass = os.environ['HERITRIX_PASSWORD']
            # app.logger.info(json.dumps(server, indent=4))
            services['jobs'][job]['url'] = server_url
            argsv.append((services['jobs'][job]['name'], job, server_url, server_user, server_pass))
        # Wait for all...
        results = pool.map(get_h3_status, argsv)
        for job, state in results:
            services['jobs'][job]['state'] = state

        # Parallel check for queue statuses:
        argsv = []
        for queue in services.get('queues', []):
            server_prefix = services['servers'][services['queues'][queue]['server']]['prefix']
            services['queues'][queue]['prefix'] = server_prefix
            queue_name = services['queues'][queue]['name']
            argsv.append((queue_name, queue, server_prefix))
        # Wait for all...
        results = pool.map(get_queue_status, argsv)
        for queue, state in results:
            services['queues'][queue]['state'] = state

        # Parallel check for HTTP status:
        argsv = []
        for http in services.get('http', []):
            argsv.append((http,services['http'][http]['url']))
        # Wait for all...
        results = pool.map(get_http_status, argsv)
        for http, state in results:
            services['http'][http]['state'] = state

        argsv = []
        for hdfs in services.get('hdfs', []):
            argsv.append((hdfs, services['hdfs'][hdfs]['url']))
        # Wait for all...
        results = pool.map(get_hdfs_status, argsv)
        for hdfs, state in results:
            services['hdfs'][hdfs]['state'] = state

        # And then write to a file
        with self.output().open('w') as f:
            f.write('{}'.format(json.dumps(services, indent=4)))

    def load_as_json(self, filename):
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, filename)
        with open(file_path, 'r') as fi:
            return json.load(fi)


def get_queue_status(args):
    queue, queue_id, server_prefix = args
    state = {}
    try:
        logger.info("Getting status for queue %s on %s" % (queue, server_prefix))
        qurl = '%s%s' % (server_prefix, queue)
        # app.logger.info("GET: %s" % qurl)
        r = s.get(qurl, timeout=(TIMEOUT, TIMEOUT))
        state['details'] = r.json()
        state['count'] = "{:0,}".format(state['details']['messages'])
        if 'error' in state['details']:
            state['status'] = "ERROR"
            state['status-class'] = "status-alert"
            state['error'] = state['details']['reason']
        elif state['details']['consumers'] == 0:
            state['status'] = "BECALMED"
            state['status-class'] = "status-oos"
            state['error'] = 'No consumers!'
        else:
            state['status'] = state['details']['messages']
            state['status-class'] = "status-good"
    except Exception as e:
        state['status'] = "DOWN"
        state['status-class'] = "status-alert"
        logger.error("Get Queue Status failed. %s" % e)

    return queue_id, state


def get_hdfs_status(args):
    hdfs_id, url = args
    state = {}
    try:
        logger.info("Getting status for hdfs %s" % (url))
        r = s.get(url, timeout=(TIMEOUT, TIMEOUT))
        state['status'] = "%s" % r.status_code
        if r.status_code / 100 == 2:
            state['status-class'] = "status-good"
            tree = etree.fromstring(r.text, etree.HTMLParser())
            percent = tree.xpath("//div[@id='dfstable']//tr[5]/td[3]")[0].text
            percent = percent.replace(" ", "")
            state['percent'] = percent
            state['remaining'] = tree.xpath("//div[@id='dfstable']//tr[4]/td[3]")[0].text.replace(" ", "")
            underr = int(tree.xpath("//div[@id='dfstable']//tr[10]/td[3]")[0].text)
            if underr != 0:
                state['status'] = "HDFS has %i under-replicated blocks!" % underr
                state['status-class'] = "status-warning"
        else:
            state['status-class'] = "status-warning"
    except Exception as e:
        logger.exception(e)
        state['status'] = "DOWN"
        state['status-class'] = "status-alert"

    return hdfs_id, state


def get_h3_status(args):
        job, job_id, server_url, server_user, server_pass = args
        # Set up connection to H3:
        h = hapy.Hapy(server_url, username=server_user, password=server_pass, timeout=TIMEOUT)
        state = {}
        try:
            logger.info("Getting status for job %s on %s" % (job, server_url))
            info = h.get_job_info(job)
            state['details'] = info
            if info.has_key('job'):
                state['status'] = info['job'].get("crawlControllerState", None)
                if not state['status']:
                    state['status'] = info['job'].get("statusDescription", None)
                state['status'] = state['status'].upper()
        except Exception as e:
            state['status'] = "DOWN"
            state['error'] = "Could not reach Heritrix! %s" % e
            # app.logger.exception(e)
        # Classify
        if state['status'] == "DOWN" or state['status'] == "EMPTY":
            state['status-class'] = "status-oos"
        elif state['status'] == "RUNNING":
            # Replacing RUNNING with docs/second rate
            rate = state['details']['job']['rateReport']['currentDocsPerSecond']
            state['rate'] = "%.1f" % float(rate)
            if rate < 1.0:
                state['status-class'] = "status-warning"
            else:
                state['status-class'] = "status-good"
        else:
            state['status-class'] = "status-warning"

        return job_id, state


def get_http_status(args):
    http, url = args
    state = {}
    try:
        logger.info("Getting status for %s" % url)
        r = s.get(url, allow_redirects=False, timeout=(TIMEOUT,TIMEOUT))
        logger.info("Got status %i" % r.status_code)
        logger.info("Got text %s" % r.text)
        state['status'] = "%s" % r.status_code
        if r.status_code / 100 == 2 or r.status_code / 100 == 3:
            state['response_time_seconds'] = r.elapsed.total_seconds()
            state['status'] = "%.3fs" % r.elapsed.total_seconds()
            state['status-class'] = "status-good"
        else:
            state['status-class'] = "status-warning"
            logger.error("ERROR was: %s" % r.text)
    except:
        state['status'] = "DOWN"
        state['status-class'] = "status-alert"

    return http, state


class RecordStatus(luigi.contrib.esindex.CopyToIndex):
    """
    Post this data to an appropriate Elasticsearch index.
    """
    task_namespace = 'monitor'
    date = luigi.DateMinuteParameter(default=datetime.datetime.today())

    host = os.environ.get('ELASTICSEARCH_HOST', 'localhost')
    port = os.environ.get('ELASTICSEARCH_PORT', 9200)
    doc_type = 'default'
    mapping = {"properties": {"service": {"type": "string", "analyzer": "keyword" }}}
    purge_existing_index = False
    index = "{}-{}".format(os.environ.get('ELASTICSEARCH_INDEX_PREFIX','pulse-'),
                             datetime.datetime.now().strftime('%Y-%m-%d'))

    def requires(self):
        return CheckStatus()

    def complete(self):
        """
        Always re-run this task.
        :return: False
        """
        return False

    def docs(self):
        with self.input().open() as f:
            status_doc = json.load(f)
        docs = []
        for status_type in status_doc:
            if "timestamp" == status_type:
                continue
            for service in status_doc[status_type]:
                doc = status_doc[status_type][service]
                # Add more default/standard fields:
                doc['service'] = service
                doc['type'] = status_type
                doc['timestamp'] = datetime.datetime.now().isoformat()
                # And append
                docs.append(doc)
        return docs


if __name__ == '__main__':
    os.environ['HERITRIX_PASSWORD'] = 'heritrix'
    os.environ['LUIGI_STATE_FOLDER'] = ".."
    luigi.run(['monitor.RecordStatus', '--local-scheduler'])
