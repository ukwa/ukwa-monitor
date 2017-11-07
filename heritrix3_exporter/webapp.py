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


logger = logging.getLogger(__name__)

# Avoid hangs when systems are unreachable:
TIMEOUT = 10
socket.setdefaulttimeout(TIMEOUT)


class Heritrix3Collector(object):

    def load_as_json(self, filename):
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, filename)
        with open(file_path, 'r') as fi:
            return json.load(fi)

    def run_api_requests(self):
        services = self.load_as_json(os.path.join(os.path.dirname(__file__), 'crawl-jobs.json'))
        pool = Pool(20)

        # Parallel check for H3 job status:
        argsv = []
        for job in services:
            server_url = job['server']
            server_user = "admin"
            server_pass = os.environ['HERITRIX_PASSWORD']
            # app.logger.info(json.dumps(server, indent=4))
            services[job]['url'] = server_url
            argsv.append((services[job]['name'], job, server_url, server_user, server_pass))
        # Wait for all...
        results = pool.map(get_h3_status, argsv)
        for job, state in results:
            services[job]['state'] = state

        return services

    def collect(self):
        stats = self.run_api_requests()

        metric = GaugeMetricFamily(
            'jenkins_job_last_successful_build_timestamp_seconds',
            'Jenkins build timestamp in unixtime for lastSuccessfulBuild',
            labels=["jobname"])

        result = json.load(urllib2.urlopen(
            "http://jenkins:8080/api/json?tree="
            + "jobs[name,lastSuccessfulBuild[timestamp]]"))

        for job in result['jobs']:
            name = job['name']
            # If there's a null result, we want to export a zero.
            status = job['lastSuccessfulBuild'] or {}
            metric.add_metric([name], status.get('timestamp', 0) / 1000.0)

        yield metric


def dict_values_to_floats(d, k, excluding=list()):
    if d.has_key(k):
        for sk in d[k]:
            if not sk in excluding:
                d[k][sk] = float(d[k][sk])
                if math.isnan(d[k][sk]) or math.isinf(d[k][sk]):
                    d[k][sk] = None


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