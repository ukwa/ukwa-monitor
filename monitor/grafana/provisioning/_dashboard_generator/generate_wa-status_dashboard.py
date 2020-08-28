#!/usr/bin/env python3.6

# Grafana seems unable to control the position of panels so that the addition
# of a new panel knocks others out of place. Plus, the repeat functions seems
# not to work. Consequently, this 'simple code' is to create the wa_status 
# dashboard with easy repetition of panels and controlled positioning.

import re
import datetime

# output filename
outFile = 'wa_status.json-template'

# dashboard prefixes
dashTitle = 'WA Status'
dashUid = 'wast'

# template files
header = 'templates/header'
panelHeader = 'templates/panelHeader'
panelTitle = 'templates/panelTitle'
panelSingle = 'templates/panelSingle'
panelSingleHadoopUsed = 'templates/panelSingleHadoopUsed'
panelStat = 'templates/panelStat'
panelStatHadoopUsed = 'templates/panelStatHadoopUsed'
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
	with open(kwargs['pnl'], 'r') as tC:
		tplC = tC.read()
	return tplC

def output(outHandle, **kwargs):
	templateCode = read_template(pnl=kwargs['pnl'])
	outHandle.write(templateCode)

def replace_output_title(outHandle, **kwargs):
	templateCode = read_template(pnl=kwargs['pnl'])
	templateCode = templateCode.replace('<title>', kwargs['title'])
	templateCode = templateCode.replace('<id>', nextID())
	templateCode = templateCode.replace('<h>', str(kwargs['h']))
	templateCode = templateCode.replace('<w>', str(kwargs['w']))
	templateCode = templateCode.replace('<x>', str(kwargs['x']))
	templateCode = templateCode.replace('<y>', str(kwargs['y']))
	outHandle.write(templateCode)

def replace_output_single(outHandle, **kwargs):
	templateCode = read_template(pnl=kwargs['pnl'])
	templateCode = templateCode.replace('<title>', kwargs['title'])
	templateCode = templateCode.replace('<id>', nextID())
	templateCode = templateCode.replace('<h>', str(kwargs['h']))
	templateCode = templateCode.replace('<w>', str(kwargs['w']))
	templateCode = templateCode.replace('<x>', str(kwargs['x']))
	templateCode = templateCode.replace('<y>', str(kwargs['y']))

	# specific thresholds replacement
	if kwargs['pnl'] == panelStat or kwargs['pnl'] == panelStatHadoopUsed:
		if 'threshold1' in kwargs:
			templateCode = templateCode.replace('<threshold1>', kwargs['threshold1'])
		else:
			templateCode = templateCode.replace('<threshold1>', 'null')
		if 'threshold2' in kwargs:
			templateCode = templateCode.replace('<threshold2>', kwargs['threshold2'])
		else:
			templateCode = templateCode.replace('<threshold2>', '0.1')
		if 'threshold3' in kwargs:
			templateCode = templateCode.replace('<threshold3>', kwargs['threshold3'])
		else:
			templateCode = templateCode.replace('<threshold3>', '1')
		if 'textmode' in kwargs:
			templateCode = templateCode.replace('<textmode>', kwargs['textmode'])
		else:
			templateCode = templateCode.replace('<textmode>', 'none')
	else:
		if 'thresholds' in kwargs:
			templateCode = templateCode.replace('<thresholds>', kwargs['thresholds'])
		else:
			templateCode = templateCode.replace('<thresholds>', '0.1,1')			# default threshhold
	# specific colours replacement
	if 'colour1' in kwargs:
		templateCode = templateCode.replace('<colour1>', kwargs['colour1'])
	else:
		templateCode = templateCode.replace('<colour1>', '#299C46')				# default panel okay colour
	if 'colour2' in kwargs:
		templateCode = templateCode.replace('<colour2>', kwargs['colour2'])
	else:
		templateCode = templateCode.replace('<colour2>', '#ED8027')				# default panel warning colour
	if 'colour3' in kwargs:
		templateCode = templateCode.replace('<colour3>', kwargs['colour3'])
	else:
		templateCode = templateCode.replace('<colour3>', '#D44A3A')				# default panel problem colour

	# add expr
	if kwargs['title'] == 'Up':
		expr = 'sum(1 - up{job=\\"' + kwargs['job'] + '\\"})'
		templateCode = templateCode.replace('<expr>', expr)
	elif kwargs['title'] == 'CPU':
		expr = 'count(sum(irate(node_cpu_seconds_total{job=\\"' + kwargs['job'] + '\\",mode=\\"idle\\"}[5m]) < 0.1) by (instance)) OR vector(0)'
		templateCode = templateCode.replace('<expr>', expr)
	elif kwargs['title'] == 'Dsk':
		expr = 'count((node_filesystem_avail_bytes{job=\\"' + kwargs['job'] + '\\",fstype!~\\"tmpfs|rootfs|cifs\\"} / node_filesystem_size_bytes{job=\\"' + kwargs['job'] + '\\",fstype!~\\"tmpfs|rootfs|cifs\\"}) < 0.04) OR vector(0)'
		templateCode = templateCode.replace('<expr>', expr)
	elif kwargs['title'] == 'Mem':
		expr = 'count(sum(node_memory_MemFree_bytes{job=\\"' + kwargs['job'] + '\\"} + node_memory_Buffers_bytes{job=\\"' + kwargs['job'] + '\\"} + node_memory_Cached_bytes{job=\\"' + kwargs['job'] + '\\"}) by (instance) / sum(node_memory_MemTotal_bytes{job=\\"' + kwargs['job'] + '\\"}) by (instance) < 0.05) OR vector(0)'
		templateCode = templateCode.replace('<expr>', expr)
	elif kwargs['title'] == 'Nodes':
		expr = 'hdfs_node_count{status=\\"dead\\",instance=\\"${HDFS_EXPORTER}\\"}'
		templateCode = templateCode.replace('<expr>', expr)
	elif kwargs['title'] == 'Under-rep':
		expr = 'hdfs_under_replicated_block_count{instance=\\"${HDFS_EXPORTER}\\"}'
		templateCode = templateCode.replace('<expr>', expr)
	elif kwargs['title'] == 'Used':
		expr = 'hdfs_used_percent{instance=\\"${HDFS_EXPORTER}\\"}'
		templateCode = templateCode.replace('<expr>', expr)
	elif kwargs['title'] == 'UTR':
		expr = 'count(uptimerobot_monitor_up==0) OR vector(0)'
		templateCode = templateCode.replace('<expr>', expr)
	elif kwargs['title'] == 'WWW' or kwargs['title'] == 'Query':
		expr = 'count(probe_http_status_code{job=\\"' + kwargs['job'] + '\\"} != 200) OR vector(0)'
		templateCode = templateCode.replace('<expr>', expr)
	elif kwargs['title'] == 'trackdb refresh':
		expr = '(time() - trackdb_refresh_timestamp) / (60*60)'
		templateCode = templateCode.replace('<expr>', expr)
	elif kwargs['title'] == 'trackdb numFound':
		expr = 'sum(trackdb_numFound - (trackdb_numFound offset 1d))'
		templateCode = templateCode.replace('<expr>', expr)

	# add last comma if not last panel
	if 'lastPanel' not in kwargs:
		templateCode = re.sub(r'}$', '},', templateCode)
	outHandle.write(templateCode)

def replace_output_footer(outHandle, **kwargs):
	templateCode = read_template(pnl=kwargs['pnl'])
	templateCode = templateCode.replace('<title>', kwargs['title'])
	templateCode = templateCode.replace('<uid>', kwargs['uid'])
	outHandle.write(templateCode)

# main -----------------------------------
def main():
	outHandle = open(outFile, 'w')
	output(outHandle, pnl = header)
	output(outHandle, pnl = panelHeader)

	# output single panels
	replace_output_title(outHandle, pnl=panelTitle, job='ingest_metadata', title='Ingest & Metadata', h=1, w=8, x=0, y=0)
	replace_output_single(outHandle, pnl=panelStat, job='ingest_metadata', title='Up', h=2, w=2, x=0, y=1)
#	replace_output_single(outHandle, pnl=panelSingle, job='ingest_metadata', title='CPU', h=2, w=2, x=2, y=1, thresholds='0.1,1.1', colour2='#ba43a9')
	replace_output_single(outHandle, pnl=panelStat, job='ingest_metadata', title='CPU', h=2, w=2, x=2, y=1, threshold2='0.1', threshold3='1.1', colour2='#ba43a9')
	replace_output_single(outHandle, pnl=panelStat, job='ingest_metadata', title='Dsk', h=2, w=2, x=4, y=1)
	replace_output_single(outHandle, pnl=panelStat, job='ingest_metadata', title='Mem', h=2, w=2, x=6, y=1)
	replace_output_single(outHandle, pnl=panelStat, job='im-access-http', title='WWW', h=2, w=2, x=0, y=3)

	replace_output_title(outHandle, pnl=panelTitle, job='hadoop', title='Hadoop', h=1, w=8, x=8, y=0)
	replace_output_single(outHandle, pnl=panelStat, job='hadoop', title='Up', h=2, w=2, x=8, y=1)
	replace_output_single(outHandle, pnl=panelStat, job='hadoop', title='CPU', h=2, w=2, x=10, y=1)
	replace_output_single(outHandle, pnl=panelStat, job='hadoop', title='Nodes', h=2, w=2, x=12, y=1)
#	replace_output_single(outHandle, pnl=panelSingleHadoopUsed, job='hadoop', title='Used', h=4, w=2, x=14, y=1)
	replace_output_single(outHandle, pnl=panelStatHadoopUsed, job='hadoop', title='Used', h=4, w=2, x=14, y=1, threshold2='85', threshold3='90')
	replace_output_single(outHandle, pnl=panelStat, job='hadoop', title='Dsk', h=2, w=2, x=8, y=3)
#	replace_output_single(outHandle, pnl=panelSingle, job='hadoop', title='Mem', h=2, w=2, x=10, y=3, thresholds='0.1,1.1')
	replace_output_single(outHandle, pnl=panelStat, job='hadoop', title='Mem', h=2, w=2, x=10, y=3, threshold2='0.1', threshold3='1.1')
	replace_output_single(outHandle, pnl=panelStat, job='hadoop', title='Under-rep', h=2, w=2, x=12, y=3)

	replace_output_title(outHandle, pnl=panelTitle, job='discovery_access', title='Discovery & Access', h=1, w=8, x=16, y=0)
	replace_output_single(outHandle, pnl=panelStat, job='discovery_access', title='Up', h=2, w=2, x=16, y=1)
	replace_output_single(outHandle, pnl=panelStat, job='discovery_access', title='CPU', h=2, w=2, x=18, y=1)
	replace_output_single(outHandle, pnl=panelStat, job='discovery_access', title='Dsk', h=2, w=2, x=20, y=1)
#	replace_output_single(outHandle, pnl=panelSingle, job='discovery_access', title='Mem', h=2, w=2, x=22, y=1, thresholds='0.1,1.1', colour2='#ba43a9')
	replace_output_single(outHandle, pnl=panelStat, job='discovery_access', title='Mem', h=2, w=2, x=22, y=1, threshold2='0.1', threshold3='1.1', colour2='#ba43a9')
#	replace_output_single(outHandle, pnl=panelSingle, job='discovery_access', title='UTR', h=2, w=2, x=16, y=3, thresholds='0.1,2.1')
	replace_output_single(outHandle, pnl=panelStat, job='discovery_access', title='UTR', h=2, w=2, x=16, y=3, threshold2='0.1', threshold3='2.1')
#	replace_output_single(outHandle, pnl=panelSingle, job='da-access-http', title='WWW', h=2, w=2, x=18, y=3, thresholds='0.1,1.1')
	replace_output_single(outHandle, pnl=panelStat, job='da-access-http', title='WWW', h=2, w=2, x=18, y=3, threshold2='0.1', threshold3='1.1')

	replace_output_title(outHandle, pnl=panelTitle, job='services', title='Services', h=1, w=8, x=0, y=5)
	replace_output_single(outHandle, pnl=panelStat, job='services', title='Up', h=2, w=2, x=0, y=6)
	replace_output_single(outHandle, pnl=panelStat, job='services', title='CPU', h=2, w=2, x=2, y=6)
	replace_output_single(outHandle, pnl=panelStat, job='services', title='Dsk', h=2, w=2, x=4, y=6)
	replace_output_single(outHandle, pnl=panelStat, job='services', title='Mem', h=2, w=2, x=6, y=6)

	replace_output_title(outHandle, pnl=panelTitle, job='gluster', title='Gluster', h=1, w=8, x=8, y=6)
	replace_output_single(outHandle, pnl=panelStat, job='gluster', title='Up', h=2, w=2, x=8, y=7)
	replace_output_single(outHandle, pnl=panelStat, job='gluster', title='CPU', h=2, w=2, x=10, y=7)
	replace_output_single(outHandle, pnl=panelStat, job='gluster', title='Dsk', h=2, w=2, x=12, y=7)
	replace_output_single(outHandle, pnl=panelStat, job='gluster', title='Mem', h=2, w=2, x=14, y=7)

	replace_output_title(outHandle, pnl=panelTitle, job='solr', title='Solr', h=1, w=8, x=16, y=5)
	replace_output_single(outHandle, pnl=panelStat, job='solr', title='Up', h=2, w=2, x=16, y=6)
	replace_output_single(outHandle, pnl=panelStat, job='solr', title='CPU', h=2, w=2, x=18, y=6)
	replace_output_single(outHandle, pnl=panelStat, job='solr', title='Dsk', h=2, w=2, x=20, y=6)
	replace_output_single(outHandle, pnl=panelStat, job='solr', title='Mem', h=2, w=2, x=22, y=6)
	replace_output_single(outHandle, pnl=panelStat, job='solr-query', title='Query', h=2, w=2, x=16, y=8)

	replace_output_title(outHandle, pnl=panelTitle, job='infrastructure', title='Infrastructure', h=1, w=8, x=8, y=9)
	replace_output_single(outHandle, pnl=panelStat, job='infrastructure', title='Up', h=2, w=2, x=8, y=10)
	replace_output_single(outHandle, pnl=panelStat, job='infrastructure', title='CPU', h=2, w=2, x=10, y=10)
	replace_output_single(outHandle, pnl=panelStat, job='infrastructure', title='Dsk', h=2, w=2, x=12, y=10)
	replace_output_single(outHandle, pnl = panelStat, job = 'infrastructure', title = 'Mem', h=2, w=2, x=14, y=10)

	replace_output_title(outHandle, pnl=panelTitle, job='wa_services', title='WA Services', h=1, w=24, x=0, y=12)
	replace_output_single(outHandle, pnl=panelStat, job='trackdb', title='trackdb refresh', h=2, w=3, x=0, y=13, textmode='value', threshold2='22', threshold3='26')
	# output last panel with final ',' removed to make output json valid
#	replace_output_single(outHandle, pnl=panelSingle, job='trackdb', title='trackdb numFound', h=2, w=3, x=3, y=13, thresholds='10,100', colour1='#D44A3A', colour3='#299C46', lastPanel=True)
	replace_output_single(outHandle, pnl=panelStat, job='trackdb', title='trackdb numFound', h=2, w=3, x=3, y=13, textmode='value', threshold2='10', threshold3='100', colour1='#D44A3A', colour3='#299C46', lastPanel=True)

	# amend dashboard values
	output(outHandle, pnl = panelFooter)
	date = datetime.datetime.now()
	formattedDate = date.strftime("%Y%m%d%H%M%S")
	replace_output_footer(outHandle, pnl=footer, title=dashTitle, uid=dashUid)

	outHandle.close()

if __name__ == '__main__':
	main()
