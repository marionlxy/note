### zabbix4.0之自动注册

Auth: braior

| 主机列表            | 主机IP       |
| :------------------ | :----------- |
| zabbix-server       | 192.168.59.3 |
| zabbix-agent(nginx) | 192.168.59.4 |
| zabbix-agent(mysql) | 192.168.59.5 |

- 首先安装在相应的主机上安装好相应的zabbix-server和zabbix-agent，zabbix-agent端分别装nginx和mysql服务，测试zabbix-server功能正常


- 在zabbix-server上添加两个主机组：nginx和mysql。


- 我们事先准备好的两个简单的模板，模板的名称为 ：Template For HTTP Nginx Service和Template For Database MySQL，分别对应监控nginx和mysql，将这两个模板导入到zabbix-server里面，后面我们在自动注册里会套用这两个模板。


![](C:\Users\szgoi\Desktop\zabbix\image\1.png)

#### 配置zabbix-agent(nginx)

- 修改zabbix-agent.conf前先对配置文件进行备份；要实现自动注册，我们还要增加一条配置项HostMetadata。


```
[root@nginx_59 ~]# cat /etc/zabbix/zabbix_agentd.conf |grep -v "^#" |grep -v "^$"
PidFile=/var/run/zabbix/zabbix_agentd.pid
LogFile=/var/log/zabbix/zabbix_agentd.log
LogFileSize=0
Server=192.168.59.3
ListenPort=10050
ListenIP=192.168.59.4
ServerActive=192.168.59.3
Hostname=nginx_59.4
HostMetadata=Linux nginx
Include=/etc/zabbix/zabbix_agentd.d/*.conf
```

- 我们配置的选项HostMetadata=Linux nginx：是指主机元数据，linux代表是linux服务器，nginx只是一个标识。我们通过这个标识符(当然这个标识符也可定义多个,用空格分隔开)，部署了nginx的实例可以通过自动注册主动请求zabbix-server将其监控，并按照事先定义好的自动注册动作关联模板。


- 配置选项和zabbix-agent(mysql)略同，只是将Hostname改为Hostname=mysql_59.5，HostMetadata修改为HostMetadata=Linux mysql。


```
[root@rab3 ~]# cat /etc/zabbix/zabbix_agentd.conf |grep -v "^#" |grep -v "^$"
PidFile=/var/run/zabbix/zabbix_agentd.pid
LogFile=/var/log/zabbix/zabbix_agentd.log
LogFileSize=0
Server=192.168.59.3
ListenPort=10050
ListenIP=192.168.59.5
ServerActive=192.168.59.3
Hostname=mysql_59.5
HostMetadata=Linux mysql
Include=/etc/zabbix/zabbix_agentd.d/*.conf
```

#### 在zabbix-server配置自动注册（nginx）

- 创建自动注册的动作

![](C:\Users\szgoi\Desktop\zabbix\image\2.png)

- 添加主机元数据，这里要用到我们前面的配置项HostMetadata=Linux nginx，同时满足这两个元素Linux和nginx的主机通过自动注册将会被监控，如下图。

![](C:\Users\szgoi\Desktop\zabbix\image\3.png)

- 配置操作选项，将自动注册的主机添加到主机，并添加到我们预先设定好的主机组，并关联我们预先导入的模板Template For HTTP nginx Service，如下图。

![](C:\Users\szgoi\Desktop\zabbix\image\4.png)

- mysql的自动注册动作的配置与上面nginx步骤雷同，两个自动注册动作结果如下，并启用两个动作：


![](C:\Users\szgoi\Desktop\zabbix\image\5.png)

- 至此，所有的配置都已完成。启动两台zabbix-agent，观察zabbix-server的主机列表，看到两台主机都已被监控，并看到相应的主机组都已添加。


![](C:\Users\szgoi\Desktop\zabbix\image\6.png)

![](C:\Users\szgoi\Desktop\zabbix\image\8.png)

- nginx_59.4很是顽强，没有被我绿，原因是我的模板优点小问题，不影响主动注册。查看告警信息，nginx_59.4主机没有启动nginx，所以直接有告警信息出现。

![](C:\Users\szgoi\Desktop\zabbix\image\7.png)

至此，自动注册功能已实现。