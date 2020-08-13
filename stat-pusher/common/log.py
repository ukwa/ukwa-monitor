'''
Common/non-script specific functions
'''

import logging

def configure(lvl='INFO'):
	logging.basicConfig(format='[%(asctime)s %(levelname)s] %(message)s', level=lvl)
