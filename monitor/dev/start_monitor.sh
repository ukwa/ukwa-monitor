#!/usr/bin/env bash

export HOST_IP=192.168.45.91
export DEPLOYMENT_IP=192.168.45.45
export PROMETHEUS_SERVICE_NAME='monitor-prometheus.dapi.wa.bl.uk'
export ALERTMANAGER_SERVICE_NAME='monitor-alerts.dapi.wa.bl.uk'
export GRAFANA_SERVICE_NAME='monitor-grafana.dapi.wa.bl.uk'

export VISUALIZER_PORT=8081
export GRAFANA_PORT=3000
export PROMETHEUS_PORT=9090
export ALERTMANAGER_PORT=9093
export DATA_GRAFANA=/mnt/nfs/data/ukwa-monitor/grafana
export DATA_PROMETHEUS=/mnt/nfs/data/ukwa-monitor/prometheus
export DATA_ALERTMANAGER=/mnt/nfs/data/ukwa-monitor/alertmanager
export HTTP_PROXY=http://explorer2:3128/

source ~/gitlab/ukwa-monitor/monitoring.sh
cd ../
docker stack deploy -c docker-compose.yml prometheus
