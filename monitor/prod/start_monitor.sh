#!/usr/bin/env bash

export HOST_IP=192.168.45.204
export PROMETHEUS_SERVICE_NAME='monitor-prometheus.api.wa.bl.uk'
export ALERTMANAGER_SERVICE_NAME='monitor-alertmanager.api.wa.bl.uk'

export VISUALIZER_PORT=8080
export GRAFANA_PORT=3000
export PROMETHEUS_PORT=9090
export ALERTMANAGER_PORT=9093
export DATA_GRAFANA=/opt/data/grafana
export DATA_PROMETHEUS=/opt/data/prometheus
export DATA_ALERTMANAGER=/opt/data/alertmanager
export HTTP_PROXY=http://explorer2:3128/

source ~/gitlab/ukwa-monitor/monitoring.sh
docker stack deploy -c ../docker-compose.yml prometheus
