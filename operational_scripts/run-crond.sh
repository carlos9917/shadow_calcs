#!/bin/sh
#crond -L /var/log/cron/cron.log "$@" && tail -f /var/log/cron/cron.log
cron -L /var/log/cron/cron.log "$@" && tail -f /var/log/cron/cron.log
