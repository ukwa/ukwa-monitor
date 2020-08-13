#!/usr/bin/env python
'''
Script to gather WA bespoke service stats and upload to push gateway service
'''

import logging

from prometheus_client import start_http_server, Summary

# script packages
from common import log
#import common

# main ----------------------------------------
def main():
	log.configure(lvl='DEBUG')
	logging.info('Start ---------------------')
	logging.info('Fin')


if __name__ == '__main__':
	main()
