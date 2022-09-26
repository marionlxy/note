# [centos7之zabbix3.2代理（zabbix-proxy）搭建](https://www.cnblogs.com/lei0213/p/8953573.html)

zabbix的强大之处也在于它是分布式监控系统，对于多机房大集群情况下，肯定不是一台zabbix-server服务器来进行信息的收集等工作，就要用到代理了。在记录zabbix-proxy之前，要系统的记录一下zabbix的监控方式。

### 一、Zabbix监控方式

zabbix自带多种类型的监控方式，大致分两类：公共的协议和zabbix专业的协议。支持多种协议的监控方式，相应地也支持多种设备的监控，从而可以对复杂的网络环境进行监控。

1.1支持的监控方式

官方链接：https://www.zabbix.com/documentation/3.2/manual/config/items/itemtypes

项类型覆盖各种方法获取数据从您的系统。 每个项目类型都有其自己的一组支持项键和必需的参数。目前由zabbix提供下列事项类型的支持

```shell
`Zabbix agent checks  #这些客户端来进行数据采集，又分为Zabbix agent（被动模式：客户端等着服务器端来要数据），Zabbix agent (active)（主动模式：客户端主动发送数据到服务器端）``SNMP agent checks   #SNMP方式，如果要监控打印机网络设备等支持SNMP设备的话，但是又不能安装agent的设备。``SNMP traps      ``IPMI checks      #IPMI即智能平台管理接口，现在是业界通过的标准。用户可以利用IPMI监视服务器的物理特性，如温度、电压、电扇工作状态、电源供应以及机箱入侵等。``Simple checks     #简单检查，选择此方式后icmping主机判断主机是否存活``VMware monitoring   #VMware监控``Log file monitoring  #监控日志文件``Calculated items    #监控项的计算``Zabbix ``internal` `checks #内部检查允许监控Zabbix的内部流程。 换句话说,您可以监视与Zabbix服务器或Zabbix代理到底发生了什么。``SSH checks       #SSH检查。Zabbix服务器必须执行SSH检查最初的配置SSH2的支持。``Telnet checks     #Telnet检查。Telnet检查表现为缺少代理的监控。 Zabbix代理不需要远程登录检查。``External checks    #Zabbix服务器执行的外部检查是检查通过运行shell脚本或二进制。外部检查不需要任何代理被监控主机上运行。``Aggregate checks    #总体检查Zabbix服务器通过直接从项目收集汇总信息数据库查询。``Trapper items     #陷阱项目接受传入的数据，而不是查询它。对于您可能要“推”到Zabbix的任何数据都是有用的。``JMX monitoring     #java管理扩展，是java平台上为应用程序、设备、系统等植入管理功能的框架。JMX可以跨越一系列异构操作系统平台、系统体系架构和网络传输协议，灵活地开发无缝集成的系统、网络和服务管理应用。``ODBC checks      #ODBC监控对应数据库监控Zabbix前端项目类型。ODBC是一个C编程语言中间件API用于访问数据库管理系统(DBMS)。 ODBC的概念是由微软,后来移植到其他平台。``#Zabbix可以查询任何数据库,支持ODBC。 为此,Zabbix不直接连接到数据库,但是使用ODBC接口和ODBC驱动程序设置。 这个函数可以更有效地监控不同数据库的多种用途——例如,检查特定数据库队列,使用统计等等。 Zabbix支持unixODBC,这是一种最常用的开源ODBCAPI`
```

1.2Agent监控方式

　　Agent分为主动和被动两种方式.

**Trapper监控方式**

Trapper是发送任意的数据给Zabbix-server,采用主动推送的方式，Trapper不需要安装客户端，Key的名称是可以灵活定义，在此工作模式下，Zabbix数据发送的程序是zabbix-sender，可以发送任何zabbix-server想要获取的数据。

前面http://www.51niux.com/?id=147关于zabbix-sender命令介绍那里已经演示了trapper方式的使用。

\#主要是主机添加Host name那里一定要是一个唯一的名称，客户端配置文件里面Host name那里定义的一定要和zabbix server端定义的Host name相一致。不然无法获取trapper方式发送的数据。Type of information(信息类型）这里也一定要跟key所上传数据类型一致，不然也是会失败的。

在这种形式下，zabbix-server不会主动连接客户端的IP，而是Trapper主动连接zabbix-server。

**被动方式**

Passive（被动模式），zabbix-server和zabbix-agent之间的通信是zabbix的专用协议，数据格式为JSON。默认情况下，zabbix-agent工作在被动模式下，工作的模式是由Key和zabbix_agentd.conf参数配置决定的。

被动模式的流程如下：

Server打开一个TCP连接。

Server发送一个key为agent.ping\n。

Agent接收到这个请求，然后响应数据<HEADER><DATALEN>1.

Server对接收到的数据进行处理。

TCP连接关闭。

**主动方式**

　　Active(主动模式），主动模式由于是Agent将采集到的数据主动发送给Server，而不需要Server每次连接Agent等待采集，所以采用主动模式会使Zabbix-Server具有最好的性能。在大型环境下，一定要将工作模式设置为主动模式，并尽可能采用更多的proxy以降低Server的负担，一般多机房，每个机房肯定都要设置proxy的。

**主动方式设置**

　　客户端的配置：/etc/zabbix/zabbix_agentd.conf配置文件中设置ServerActive=192.168.1.103（这个IP可以是server也可以是proxy的IP地址），然后重启zabbix_agentd服务。

　　服务端的配置：服务器端items的检测方式（Type）修改为Zabbix agent(active)

**主动方式的请求周期**

Agent向Server建立一个TCP的连接。

Agent请求需要检测的数据列表。

Server响应Agent，发送一个Items列表（item key、delay）。

Agent响应请求。

TCP连接完成本次会话后关闭。

Agent开始周期性的收集数据。

\#下面是Agent要向Server发送数据了：

Agent向Server建立一个TCP连接。

Agent发送在采集周期内，需要采集数据给Server.

Server处理Agent发送的数据。

TCP连接关闭。

###  二、zabbix-proxy搭建

2.1概述

　　官网链接：https://www.zabbix.com/documentation/3.2/manual/distributed_monitoring/proxies

　　zabbix proxy可以代替zabbix server检索客户端的数据，然后把数据汇报给zabbix server，并且在一定程度上分担了zabbix server的压力.zabbix proxy可以非常简便的实现了集中式、分布式监控.

zabbix proxy使用场景:

```
`监控远程区域设备``监控本地网络不稳定区域``当zabbix监控上千设备时，使用它来减轻server的压力``简化zabbix的维护`
```

![img](https://images2018.cnblogs.com/blog/976930/201804/976930-20180426170112154-45587367.png)

\#代理需要Zabbix服务器只有一个TCP连接。 这种方式更容易绕过防火墙,你只需要配置一个防火墙规则。Zabbix代理必须使用一个单独的数据库。 代理服务器收集的所有数据都会在本地存储，然后再发送到服务器。 这样就不会因为服务器的任何临时通信问题而丢失数据。 代理配置文件中的ProxyLocalBuffer和ProxyOfflineBuffer参数控制数据在本地保存多长时间。

proxy的配置文件参数：https://www.zabbix.com/documentation/3.2/manual/appendix/config/zabbix_proxy

Zabbix代理是一个数据收集器。 它不计算触发,处理事件或发送警报。

### 2.2zabbix-proxy的安装配置

zabbix-proxy环境准备

```shell
`systemctl stop firewalld``systemctl disable firewalld` `setenforce 0``sed -i ``'s/SELINUX=enforcing/SELINUX=disabled/g'` `/etc/selinux/config`
```

 zabbix-server准备环境：

　　1、server搭建完成，并可正常监控

　　2、保证telnet server的10050和10051端口正常（默认zabbix-server的ListenIP=127.0.0.1，这种情况下telnet 10051是失败的，需要在后面加上服务器的IP地址）

　　![img](https://images2018.cnblogs.com/blog/976930/201804/976930-20180426170514488-1485676284.png)

**zabbix-proxy操作**

　　安装必要的插件

```
`yum install -y lrzsz wget gcc gcc-c++ vim`
```

　  创建用户和组

```
`groupadd zabbix -g 201``useradd -g zabbix -u 201 -m zabbix`
```

　　下载安装包

　　wget [https://sourceforge.net/projects/zabbix/files/ZABBIX%20Latest%20Stable/3.2.6/zabbix-3.2.6.tar.gz](https://sourceforge.net/projects/zabbix/files/ZABBIX Latest Stable/3.2.6/zabbix-3.2.6.tar.gz/download)

　　安装

```shell
`#tar zxf zabbix-3.2.6.tar.gz``#./configure --prefix=/usr/local/zabbix-3.2.6 --sysconfdir=/etc/zabbix --enable-proxy --enable-agent --enable-ipv6 --with-mysql=/usr/bin/mysql_config --with-net-snmp --with-libcurl --with-openipmi --with-unixodbc  --with-ssh2 --enable-java``#make``#make install`
```

　　

```shell
`#ln -s /usr/local/zabbix-3.2.6 /usr/local/zabbix_proxy`
```

　　安装mariadb或者msyql数据库

```shell
`yum install -y mariadb mariadb-server mariadb-devel`
```

　　启动数据库，并设置为开机自启动。

```shell
`# systemctl start mariadb``# systemctl enable mariadb`
```

　　配置数据库



```shell
mysqladmin -uroot password '123456'
mysql -uroot -p123456 -e 'create database zabbix_proxy character set utf8;'
mysql -uroot -p123456 -e "grant all privileges on zabbix_proxy.* to zabbix@localhost identified by 'zabbix';"
mysql -uroot -p123456 -e "flush privileges;"
mysql -uzabbix -pzabbix zabbix_proxy </root/zabbix-3.2.6/database/mysql/schema.sql
```



　　zabbix-proxy配置文件

```shell
`#cd /etc/zabbix/``#cp zabbix_proxy.conf zabbix_proxy.conf.bak` `vim /etc/zabbix/zabbix_proxy.conf`
```

　　配置文件内容（配置文件中不能有汉字）

```sh
`erver=172.16.5.238``Hostname=zabbix_proxy_172.16.5.239``LogFile=/tmp/zabbix_proxy.log``DBHost=localhost``DBName=zabbix_proxy``DBUser=zabbix``DBPassword=zabbix``ConfigFrequency=120 #主动去server端去拉去配置更新的频率120秒一次``DataSenderFrequency=60 #发送采集的监控数据到服务器端，默认是1秒，我们一分钟发送一次`
```

 　启动服务

```shell
`/usr/local/zabbix_proxy/sbin/zabbix_proxy`
```

![img](https://images2018.cnblogs.com/blog/976930/201804/976930-20180426173825175-1727298870.png)

　　zabbix-server端配置

![img](https://images2018.cnblogs.com/blog/976930/201804/976930-20180426173954816-1544451325.png)

下面是上图中参数的介绍：

```sh
`Proxy name ： 输入代理名称。 它必须与代理配置文件中的Hostname参数中的名称相同。``Proxy mode ： 选择代理模式。Active（主动模式） - 代理将连接到Zabbix服务器并请求配置数据.Passive（被动模式） - Zabbix服务器连接到代理。请注意，在使用活动代理时，没有加密通信（敏感）代理配置数据可能可用于访问Zabbix服务器陷阱端口的各方。 这是可能的，因为任何人都可以伪装成活动代理，并且如果不发生身份验证，则请求配置数据。``Hosts   ： 添加要由代理监视的主机。已经由另一个代理监视的主机在其他主机选项中显示为灰色。``Description： 输入代理描述。`
```

![img](https://images2018.cnblogs.com/blog/976930/201804/976930-20180426174057400-1815959845.png)

 

 下面是上图中参数的介绍：

```sh
`Connections to proxy：服务器如何连接到被动代理：无加密（默认），使用PSK（预共享密钥）或证书。``Connections ``from` `proxy：从活动代理中选择允许的连接类型。 可以同时选择几种连接类型（用于测试和切换到其他连接类型）。 默认为“无加密”。``#点击Certificate之后又两个参数：``Issuer：允许颁发证书。 证书首先通过CA（认证机构）验证。 如果CA有效，则由CA签名，则可以使用Issuer字段来进一步限制允许的CA。 该字段是可选的，如果您的Zabbix安装使用多个CA的证书，则使用该字段。``Subject：允许的证书。 证书首先通过CA验证。 如果它有效，由CA签名，则主题字段可用于仅允许Subject字符串的一个值。 如果此字段为空，则接受由配置的CA签名的任何有效证书。``#点击PSK之后又两个参数：``PSK identity：预共享密钥身份字符串。``PSK ： 预共享密钥（hex-``string``）。 如果Zabbix使用mbed TLS（PolarSSL）库，Zabbix将使用GnuTLS或OpenSSL库，64位十六进制（32字节PSK），最大长度为512位十六进制数（256字节PSK）。 示例：1f87b595725ac58dd977beef14b97461a7c1045b9a1c963065002c5473194952`
```

![img](https://images2018.cnblogs.com/blog/976930/201804/976930-20180426174117295-1441907835.png)

![img](https://images2018.cnblogs.com/blog/976930/201804/976930-20180426175138785-1892042558.png)

　　客户端配置

　　# vim /etc/zabbix/zabbix_agentd.conf #下面是要修改的地方

```sh
`Server=172.16.5.239      #agentd被动模式下的server或者proxy的IP地址``ServerActive=172.16.5.239   #如果agentd端是被动模式的话，此条和下面那条并不非用配置，但是如果agentd端是主动模式的话，此条一定要配置上。``Hostname=172.16.5.240`
```

　　# /etc/init.d/zabbix_agentd restart #重启zabbix_agentd服务

![img](https://images2018.cnblogs.com/blog/976930/201804/976930-20180426175249350-484762184.png)

 

 　proxy端测试一下：

```
`/usr/local/zabbix-3.2.6/bin/zabbix_get -s 172.16.5.240 -k agent.ping`
```

![img](https://images2018.cnblogs.com/blog/976930/201804/976930-20180426174952268-1171504781.png)

 

### 主动模式的使用

1、前面我们说了被动模式适合小型的监控模式，如果成百上千的话，我们尽量使用主动模式。但是怎么用呢？手动模式下只需要配置zabbix-agentd配置文件里面的Server=192.168.1.58参数即可，ServerActive=和Hostname=对zabbix来说不是很重要。但如果服务器要使用zabbix主动模式的话，必须这里要启用ServerActive和Hostname，并且Hostname必须要和主机名称一模一样。否则监控不成功。

 ![img](https://img2018.cnblogs.com/blog/976930/201910/976930-20191030171619005-1525420150.png)

 

 2、就算是这样也并没有完全启用主动模式，我们还需要修改windows和linux以及zabbix-agent模板的监控模式。这里我们之说linux，把监控项和自动发现里面的模板全都改成Zabbix客户端(主动式)

　　![img](https://img2018.cnblogs.com/blog/976930/201910/976930-20191030171810216-794591475.png)

　　![img](https://img2018.cnblogs.com/blog/976930/201910/976930-20191030171909915-1377945726.png)

###  ping检测

 　1、我们知道zabbix-server已经有了fping的功能，不会的同学可以看https://www.cnblogs.com/lei0213/p/8859326.html这边帖子。那只限于zabbix-server有了。这里zabbix-proxy并没有这个功能。所以我们要单独给proxy安装fping，方法看也是这个帖子。

　　 2、但是会报两个错误。

　　错误一

```sh
`At least one of ``'/usr/sbin/fping'``, ``'/usr/sbin/fping6'` `must exist. Both are missing in the system`
```

　　他的意思你说你没有安装fping，我们安装即可。但是proxy上没有zabbix-server配置文件，所以这里我们只需要做软连接到/usr/sbin/fping下就行。

　　错误二

```
`fping failed: (null): can't create socket (must run as root?) : Permission denied`
```

　　他的意思是说你的fping文件没有权限，所以需要给他权限。

```
`chmod ``4755` `/``usr``/``sbin``/``fping或者chmod u``+``s ``/``usr``/``sbin``/``fping`
```

　　如下状态都是已启用就行。错误一和错误二都是在这里提醒的。

　　![img](https://img2018.cnblogs.com/blog/976930/201910/976930-20191030172513045-1310806.png)

参考地址：http://www.51niux.com/?id=156