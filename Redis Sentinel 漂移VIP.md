## Redis Sentinel 漂移VIP

### 原理

![img](http://img.liuwenqi.com/blog/2019-10-26-102651.png)

使用一个内网虚拟IP，所有入口及出口redis连接均通过虚拟VIP

```sh
## 主redis手动绑定虚拟VIP
/sbin/ip  addr add 192.168.56.250/24 dev eth1
/sbin/arping -q   -c 3 -A 192.168.56.250 -I eth1 
```

### 修改步骤

> 如何在进行redis故障转移时，将VIP漂移到新的主redis服务器上。

这里可以使用`redis sentinel`的一个参数`client-reconfig-script`，这个参数配置执行脚本，sentinel在做failover的时候会执行这个脚本，并且传递6个参数<master-name>、 <role>、 <state>、 <from-ip>、 <from-port>、 <to-ip> 、<to-port>，其中<to-ip>是新主redis的IP地址，可以在这个脚本里做VIP漂移操作。

### 修改所有redis-sentinel配置文件

- `/etc/sentinel.conf`，增加上面一行。##配置文件对应目录修改

```reStructuredText
sentinel client-reconfig-script master8000   /scripts/redis_vip_check.sh
```

### 创建脚本

> 每台服务器都需要创建

/scripts/目录下创建nredis_vip_check.sh脚本文件，这个脚本做VIP漂移操作，内容如下：
\#redis_vip_check.sh脚本内容

```sh
#!/bin/bash
MASTER_IP=$6  #第六个参数是新主redis的ip地址
LOCAL_IP='192.168.56.101'  #其他两个服务器上为192.168.56.102，192.168.56.103
VIP='192.168.56.250'
NETMASK='24'
INTERFACE='eth1'
if [ ${MASTER_IP} = ${LOCAL_IP} ];then   
    /sbin/ip  addr  add ${VIP}/${NETMASK}  dev ${INTERFACE}  #将VIP绑定到该服务器上
    /sbin/arping -q -c 3 -A ${VIP} -I ${INTERFACE}
    exit 0
else 
   /sbin/ip  addr del  ${VIP}/${NETMASK}  dev ${INTERFACE}   #将VIP从该服务器上删除
   exit 0
fi
exit 1  #如果返回1，sentinel会一直执行这个脚本
```