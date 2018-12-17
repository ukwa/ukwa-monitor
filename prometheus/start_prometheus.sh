#!/usr/bin/env bash

source ~/gitlab/ukwa-monitor/prometheus.sh
docker stack deploy -c docker-compose.yml prometheus
