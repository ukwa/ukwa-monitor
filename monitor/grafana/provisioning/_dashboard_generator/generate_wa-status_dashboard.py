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
panelHeight = 1
panelTitle = 'templates/panelTitle'
panelTitleTitleDict = {'ingest_metadata':'Ingest & Metadata', 'hadoop':'Hadoop', 'discovery_access':'Discovery & Access', 'gluster':'Gluster', 'solr':'Solr', 'infrastructure':'Infrastructure'}
panelTitleWidth = 8
panelTitleXDict = {'ingest_metadata':panelTitleWidth * 0, 'hadoop':panelTitleWidth * 1, 'discovery_access':panelTitleWidth * 2, 'gluster':panelTitleWidth * 1, 'solr':panelTitleWidth * 2, 'infrastructure':panelTitleWidth * 1}
panelTitleYDict = {'ingest_metadata':panelHeight * 0, 'hadoop':panelHeight * 0, 'discovery_access':panelHeight * 0, 'gluster':panelHeight * 2, 'solr':panelHeight * 2, 'infrastructure':(panelHeight * 2) * 2}
panelSingle = 'templates/panelSingle'
panelSingleWidth = 2
panelSingleXDict = {
	'ingest_metadata':	{'Up':panelSingleWidth * 0, 'CPU':panelSingleWidth * 1, 'Dsk':panelSingleWidth * 2, 'Mem':panelSingleWidth * 3},
	'hadoop':		{'Up':panelTitleWidth + (panelSingleWidth * 0), 'CPU':panelTitleWidth + (panelSingleWidth * 1), 'Dsk':panelTitleWidth + (panelSingleWidth * 2), 'Mem':panelTitleWidth + (panelSingleWidth * 3)},
	'discovery_access':	{'Up':(panelTitleWidth * 2) + (panelSingleWidth * 0), 'CPU':(panelTitleWidth * 2) + (panelSingleWidth * 1), 'Dsk':(panelTitleWidth * 2) + (panelSingleWidth * 2), 'Mem':(panelTitleWidth * 2) + (panelSingleWidth * 3)},
	'gluster':		{'Up':panelTitleWidth + (panelSingleWidth * 0), 'CPU':panelTitleWidth + (panelSingleWidth * 1), 'Dsk':panelTitleWidth + (panelSingleWidth * 2), 'Mem':panelTitleWidth + (panelSingleWidth * 3)},
	'solr':			{'Up':(panelTitleWidth * 2) + (panelSingleWidth * 0), 'CPU':(panelTitleWidth * 2) + (panelSingleWidth * 1), 'Dsk':(panelTitleWidth * 2) + (panelSingleWidth * 2), 'Mem':(panelTitleWidth * 2) + (panelSingleWidth * 3)},
	'infrastructure':	{'Up':panelTitleWidth + (panelSingleWidth * 0), 'CPU':panelTitleWidth + (panelSingleWidth * 1), 'Dsk':panelTitleWidth + (panelSingleWidth * 2), 'Mem':panelTitleWidth + (panelSingleWidth * 3)}
}
panelSingleYDict = {
	'ingest_metadata':	{'Up':panelHeight, 'CPU':panelHeight, 'Dsk':panelHeight, 'Mem':panelHeight},
	'hadoop':		{'Up':panelHeight, 'CPU':panelHeight, 'Dsk':panelHeight, 'Mem':panelHeight},
	'discovery_access':	{'Up':panelHeight, 'CPU':panelHeight, 'Dsk':panelHeight, 'Mem':panelHeight},
	'gluster':		{'Up':panelHeight * 3, 'CPU':panelHeight * 3, 'Dsk':panelHeight * 3, 'Mem':panelHeight * 3},
	'solr':			{'Up':panelHeight * 3, 'CPU':panelHeight * 3, 'Dsk':panelHeight * 3, 'Mem':panelHeight * 3},
	'infrastructure':	{'Up':panelHeight * 5, 'CPU':panelHeight * 5, 'Dsk':panelHeight * 5, 'Mem':panelHeight * 5}
}
panelFooter = 'templates/panelFooter'
footer = 'templates/footer'
dashTitle = 'WA Status-'
dashUid = 'wast-'
ID = 0

# functions ------------------------------
def nextID():
	global ID
	ID=ID + 1
	return str(ID)

def output(**kwargs):
	# read template file
	templateCode = ''
	tmpFl = kwargs['tmpFl']
	with open(tmpFl, 'r') as tC:
		templateCode = tC.read()

	# output code blocks
	if tmpFl == panelTitle or tmpFl == panelSingle or tmpFl == footer:
		templateCode = templateCode.replace('<h>', str(panelHeight))

		if tmpFl == panelTitle:
			templateCode = templateCode.replace('<title>', panelTitleTitleDict[kwargs['title']])
			templateCode = templateCode.replace('<id>', nextID())
			templateCode = templateCode.replace('<w>', str(panelTitleWidth))
			templateCode = templateCode.replace('<x>', str(panelTitleXDict[kwargs['job']]))
			templateCode = templateCode.replace('<y>', str(panelTitleYDict[kwargs['job']]))
#			print("\ntemplate: {}\ttitle: {}\tx: {}\ty: {}\n".format(tmpFl, panelTitleTitleDict[kwargs['title']], panelTitleXDict[kwargs['job']], panelTitleYDict[kwargs['job']]))		#### debugging

		elif tmpFl == panelSingle:
			templateCode = templateCode.replace('<title>', kwargs['title'])
			templateCode = templateCode.replace('<id>', nextID())
			templateCode = templateCode.replace('<w>', str(panelSingleWidth))
			templateCode = templateCode.replace('<x>', str(panelSingleXDict[kwargs['job']][kwargs['title']]))
			templateCode = templateCode.replace('<y>', str(panelSingleYDict[kwargs['job']][kwargs['title']]))
#			print("template: {}\tjob: {}\ttitle: {}\tx: {}\ty: {}".format(tmpFl, kwargs['job'], kwargs['title'], panelSingleXDict[kwargs['job']][kwargs['title']], panelSingleYDict[kwargs['job']][kwargs['title']]))		#### debugging

			# add expr
			exprUp = 'sum(1 - up{job=\\"' + kwargs['job'] + '\\"})'
			exprCpu = 'count(sum(irate(node_cpu_seconds_total{job=\\"' + kwargs['job'] + '\\",mode=\\"idle\\"}[5m]) < 0.1) by (instance)) OR vector(0)'
			exprDsk = 'count((node_filesystem_avail_bytes{job=\\"' + kwargs['job'] + '\\",fstype!~\\"tmpfs|cifs\\"} / node_filesystem_size_bytes{job=\\"' + kwargs['job'] + '\\",fstype!~\\"tmpfs|cifs\\"}) < 0.04) OR vector(0)'
			exprMem = 'count((node_memory_MemFree_bytes{job=\\"' + kwargs['job'] + '\\"} / node_memory_MemTotal_bytes{job=\\"' + kwargs['job'] + '\\"}) < 0.01) OR vector(0)'
			if kwargs['title'] == 'Up':
				templateCode = templateCode.replace('<expr>', exprUp)
			elif kwargs['title'] == 'CPU':
				templateCode = templateCode.replace('<expr>', exprCpu)
			elif kwargs['title'] == 'Dsk':
				templateCode = templateCode.replace('<expr>', exprDsk)
			else:
				templateCode = templateCode.replace('<expr>', exprMem)

			# remove last comma if last panel
			if 'lastPanel' in kwargs:
				templateCode = re.sub(r'},$', '}', templateCode)

		elif tmpFl == footer:
			templateCode = templateCode.replace('<title>', kwargs['title'])
			templateCode = templateCode.replace('<uid>', kwargs['uid'])
####			print("template: {}\n\ttitle: {}\n\tuid: {}".format(tmpFl, kwargs['title'], kwargs['uid']))		#### debugging

	# print code block
	print(templateCode, end="")

# main -----------------------------------
def main():
	output(tmpFl = header)
	output(tmpFl = panelHeader)

	# iterate through job names
	for jobName in ['ingest_metadata', 'hadoop', 'discovery_access', 'gluster', 'solr', 'infrastructure']:
		output(tmpFl = panelTitle, job = jobName, title = jobName)
		output(tmpFl = panelSingle, job = jobName, title = 'Up')
		output(tmpFl = panelSingle, job = jobName, title = 'CPU')
		output(tmpFl = panelSingle, job = jobName, title = 'Dsk')
		if jobName != 'infrastructure':
			output(tmpFl = panelSingle, job = jobName, title = 'Mem')

	# last singlestat panel
	output(tmpFl = panelSingle, job = 'infrastructure', title = 'Mem', lastPanel = True)

	# amend dashboard values
	output(tmpFl = panelFooter)
	date = datetime.datetime.now()
	formattedDate = date.strftime("%Y%m%d%H%M%S")
	output(tmpFl = footer, title = dashTitle + formattedDate, uid = dashUid + formattedDate)

if __name__ == '__main__':
	main()
