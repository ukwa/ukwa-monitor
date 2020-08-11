#!/usr/bin/env bash

export PROMETHEUS_SERVICE_NAME='monitor-prometheus.api.wa.bl.uk'
export ALERTMANAGER_SERVICE_NAME='monitor-alerts.api.wa.bl.uk'
export GRAFANA_SERVICE_NAME='monitor-grafana.api.wa.bl.uk'
export FC_EMBEDDED_SERVICE_NAME='192.168.45.15:9191'

export VISUALIZER_PORT=8080
export GRAFANA_PORT=3000
export PROMETHEUS_PORT=9090
export ALERTMANAGER_PORT=9093
export DATA_GRAFANA=/opt/data/grafana
export DATA_PROMETHEUS=/opt/data/prometheus
export DATA_ALERTMANAGER=/opt/data/alertmanager
export HTTP_PROXY=http://explorer2:3128/
export HDFS_EXPORTER='hdfs-exporter.api.wa.bl.uk:80'

export ALERT_RECEIVER='prod'
export ALERT_EMAIL_DEV='gil.hoggarth@bl.uk'
export ALERT_EMAIL_BETA='gil.hoggarth@bl.uk'
export ALERT_EMAIL_PROD='wa=sysadm@bl.uk'

source ~/gitlab/ukwa-monitor/monitoring.sh
cd ../
envsubst < ./alertmanager/config.yml-template > ./alertmanager/config.yml
envsubst < ./grafana/grafana.ini-template > ./grafana/grafana.ini
envsubst < ./grafana/provisioning/datasources/prometheus.yaml-template > ./grafana/provisioning/datasources/prometheus.yaml
envsubst < ./grafana/provisioning/datasources/frequent_crawl.yaml-template > ./grafana/provisioning/datasources/frequent_crawl.yaml
envsubst < ./prometheus/prometheus.yml-template > ./prometheus/prometheus.yml
envsubst < ./grafana/provisioning/dashboards/daily_dashboard.json-template > ./grafana/provisioning/dashboards/daily_dashboard.json
envsubst < ./grafana/provisioning/dashboards/wa_status.json-template > ./grafana/provisioning/dashboards/wa_status.json

docker stack deploy -c docker-compose.yml monitor
