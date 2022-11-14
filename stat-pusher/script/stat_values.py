'''
get stat value
Depending on service and data return, method of getting stat value expected to differ. 
This module is to cater for each variant.
'''

import logging
import ast
import requests
from urllib.error import HTTPError
import sys
import dateutil.parser
import datetime

logger = logging.getLogger(__name__)



def get_json_value(uri, match):
	logger.debug(f"uri [{uri}]")

	# convert match string into list, to traverse uri json response
	matchList = ast.literal_eval(match)
	logger.debug(f"matchList [{matchList}] type [{type(matchList)}]")

	# get response
	try:
		r = requests.get(uri)
		logger.debug(f"Response code [{r.status_code}]")
		r.raise_for_status()
		response = r.json()
	except HTTPError as he:
		logger.error(f"HTTP error trying  to get [{uri}]\n[{he}]")
		sys.exit()
	except Exception as e:
		logger.error(f"Failed to get [{uri}]\n[{e}]")
		sys.exit()

	# extract value
	value = response
	for k in matchList:
		if k in value:
			value = value[k]
		elif k in value[0]:
			value = value[0][k]
		else:
			logger.error(f"match key [{k}] not found in uri {uri}\njson [{value}]")
			sys.exit()
	logger.debug(f"Value [{value}] type [{type(value)}]")

	# ensure numerical value
	if type(value) is not int and type(value) is not float:
		# if value is a timestamp, get unixtime
		dt = None
		try:
			dt = dateutil.parser.parse(value)
		except Exception as e:
			logger.error(f"Value [{value}] type [{type(value)}] not recognised as datestamp")
			sys.exit()
		if isinstance(dt, datetime.datetime):
			logger.debug(f"timestamp dt [{dt}] type [{type(dt)}]")
			value = dt.timestamp()
			logger.debug(f"Value epoch [{value}]")
		else:
			logger.error(f"Value [{value}] type [{type(value)}] not convertible to numeric")
			sys.exit()

	return value
