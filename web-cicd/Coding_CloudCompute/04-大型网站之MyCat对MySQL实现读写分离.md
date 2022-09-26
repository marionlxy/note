## 大型网站之MyCat对MySQL实现读写分离

-Author：bavdu

-Mail：bavduer@163.com

-GitHub：https://github.com/bavdu

---

**/* MyCat简介 */**  [MyCat下载](https://github.com/MyCATApache/Mycat-Server/archive/1.6.5-RELEASE.tar.gz)

&emsp;&emsp;MyCAT是一个开源软件,面向企业的“大型数据库集群”. MyCAT是一个数据库中间件,它是MySQL的替代品,支持事务和ACID作为企业数据库的MySQL集群,MyCAT可以取代昂贵的Oracle集群,MyCAT也是一种新型数据库,它看起来像是一个集成了内存缓存技术,NoSQL技术和HDFS大数据的SQL Server.

&emsp;&emsp;而作为一种新型的现代企业数据库产品, MyCAT与传统的数据库和新的分布式数据仓库相结合. 总之MyCAT是一个全新的数据库中间件.Mycat的目标是以低成本顺利地将当前的独立数据库和应用程序迁移到云端,并解决数据存储和业务规模快速增长带来的瓶颈问题



**/* 环境准备 */**

```shell
system：CentOS 7.5
mysql: 
	192.168.13.21
	192.168.13.22

mycat:
	192.168.13.20
```



**/* MySQL主从复制 */**

```shell
##MySQL5.7 主从复制 
下载安装源地址:https://dev.mysql.com/get/mysql80-community-release-el7-1.noarch.rpm

$ rpm -ivh https://dev.mysql.com/get/mysql80-community-release-el7-1.noarch.rpm
$ yum -y install mysql-community-server
$ systemctl start mysqld && systemctl enable mysqld

  ##------------------------------------主库设置------------------------------------##
[root@master ~]# vi /etc/my.cnf			//开启二进制日志并设置服务ID
[mysqld]
server-id=21
log-bin=mysql-bin

[root@master ~]# systemctl start mysqld && systemctl enable mysqld
[root@master ~]# grep 'password' /var/log/mysqld.log
2018-09-28T01:53:04.173732Z 1 [Note] A temporary password is generated for root@localhost: ied,1qj(y/gH //注意修改密码

[root@master ~]# mysql -uroot -p'(BavDu..0928)'

mysql> CREATE USER 'replication'@'192.168.13.22' IDENTIFIED BY "#BavDu..0928#";
Query OK, 0 rows affected (0.01 sec)

mysql> GRANT REPLICATION SLAVE ON *.* TO 'replication'@'192.168.13.22';
Query OK, 0 rows affected (0.00 sec)

mysql> SHOW MASTER STATUS;
+------------------+----------+--------------+------------------+-------------------+
| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set |
+------------------+----------+--------------+------------------+-------------------+
| mysql-bin.000002 |      877 |              |                  |                   |
+------------------+----------+--------------+------------------+-------------------+
1 row in set (0.00 sec)

  ##------------------------------------主库设置------------------------------------##

  ##------------------------------------从库设置------------------------------------##
[root@slave ~]# vi /etc/my.cnf
[mysqld]
server_id=22

[root@slave ~]# systemctl start mysqld && systemctl enable mysqld
[root@slave ~]# grep 'password' /var/log/mysqld.log
2018-09-28T02:07:33.890742Z 1 [Note] A temporary password is generated for root@localhost: dFS:z5DQ/<h5
[root@slave ~]# mysql -uroot -p'(BavDu..0928)'

mysql> CHANGE MASTER TO
    -> MASTER_HOST='192.168.13.21',
    -> MASTER_USER='replication',
    -> MASTER_PASSWORD='#BavDu..0928#',
    -> MASTER_LOG_FILE='mysql-bin.000001',
    -> MASTER_LOG_POS=877;

mysql> start slave;
mysql> show slave status\G;
*************************** 1. row ***************************
               Slave_IO_State: Waiting for master to send event
                  Master_Host: 192.168.13.21
                  Master_User: replication
                  Master_Port: 3306
                Connect_Retry: 60
              Master_Log_File: mysql-bin.000001
          Read_Master_Log_Pos: 1206
               Relay_Log_File: slave-relay-bin.000002
                Relay_Log_Pos: 649
        Relay_Master_Log_File: mysql-bin.000001
             Slave_IO_Running: Yes
            Slave_SQL_Running: Yes
   ##------------------------------------从库设置------------------------------------##
```



**/* 安装MyCat */**

```shell
##构建Java环境
[root@mycat ~]# tar xf jdk-8u181-linux-x64.tar -C /usr/local/
[root@mycat ~]# mv /usr/local/jdk1.8.0_181 /usr/local/java

[root@mycat ~]# vim /etc/profile
export JAVA_HOME=/usr/local/java
export PATH=$JAVA_HOME/bin:$PATH
export CLASSPATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar

[root@mycat ~]# java -version
java version "1.8.0_181"
Java(TM) SE Runtime Environment (build 1.8.0_181-b13)
Java HotSpot(TM) 64-Bit Server VM (build 25.181-b13, mixed mode)

##安装MyCat服务
[root@mycat ~]# wget http://dl.mycat.io/1.6.5/Mycat-server-1.6.5-release-20180122220033-linux.tar.gz
[root@mycat ~]# tar xf Mycat-server-1.6.5-release-20180122220033-linux.tar.gz -C /usr/local/

[root@mycat mycat]# vim /etc/profile
export MYCAT_HOME=/usr/local/mycat
[root@mycat mycat]# source /etc/profile
[root@mycat mycat]# ln -s /usr/local/mycat/bin/mycat /usr/bin/mycat

[root@mycat ~]# vim /usr/local/mycat/conf/server.xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mycat:server SYSTEM "server.dtd">
<mycat:server xmlns:mycat="http://io.mycat/">

        <system>
        <property name="defaultSqlParser">druidparser</property>

        </system>

        <user name="root" defaultAccount="true">
                <property name="password">(BavDu..0928)</property>
                <property name="schemas">TEST_DB</property>
        </user>

        <user name="user">
                <property name="password">(BavDu..0928)</property>
                <property name="schemas">TEST_DB</property>
                <property name="readOnly">true</property>
        </user>
</mycat:server>

[root@mycat ~]# vim /usr/local/mycat/conf/schema.xml
<?xml version="1.0"?>
<!DOCTYPE mycat:schema SYSTEM "schema.dtd">
<mycat:schema xmlns:mycat="http://io.mycat/">

        <schema name="TEST_DB" checkSQLschema="false" sqlMaxLimit="100" dataNode="dn1">

        </schema>

        <dataNode name="dn1" dataHost="localhost1" database="TEST_DB" />

        <dataHost name="localhost1" maxCon="1000" minCon="10" balance="1" writeType="0" dbType="mysql" dbDriver="native">
                <heartbeat>select user()</heartbeat>
                <writeHost host="hostM1" url="192.168.13.21:3306" user="root" password="(BavDu..0928)">
                        <readHost host="hostS1" url="192.168.13.22:3306" user="root" password="(Bavdu..0928)"/>
                </writeHost>
        </dataHost>
</mycat:schema>

[root@mycat ~]# vim /usr/local/mycat/conf/wrapper.conf
wrapper.java.command=%JAVA_HOME%/bin/java

[root@mycat ~]# /usr/local/mycat/bin/mycat start

[root@mycat ~]# yum -y install mariadb
```



**/* 测试MyCat读写分离 */**

```shell
[root@mycat mycat]# mysql -uroot -p'(BavDu..0928)' -h192.168.13.20 -P8066 -DTEST_DB
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MySQL connection id is 5
Server version: 5.6.29-mycat-1.6.5-release-20180122220033 MyCat Server (OpenCloundDB)

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MySQL [TEST_DB]> show databases;
+----------+
| DATABASE |
+----------+
| TEST_DB  |
+----------+
1 row in set (0.00 sec)

MySQL [TEST_DB]> use TEST_DB
Database changed
MySQL [TEST_DB]> create table testtest (id bigint not null primary key, user_id varchar(100), travel_date date, fee decimal, days int);
Query OK, 0 rows affected (0.13 sec)

MySQL [TEST_DB]> insert into testtest (id,user_id,travel_date,fee,days) values (1,'100', 20160816, 2000, 5);
Query OK, 1 row affected (0.49 sec)

MySQL [TEST_DB]> insert into testtest (id,user_id,travel_date,fee,days) values (2,'300', 20160916, 5000, 3);
Query OK, 1 row affected (0.05 sec)

MySQL [TEST_DB]>


```

