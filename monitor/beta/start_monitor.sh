#!/usr/bin/env bash

export PROMETHEUS_SERVICE_NAME='monitor-prometheus.bapi.wa.bl.uk'
export ALERTMANAGER_SERVICE_NAME='monitor-alerts.bapi.wa.bl.uk'
export GRAFANA_SERVICE_NAME='monitor-grafana.bapi.wa.bl.uk'
export FC_EMBEDDED_SERVICE_NAME='192.168.45.34:9191'

export VISUALIZER_PORT=8080
export GRAFANA_PORT=3000
export PROMETHEUS_PORT=9090
export ALERTMANAGER_PORT=9093
export DATA_PREFIX=/mnt/gluster/beta/monitor/data
export DATA_GRAFANA=${DATA_PREFIX}/ukwa-monitor/grafana
export DATA_PROMETHEUS=${DATA_PREFIX}/ukwa-monitor/prometheus
export DATA_ALERTMANAGER=${DATA_PREFIX}/ukwa-monitor/alertmanager
export HTTP_PROXY=http://explorer2:3128/
export HDFS_EXPORTER='hdfs-exporter.bapi.wa.bl.uk:80'

export ALERT_RECEIVER='beta'
export ALERT_EMAIL_DEV='gil.hoggarth@bl.uk'
export ALERT_EMAIL_BETA='gil.hoggarth@bl.uk'
export ALERT_EMAIL_PROD='wa-sysadm@bl.uk'

source ~/gitlab/ukwa-monitor/monitoring.sh
cd ../
envsubst < ./alertmanager/config.yml-template > ./alertmanager/config.yml
envsubst < ./grafana/grafana.ini-template > ./grafana/grafana.ini
envsubst < ./grafana/provisioning/datasources/prometheus.yaml-template > ./grafana/provisioning/datasources/prometheus.yaml
envsubst < ./grafana/provisioning/datasources/frequent_crawl.yaml-template > ./grafana/provisioning/datasources/frequent_crawl.yaml
envsubst < ./prometheus/prometheus.yml-template > ./prometheus/prometheus.yml
envsubst < ./grafana/provisioning/dashboards/wa_status.json-template > ./grafana/provisioning/dashboards/wa_status.json

docker stack deploy -c docker-compose.yml monitor
