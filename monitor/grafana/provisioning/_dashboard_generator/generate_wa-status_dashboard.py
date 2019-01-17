#!/usr/bin/env python3.6

# Grafana seems unable to control the position of panels so that the addition
# of a new panel knocks others out of place. Plus, the repeat functions seems
# not to work. Consequently, this 'simple code' is to create the wa_status 
# dashboard with easy repetition of panels and controlled positioning.

import re
import datetime

# dashboard prefixes
dashTitle = 'WA Status-'
dashUid = 'wast-'

# template files
header = 'templates/header'
panelHeader = 'templates/panelHeader'
panelTitle = 'templates/panelTitle'
panelSingle = 'templates/panelSingle'
panelFooter = 'templates/panelFooter'
footer = 'templates/footer'

# panel ID, increments on usage so all unique in panels
ID = 0

# functions ------------------------------
def nextID():
	global ID
	ID=ID + 1
	return str(ID)

def read_template(**kwargs):
	tplC = ''
	with open(kwargs['tmpFl'], 'r') as tC:
		tplC = tC.read()
	return tplC

def output(**kwargs):
	templateCode = read_template(tmpFl=kwargs['tmpFl'])
#	print(templateCode, end="")

def replace_output_title(**kwargs):
	templateCode = read_template(tmpFl=kwargs['tmpFl'])

	# replacements
	templateCode = templateCode.replace('<title>', kwargs['title'])
	templateCode = templateCode.replace('<id>', nextID())
	templateCode = templateCode.replace('<h>', str(kwargs['h']))
	templateCode = templateCode.replace('<w>', str(kwargs['w']))
	templateCode = templateCode.replace('<x>', str(kwargs['x']))
	templateCode = templateCode.replace('<y>', str(kwargs['y']))

	print("template: {}\tjob: {}\ttitle: {}\th: {}\tw: {}\t\tx: {}\ty: {}".format(kwargs['tmpFl'], kwargs['job'], kwargs['title'], kwargs['h'], kwargs['w'], kwargs['x'], kwargs['y']))		#### debugging
#	print(templateCode, end="")

def replace_output_single(**kwargs):
	templateCode = read_template(tmpFl=kwargs['tmpFl'])

	# replacements
	templateCode = templateCode.replace('<title>', kwargs['title'])
	templateCode = templateCode.replace('<id>', nextID())
	templateCode = templateCode.replace('<h>', str(kwargs['h']))
	templateCode = templateCode.replace('<w>', str(kwargs['w']))
	templateCode = templateCode.replace('<x>', str(kwargs['x']))
	templateCode = templateCode.replace('<y>', str(kwargs['y']))

	# add expr
	if kwargs['title'] == 'Up':
		exprUp = 'sum(1 - up{job=\\"' + kwargs['job'] + '\\"})'
		templateCode = templateCode.replace('<expr>', exprUp)
	elif kwargs['title'] == 'CPU':
		exprCpu = 'count(sum(irate(node_cpu_seconds_total{job=\\"' + kwargs['job'] + '\\",mode=\\"idle\\"}[5m]) < 0.1) by (instance)) OR vector(0)'
		templateCode = templateCode.replace('<expr>', exprCpu)
	elif kwargs['title'] == 'Dsk':
		exprDsk = 'count((node_filesystem_avail_bytes{job=\\"' + kwargs['job'] + '\\",fstype!~\\"tmpfs|cifs\\"} / node_filesystem_size_bytes{job=\\"' + kwargs['job'] + '\\",fstype!~\\"tmpfs|cifs\\"}) < 0.04) OR vector(0)'
		templateCode = templateCode.replace('<expr>', exprDsk)
	else:
		exprMem = 'count((node_memory_MemFree_bytes{job=\\"' + kwargs['job'] + '\\"} / node_memory_MemTotal_bytes{job=\\"' + kwargs['job'] + '\\"}) < 0.01) OR vector(0)'
		templateCode = templateCode.replace('<expr>', exprMem)

	# remove last comma if last panel
	if 'lastPanel' in kwargs:
		templateCode = re.sub(r'},$', '}', templateCode)

	print("template: {}\tjob: {}\ttitle: {}\t\th: {}\tw: {}\t\t\tx: {}\ty: {}".format(kwargs['tmpFl'], kwargs['job'], kwargs['title'], kwargs['h'], kwargs['w'], kwargs['x'], kwargs['y']))		#### debugging
#	print(templateCode, end="")

def replace_output_footer(**kwargs):
	templateCode = read_template(tmpFl=kwargs['tmpFl'])

	templateCode = templateCode.replace('<title>', kwargs['title'])
	templateCode = templateCode.replace('<uid>', kwargs['uid'])

	print("\ntemplate: {}\ttitle: {}\tuid: {}".format(kwargs['tmpFl'], kwargs['title'], kwargs['uid']))		#### debugging
#	print(templateCode, end="")

# main -----------------------------------
def main():
	output(tmpFl = header)
	output(tmpFl = panelHeader)

	# output single panels
	replace_output_title(tmpFl=panelTitle, job='ingest_metadata', title='Ingest & Metadata', h=1, w=8, x=0, y=0)
	replace_output_single(tmpFl=panelSingle, job='ingest_metadata', title='Up', h=1, w=2, x=0, y=1)
	replace_output_single(tmpFl=panelSingle, job='ingest_metadata', title='CPU', h=1, w=2, x=2, y=1)
	replace_output_single(tmpFl=panelSingle, job='ingest_metadata', title='Dsk', h=1, w=2, x=4, y=1)
	replace_output_single(tmpFl=panelSingle, job='ingest_metadata', title='Mem', h=1, w=2, x=6, y=1)


	# output last singlestat panel with final ',' removed to make output json valid
	replace_output_single(tmpFl = panelSingle, job = 'infrastructure', title = 'Mem', h=1, w=2, x=14, y=6, lastPanel = True)

	# amend dashboard values
	output(tmpFl = panelFooter)
	date = datetime.datetime.now()
	formattedDate = date.strftime("%Y%m%d%H%M%S")
	replace_output_footer(tmpFl = footer, title = dashTitle + formattedDate, uid = dashUid + formattedDate)

if __name__ == '__main__':
	main()
