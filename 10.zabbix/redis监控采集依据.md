## 监控采集依据

类似吞吐量，缓存的查询次数，命中率之类的

## 主要通过info命令进行采集(redis基础数据采集)

> redis 自定义监控项

```shell
UserParameter=Redis.Status,/usr/local/redis/bin/redis-cli -h 127.0.0.1 -p 6379 ping |grep -c PONG
UserParameter=Redis_conn[*],/usr/local/redis/bin/redis-cli -h $1 -p $2 info | grep -w "connected_clients" | awk -F':' '{print $2}'
UserParameter=Redis_rss_mem[*],/usr/local/redis/bin/redis-cli -h $1 -p $2 info | grep -w "used_memory_rss" | awk -F':' '{print $2}'
UserParameter=Redis_lua_mem[*],/usr/local/redis/bin/redis-cli -h $1 -p $2 info | grep -w "used_memory_lua" | awk -F':' '{print $2}'
UserParameter=Redis_cpu_sys[*],/usr/local/redis/bin/redis-cli -h $1 -p $2 info | grep -w "used_cpu_sys" | awk -F':' '{print $2}'
UserParameter=Redis_cpu_user[*],/usr/local/redis/bin/redis-cli -h $1 -p $2 info | grep -w "used_cpu_user" | awk -F':' '{print $2}'
UserParameter=Redis_cpu_sys_cline[*],/usr/local/redis/bin/redis-cli -h $1 -p $2 info | grep -w "used_cpu_sys_children" | awk -F':' '{print $2}'
UserParameter=Redis_cpu_user_cline[*],/usr/local/redis/bin/redis-cli -h $1 -p $2 info | grep -w "used_cpu_user_children" | awk -F':' '{print $2}'
UserParameter=Redis_keys_num[*],/usr/local/redis/bin/redis-cli -h $1 -p $2 info | grep -w "$$1" | grep -w "keys" | grep db$3 | awk -F'=' '{print $2}' | awk -F',' '{print $1}'
UserParameter=Redis_loading[*],/usr/local/redis/bin/redis-cli -h $1 -p $2 info | grep loading | awk -F':' '{print $$2}'
Redis.Status --检测Redis运行状态， 返回整数
Redis_conn  --检测Redis成功连接数，返回整数
Redis_rss_mem  --检测Redis系统分配内存，返回整数
Redis_lua_mem  --检测Redis引擎消耗内存，返回整数
Redis_cpu_sys --检测Redis主程序核心CPU消耗率，返回整数
Redis_cpu_user --检测Redis主程序用户CPU消耗率，返回整数
Redis_cpu_sys_cline --检测Redis后台核心CPU消耗率，返回整数
Redis_cpu_user_cline --检测Redis后台用户CPU消耗率，返回整数
Redis_keys_num --检测库键值数，返回整数
Redis_loding --检测Redis持久化文件状态，返回整数
```

## 监控采集依据

类似吞吐量，缓存的查询次数，命中率之类的

## 主要通过info命令进行采集

```
uptime_in_days				##redis启动的天数
connected_clients			##redis连接的客户端数
blocked_clients:            ##正在等待阻塞命令（BLPOP、BRPOP、BRPOPLPUSH）的客户端的数量
used_memory_peak_human:		##reids所用内存的高峰期
used_memory:				##redis运行起来使用的内存数
expired_keys:				##过期的key数量
evicted_keys:				##删除过期的key数量
keyspace_misses:			##没命中的key数量
keyspace_hits:				##命中的key数量
connected_slaves:			##已连接的从服务器数
rejected_connections:		##因为超过最大连接数被拒接的请求数量
```

## 安装telnet

```shell
yum -y install telnet
```

## 五、在被监控端上编写自动发现脚本

##### 1、创建zabbix脚本存放目录

```shell
mkdir -p /etc/zabbix/scripts
```

##### 2、编写自动发现redis脚本

```shell
vim /etc/zabbix/scripts/redis_discovery.sh

#!/bin/bash

port=(`sudo netstat -tpln | awk -F "[ :]+" '/redis/ && /0.0.0.0/ {print $5}'`)
printf '{\n'
printf '\t"data":[\n'
   for key in ${!port[@]}
       do
           if [[ "${#port[@]}" -gt 1 && "${key}" -ne "$((${#port[@]}-1))" ]];then
  socket=`ps aux|grep ${port[${key}]}|grep -v grep|awk -F '=' '{print $10}'|cut -d ' ' -f 1`
              printf '\t {\n'
              printf "\t\t\t\"{#REDISPORT}\":\"${port[${key}]}\"},\n"
         else [[ "${key}" -eq "((${#port[@]}-1))" ]]
  socket=`ps aux|grep ${port[${key}]}|grep -v grep|awk -F '=' '{print $10}'|cut -d ' ' -f 1`
              printf '\t {\n'
              printf "\t\t\t\"{#REDISPORT}\":\"${port[${key}]}\"}\n"
           fi
   done
              printf '\t ]\n'
              printf '}\n'
```

##### 3、给予脚本执行权限

```shell
chmod +x /etc/zabbix/scripts/redis_discovery.sh
```

##### 4、允许zabbix用户无密码运行netstat

```shell
vim /etc/sudoers

#Defaults    requiretty							#注释掉
zabbix  ALL=(root)      NOPASSWD:/bin/netstat		#添加
```

##### 5、编辑zabbix_agentd的配置文件支持自定义脚本

```shell
vim /etc/zabbix/zabbix_agentd.conf

UnsafeUserParameters=1
```

##### 6、编辑zabbix_agentd的配置文件添加zabbix配置文件目录

```shell
vim /etc/zabbix/zabbix_agentd.conf

Include=/etc/zabbix/zabbix_agentd.conf.d/
```

##### 7、创建key文件

```shell
vim /etc/zabbix/zabbix_agentd.conf.d/redis_status.conf

UserParameter=redis.discovery[*],/etc/zabbix/scripts/redis_discovery.sh $1
UserParameter=redis.status[*],(echo info; sleep 1) | telnet 127.0.0.1 $1 2>&1 |grep $2|cut -d : -f2



参数说明：
其中的格式为UserParameter=<key>,<command>

<key>：就是在web端添加监控脚本时的key值
<command>：就是该key值对应的执行脚本，也就是脚本执行路径
```

##### 8、重启zabbix_agentd服务

```shell
service zabbix_agentd restart
```

##### 9. 在zabbix server端进行测试

```shell
zabbix_get -s zabbix_agent_ip -p10050 -k"redis.discovery"
zabbix_get -s zabbix_agent_ip -p10050 -k"redis.status[6379,expired_keys:]"
```

#### 通过zabbix web

添加模板》》添加应用集》添加监控项》添加触发器》添加报警

》》在grafana 添加形成报表数据 