#!/usr/bin/env bash

#### Swarm environment determined in script, from hostname

# setup venv
export PYTHONPATH=~/github/ukwa-monitor/stat-pusher
source $PYTHONPATH/venv/bin/activate
cd $PYTHONPATH

# ensure log directory exists
[[ -d logs/ ]] || mkdir logs

# ensure python libraries installed
pip install -r ldl-requirements.txt

# run stat-pusher script
if [[ ${HOSTNAME} =~ ^prod ]]; then
	nohup python ldl-pusher.py  > /dev/null &	# disable generation of large logs over time
else
	nohup python ldl-pusher.py &
fi
