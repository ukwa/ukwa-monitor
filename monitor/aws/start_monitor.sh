#!/bin/env bash
set -o nounset
export SERVER_IP=$(nmcli c s System\ eth0 | grep IP4.ADDRESS | awk '{print $2}' | awk -F '/' '{print $1}')


# source monitor settings or exit
SETTINGS=~/github/aws-fc-setup/monitor/settings.sh
if [[ -f ${SETTINGS} ]]; then
	source ${SETTINGS}
else
	echo -e "ERROR: Monitor settings [${SETTINGS}] missing"
	exit 1
fi
if [[ "${GRAFANA_ADMIN_PASSWORD}" == "" ]]; then
	echo -e "ERROR: GRAFANA_ADMIN_PASSWORD missing"
	exit 1
fi
if [[ "${SLACK_API_URL}" == "" ]]; then
	echo -e "ERROR: SLACK_API_URL missing"
	exit 1
fi


# common
STORAGE_PATH=/mnt/data/monitor
[[ -d ${STORAGE_PATH}/ ]] || mkdir -p ${STORAGE_PATH}


# alertmanager
export ALERTMANAGER_SERVICE_NAME='monitor'
export ALERTMANAGER_DATA=${STORAGE_PATH}/alertmanager
export ALERTMANAGER_PORT=9093
[[ -d ${ALERTMANAGER_DATA}/ ]] || mkdir -p ${ALERTMANAGER_DATA}
envsubst < ./alertmanager/config.yml-template > ./alertmanager/config.yml
sudo chown nobody:nobody ${ALERTMANAGER_DATA}


# prometheus
export PROMETHEUS_SERVICE_NAME='monitor'
export FC_PROMETHEUS_SERVICE_NAME='fc'
export PROMETHEUS_DATA=${STORAGE_PATH}/prometheus
export PROMETHEUS_PORT=9090
[[ -d ${PROMETHEUS_DATA}/ ]] || mkdir -p ${PROMETHEUS_DATA}
sudo chown -R root:root ${PROMETHEUS_DATA}
envsubst < ./prometheus/prometheus.yml-template > ./prometheus/prometheus.yml


# grafana
export GRAFANA_SERVICE_NAME='monitor'
export GRAFANA_PORT=3000
export GRAFANA_DATA=${STORAGE_PATH}/grafana
export FC_EMBEDDED_SERVICE_IP='172.31.43.254'
export GRAFANA_ORG_NAME='blukwa'
[[ -d ${GRAFANA_DATA}/ ]] || mkdir -p ${GRAFANA_DATA}
chown -R ${USER}:${USER} ${GRAFANA_DATA}
envsubst < ./grafana/grafana.ini-template > ./grafana/grafana.ini
envsubst < ./grafana/provisioning/dashboards/blukwa.yaml-template > ./grafana/provisioning/dashboards/blukwa.yaml
envsubst < ./grafana/provisioning/datasources/prometheus.yaml-template > ./grafana/provisioning/datasources/prometheus.yaml
envsubst < ./grafana/provisioning/datasources/frequent_crawl.yaml-template > ./grafana/provisioning/datasources/frequent_crawl.yaml


# start monitoring stacks
docker stack deploy -c docker-compose.yml monitor
