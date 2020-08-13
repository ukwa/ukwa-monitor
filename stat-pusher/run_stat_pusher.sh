#!/usr/bin/env bash

# read script environ argument
ENVIRON=$1
if ! [[ ${ENVIRON} =~ dev|beta|prod ]]; then
	echo "ERROR: Script $0 requires environment argument"
	exit
fi

# if wa-internal envars needed, source file
source ~/gitlab/ukwa-monitor/monitoring.sh

# setup venv
#### venv created via 'virtualenv -p /usr/local/bin/python3.7 venv'
export PYTHONPATH=~/github/ukwa-monitor/stat-pusher
source $PYTHONPATH/venv/bin/activate
cd $PYTHONPATH

# ensure python libraries installed
pip install -r requirements.txt

# run stat-pusher script
python update_pushgateway_stats.py ${ENVIRON}
