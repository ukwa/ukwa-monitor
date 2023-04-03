import os, sys, logging
logger = logging.getLogger(__name__)


# functions -----------------
def start(logFpfn, logLevel):
	scriptHandler = logging.FileHandler(logFpfn)
	formatter = logging.Formatter("[%(asctime)s %(funcName)s %(levelname)s]  %(message)s")
	logging.root.addHandler(scriptHandler)
	logging.root.setLevel(logging.WARNING)
	logger = logging.getLogger('__main__')
	if logLevel == 'DEBUG': logging.getLogger().setLevel(logging.DEBUG)
	elif logLevel == 'INFO': logging.getLogger().setLevel(logging.INFO)
	else: logging.getLogger().setLevel(logging.WARNING)
	logger.info(f"Start {'-'*38}")

def stop():
	logger.info(f"Fin {'-'*40}")
