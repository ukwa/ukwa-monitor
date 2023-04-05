import os, sys, logging
logger = logging.getLogger(__name__)


# functions -----------------
def configure(logFpfn, logLevel):
	scriptHandler = logging.FileHandler(logFpfn)
	formatter = logging.Formatter("[%(asctime)s %(funcName)s %(levelname)s]  %(message)s")
	scriptHandler.setFormatter(formatter)
	logging.root.addHandler(scriptHandler)
	logging.root.setLevel(logging.WARNING)
	logger = logging.getLogger('__main__')
	if logLevel == 'DEBUG': logging.getLogger().setLevel(logging.DEBUG)
	elif logLevel == 'INFO': logging.getLogger().setLevel(logging.INFO)
	else: logging.getLogger().setLevel(logging.WARNING)

def list_settings(settings):
	for _k in settings:
		_t = f"{_k}:"
		logger.info(f"{_t:15}\t{settings[_k]}")

def start():
	logger.info(f"Start {'-'*38}")

def stop():
	logger.info(f"Fin {'-'*40}")
