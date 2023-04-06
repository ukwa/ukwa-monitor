import re
from modules7 import rw

# hacky copy of template variables and values
panelStat = 'templates7/panelStat'
panelStatHadoopUsed = 'templates7/panelStatHadoopUsed'

# panel ID, increments on usage so all unique in panels
ID = 0


# internal functions -----
def _next_id():
	global ID
	ID += 1
	return str(ID)

# functions --------------
def space(oH, **kwargs):
	templateCode = rw.read_template(pnl=kwargs['pnl'])
	templateCode = templateCode.replace('<id>', _next_id())
	templateCode = templateCode.replace('<h>', str(kwargs['h']))
	templateCode = templateCode.replace('<w>', str(kwargs['w']))
	templateCode = templateCode.replace('<x>', str(kwargs['x']))
	templateCode = templateCode.replace('<y>', str(kwargs['y']))
	oH.write(templateCode)

def title(oH, **kwargs):
	templateCode = rw.read_template(pnl=kwargs['pnl'])
	templateCode = templateCode.replace('<title>', kwargs['title'])
	templateCode = templateCode.replace('<id>', _next_id())
	templateCode = templateCode.replace('<h>', str(kwargs['h']))
	templateCode = templateCode.replace('<w>', str(kwargs['w']))
	templateCode = templateCode.replace('<x>', str(kwargs['x']))
	templateCode = templateCode.replace('<y>', str(kwargs['y']))
	oH.write(templateCode)

def single(oH, **kwargs):
	templateCode = rw.read_template(pnl=kwargs['pnl'])
	templateCode = templateCode.replace('<title>', kwargs['title'])
	templateCode = templateCode.replace('<id>', _next_id())
	templateCode = templateCode.replace('<h>', str(kwargs['h']))
	templateCode = templateCode.replace('<w>', str(kwargs['w']))
	templateCode = templateCode.replace('<x>', str(kwargs['x']))
	templateCode = templateCode.replace('<y>', str(kwargs['y']))

	# specific thresholds replacement
	if kwargs['pnl'] == panelStat or kwargs['pnl'] == panelStatHadoopUsed:
		if 'threshold1' in kwargs: templateCode = templateCode.replace('<threshold1>', kwargs['threshold1'])
		else: templateCode = templateCode.replace('<threshold1>', 'null')
		if 'threshold2' in kwargs: templateCode = templateCode.replace('<threshold2>', kwargs['threshold2'])
		else: templateCode = templateCode.replace('<threshold2>', '0.1')
		if 'threshold3' in kwargs: templateCode = templateCode.replace('<threshold3>', kwargs['threshold3'])
		else: templateCode = templateCode.replace('<threshold3>', '1')
		if 'textmode' in kwargs: templateCode = templateCode.replace('<textmode>', kwargs['textmode'])
		else: templateCode = templateCode.replace('<textmode>', 'none')
	else:
		if 'thresholds' in kwargs: templateCode = templateCode.replace('<thresholds>', kwargs['thresholds'])
		else: templateCode = templateCode.replace('<thresholds>', '0.1,1')			# default threshhold
	# specific colours replacement
	if 'colour1' in kwargs: templateCode = templateCode.replace('<colour1>', kwargs['colour1'])
	else: templateCode = templateCode.replace('<colour1>', '#299C46')				# default panel okay colour
	if 'colour2' in kwargs: templateCode = templateCode.replace('<colour2>', kwargs['colour2'])
	else: templateCode = templateCode.replace('<colour2>', '#ED8027')				# default panel warning colour
	if 'colour3' in kwargs: templateCode = templateCode.replace('<colour3>', kwargs['colour3'])
	else: templateCode = templateCode.replace('<colour3>', '#D44A3A')				# default panel problem colour

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
	elif kwargs['title'] == 'UTR':
		expr = 'count(uptimerobot_monitor_up==0) OR vector(0)'
		templateCode = templateCode.replace('<expr>', expr)
	elif kwargs['title'] == 'WWW' or kwargs['title'] == 'Query':
		expr = 'count(probe_http_status_code{job=\\"' + kwargs['job'] + '\\"} != 200) OR vector(0)'
		templateCode = templateCode.replace('<expr>', expr)
	elif kwargs['title'] == 'Refresh':
		expr = '(time() - trackdb_refresh_timestamp) / (60*60)'
		templateCode = templateCode.replace('<expr>', expr)
	elif kwargs['title'] == 'numFound':
		expr = 'sum(trackdb_numFound - (trackdb_numFound offset 1d))'
		templateCode = templateCode.replace('<expr>', expr)
	elif kwargs['job'] == 'hadoop':
		if kwargs['title'] == 'Nodes':
			expr = 'hdfs_node_count{status=\\"dead\\",instance=\\"${HDFS_EXPORTER}\\"}'
			templateCode = templateCode.replace('<expr>', expr)
		elif kwargs['title'] == 'Under-rep':
			expr = 'hdfs_under_replicated_block_count{instance=\\"${HDFS_EXPORTER}\\"}'
			templateCode = templateCode.replace('<expr>', expr)
		elif kwargs['title'] == 'Used':
			expr = 'hdfs_used_percent{instance=\\"${HDFS_EXPORTER}\\"}'
			templateCode = templateCode.replace('<expr>', expr)
	elif kwargs['job'] == 'h3stats':
		if kwargs['title'] == 'Dead Nodes':
			expr = 'hadoop3stats{instance=\\"deadNodes\\",job=\\"h3stats\\"}'
			templateCode = templateCode.replace('<expr>', expr)
		elif kwargs['title'] == 'Under-rep':
			expr = 'hadoop3stats{instance=\\"underReplicatedBlocks\\",job=\\"h3stats\\"}'
			templateCode = templateCode.replace('<expr>', expr)
		elif kwargs['title'] == 'Used':
			expr = 'hadoop3stats{instance=\\"usedPercent\\",job=\\"h3stats\\"}'
			templateCode = templateCode.replace('<expr>', expr)
	elif kwargs['title'] == 'LDLs':
		expr = 'sum(last_over_time(recent_connections{job=\\"ldl_rr\\",instance=~\\"DLS-.+\\"}[30m]))'
		templateCode = templateCode.replace('<expr>', expr)

	# add last comma if not last panel
	if 'lastPanel' not in kwargs:
		templateCode = re.sub(r'}$', '},', templateCode)
	oH.write(templateCode)

def footer(oH, **kwargs):
	templateCode = rw.read_template(pnl=kwargs['pnl'])
	templateCode = templateCode.replace('<title>', kwargs['title'])
	templateCode = templateCode.replace('<uid>', kwargs['uid'])
	oH.write(templateCode)
