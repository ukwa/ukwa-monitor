#!/usr/bin/env bash

export VISUALIZER_PORT=8081
export DATA_GRAFANA=/mnt/nfs/data/ukwa-monitor/grafana
export DATA_PROMETHEUS=/mnt/nfs/data/ukwa-monitor/prometheus
export DATA_ALERTMANAGER=/mnt/nfs/data/ukwa-monitor/altermanager
export HTTP_PROXY=http://explorer2:3128/

source ~/gitlab/ukwa-monitor/monitoring.sh
docker stack deploy -c ../docker-compose.yml prometheus
