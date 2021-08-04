#!/bin/sh
curl -v -X POST http://monitor-prometheus.api.wa.bl.uk/-/reload
curl -v -X POST http://monitor-alerts.api.wa.bl.uk/-/reload

