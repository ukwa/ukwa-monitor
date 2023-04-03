#!/usr/bin/env python3
'''
Simple python3 script to report WA hadoop3 stats scrapped from namenode /jmx
'''
import os, sys, logging
import __main__
#import daemon, lockfile, signal
from modules import pid

# globals 
logger = logging.getLogger(__name__)
SCRIPTNAME = os.path.splitext(os.path.basename(__main__.__file__))[0]
PIDFILE = f"{SCRIPTNAME}.pid"
UID = os.getuid()
GID = os.getgid()



# script --------------------
# IF/WHEN UPGRADED TO PY3.7 AND python-daemon, THE DAEMONIZED SCRIPT IS NOT AWARE OF WRAPPER OUTSIDE OF script()
# SO MODULES IMPORTED WITHIN script()
def script():
	from modules import config
	from modules import log
	from modules import srv

	# read service environment variables, configure logger
	settings = config.settings_read()
	log.start(settings['logfpfn'], settings['loglevel'])

	# create and bind service socket
	srv.bind_to_socket(settings)

	while True:
		# listen for request
		request = srv.listen_for_request()



if __name__ == '__main__':
	if os.path.exists(f"{PIDFILE}.lock"):
		print(f"ERROR: pid file [{PIDFILE}.lock] exists")
		sys.exit(1)

# IF/WHEN UPGRADE TO PY3.7, USE python-daemon PACKAGE
#	with daemon.DaemonContext(stdout=sys.stdout, stderr=sys.stderr, uid=UID, gid=GID, pidfile=lockfile.FileLock(PIDFILE)):
#		script()

	pid.create(f"{PIDFILE}.lock")
	script()
	pid.delete(f"{PIDFILE}.lock")
