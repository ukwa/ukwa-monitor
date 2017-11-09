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


class HDFSCollector(object):

    def load_as_json(self, filename):
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, filename)
        with open(file_path, 'r') as fi:
            return json.load(fi)

    def run_api_requests(self):
        services = self.load_as_json(os.path.join(os.path.dirname(__file__), 'hdfs-services.json'))
        pool = Pool(20)

        # Parallel check for H3 job status:
        argsv = []
        for hdfs in services.get('hdfs', []):
            argsv.append((hdfs, services['hdfs'][hdfs]['url']))
        # Wait for all...
        results = pool.map(get_hdfs_status, argsv)
        for hdfs, state in results:
            services['hdfs'][hdfs]['state'] = state

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
            state['percent-used'] = float(percent.replace("%",""))
            state['remaining'] = tree.xpath("//div[@id='dfstable']//tr[4]/td[3]")[0].text.replace(" ", "")
            underr = int(tree.xpath("//div[@id='dfstable']//tr[10]/td[3]")[0].text)
            state['under-replicated-blocks'] = underr
            state['live-nodes'] = int(tree.xpath("//div[@id='dfstable']//tr[7]/td[3]")[0].text)
            state['dead-nodes'] = int(tree.xpath("//div[@id='dfstable']//tr[8]/td[3]")[0].text)
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

if __name__ == "__main__":
    REGISTRY.register(HDFSCollector())
    start_http_server(9118)
    while True: time.sleep(1)