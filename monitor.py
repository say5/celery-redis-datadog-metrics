#!/usr/bin/env python

import argparse
import base64
import json
import os
import redis
from datadog import initialize, statsd

PRIORITY_SEP = '\x06\x16'

def get_args():
    description = 'Tool to collect metrics about celery tasks in Redis powered broker'
    formatter_class = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=formatter_class)
    parser.add_argument('--redis-host',
                        type=str,
                        required=True,
                        help='Redis hostname',
                        dest='redis_host')
    parser.add_argument('--redis-port',
                        type=int,
                        default=6379,
                        help='Redis port',
                        dest='redis_port')
    parser.add_argument('--redis-pass',
                        type=str,
                        default='',
                        help='Redis password',
                        dest='redis_pass')
    parser.add_argument('--redis-db',
                        type=str,
                        default='0',
                        help='Redis database',
                        dest='redis_db')
    parser.add_argument('--priority-steps',
                        type=str,
                        default='0,3,6,9',
                        help='Celery priority steps',
                        dest='priority_steps')
    parser.add_argument('--chunk-size',
                        type=int,
                        default=10000,
                        help='Chunk size to get from redis',
                        dest='chunk_size')
    parser.add_argument('--celery-queue',
                        type=str,
                        required=True,
                        help='Celery queue name',
                        dest='celery_queue')
    parser.add_argument('--dd-statsd-host',
                        type=str,
                        required=True,
                        help='DD statsd hostname',
                        dest='dd_statsd_host')
    parser.add_argument('--dd-statsd-port',
                        type=int,
                        default=8125,
                        help='DD statsd port',
                        dest='dd_statsd_port')
    parser.add_argument('--dd-metric-prefix',
                        type=str,
                        required=True,
                        help='DD metric prefix',
                        dest='dd_metric_prefix')
    return parser.parse_args()


def redis_connect(args):
    connection = redis.StrictRedis(
      host=args.redis_host,
      port=args.redis_port,
      password=args.redis_pass,
      db=args.redis_db
    )
    return connection


def make_queue_name_for_pri(queue, pri):
    return '{0}{1}{2}'.format(*((queue, PRIORITY_SEP, pri) if pri else
                                (queue, '', '')))


def datadog_init(args):
    options = {
        'statsd_host': args.dd_statsd_host,
        'statsd_port': args.dd_statsd_port,
    }
    initialize(**options)


def get_stat(args, redis):
    # https://stackoverflow.com/questions/5544629/retrieve-list-of-tasks-in-a-queue-in-celery?lq=1
    priority_names = [make_queue_name_for_pri(args.celery_queue, pri) for pri in
                      str(args.priority_steps).split(',')]

    stat = {}
    for queue in priority_names:
        # size of queue
        qlen = redis.llen(queue)
        # number of chunks to get
        chunk_n = (qlen + args.chunk_size - 1) // args.chunk_size
        for chunk in range(0, chunk_n):
            for task in redis.lrange(queue, chunk*args.chunk_size, chunk*args.chunk_size+args.chunk_size):
                payload = json.loads(task)
                task = payload['headers']['task']
                prio = payload['properties']['priority']
                key = '{0}{1}'.format(task, prio)
                if not key in stat:
                    stat[key] = 1
                else:
                    stat[key] += 1
    for task, count in stat.items():
        metric = '{0}{1}'.format(args.dd_metric_prefix, task)
        print('{0}->{1}'.format(task, count))
        statsd.gauge(metric, count)


def main():
    args = get_args()
    datadog_init(args)
    redis = redis_connect(args)
    get_stat(args, redis)


if __name__ == '__main__':
    main()
