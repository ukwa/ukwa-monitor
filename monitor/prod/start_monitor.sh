#!/usr/bin/env bash

export HOST_IP=$(hostname -i |  grep -oP "192\.168\.45\.[0-9]+")
export PROMETHEUS_SERVICE_NAME='monitor-prometheus.api.wa.bl.uk'
export ALERTMANAGER_SERVICE_NAME='monitor-alerts.api.wa.bl.uk'
export GRAFANA_SERVICE_NAME='monitor-grafana.api.wa.bl.uk'

export VISUALIZER_PORT=8080
export GRAFANA_PORT=3000
export PROMETHEUS_PORT=9090
export ALERTMANAGER_PORT=9093
export DATA_GRAFANA=/mnt/gluster/prod/data/grafana
export DATA_PROMETHEUS=/mnt/gluster/prod/data/prometheus
export DATA_ALERTMANAGER=/mnt/gluster/prod/data/alertmanager
export HTTP_PROXY=http://explorer2:3128/

export ALERT_EMAIL='wa-sysadm@bl.uk'

source ~/gitlab/ukwa-monitor/monitoring.sh
cd ../
envsubst < ./alertmanager/config.yml-template > ./alertmanager/config.yml
envsubst < ./grafana/grafana.ini-template > ./grafana/grafana.ini
envsubst < ./grafana/provisioning/datasources/prometheus.yaml-template > ./grafana/provisioning/datasources/prometheus.yaml
envsubst < ./prometheus/prometheus.yml-template > ./prometheus/prometheus.yml
docker stack deploy -c docker-compose.yml prometheus
