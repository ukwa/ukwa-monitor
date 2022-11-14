'''
Common/non-script specific functions
'''

import logging

def configure(lvl='INFO'):
	logging.basicConfig(format='[%(asctime)s %(funcName)s %(levelname)s] %(message)s', level=lvl)

def configure_file(eset):
	scriptHandler = logging.FileHandler(eset['logfpfn'])
	formatter = logging.Formatter("[%(asctime)s %(funcName)s %(levelname)s]  %(message)s")
	scriptHandler.setFormatter(formatter)
	logging.root.addHandler(scriptHandler)
	logging.root.setLevel(logging.WARNING)
	if eset['loglevel'] == 'ERROR': logging.getLogger().setLevel(logging.ERROR)
	elif eset['loglevel'] == 'WARNING': logging.getLogger().setLevel(logging.WARNING)
	elif eset['loglevel'] == 'DEBUG': logging.getLogger().setLevel(logging.DEBUG)
	else: logging.getLogger().setLevel(logging.INFO)
	logger = logging.getLogger('__main__')
