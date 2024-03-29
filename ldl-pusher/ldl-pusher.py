#!/usr/bin/env python
'''
Pushes LDL monitoring curls into prometheus
'''

import os, sys, logging
import socket, re
import configparser
from http.server import BaseHTTPRequestHandler, HTTPServer
import datetime
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

from common import log

# globals
logger = logging.getLogger(__name__)

SETTINGSFILE = 'settings'
REQUEST = re.compile("^\w+\s+(/.+)\s+HTTP/\d.\d$")
HOSTREQ = re.compile("^/wa/monitor\?host=(.+)$")
LDLHOST = re.compile("^DLS-(BSP|LON|NLS|NLW)-WB0[1-4]$")
YMDHM = '%Y%m%d%H%M'

# environ settings
eset = ''
# dldl - dictionary of latest LDL connections
dldl = {'DLS-BSP-WB01':0, 'DLS-BSP-WB02':0, 'DLS-BSP-WB03':0, 'DLS-BSP-WB04':0, 'DLS-LON-WB01':0, 'DLS-LON-WB02':0, 'DLS-LON-WB03':0, 'DLS-LON-WB04':0, 'DLS-NLS-WB01':0, 'DLS-NLW-WB01':0}
# last YYYYMMDDHHMM push to gateway happened
pushymdhm = datetime.datetime.now()


# classes and functions -----------------------
def _read_settings(environ):
	cfg = configparser.ConfigParser()
	if os.path.isfile(SETTINGSFILE):
		cfg.read(SETTINGSFILE)
		if environ in cfg.sections():
			return cfg[environ]
		else:
			print(f"Section [{environ}] missing from [{SETTINGSFILE}] settings file")
			sys.exit(1)
	else:
		print(f"Settings file [{SETTINGSFILE}] missing")
		sys.exit(1)

class webServer(BaseHTTPRequestHandler):
	global REQUEST
	def _set_headers(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()

	def do_HEAD(self):
		self._set_headers()

	def do_GET(self):
		self._set_headers()

		# grab request
		try:
			reqMatch = REQUEST.match(self.requestline)
			request = reqMatch.group(1)
		except Exception as e:
			logger.warning(f"Failed to match request in [{self.requestline}]")

		# process request
		_process_request(request)

def _time_gap(now, push):
	mins = 0
	try:
		_td = (now - push)	# _td = time difference
		mins, _secs = divmod(_td.days * (24 * 60 * 60) + _td.seconds, 60)
		logger.debug(f"time difference _td: [{_td} /{type(_td)}]  mins [{mins} /{type(mins)}]")
	except Exception as e:
		logger.warning(f"Caught datetime delta issue\nError: [{e}]")
	return mins

def _process_request(request):
	global HOSTREQ
	global LDLHOST
	global YMDHM
	global eset
	global dldl
	global pushymdhm
	logger.debug(f"Received request:  {request}  pushymdhm [{pushymdhm}]")

	# get hostname, skip further processing if fail
	hostReqMatch = HOSTREQ.match(request)
	if hostReqMatch:
		hostReq = hostReqMatch.group(1)
	else:
		logger.warning(f"Failed to get hostname from [{request}]")
		return

	# check hostname is LDL VM
	ldlHostMatch = LDLHOST.match(hostReq)
	if ldlHostMatch:
		ldlHost = hostReq
	else:
		logger.warning(f"Skipping non LDL DLS VM hostname [{hostReq}]")
		return

	# get current time
	nowymdhm = datetime.datetime.now()

	# update LDL in dldl
	dldl[ldlHost] = nowymdhm

	# on schedule, report LDL connection status to pushgateway
	schedule = int(eset['schedule'])
	timeGapSincePushMins = _time_gap(nowymdhm, pushymdhm)
	if timeGapSincePushMins < schedule:
		logger.debug(f"Insufficient time gap: [{nowymdhm.strftime(YMDHM)} - {pushymdhm.strftime(YMDHM)}] = [{timeGapSincePushMins}], schedule [{schedule}]")
	else:
		logger.debug(f"Pushing to [{eset['pushgtw']}]")
		logger.debug(f"Schedule: [{nowymdhm.strftime(YMDHM)} - {pushymdhm.strftime(YMDHM)}] = [{timeGapSincePushMins}], schedule [{schedule}]")
		logger.debug(f"dldl {dldl}")

		# set registry and gauge for metrics
		registry = CollectorRegistry()
		g = Gauge(eset['metric'], eset['desc'], labelnames=['instance'], registry=registry)

		# write-open output file for local record of metrics
		## (done via output rather than log so that log doesn't become huge over time)
		upCount = 0
		with open(eset['output'], 'w') as out:
			out.write(f"Output datestamp:\t{nowymdhm.strftime(YMDHM)}\n")

			# for each host, set metric
			for _ldl in dldl:
				if dldl[_ldl]:
					logger.debug(f"Adding [{_ldl}] instance")

					# get time gap in mins between time now and last _ldl curl recived
					_tg = _time_gap(nowymdhm, dldl[_ldl])

					# set _ldl metric
					up = 0
					if _tg < schedule: up = 1
					else: logger.debug(f"LDL [{_ldl}] hasn't curled in {schedule} minutes")
					g.labels(instance=_ldl).set(up)
					upCount += up
					logger.debug(f"Collating ldl updates: [{_ldl}]  [{_tg}]  [{up}/{upCount}]")

					# write result to output
					out.write(f"\t{_ldl}:\t{dldl[_ldl]}\tRecent [{_tg < schedule}]\n")
				else:
					logger.debug(f"Skipping [{_ldl}] as no date value")

			out.write(f"Pushed to gateway:\tjob={eset['job']}, recent_connections={upCount}\n")
			out.write("\n")

		# close output
		out.close()

		# push to prometheus service
		logger.debug(f"Pushing to gateway:\tjob={eset['job']}, recent_connections={upCount}\n")
		push_to_gateway(eset['pushgtw'], registry=registry, job=eset['job'])
		logger.debug(f"Pushed to gateway:\tjob={eset['job']}, recent_connections={upCount}\n")

		# store push time
		pushymdhm = nowymdhm

# script --------------------------------------
def script(eset):
	global pushymdhm
	log.configure_file(eset)

	# create web service
	monitorServer = HTTPServer((eset['hostname'], int(eset['port'])), webServer)
	logger.info(f"Started LDL monitoring web server:  {eset['hostname']}:{eset['port']}")
	logger.info(f"Pushing to {eset['pushgtw']} gateway every {eset['schedule']} minutes")
	try:
		monitorServer.serve_forever()
	except Exception as e:
		logger.warning(f"LDL monitoring web server exiting")
		logger.warning(f"Message: [{e}]")

	# close and end
	monitorServer.server_close()
	logger.error(f"//////////////////// RUNNING AS DAEMON - SHOULD NEVER FINISH /////////////////////\n")

# main ----------------------------------------
if __name__ == '__main__':
	# get swarm environment
	senvMatch = re.match('^(dev|beta|prod|monitor)', socket.gethostname())
	if senvMatch:
		environ = senvMatch.group(1)
	else:
		print(f"Swarm environment not identified from [{socket.gethostname()}]")
		sys.exit(1)
	if environ == 'monitor': environ = 'prod'

	# read environment settings
	eset = _read_settings(environ)

	# run 
	script(eset)
