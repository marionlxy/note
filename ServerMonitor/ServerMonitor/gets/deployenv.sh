#!/usr/bin/env bash
#
# @path: none
# @date: 2019/08/28
# @usage: create monitor environment.


/bin/mkdir "/tasks"
/bin/mkdir "/var/log/monitor"
echo '*/5 * * * *	/bin/bash /tasks/monitor.sh &' >>/var/spool/cron/root
