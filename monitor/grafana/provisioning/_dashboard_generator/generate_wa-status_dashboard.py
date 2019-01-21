#!/usr/bin/env python3.6

# Grafana seems unable to control the position of panels so that the addition
# of a new panel knocks others out of place. Plus, the repeat functions seems
# not to work. Consequently, this 'simple code' is to create the wa_status 
# dashboard with easy repetition of panels and controlled positioning.

import re
import datetime

# output filename
outFile = 'wa-status_json.out'

# dashboard prefixes
dashTitle = 'WA Status-'
dashUid = 'wast-'

# template files
header = 'templates/header'
panelHeader = 'templates/panelHeader'
panelTitle = 'templates/panelTitle'
panelSingle = 'templates/panelSingle'
panelSingleIMCPU = 'templates/panelSingleIMCPU'
panelSingleHadoopUsed = 'templates/panelSingleHadoopUsed'
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

def output(outHandle, **kwargs):
	templateCode = read_template(tmpFl=kwargs['tmpFl'])
	outHandle.write(templateCode)

def replace_output_title(outHandle, **kwargs):
	templateCode = read_template(tmpFl=kwargs['tmpFl'])

	# replacements
	templateCode = templateCode.replace('<title>', kwargs['title'])
	templateCode = templateCode.replace('<id>', nextID())
	templateCode = templateCode.replace('<h>', str(kwargs['h']))
	templateCode = templateCode.replace('<w>', str(kwargs['w']))
	templateCode = templateCode.replace('<x>', str(kwargs['x']))
	templateCode = templateCode.replace('<y>', str(kwargs['y']))

	print("template: {}\tjob: {}\ttitle: {}\th: {}\tw: {}\t\tx: {}\ty: {}".format(kwargs['tmpFl'], kwargs['job'], kwargs['title'], kwargs['h'], kwargs['w'], kwargs['x'], kwargs['y']))		# action reporting
	outHandle.write(templateCode)

def replace_output_single(outHandle, **kwargs):
	templateCode = read_template(tmpFl=kwargs['tmpFl'])

	# replacements
	templateCode = templateCode.replace('<title>', kwargs['title'])
	templateCode = templateCode.replace('<id>', nextID())
	templateCode = templateCode.replace('<h>', str(kwargs['h']))
	templateCode = templateCode.replace('<w>', str(kwargs['w']))
	templateCode = templateCode.replace('<x>', str(kwargs['x']))
	templateCode = templateCode.replace('<y>', str(kwargs['y']))
	if 'thresholds' in kwargs:
		templateCode = templateCode.replace('<thresholds>', kwargs['thresholds'])
	else:
		templateCode = templateCode.replace('<thresholds>', '0.1,1')			# default threshhold
	if 'colour' in kwargs:
		templateCode = templateCode.replace('<colour>', kwargs['colour'])
	else:
		templateCode = templateCode.replace('<colour>', 'rgba(237, 129, 40, 0.89)')			# default panel mid colour

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
	elif kwargs['title'] == 'Mem':
		exprMem = 'count((node_memory_MemFree_bytes{job=\\"' + kwargs['job'] + '\\"} / node_memory_MemTotal_bytes{job=\\"' + kwargs['job'] + '\\"}) < 0.01) OR vector(0)'
		templateCode = templateCode.replace('<expr>', exprMem)
	elif kwargs['title'] == 'Nodes':
		exprMem = 'hdfs_node_count{status=\\"dead\\",instance=\\"ingest:9118\\"}'
		templateCode = templateCode.replace('<expr>', exprMem)
	elif kwargs['title'] == 'Under-rep':
		exprMem = 'hdfs_under_replicated_block_count{instance=\\"ingest:9118\\"}'
		templateCode = templateCode.replace('<expr>', exprMem)
	elif kwargs['title'] == 'Used':
		exprMem = 'hdfs_used_percent{instance=\\"ingest:9118\\"}'
		templateCode = templateCode.replace('<expr>', exprMem)

	# remove last comma if last panel
	if 'lastPanel' in kwargs:
		templateCode = re.sub(r'},$', '}', templateCode)

	print("template: {}\tjob: {}\ttitle: {}\t\th: {}\tw: {}\t\t\tx: {}\ty: {}".format(kwargs['tmpFl'], kwargs['job'], kwargs['title'], kwargs['h'], kwargs['w'], kwargs['x'], kwargs['y']))		# action reporting
	outHandle.write(templateCode)

def replace_output_footer(outHandle, **kwargs):
	templateCode = read_template(tmpFl=kwargs['tmpFl'])

	templateCode = templateCode.replace('<title>', kwargs['title'])
	templateCode = templateCode.replace('<uid>', kwargs['uid'])

	print("\ntemplate: {}\ttitle: {}\tuid: {}".format(kwargs['tmpFl'], kwargs['title'], kwargs['uid']))		# action reporting
	outHandle.write(templateCode)

# main -----------------------------------
def main():
	outHandle = open(outFile, 'w')
	output(outHandle, tmpFl = header)
	output(outHandle, tmpFl = panelHeader)

	# output single panels
	replace_output_title(outHandle, tmpFl=panelTitle, job='ingest_metadata', title='Ingest & Metadata', h=1, w=8, x=0, y=0)
	replace_output_single(outHandle, tmpFl=panelSingle, job='ingest_metadata', title='Up', h=1, w=2, x=0, y=1)
	replace_output_single(outHandle, tmpFl=panelSingle, job='ingest_metadata', title='CPU', h=1, w=2, x=2, y=1, thresholds='0.1,1.5', colour='#ba43a9')
	replace_output_single(outHandle, tmpFl=panelSingle, job='ingest_metadata', title='Dsk', h=1, w=2, x=4, y=1)
	replace_output_single(outHandle, tmpFl=panelSingle, job='ingest_metadata', title='Mem', h=1, w=2, x=6, y=1)
	replace_output_title(outHandle, tmpFl=panelTitle, job='hadoop', title='Hadoop', h=1, w=8, x=8, y=0)
	replace_output_single(outHandle, tmpFl=panelSingle, job='hadoop', title='Up', h=1, w=2, x=8, y=1)
	replace_output_single(outHandle, tmpFl=panelSingle, job='hadoop', title='CPU', h=1, w=2, x=10, y=1)
	replace_output_single(outHandle, tmpFl=panelSingle, job='hadoop', title='Dsk', h=1, w=2, x=12, y=1)
	replace_output_single(outHandle, tmpFl=panelSingle, job='hadoop', title='Mem', h=1, w=2, x=14, y=1)
	replace_output_single(outHandle, tmpFl=panelSingle, job='hadoop', title='Nodes', h=1, w=2, x=8, y=2)
	replace_output_single(outHandle, tmpFl=panelSingle, job='hadoop', title='Under-rep', h=1, w=2, x=10, y=2)
	replace_output_single(outHandle, tmpFl=panelSingleHadoopUsed, job='hadoop', title='Used', h=2, w=2, x=12, y=2)
	replace_output_title(outHandle, tmpFl=panelTitle, job='discovery_access', title='Discovery & Access', h=1, w=8, x=16, y=0)
	replace_output_single(outHandle, tmpFl=panelSingle, job='discovery_access', title='Up', h=1, w=2, x=16, y=1)
	replace_output_single(outHandle, tmpFl=panelSingle, job='discovery_access', title='CPU', h=1, w=2, x=18, y=1)
	replace_output_single(outHandle, tmpFl=panelSingle, job='discovery_access', title='Dsk', h=1, w=2, x=20, y=1)
	replace_output_single(outHandle, tmpFl=panelSingle, job='discovery_access', title='Mem', h=1, w=2, x=22, y=1)
	replace_output_title(outHandle, tmpFl=panelTitle, job='gluster', title='Gluster', h=1, w=8, x=8, y=4)
	replace_output_single(outHandle, tmpFl=panelSingle, job='gluster', title='Up', h=1, w=2, x=8, y=5)
	replace_output_single(outHandle, tmpFl=panelSingle, job='gluster', title='CPU', h=1, w=2, x=10, y=5)
	replace_output_single(outHandle, tmpFl=panelSingle, job='gluster', title='Dsk', h=1, w=2, x=12, y=5)
	replace_output_single(outHandle, tmpFl=panelSingle, job='gluster', title='Mem', h=1, w=2, x=14, y=5)
	replace_output_title(outHandle, tmpFl=panelTitle, job='solr', title='Solr', h=1, w=8, x=16, y=2)
	replace_output_single(outHandle, tmpFl=panelSingle, job='solr', title='Up', h=1, w=2, x=16, y=3)
	replace_output_single(outHandle, tmpFl=panelSingle, job='solr', title='CPU', h=1, w=2, x=18, y=3)
	replace_output_single(outHandle, tmpFl=panelSingle, job='solr', title='Dsk', h=1, w=2, x=20, y=3, thresholds='0.1,1.5', colour='#ba43a9')
	replace_output_single(outHandle, tmpFl=panelSingle, job='solr', title='Mem', h=1, w=2, x=22, y=3)
	replace_output_title(outHandle, tmpFl=panelTitle, job='infrastructure', title='Infrastructure', h=1, w=8, x=8, y=6)
	replace_output_single(outHandle, tmpFl=panelSingle, job='infrastructure', title='Up', h=1, w=2, x=8, y=7)
	replace_output_single(outHandle, tmpFl=panelSingle, job='infrastructure', title='CPU', h=1, w=2, x=10, y=7)
	replace_output_single(outHandle, tmpFl=panelSingle, job='infrastructure', title='Dsk', h=1, w=2, x=12, y=7)


	# output last singlestat panel with final ',' removed to make output json valid
	replace_output_single(outHandle, tmpFl = panelSingle, job = 'infrastructure', title = 'Mem', h=1, w=2, x=14, y=6, lastPanel = True)

	# amend dashboard values
	output(outHandle, tmpFl = panelFooter)
	date = datetime.datetime.now()
	formattedDate = date.strftime("%Y%m%d%H%M%S")
	replace_output_footer(outHandle, tmpFl = footer, title = dashTitle + formattedDate, uid = dashUid + formattedDate)

	outHandle.close()

if __name__ == '__main__':
	main()
