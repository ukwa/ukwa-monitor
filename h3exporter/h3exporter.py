#!/usr/bin/env python3
'''
Simple python3 script to report WA hadoop3 stats scrapped from namenode /jmx
Runs as a daemon via systemctl --user
'''
import os, sys, logging
import __main__
import time

# script modules
from modules import config
from modules import log
from modules import h3stats

# globals 
logger = logging.getLogger(__name__)
SCRIPTNAME = os.path.splitext(os.path.basename(__main__.__file__))[0]
CONFIG = '/home/monitor/github/ukwa-monitor/h3exporter/config/settings'


# script --------------------
def script():
	# read config
	global CONFIG
	settings = config.settings_read(CONFIG)

	# read service environment variables, configure logger
	log.configure(settings['logfpfn'], settings['loglevel'])
	log.start()
	log.list_settings(settings)

	# previous values
	prevUsedPercent = prevDeadNodes = prevUnderReplicated = 0
	while True:
		# get hadoop3 stats
		failStatus, usedPercent, deadNodes, underReplicated = h3stats.get_hadoop_stats(settings)
		if failStatus:
			logger.warning(f"Failed to get hadoop3 stats")
			continue

		# send stats to prometheus if change
		if ( int(usedPercent) != int(prevUsedPercent) ) \
			or ( deadNodes != prevDeadNodes ) \
			or ( underReplicated != prevUnderReplicated):
			h3stats.send_hadoop_stats(settings, usedPercent, deadNodes, underReplicated)

			# update previous values
			prevUsedPercent = usedPercent
			prevDeadNodes = deadNodes
			prevUnderReplicated = underReplicated

		# sleep until next time to send hadoop3 stats
		time.sleep(int(settings['sleep']))

	log.stop('Unexpected stop')

if __name__ == '__main__':
	script()
