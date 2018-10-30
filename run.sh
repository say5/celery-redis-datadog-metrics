#!/bin/bash

if [ -n "$REDIS_SSL" ]; then
  SSL='--ssl'
fi

while /bin/true
do
  ./monitor.py \
    --redis-host ${REDIS_HOST} \
    --redis-port ${REDIS_PORT:-6379} \
    --redis-pass ${REDIS_PASS:-''} \
    --redis-db ${REDIS_DB:-0} \
    --priority-steps ${PRIORITY_STEPS:-'0,3,6,9'} \
    --chunk-size ${CHUNK_SIZE:-10000} \
    --celery-queue ${CELERY_QUEUE:-celery} \
    --dd-statsd-host ${STATSD_HOST:-localhost} \
    --dd-statsd-port ${STATSD_PORT:-8125} \
    --dd-metric-prefix ${DD_METRIC_PREFIX:-celery.} ${SSL:-''}
  sleep ${SLEEP:-600}
done
