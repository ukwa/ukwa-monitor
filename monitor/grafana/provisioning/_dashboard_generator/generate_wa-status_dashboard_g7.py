#!/usr/bin/env python3
# 'Simple code' is to create the wa_status dashboard with easy repetition of panels and controlled positioning.
# Script name includes 'g7' as targetted for grafana v7 (panels, visualisations seem to get replaced over time; e.g., previous v5 used singleStat)

# modules for 'g7'
from modules7 import rw
from modules7 import replace

# output filename
outFile = 'wa_status.json-template'
# dashboard prefixes
dashTitle = 'WA Status'
dashUid = 'wast'
# template files for 'g7'
header = 'templates7/header'
panelHeader = 'templates7/panelHeader'
panelBanner = 'templates7/panelBanner'
panelTitle = 'templates7/panelTitle'
panelStat = 'templates7/panelStat'
panelStatHadoopUsed = 'templates7/panelStatHadoopUsed'
panelSpace = 'templates7/panelSpacer'
panelFooter = 'templates7/panelFooter'
footer = 'templates7/footer'
# hwxy values
HEIGHT = 2
WIDTH = 2
FIRSTCOL = 0
titleHeight = 1
blockWidth = 8

# main -----------------------------------
def script():
	oH = open(outFile, 'w')		# get output handle (oH) for output file
	rw.output(oH, pnl=header)	# write page header template to output handle 
	rw.output(oH, pnl=panelHeader)	# write panel header to output handle

	# output single panels -----
	# hwxy: As grafana panel positioning shrinks to earliest, top left position, hwxy defined here isn't necessarily implemented
	# Consequently, below hxwy vars are used to try to set panel positions relative to previous panels.
	# hw is used solely for panelStat height and width, as these are key values and other panels vary too much.
	# Comment at line end of each panel represents what the xy values are expected to be following the intention of the vars (x.y).
	# These can be checked with actual values in grafana, via panel Inspect > Panel JSON

	# first 'row' of sections -----
	blockRow = 0

	## hadoop 0.20
	xpos = FIRSTCOL		# panel x position for hadoop 0.20, 0
	ypos = blockRow		# panel y position for hadoop 0.20, 0
	blockCol = xpos		# set block beginning column
	replace.title(oH, pnl=panelTitle, title='Hadoop 0.20', h=titleHeight, w=blockWidth, x=xpos, y=ypos)
	ypos += titleHeight	# increment ypos by title height
	for _title in ['Up', 'CPU', 'Nodes']:
		replace.single(oH, pnl=panelStat, job='hadoop', title=_title, h=HEIGHT, w=WIDTH, x=xpos, y=ypos)
		xpos += WIDTH	# increment xpos by WIDTH
	replace.single(oH, pnl=panelStatHadoopUsed, job='hadoop', title='Used', threshold2='85', threshold3='96', h=4, w=2, x=xpos, y=ypos)
	xpos = blockCol		# reset xpos to beginning of block
	ypos += HEIGHT		# increment ypos by HEIGHT
	replace.single(oH, pnl=panelStat, job='hadoop', title='Dsk', h=HEIGHT, w=WIDTH, x=xpos, y=ypos)
	xpos += WIDTH		# increment xpos by WIDTH
	replace.single(oH, pnl=panelStat, job='hadoop', title='Mem', threshold2='0.1', threshold3='1.1', h=HEIGHT, w=WIDTH, x=xpos, y=ypos)
	xpos += WIDTH		# increment xpos by WIDTH
	replace.single(oH, pnl=panelStat, job='hadoop', title='Under-rep', h=HEIGHT, w=WIDTH, x=xpos, y=ypos)

	# gluster
	xpos = blockWidth	# panel x position for gluster, 8
	ypos = blockRow		# panel x position for gluster, 0
	blockCol = xpos
	replace.title(oH, pnl=panelTitle, title='Gluster', h=titleHeight, w=blockWidth, x=xpos, y=ypos)
	ypos += titleHeight
	for _title in ['Up', 'CPU', 'Dsk', 'Mem']:
		replace.single(oH, pnl=panelStat, job='gluster', title=_title, h=HEIGHT, w=WIDTH, x=xpos, y=ypos)
		xpos += WIDTH
	xpos = blockCol
	ypos += HEIGHT
	replace.space(oH, pnl=panelSpace, h=HEIGHT, w=blockWidth, x=xpos, y=ypos)

	## hadoop 3
	xpos += blockWidth	# panel x position for hadoop 3, blockWidth as previous spacer, 16
	ypos = blockRow		# panel x position for hadoop 3, 0
	blockCol = xpos
	replace.title(oH, pnl=panelTitle, title='Hadoop 3', h=titleHeight, w=blockWidth, x=xpos, y=ypos)
	ypos += titleHeight
	for _title in ['Up', 'CPU']:
		replace.single(oH, pnl=panelStat, job='hadoop3', title=_title, h=HEIGHT, w=WIDTH, x=xpos, y=ypos)
		xpos += WIDTH
	replace.single(oH, pnl=panelStat, job='h3stats', title='Dead Nodes' threshold2='0.9', threshold3='1.2', h=HEIGHT, w=WIDTH, x=xpos, y=ypos)
	xpos += WIDTH
	replace.single(oH, pnl=panelStatHadoopUsed, job='h3stats', title='Used', threshold2='85', threshold3='96', h=4, w=2, x=xpos, y=ypos)
	xpos = blockCol
	ypos += HEIGHT
	replace.single(oH, pnl=panelStat, job='hadoop3', title='Dsk', h=HEIGHT, w=WIDTH, x=xpos, y=ypos)
	xpos += WIDTH
	replace.single(oH, pnl=panelStat, job='hadoop3', title='Mem', threshold2='0.1', threshold3='1.1', h=HEIGHT, w=WIDTH, x=xpos, y=ypos)
	xpos += WIDTH
	replace.single(oH, pnl=panelStat, job='h3stats', title='Under-rep', threshold2='9', threshold3='250', h=HEIGHT, w=WIDTH, x=xpos, y=ypos)

	# second 'row' of sections -----
	blockRow = (titleHeight + HEIGHT + HEIGHT)	# blockRow set to exceed above titles and panels, 5

	## infrastructure
	xpos = FIRSTCOL		# panel x position for infrastructure, 0
	ypos = blockRow		# panel x position for infrastructure, 5
	blockCol = xpos
	replace.title(oH, pnl=panelTitle, title='Infrastructure', h=titleHeight, w=blockWidth, x=xpos, y=ypos)
	ypos += titleHeight
	for _title in ['Up', 'CPU', 'Dsk', 'Mem']:
		replace.single(oH, pnl=panelStat, job='infrastructure', title=_title, h=HEIGHT, w=WIDTH, x=xpos, y=ypos)
		xpos += WIDTH
	xpos = blockCol
	ypos += HEIGHT
	replace.single(oH, pnl=panelStat, job='infrastructure', title='LDLs', h=HEIGHT, w=WIDTH, x=xpos, y=ypos, textmode='value', colour1='#D44A3A', colour3='#299C46', threshold2='8.5', threshold3='9.5')

	# services
	xpos = blockWidth	# panel x position for services, 8
	ypos = blockRow		# panel x position for services, 5
	blockCol = xpos
	replace.title(oH, pnl=panelTitle, title='Services', h=titleHeight, w=blockWidth, x=xpos, y=ypos)
	ypos += titleHeight
	for _title in ['Up', 'CPU', 'Dsk', 'Mem']:
		replace.single(oH, pnl=panelStat, job='services', title=_title, h=HEIGHT, w=WIDTH, x=xpos, y=ypos)
		xpos += WIDTH
	xpos = blockCol
	ypos += HEIGHT
	replace.space(oH, pnl=panelSpace, h=HEIGHT, w=blockWidth, x=xpos, y=ypos)

	# solr servers
	xpos += blockWidth	# panel x position for solr, 16
	ypos = blockRow		# panel x position for solr, 5
	blockCol = xpos
	replace.title(oH, pnl=panelTitle, title='Solr', h=titleHeight, w=blockWidth, x=xpos, y=ypos)
	ypos += titleHeight
	for _title in ['Up', 'CPU', 'Dsk', 'Mem']:
		replace.single(oH, pnl=panelStat, job='solr', title=_title, h=HEIGHT, w=WIDTH, x=xpos, y=ypos)
		xpos += WIDTH
	xpos = blockCol
	ypos += HEIGHT
	replace.single(oH, pnl=panelStat, job='solr-query', title='Query', h=HEIGHT, w=WIDTH, x=xpos, y=ypos)

	# third 'row' of sections -----
	blockRow = ((titleHeight + HEIGHT + HEIGHT) *2)	# blockRow set to exceed above titles and panels, 10

	# ingest & metadata
	xpos = FIRSTCOL		# panel x position for ingest & metadata, 0
	ypos = blockRow		# panel x position for ingest & metadata, 10
	blockCol = xpos
	replace.title(oH, pnl=panelTitle, title='Ingest & Metadata', h=titleHeight, w=blockWidth, x=xpos, y=ypos)
	ypos += titleHeight
	for _title in ['Up', 'CPU', 'Dsk', 'Mem']:
		replace.single(oH, pnl=panelStat, job='ingest_metadata', title=_title, h=HEIGHT, w=WIDTH, x=xpos, y=ypos)
		xpos += WIDTH
	xpos = blockCol
	ypos += HEIGHT
	replace.single(oH, pnl=panelStat, job='im-access-http', title='WWW', h=HEIGHT, w=WIDTH, x=xpos, y=ypos)

	#trackdb
	xpos = blockWidth	# panel x position for trackdb, 8
	ypos = blockRow		# panel x position for trackdb, 10
	replace.title(oH, pnl=panelTitle, title='TrackDB', h=titleHeight, w=blockWidth,  x=xpos, y=ypos)
	replace.single(oH, pnl=panelStat, job='trackdb', title='Refresh', textmode='value', threshold2='22', threshold3='26', h=HEIGHT, w=(WIDTH*2), x=xpos, y=ypos)
	xpos += (WIDTH * 2)
	replace.single(oH, pnl=panelStat, job='trackdb', title='numFound', textmode='value', threshold2='10', threshold3='100', colour1='#D44A3A', colour3='#299C46', h=HEIGHT, w=(WIDTH*2), x=xpos, y=ypos)

	# discovery & access
	xpos += (blockWidth / 2)	# panel x position for discovery_access
	ypos = blockRow		# panel x position for discovery_access
	blockCol = xpos
	replace.title(oH, pnl=panelTitle, title='Discovery & Access', h=titleHeight, w=blockWidth, x=xpos, y=ypos)
	ypos += titleHeight
	for _title in ['Up', 'CPU', 'Dsk', 'Mem']:
		replace.single(oH, pnl=panelStat, job='discovery_access', title=_title, h=HEIGHT, w=WIDTH, x=xpos, y=ypos)
		xpos += WIDTH
	xpos = blockCol
	ypos += HEIGHT
	replace.single(oH, pnl=panelStat, job='discovery_access', title='UTR', threshold2='0.1', threshold3='2.1', h=HEIGHT, w=WIDTH, x=xpos, y=ypos)

	#### tag last panel as 'lastPanel=True' so that the template ',' is removed (to make json valid)
	xpos += WIDTH
	replace.single(oH, pnl=panelStat, job='da-access-http', title='WWW', threshold2='0.1', threshold3='1.1', h=HEIGHT, w=WIDTH, x=xpos, y=ypos, lastPanel=True)


	# amend dashboard values
	rw.output(oH, pnl = panelFooter)
	replace.footer(oH, pnl=footer, title=dashTitle, uid=dashUid)

	oH.close()

if __name__ == '__main__':
	script()
