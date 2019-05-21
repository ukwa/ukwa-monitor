#!/bin/sh
source ~/gitlab/uptime-robot.sh

docker stack deploy -c docker-compose.yml metrics
