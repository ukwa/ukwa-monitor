import os
import sys
import logging
import configparser

stgFile = 'settings'
environ = ''

logger = logging.getLogger(__name__)



# functions ------------------------
def read(env='dev'):
	global stgFile
	global environ
	cfg = configparser.ConfigParser()

	# test settings file exists
	if os.path.isfile(stgFile):
		logger.debug(f"Reading [{env}] settings")
		# read environ settings file
		cfg.read(stgFile)

		if env in cfg.sections():
			environ = cfg[env]
		else:
			logger.error(f"[{env}] section missing from [{stgFile}] settings file")
			sys.exit()
	else:
		logger.error(f"[{stgFile}] settings file missing")
		sys.exit()

	logger.info(f"Using {env} environment settings")

def get(key):
	global environ
	if key in environ:
		logger.debug(f"setting {key}: [{environ[key]}]")
		return environ[key]
	else:
		logger.error(f"No cfg key [{key}] declared")
		sys.exit()
