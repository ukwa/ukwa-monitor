#!/usr/bin/env python
'''
Pushes LDL monitoring curls into prometheus
'''

import os, sys, logging
import socket, re
import configparser
import daemon, lockfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

from common import log

# globals
PIDFILE = f"{__file__}.pid"
LOCKFILE = f"{PIDFILE}.lock"
SETTINGSFILE = 'settings'
REQUEST = re.compile("^\w+\s+(/.+)\s+HTTP/\d.\d$")
LDLHOST = re.compile("^/wa/monitor\?host=(.+)$")

logger = logging.getLogger(__name__)
eset = ''


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
	global eset
	logger.debug(f"request: [{request}]")

	# get hostname, skip further processing if fail
	ldlHostMatch = LDLHOST.match(request)
	if ldlHostMatch:
		ldlHost = ldlHostMatch.group(1)
	else:
		logger.warning(f"Failed to get hostname from [{request}]")
		return
	logger.debug(f"ldlHost: [{ldlHost}]")

	# set pushgateway values
	registry = CollectorRegistry()
	g = Gauge(eset['metric'], eset['desc'], labelnames=['instance'], registry=registry)
	g.labels(instance=ldlHost).set(1)

	# push to prometheus service
	logger.debug(f"pushgtw: [{eset['pushgtw']}]")
	logger.info(f"Pushing to gateway [job={eset['job']}, metric={eset['metric']}, request={request}, instance={ldlHost}]")
	push_to_gateway(eset['pushgtw'], registry=registry, job=eset['job'])



# script --------------------------------------
def script(eset):
	log.configure_file(eset)

	# create web service
	monitorServer = HTTPServer((eset['hostname'], int(eset['port'])), webServer)
	logger.info(f"Started LDL monitoring web server [{eset['hostname']}:{eset['port']}]")
	try:
		monitorServer.serve_forever()
	except Exception as e:
		logger.warning(f"LDL monitoring web server exiting")
		logger.warning(f"Message: [{e}]")

	# close and end
	monitorServer.server_close()
	logger.info(f"Fin ----\n")

# main ----------------------------------------
if __name__ == '__main__':
	# check for lockfile
	if os.path.exists(LOCKFILE):
		print(f"Exiting as [{LOCKFILE}] exists")
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
