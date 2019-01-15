#!/usr/bin/env python3.6

# Grafana seems unable to control the position of panels so that the addition
# of a new panel knocks others out of place. Plus, the repeat functions seems
# not to work. Consequently, this 'simple code' is to create the wa_status 
# dashboard with easy repetition of panels and controlled positioning.

import re
import datetime

# template files
header = 'templates/header'
panelHeader = 'templates/panelHeader'
panelFooter = 'templates/panelFooter'
footer = 'templates/footer'
titleBar = 'templates/titleBar'
title = 'WA Status-'
uid = 'wast-'

# functions ------------------------------
def output(**kwargs):
	# read template file
	templateCode = ''
	templateFile = kwargs['templateFile']
	with open(templateFile, 'r') as tC:
		templateCode = tC.read()

	# replace panel placeholders
	if 'replaceDict' in kwargs:
		for key in kwargs['replaceDict']:
			value = kwargs['replaceDict'][key]
			templateCode = templateCode.replace(key, value)

	if 'lastPanel' in kwargs:
		templateCode = re.sub(r'},$', '}', templateCode)

	# print code block
	print(templateCode, end="")

# main -----------------------------------
def main():
	output(templateFile = header)
	output(templateFile = panelHeader)

	# panels -------
	replaceDict = { '<title>': 'Ingest & Metadata', '<id>':'4', '<h>':'1', '<w>':'7', '<x>':'0', '<y>':'0' }
	output(templateFile = titleBar, replaceDict = replaceDict)

	replaceDict = { '<title>': 'Hadoop', '<id>':'5', '<h>':'1', '<w>':'7', '<x>':'7', '<y>':'0' }
	output(templateFile = titleBar, replaceDict = replaceDict, lastPanel = True)
	# eo panels ----

	output(templateFile = panelFooter)

	# amend dashboard values
	date = datetime.datetime.now()
	formattedDate = date.strftime("%Y%m%d%H%M%S")
	replaceDict = { '<title>':title+formattedDate, '<uid>':uid+formattedDate }
	output(templateFile = footer, replaceDict = replaceDict)

if __name__ == '__main__':
	main()
