#!/bin/env bash
set -o nounset


# source monitor settings or exit
SETTINGS=~/github/aws-fc-setup/monitor/settings.sh
if [[ -f ${SETTINGS} ]]; then
	source ${SETTINGS}
else
	echo -e "ERROR: Monitor settings [${SETTINGS}] missing"
	exit 1
fi


# common
STORAGE_PATH=/mnt/data/monitor
[[ -d ${STORAGE_PATH}/ ]] || mkdir -p ${STORAGE_PATH}


# alertmanager
#export ALERTMANAGER_SERVICE_NAME='monitor'
#export ALERTMANAGER_DATA=${STORAGE_PATH}/alertmanager
#export ALERTMANAGER_PORT=9093
#[[ -d ${ALERTMANAGER_DATA}/ ]] || mkdir -p ${ALERTMANAGER_DATA}
#envsubst < ./alertmanager/config.yml-template > ./alertmanager/config.yml


# prometheus
export PROMETHEUS_SERVICE_NAME='monitor'
export PROMETHEUS_DATA=${STORAGE_PATH}/prometheus
export PROMETHEUS_PORT=9090
[[ -d ${PROMETHEUS_DATA}/ ]] || mkdir -p ${PROMETHEUS_DATA}
sudo chown -R root:root ${PROMETHEUS_DATA}
envsubst < ./prometheus/prometheus.yml-template > ./prometheus/prometheus.yml


# grafana
export GRAFANA_SERVICE_NAME='monitor'
export GRAFANA_PORT=3000
export GRAFANA_DATA=${STORAGE_PATH}/grafana
export FC_EMBEDDED_SERVICE_NAME='172.31.43.254'
[[ -d ${GRAFANA_DATA}/ ]] || mkdir -p ${GRAFANA_DATA}
chown -R ${USER}:${USER} ${GRAFANA_DATA}
envsubst < ./grafana/grafana.ini-template > ./grafana/grafana.ini
envsubst < ./grafana/provisioning/datasources/prometheus.yaml-template > ./grafana/provisioning/datasources/prometheus.yaml
envsubst < ./grafana/provisioning/datasources/frequent_crawl.yaml-template > ./grafana/provisioning/datasources/frequent_crawl.yaml


# start monitoring stacks
docker stack deploy -c docker-compose.yml monitor
