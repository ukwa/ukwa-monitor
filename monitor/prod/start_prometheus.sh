#!/usr/bin/env bash

export VISUALIZER_PORT=8080
export DATA_GRAFANA=/opt/data/grafana
export DATA_PROMETHEUS=/opt/data/prometheus
export DATA_ALERTMANAGER=/opt/data/altermanager
export HTTP_PROXY=http://explorer2:3128/

source ~/gitlab/ukwa-monitor/monitoring.sh
docker stack deploy -c ../docker-compose.yml prometheus
