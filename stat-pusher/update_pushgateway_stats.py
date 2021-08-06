#!/usr/bin/env python
'''
Script to gather WA bespoke service stats and upload to push gateway service
'''

# python libraries
import logging
import os
import sys
import json
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# script packages
from common import log
from script import args, settings, stat_values


# main ----------------------------------------
def main():
	log.configure(lvl='INFO')
	logging.info('Start ---------------------')


	# get script environ argument
	environ = args.passed()

	# read environment settings
	settings.read(env=environ)

	# read stats file
	statTests = ''
	if os.path.isfile(settings.get('statsfile')):
		try:
			with open(settings.get('statsfile'), 'r') as infile:
				statTests = json.load(infile)
		except Exception as e:
			logging.error(f"Failed to read statsfile [{settings.get('statsfile')}]\n[{e}]")
			sys.exit()
	else:
		logging.error(f"statsfile [{settings.get('statsfile')}] to test for [{environ}] environment missing")	
		sys.exit()

	# loop through wa service stats
	for job in statTests:
		# declare registry per job, inside loop for each stat:
		registry = CollectorRegistry()
		# Store gauges by name, so we can re-use the same metrics with different labels:
		gauges = {}
		
		for stat in statTests[job]:
			# get stat details
			try:
				name = job + '_' + stat
				# Allow name to be overridden in config:
				if 'name' in statTests[job][stat]:
					name = statTests[job][stat]['name']
				host = statTests[job][stat]['host']
				label = statTests[job][stat]['label']
				desc = statTests[job][stat]['desc']
				kind = statTests[job][stat]['kind']
				uri = statTests[job][stat]['uri']
				match = statTests[job][stat]['match']
			except Exception as e:
				logging.error(f"Children of job [{job}] stat [{stat}] missing\n[{e}]")
				sys.exit()

			# Get the value and send it, but cope if there are no matches:
			try:
				# get stat value
				if kind == 'json':
					value = stat_values.get_json_value(uri, match)

				# set pushgateway submission details
				if name in gauges:
					g = gauges[name]
				else:
					g = Gauge(name, desc, labelnames=['instance','label'], registry=registry)
					gauges[name] = g
				g.labels(instance=host,label=label).set(value)
				logging.info(f"Added job [{job}] host [{host}] name [{name}] label [{label}] value [{value}]")
			except Exception as e:
				logging.error(f"Match not found for job [{job}] stat [{stat}] missing\n[{e}]")

		# upload to push gateway
		push_to_gateway(settings.get('pushgtw'), registry=registry, job=job)
		logging.info(f"Uploaded all [{job}] stats.")

	logging.info('Fin')


if __name__ == '__main__':
	main()
