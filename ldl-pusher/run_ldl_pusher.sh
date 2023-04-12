#!/usr/bin/env bash
DEBUG=

# get argument if provided
if [[ $1 ]]; then
	if [[ $1 == 'debug' ]]; then
		DEBUG=1
	fi
fi

# setup venv
export PYTHONPATH=~/github/ukwa-monitor/ldl-pusher
source ${PYTHONPATH}/venv/bin/activate

# ensure log directory exists
[[ -d ${PYTHONPATH}/logs/ ]] || mkdir ${PYTHONPATH}/logs

# ensure python libraries installed
cd ${PYTHONPATH}/
pip install -r requirements.txt

# run ldl-pusher script
if [[ ${DEBUG} -eq 1 ]]; then
	${PYTHONPATH}/ldl-pusher.py &		# if debug argument given, don't push to /dev/null (for live service debugging)

elif [[ ${HOSTNAME} =~ ^(monitor|prod) ]]; then
	${PYTHONPATH}/ldl-pusher.py  > /dev/null &	# disable generation of large logs over time
else
	${PYTHONPATH}/ldl-pusher.py &
fi
