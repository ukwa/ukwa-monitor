import os, sys
import socket
import configparser

CONFIG = 'config/settings'

# functions -----------------
def settings_read():
	global CONFIG
	config = {}

	# exit if no configuration file
	if not os.path.exists(CONFIG):
		print(f"ERROR: configuration settings file [{CONFIG}] missing")
		sys.exit(1)

	# get hostname, to determine appropriate settings
	_hn = socket.gethostname()
	if _hn.startswith('dev'): senv = 'dev'
	elif _hn.startswith('beta'): senv = 'beta'
	else: senv = 'prod'

	# parse config
	cfg = configparser.ConfigParser()
	cfg.read(CONFIG)

	# check senv (service environment) settings in config
	if senv not in cfg:
		print(f"ERROR: No service env [{senv}] settings in [{CONFIG}]")
		sys.exit(1)

	# gather settings
	config['senv'] = senv
	for _k in cfg[senv]:
		config[_k] = cfg[senv][_k]

	return config
