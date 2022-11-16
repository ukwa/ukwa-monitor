#!/usr/bin/env python
'''
Pushes LDL monitoring curls into prometheus
'''

import os, sys, logging
import socket, re
import configparser
import daemon, lockfile
from http.server import BaseHTTPRequestHandler, HTTPServer
import datetime
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

from common import log

# globals
logger = logging.getLogger(__name__)

PIDFILE = f"{__file__}.pid"
LOCKFILE = f"{PIDFILE}.lock"
SETTINGSFILE = 'settings'
REQUEST = re.compile("^\w+\s+(/.+)\s+HTTP/\d.\d$")
LDLHOST = re.compile("^/wa/monitor\?host=(.+)$")
YMDHM = '%Y%m%d%H%M'
SCHEDULE = 15
INSTANCE = 'ldl_connection_count'

# environ settings
eset = ''
# dldl - dictionary of latest LDL connections
dldl = {'DLS-BSP-WB01':0, 'DLS-BSP-WB02':0, 'DLS-BSP-WB03':0, 'DLS-BSP-WB04':0, 'DLS-LON-WB01':0, 'DLS-LON-WB02':0, 'DLS-LON-WB03':0, 'DLS-LON-WB04':0, 'DLS-NLS-WB01':0, 'DLS-NLW-WB01':0}
# last YYYYMMDDHHMM push to gateway happened
pushymdhm = 0


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

def _process_request(request):
	global YMDHM
	global SCHEDULE
	global INSTANCE
	global eset
	global dldl
	global pushymdhm
	logger.debug(f"Received request:  {request}")

	# get hostname, skip further processing if fail
	ldlHostMatch = LDLHOST.match(request)
	if ldlHostMatch:
		ldlHost = ldlHostMatch.group(1)
	else:
		logger.warning(f"Failed to get hostname from [{request}]")
		return

	# get current time
	nowymdhm = int((datetime.datetime.now()).strftime(YMDHM))

	# update LDL in dldl
	dldl[ldlHost] = nowymdhm

	# on schedule, report LDL connection status to pushgateway
	logger.debug(f"dldl {dldl}")
	if (nowymdhm - pushymdhm) > SCHEDULE:
		# count LDLs responded in last SCHEDULE period
		up = 0
		for _ldl in dldl:
			if (nowymdhm - dldl[_ldl]) < SCHEDULE: up += 1
			else: logger.debug(f"LDL [{_ldl}] hasn't curled in {SCHEDULE} minutes")

		# set pushgateway values and push to prometheus service
		registry = CollectorRegistry()
		g = Gauge(eset['metric'], eset['desc'], labelnames=['instance'], registry=registry)
		g.labels(instance=INSTANCE).set(up)
		push_to_gateway(eset['pushgtw'], registry=registry, job=eset['job'])

		# write latest push to output file (done via output rather than log so log doesn't 
		# become huge over time)
		with open(eset['output'], 'w') as out:
			out.write(f"Output datestamp:\t{nowymdhm}\n")
			out.write(f"Pushing to gateway:\tjob={eset['job']}, instance={INSTANCE}, recent_connections={up}\n")
			for _ldl in dldl: out.write(f"\t{_ldl}:\t{dldl[_ldl]}\n")
			out.write("\n")
		out.close()

		# store push time
		pushymdhm = nowymdhm

# script --------------------------------------
def script(eset):
	log.configure_file(eset)

	# create web service
	monitorServer = HTTPServer((eset['hostname'], int(eset['port'])), webServer)
	logger.info(f"Started LDL monitoring web server:  {eset['hostname']}:{eset['port']}")
	try:
		monitorServer.serve_forever()
	except Exception as e:
		logger.warning(f"LDL monitoring web server exiting")
		logger.warning(f"Message: [{e}]")

	# close and end
	monitorServer.server_close()
	logger.warning(f"//////////////////// RUNNING AS DAEMON - SHOULD NEVER FINISH /////////////////////\n")

# main ----------------------------------------
if __name__ == '__main__':
	# check for lockfile
	if os.path.exists(LOCKFILE):
		print(f"Exiting as [{LOCKFILE}] exists, service already be running")
		sys.exit(1)

	# get swarm environment
	senvMatch = re.match('^(dev|beta|prod)', socket.gethostname())
	if senvMatch:
		environ = senvMatch.group(1)
	else:
		print(f"Swarm environment not identified from [{socket.gethostname()}]")
		sys.exit(1)

	# read environment settings
	eset = _read_settings(environ)

	# run daemon
	with daemon.DaemonContext(
		stdout = sys.stdout,
		stderr = sys.stderr,
		uid = int(eset['uid']),
		gid = int(eset['gid']),
		pidfile = lockfile.FileLock(PIDFILE)
	):
		script(eset)
