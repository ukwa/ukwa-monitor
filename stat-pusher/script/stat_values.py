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
	logging.debug("uri [{}]".format(uri))

	# convert match string into list, to traverse uri json response
	matchList = ast.literal_eval(match)
	logging.debug("matchList [{}] type [{}]".format(matchList, type(matchList)))

	# get response
	try:
		r = requests.get(uri)
		response = r.json()
	except Exception as e:
		logging.error("Failed to get [{}]\n[{}]".format(uri, e))
		sys.exit()

	#### NEED TO ENSURE RESPONSE IS SUCCESSFUL ########################################


	# extract value
	for k in matchList:
		if k in response:
			response = response[k]
		elif k in response[0]:
			response = response[0][k]
		else:
			logging.error("match key [{}] not found in uri {}\njson [{}]".format(k, uri, response))
			sys.exit()
	logging.debug("response [{}] type [{}]".format(response, type(response)))

	# ensure numerical value
	if type(response) is not int:
		if type(response) is float:
			response = int(response)

		# if value is a timestamp, get unixtime
		#### NEED TO WORK OUT PROCESSING OF STRING INTO UNIXTIME ############################
		elif dateutil.parser.parse(response):
			dst = calendar.timegm(dateutil.parser.parse(response))
			
			logging.debug("date string [{}] dst [{}]".format(response, type(dst)))
			response = 42
		else:
			response = 4

	return response
