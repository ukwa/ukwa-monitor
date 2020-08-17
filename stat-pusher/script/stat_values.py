'''
get stat value
Depending on service and data return, method of getting stat value expected to differ. 
This module is to cater for each variant.
'''

import logging
import ast
import requests
import sys
import dateutil.parser
import calendar

def get_json_value(uri, match):
	logging.debug(f"uri [{uri}]")

	# convert match string into list, to traverse uri json response
	matchList = ast.literal_eval(match)
	logging.debug(f"matchList [{matchList}] type [{type(matchList)}]")

	# get response
	try:
		r = requests.get(uri)
		logging.debug(f"Response code [{r.status_code}]")
		r.raise_for_status()
		response = r.json()
	except HTTPError as he:
		logging.error(f"HTTP error trying  to get [{uri}]\n[{he}]")
		sys.exit()
	except Exception as e:
		logging.error(f"Failed to get [{uri}]\n[{e}]")
		sys.exit()

	# extract value
	for k in matchList:
		if k in response:
			response = response[k]
		elif k in response[0]:
			response = response[0][k]
		else:
			logging.error(f"match key [{k}] not found in uri {uri}\njson [{response}]")
			sys.exit()
	logging.debug(f"Value [{response}] type [{type(response)}]")

	# ensure numerical value
	if type(response) is not int:
		if type(response) is float:
			response = int(response)

		# if value is a timestamp, get unixtime
		#### NEED TO WORK OUT PROCESSING OF STRING INTO UNIXTIME ############################
		elif dateutil.parser.parse(response):
			#dst = calendar.timegm(dateutil.parser.parse(response))
			
			#logging.debug(f"date string [{response}] dst [{type(dst)}]")
			response = 42
		else:
			logging.error(f"Value [{response}] type [{type(response)}] not convertible to numeric")
			sys.exit()

	return response
