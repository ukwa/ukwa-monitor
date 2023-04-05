#!/usr/bin/env python3
'''
Simple python3 script to report WA hadoop3 stats scrapped from namenode /jmx
Runs as a daemon via systemctl --user
'''
import os, sys, logging
import __main__
from http.server import BaseHTTPRequestHandler, HTTPServer
import re

# script modules
from modules import config
from modules import log

# globals 
logger = logging.getLogger(__name__)
SCRIPTNAME = os.path.splitext(os.path.basename(__main__.__file__))[0]
CONFIG = 'config/settings'
REQUEST = re.compile("^\w+\s+(/.+)\s+HTTP/\d.\d$")


# classes and functions -----
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
			# process request
			if request:
				process_request(request)
		except Exception as e:
			logger.warning(f"Failed to match request in [{self.requestline}]")

def process_request(request):
	logger.debug(f"Received request: [{request}]")


# script --------------------
def script():
	global CONFIG

	# read service environment variables, configure logger
	settings = config.settings_read(CONFIG)
	log.configure(settings['logfpfn'], settings['loglevel'])
	log.start()
	log.list_settings(settings)

	# create web service
	monitorServer = HTTPServer((settings['host'], int(settings['port'])), webServer)
	logger.info(f"Started Hadoop3 stats web server:  {settings['host']}:{settings['port']}")
	try:
		monitorServer.serve_forever()
	except Exception as e:
		logger.warning(f"Hadoop3 stats web server exiting")
		logger.warning(f"Message: [{e}]")

	# close and end
	monitorServer.server_close()
	logger.error(f"//////////////////// RUNNING AS DAEMON - SHOULD NEVER FINISH /////////////////////\n")


if __name__ == '__main__':
	script()
