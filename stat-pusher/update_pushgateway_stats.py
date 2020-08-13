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


	logging.info('Fin')


if __name__ == '__main__':
	main()
