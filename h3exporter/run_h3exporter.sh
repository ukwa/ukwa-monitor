#!/usr/bin/env bash
#### Swarm environment also determined in script, from hostname, for settings

# setup venv
export PYTHONPATH=/home/monitor/github/ukwa-monitor/h3exporter
source ${PYTHONPATH}/venv/bin/activate

# ensure log directory exists
[[ -d ${PYTHONPATH}/logs/ ]] || mkdir  ${PYTHONPATH}/logs

# ensure python libraries installed
cd ${PYTHONPATH}
pip install -r requirements.txt

# run h3exporter script
${PYTHONPATH}/h3exporter.py & 
exit 0


# ------
if [[ $(hostname -s) =~ ^(prod|monitor) ]]; then
	${PYTHONPATH}/h3exporter.py  > /dev/null &	# disable generation of large logs over time
else
	${PYTHONPATH}/h3exporter.py & 
fi
