import os
import sys
import logging
import configparser

stgFile = 'settings'
environ = ''

# functions ------------------------
def read(env='dev'):
	global stgFile
	global environ
	cfg = configparser.ConfigParser()

	# test settings file exists
	if os.path.isfile(stgFile):
		logging.debug(f"Reading [{env}] settings")
		# read environ settings file
		cfg.read(stgFile)

		if env in cfg.sections():
			environ = cfg[env]
		else:
			logging.error(f"[{env}] section missing from [{stgFile}] settings file")
			sys.exit()
	else:
		logging.error(f"[{stgFile}] settings file missing")
		sys.exit()

	logging.info(f"Using {env} environment settings")

def get(key):
	global environ
	if key in environ:
		logging.debug(f"setting {key}: [{environ[key]}]")
		return environ[key]
	else:
		logging.error(f"No cfg key [{key}] declared")
		sys.exit()
