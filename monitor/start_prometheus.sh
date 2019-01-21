#!/usr/bin/env bash

source ~/gitlab/ukwa-monitor/monitoring.sh
docker stack deploy -c docker-compose.yml prometheus
