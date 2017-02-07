import os
import json
import luigi
import socket
import logging
import requests
import datetime
import xml.etree.ElementTree as etree
from hapy import hapy

logger = logging.getLogger('luigi-interface')

# Avoid hangs when systems are unreachable:
TIMEOUT = 6
socket.setdefaulttimeout(TIMEOUT)


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

        for job in services.get('jobs', []):
            server = services['servers'][services['jobs'][job]['server']]
            server_url = server['url']
            server_user =  server['user']
            server_pass = os.environ['HERITRIX_PASSWORD']
            # app.logger.info(json.dumps(server, indent=4))
            services['jobs'][job]['state'] = self.get_h3_status(services['jobs'][job]['name'], server_url, server_user, server_pass)
            services['jobs'][job]['url'] = server_url

        for queue in services.get('queues', []):
            server_prefix = services['servers'][services['queues'][queue]['server']]['prefix']
            services['queues'][queue]['prefix'] = server_prefix
            services['queues'][queue]['state'] = self.get_queue_status(services['queues'][queue]['name'], server_prefix)

        for http in services.get('http', []):
            services['http'][http]['state'] = self.get_http_status(services['http'][http]['url'])

        for hdfs in services.get('hdfs', []):
            services['hdfs'][hdfs]['state'] = self.get_hdfs_status(services['hdfs'][hdfs])

        with self.output().open('w') as f:
            f.write('{}'.format(json.dumps(services, indent=4)))

    def get_h3_status(self, job, server_url, server_user, server_pass):
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
        if state['status'] == "DOWN":
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

        return state

    def get_queue_status(self, queue, server_prefix):
        state = {}
        try:
            logger.info("Getting status for queue %s on %s" % (queue, server_prefix))
            qurl = '%s%s' % (server_prefix, queue)
            # app.logger.info("GET: %s" % qurl)
            r = requests.get(qurl, timeout=TIMEOUT)
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

        return state

    def get_http_status(self, url):
        state = {}
        try:
            logger.info("Getting status for %s" % (url))
            r = requests.get(url, allow_redirects=False, timeout=TIMEOUT)
            state['status'] = "%s" % r.status_code
            if r.status_code / 100 == 2 or r.status_code / 100 == 3:
                state['status'] = "%.3fs" % r.elapsed.total_seconds()
                state['status-class'] = "status-good"
            else:
                state['status-class'] = "status-warning"
        except:
            state['status'] = "DOWN"
            state['status-class'] = "status-alert"

        return state

    def get_hdfs_status(self, hdfs):
        state = {}
        try:
            logger.info("Getting status for hdfs %s" % (hdfs))
            r = requests.get(hdfs['url'], timeout=TIMEOUT)
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

        return state

    def load_as_json(self, filename):
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, filename)
        with open(file_path, 'r') as fi:
            return json.load(fi)


if __name__ == '__main__':
    os.environ['HERITRIX_PASSWORD'] = 'heritrix'
    os.environ['LUIGI_STATE_FOLDER'] = ".."
    luigi.run(['monitor.CheckStatus', '--local-scheduler'])
