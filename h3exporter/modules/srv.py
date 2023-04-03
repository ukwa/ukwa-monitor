import os, sys, logging
logger = logging.getLogger(__name__)
import zmq

ZMQSOCKET = ''

# functions -----------------
def bind_to_socket(settings):
	global ZMQSOCKET
	protocol = settings['protocol']
	host = settings['host']
	port = settings['port']
	try:
		_context = zmq.Context()
		_socket = _context.socket(zmq.REP)
		_socket.bind(f"{protocol}://{host}:{port}")
	except Exception as e:
		logger.error(f"Failed to bind socket")
		logger.error(f"protocol:\t [{protocol}]")
		logger.error(f"host:\t [{host}]")
		logger.error(f"port:\t [{port}]")
		logger.error(f"Error: [{e}]")
		sys.exit(1)
	ZMQSOCKET = _socket

def listen_for_request():
	global ZMQSOCKET
	try:
		_request = ZMQSOCKET.recv_json()
	except Exception as e:
		logger.error(f"Failed listening\nError: [{e}]")
		sys.exit(1)
	return _request
