def read_template(**kwargs):
	tplC = ''
	with open(kwargs['pnl'], 'r') as tC:
		tplC = tC.read()
	return tplC

def output(outHandle, **kwargs):
	templateCode = read_template(pnl=kwargs['pnl'])
	outHandle.write(templateCode)
