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
export PYTHONPATH=~/github/ukwa-monitor/stat-pusher
source $PYTHONPATH/venv/bin/activate
cd $PYTHONPATH

# ensure log directory exists
[[ -d logs/ ]] || mkdir logs

# ensure python libraries installed
pip install -r ldl-requirements.txt

# run stat-pusher script
if [[ ${DEBUG} -eq 1 ]]; then
	nohup python ldl-pusher.py &		# if debug argument given, don't push to /dev/null (for live service debugging)

elif [[ ${HOSTNAME} =~ ^(monitor|prod) ]]; then
	nohup python ldl-pusher.py  > /dev/null &	# disable generation of large logs over time
else
	nohup python ldl-pusher.py &
fi
