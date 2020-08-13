#!/usr/bin/env python
'''
Script to gather WA bespoke service stats and upload to push gateway service
'''

# python libraries
import logging
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# script packages
from common import log
from script import args, settings


# main ----------------------------------------
def main():
	log.configure(lvl='DEBUG')
	logging.info('Start ---------------------')


	# get script environ argument
	environ = args.passed()

	# read environment settings
	settings.read(env=environ)

	# loop through wa service stats

	# declare registry, inside loop for service
	registry = CollectorRegistry()

	# set/get stat values
	statJob = 'gilh'
	statName = statJob + '_' + 'unixtime'
	statDesc = 'set to current unix time'
	statValue = 824
	g = Gauge(statName, statDesc, registry=registry)
	g.set(statValue)
	logging.debug("Added job [{}] statName [{}] statValue [{}]".format(statJob, statName, statValue))

	# upload to push gateway
	push_to_gateway(settings.get('pushgtw'), registry=registry, job=statJob)

	logging.info('Fin')


if __name__ == '__main__':
	main()
