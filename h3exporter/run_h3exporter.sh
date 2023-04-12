#!/usr/bin/env bash
#### Swarm environment also determined in script, from hostname, for settings
DEBUG=

# get argument if provided
if [[ $1 ]]; then
	if [[ $1 == 'debug' ]]; then
		DEBUG=1
	fi
fi

# setup venv
export PYTHONPATH=~/github/ukwa-monitor/h3exporter
source ${PYTHONPATH}/venv/bin/activate

# ensure log directory exists
[[ -d ${PYTHONPATH}/logs/ ]] || mkdir  ${PYTHONPATH}/logs

# ensure python libraries installed
cd ${PYTHONPATH}/
pip install -r requirements.txt

# run h3exporter script
if [[ ${DEBUG} -eq 1 ]]; then
	${PYTHONPATH}/h3exporter.py &		# if debug argument given, don't push to /dev/null (for live service debugging)

elif [[ ${HOSTNAME} =~ ^(monitor|prod) ]]; then
	${PYTHONPATH}/h3exporter.py  > /dev/null &	# disable generation of large logs over time
else
	${PYTHONPATH}/h3exporter.py &
fi
