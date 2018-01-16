import os
import math
import json
import time
import socket
import urllib2
from multiprocessing import Pool, Process
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY
import logging
from hapy import hapy
from multiprocessing import Pool, Process

# Avoid warnings about certs.
import urllib3
urllib3.disable_warnings()


logger = logging.getLogger(__name__)

# Avoid hangs when systems are unreachable:
TIMEOUT = 10
socket.setdefaulttimeout(TIMEOUT)


class Heritrix3Collector(object):

    def __init__(self):
        self.pool = Pool(20)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pool.close()

    def load_as_json(self, filename):
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, filename)
        with open(file_path, 'r') as fi:
            return json.load(fi)

    def lookup_services(self):
        # Load the config file:
        service_list = self.load_as_json(os.path.join(os.path.dirname(__file__), 'crawl-jobs.json'))

        # Find the services. If there are any DNS Service Discovery entries, filter them out.
        services = []
        dns_sd = []
        for job in service_list:
            if 'dns_sd_name' in job:
                dns_sd.append(job)
            else:
                services.append(job)

        # For each DNS SD entry, use DNS to discover the service:
        for job in dns_sd:
            dns_name = job['dns_sd_name']
            try:
                # Look up service IP addresses via DNS:
                (hostname, alias, ipaddrlist) = socket.gethostbyname_ex(dns_name)
                for ip in ipaddrlist:
                    # Find the IP-level hostname via reverse lookup:
                    (r_hostname, r_aliaslist, r_ipaddrlist) = socket.gethostbyaddr(ip)
                    dns_job = dict(job)
                    dns_job['url'] = 'https://%s:8443/' % r_hostname
                    dns_job['id'] = r_hostname
                    services.append(dns_job)
            except socket.gaierror as e:
                print(e)
                pass

        return services

    def run_api_requests(self):
        # Find the list of Heritrixen to talk to
        services = self.lookup_services()

        # Parallel check for H3 job status:
        argsv = []
        for job in services:
            server_url = job['url']
            server_user = os.getenv('HERITRIX_USERNAME', "admin")
            server_pass = os.getenv('HERITRIX_PASSWORD', "heritrix")
            # app.logger.info(json.dumps(server, indent=4))
            argsv.append((job['id'], job['job_name'], server_url, server_user, server_pass))
        # Wait for all...
        result_list = self.pool.map(get_h3_status, argsv)
        results = {}
        for job, status in result_list:
            results[job] = status

        # Merge the results in:
        for job in services:
            job['state'] = results[job['id']]

        return services

    def collect(self):
        stats = self.run_api_requests()

        m_uri_down = GaugeMetricFamily(
            'heritrix3_crawl_job_uris_downloaded_total',
            'Total URIs downloaded by a Heritrix3 crawl job',
            labels=["job-name", "deployment", "status", "id"])

        m_uri_known = GaugeMetricFamily(
            'heritrix3_crawl_job_uris_known_total',
            'Total URIs discovered by a Heritrix3 crawl job',
            labels=["job-name", "deployment", "status", "id"])

        result = self.run_api_requests()

        for job in result:
            #print(json.dumps(job))
            # Get hold of the state and flags etc
            name = job['job_name']
            id = job['id']
            deployment = job['deployment']
            state = job['state'] or {}
            status = state['status'] or None

            # Get the URI metrics
            try:
                docs_total = state['details']['job']['uriTotalsReport']['downloadedUriCount'] or 0.0
                known_total = state['details']['job']['uriTotalsReport']['totalUriCount'] or 0.0
            except KeyError:
                docs_total = 0.0
                known_total = 0.0
                print("Printing results in case there's an error:")
                print(json.dumps(job))
            m_uri_down.add_metric([name,deployment, status, id], docs_total)
            m_uri_known.add_metric([name,deployment, status, id], known_total)

            #metric.add_metric([name], status.get('timestamp', 0) / 1000.0)

        yield m_uri_down
        yield m_uri_known



def dict_values_to_floats(d, k, excluding=list()):
    if d.has_key(k):
        for sk in d[k]:
            if not sk in excluding:
                d[k][sk] = float(d[k][sk])
                if math.isnan(d[k][sk]) or math.isinf(d[k][sk]):
                    d[k][sk] = None


def get_h3_status(args):
    job_id, job_name, server_url, server_user, server_pass = args
    # Set up connection to H3:
    h = hapy.Hapy(server_url, username=server_user, password=server_pass, timeout=TIMEOUT)
    state = {}
    try:
        logger.info("Getting status for job %s on %s" % (job_name, server_url))
        info = h.get_job_info(job_name)
        state['details'] = info
        if info.has_key('job'):
            state['status'] = info['job'].get("crawlControllerState", None)
            if not state['status']:
                state['status'] = info['job'].get("statusDescription", None)
            state['status'] = state['status'].upper()
            # Also look to store useful numbers as actual numbers:
            dict_values_to_floats(info['job'], 'loadReport')
            dict_values_to_floats(info['job'], 'heapReport')
            dict_values_to_floats(info['job'], 'rateReport')
            dict_values_to_floats(info['job'], 'sizeTotalsReport')
            dict_values_to_floats(info['job'], 'uriTotalsReport')
            dict_values_to_floats(info['job'], 'frontierReport', ['lastReachedState'])
    except Exception as e:
        state['status'] = "DOWN"
        state['error'] = "Exception while checking Heritrix! %s" % e
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


if __name__ == "__main__":
    REGISTRY.register(Heritrix3Collector())
    start_http_server(9118)
    while True: time.sleep(1)
