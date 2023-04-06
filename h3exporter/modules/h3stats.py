import os, sys, logging
logger = logging.getLogger(__name__)
import requests
import json
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway


# internal functions --------
def _get_url(url):
	'''
	Seems that hadoop3/jmx "json" isn't wellformed, at least according to
	https://jsononline.net/string-to-json and in testing.
	So not using qs as requests parameter
	(https://docs.python-requests.org/en/latest/user/quickstart/#passing-parameters-in-urls)
	but instead using complete url in in requests.get().
	'''
	res = False
	logger.debug(f"Getting [{url}]")
	try:
		res = requests.get(url)
	except Exception as e:
		logger.error(f"Failed to get [{url}]")
		return False

	# check response
	if res.status_code != requests.codes.ok:
		logger.error(f"Response code not okay for [{url}]")
		logger.error(f"Response code: [{res.status_code}]")
		return False
	else:
		return res

# functions -----------------
def get_hadoop_stats(settings):
	status = 0
	usedPercent = 0
	deadNodes = 0
	underReplicated = 0

	# get urls, check response, gather values
	for url in [ settings['namenodeinfo'], settings['fsnamesystem'] ]:
		res = _get_url(url)
		if not res:
			return 1, False, False, False

		# annoyingly, res.json() doesn't create nested json, just series of key/value strings
		# Consequently, Hadoop3 json blobs (like DeadNodes) must be converted again into json
		# This block is wrapped in try/except in case the returned dataset is unexpected
		try:
			resJson = res.json()
			if 'beans' in resJson:
				beans = resJson['beans']
				for _dbeans in beans:
					if 'PercentUsed' in _dbeans:
						usedPercent = float(_dbeans['PercentUsed'])
					if 'DeadNodes' in _dbeans:
						deadNodes = len(json.loads(_dbeans['DeadNodes']))
					if 'UnderReplicatedBlocks' in _dbeans:
						underReplicated = int(_dbeans['UnderReplicatedBlocks'])
			else:
				logger.warning(f"No 'beans' in resJson: {resJson}")
				status = 1
		except Exception as e:
			logger.warning(f"Failed traversing response json [{e}]")
			status = 1

	logger.debug(f"usedPercent:\t\t [{usedPercent}]")
	logger.debug(f"deadNodes:\t\t [{deadNodes}]")
	logger.debug(f"underReplicated:\t [{underReplicated}]")
	return status, usedPercent, deadNodes, underReplicated

def send_hadoop_stats(settings, usedPercent, deadNodes, underReplicated):
	registry = CollectorRegistry()
	g = Gauge(settings['metric'], settings['desc'], labelnames=['instance'], registry=registry)
	g.labels(instance='usedPercent').set(usedPercent)
	g.labels(instance='deadNodes').set(deadNodes)
	g.labels(instance='underReplicatedBlocks').set(underReplicated)

	# push to prometheus
	try:
		push_to_gateway(settings['pushgtw'], registry=registry, job=settings['job'])
		logger.info(f"Pushed to gateway {settings['pushgtw']} {usedPercent}%, deadnodes {deadNodes}, under-rep {underReplicated}")
	except Exception as e:
		logger.warning(f"Failed push to gateway\nError: [{e}]")
