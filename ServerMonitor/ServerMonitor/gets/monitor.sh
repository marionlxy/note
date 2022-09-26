#!/usr/bin/env bash
#
# @path:/tasks/cpuMonitor.sh
# @date: 2019/08/28
# @usage: cpu monitor record log.

US=$(vmstat | awk 'BEGIN{ FS=" " }NR==3{ print $13 }')
SY=$(vmstat | awk 'BEGIN{ FS=" " }NR==3{ print $14 }')
ID=$(vmstat | awk 'NR==3{ print $15 }')
TOTAL=$(free -mw | awk 'NR==2{ print $2 }')
USE=$(free -mw | awk 'BEGIN{ FS=" " }NR==2{ print $3 }')
FREE=$(free -mw | awk 'BEGIN{ FS=" " }NR==2{ print $4 }')
CACHE=$(free -mw | awk 'BEGIN{ FS=" " }NR==2{ print $7 }')
memoryRate=$(echo "scale=1;((${USE}+${CACHE})/${TOTAL})*100" | bc -ql)
diskRate=$(df -Th | awk 'BEGIN{ FS=" " }NR==2{ print $6 }')

fileSize=$(du -sh /var/log/monitor/monitor.log | awk '{ print $1 }')
if [ "${fileSize}" == "2.1M" ];then
  mv /var/log/monitor/monitor.{log,log.bak-$(date +%Y%m%d%H%M%S)}
  touch /var/log/monitor/{example.log,monitor.log}
else
  echo "$(date +%Y%m%d%H%M%S) - ${HOSTNAME} - {\"cpu\": {\"user\": ${US}, \"system\": ${SY}, \"idle\": ${ID}}, \"memory\": {\"total\": ${TOTAL}, \"free\": ${FREE}, \"percent\": ${memoryRate}}, \"disk\": {\"percent\": \"${diskRate}\"}}" >>/var/log/monitor/monitor.log
fi
