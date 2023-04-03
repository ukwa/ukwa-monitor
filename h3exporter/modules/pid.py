import os, sys


# functions -----------------
def create(pf):
	if not os.path.exists(pf):
		with open(pf, 'w') as ph:
			ph.write(str(os.getpid()))

def delete(pf):
	if os.path.exists(pf):
		try:
			os.remove(pf)
		except Exception as e:
			print(f"ERROR: failed to delete pid file [{pf}]")
			sys.exit(1)
