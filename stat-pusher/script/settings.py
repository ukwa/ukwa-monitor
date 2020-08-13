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
		logging.debug("Reading [{}] settings".format(env))
		# read environ settings file
		cfg.read(stgFile)

		if env in cfg.sections():
			environ = cfg[env]
	else:
		logging.error("[{}] settings file missing".format(stgFile))
		sys.exit()

	logging.info("Using {} environment settings".format(env))

def get(key):
	global environ
	if key in environ:
		logging.debug("setting {}: {}".format(key, environ[key]))
		return environ[key]
	else:
		logging.error("No cfg key [{}] declared".format(key))
		sys.exit()
