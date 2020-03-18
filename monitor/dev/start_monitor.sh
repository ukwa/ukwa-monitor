#!/usr/bin/env bash

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
export HDFS_EXPORTER='hdfs-exporter.dapi.wa.bl.uk:80'

export ALERT_EMAIL='gil.hoggarth@bl.uk'

source ~/gitlab/ukwa-monitor/monitoring.sh
cd ../
envsubst < ./alertmanager/config.yml-template > ./alertmanager/config.yml
envsubst < ./grafana/grafana.ini-template > ./grafana/grafana.ini
envsubst < ./grafana/provisioning/datasources/prometheus.yaml-template > ./grafana/provisioning/datasources/prometheus.yaml
envsubst < ./prometheus/prometheus.yml-template > ./prometheus/prometheus.yml
envsubst < ./grafana/provisioning/dashboards/daily_dashboard.json-template > ./grafana/provisioning/dashboards/daily_dashboard.json
envsubst < ./grafana/provisioning/dashboards/wa_status.json-template > ./grafana/provisioning/dashboards/wa_status.json

docker stack deploy -c docker-compose.yml monitor
