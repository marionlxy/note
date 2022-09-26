# ProxySQL实现MySQL读写分离

| [日期：2019-05-13] | 来源：Linux社区 作者：Masuri | [字体：[大](javascript:ContentSize(16)) [中](javascript:ContentSize(0)) [小](javascript:ContentSize(12))] |
| ------------------ | ---------------------------- | ------------------------------------------------------------ |
|                    |                              |                                                              |



## MySQL读写分离(ProxySQL)

### 读写分离原理

读写分离就是用户在发送请求时，请求经过中间件，中间件将请求中的读和写操作分辨出来将读请求发送给后端的从服务器，将写请求发送给后端的主服务器，再又主服务器通过主从复制将数据复制给其他从服务器
![MySQL读写分离(ProxySQL)](https://www.linuxidc.com/upload/2019_05/190513192673961.png)

### 常见MySQL中间件

| 名称        | 公司                                                     | 站点地址                                                   |
| :---------- | :------------------------------------------------------- | :--------------------------------------------------------- |
| mysql-proxy | [Oracle](https://www.linuxidc.com/topicnews.aspx?tid=12) | https://downloads.mysql.com/archives/proxy                 |
| Atlas       | Qihoo                                                    | https://github.com/Qihoo360/Atlas/blob/master/README_ZH.md |
| dbproxy     | 美团                                                     | https://github.com/Meituan-Dianping/DBProxy                |
| Cetus       | 网易乐得                                                 | https://github.com/Lede-Inc/cetus                          |
| Amoeba      | https://sourceforge.net/projects/amoeba/                 |                                                            |
| Cobar       | 阿里巴巴                                                 | Amoeba的升级版                                             |
| Mycat       | 基于Cobar                                                | http://www.mycat.io                                        |
| ProxySQL    | https://proxysql.com/                                    |                                                            |

本文以ProxySQL为例来介绍读写分离的使用方法

### ProxySQL简介

ProxySQL为MySQL的中间件，其有两个版本官方版和percona版，percona版是基于官方版基础上修改而来。ProxySQL是由C++语言开发，轻量级但性能优异（支持处理千亿级数据），其具有中间件所需要的绝大多数功能，如：

1. 多种方式的读写分离
2. 定制基于用户、基于schema、基于语言的规则对SQL语句进行路由
3. 缓存查询结果
4. 后端节点的控制
   ...
   官方站点：https://proxysql.com/
   官方手册：https://github.com/sysown/proxysql/wiki

#### ProxySQL安装后生成的文件

```
/etc/init.d/proxysql            #此为服务脚本存放在init.d目录下所以需要使用service命令去启动他
/etc/proxysql.cnf
/usr/bin/proxysql
/usr/share/proxysql/tools/proxysql_galera_checker.sh
/usr/share/proxysql/tools/proxysql_galera_writer.pl
```

#### ProxySQL所使用的端口

ProxySQL所使用的端口为6032和6033
6032:用来配置ProxySQL，是个管理接口
6033:用来被远程用户连接端口

#### ProxySQL内置数据库

```
MySQL [(none)]> SHOW DATABASES;
+-----+---------------+-------------------------------------+
| seq | name          | file                                |
+-----+---------------+-------------------------------------+
| 0   | main          |                                     |       
| 2   | disk          | /var/lib/proxysql/proxysql.db       |
| 3   | stats         |                                     |
| 4   | monitor       |                                     |
| 5   | stats_history | /var/lib/proxysql/proxysql_stats.db |
+-----+---------------+-------------------------------------+
5 rows in set (0.00 sec)
```

以上这些库中主要配置的库为main库，里面存放了ProxySQL的各种配置。

#### ProxySQL main库内的表

```
MySQL [(none)]> show tables;
+--------------------------------------------+
| tables                                     |
+--------------------------------------------+
| global_variables                           |
| mysql_collations                           |
| mysql_group_replication_hostgroups         |
| mysql_query_rules                          |
| mysql_query_rules_fast_routing             |
| mysql_replication_hostgroups               |
| mysql_servers                              |
| mysql_users                                |
| proxysql_servers                           |
| runtime_checksums_values                   |
| runtime_global_variables                   |
| runtime_mysql_group_replication_hostgroups |
| runtime_mysql_query_rules                  |
| runtime_mysql_query_rules_fast_routing     |
| runtime_mysql_replication_hostgroups       |
| runtime_mysql_servers                      |
| runtime_mysql_users                        |
| runtime_proxysql_servers                   |
| runtime_scheduler                          |
| scheduler                                  |
+--------------------------------------------+
20 rows in set (0.00 sec)
```

main库中的表分为runtime开头和非runtime开头
runtime开头为运行时的设置
非runtime开头为需要设置的配置
所有的配置修改后需要执行命令才能加载到runtime生效

```
LOAD ... TO RUNTIME
```

所有的配置修改后需要执行命令才能永久保存

```
SAVE ... TO DISK
```

#### 日志查看

查看read_only和replication_log的监控日志

```
MySQL [(none)]> select * from mysql_server_read_only_log;
Empty set (0.00 sec)

MySQL [(none)]> select * from mysql_server_replication_lag_log;
Empty set (0.00 sec)
```

### ProxySQL实现读写分离

ProxySQL在实现读写分离之前先要实现主从复制的共功能
本实验总计使用4台主机，详细配置如下

| 主机     | ip地址         |
| :------- | :------------- |
| Client   | 192.168.73.113 |
| ProxySQL | 192.168.73.112 |
| Master   | 192.168.73.110 |
| Slave    | 192.168.73.111 |

注意事项：在实现主从复制时从节点在配置文件中必须要设置read_only，这是ProxySQL区分是用来作为读服务器还是写服务器的依据

------

#### 一、实现主从复制

#### 主节点配置

1.修改配置文件

```
[root@Master ~]# vim /etc/my.cnf
[mysqld]
server-id=1
log-bin
binlog-format=row
```

2.启动MySQL服务

```
[root@Master ~]# systemctl start mariadb
[root@Master ~]# mysql -e "SHOW MASTER LOGS;"
+--------------------+-----------+
| Log_name           | File_size |
+--------------------+-----------+
| mariadb-bin.000001 |       245 |
+--------------------+-----------+
```

3.创建用来复制的账号

```
[root@Master ~]# mysql -e "GRANT REPLICATION SLAVE ON *.* TO 'repluser'@'192.168.73.%' IDENTIFIED BY 'CentOS';"
```

#### 从节点配置

1.修改配置文件

```
[root@Slave ~]# vim /etc/my.cnf
[mysqld]
server-id=2
log-bin
binlog-format=row
read-only               #必须写
```

2.启动数据库服务

```
[root@Slave ~]# systemctl start mariadb
```

3.写入CHANGE MASTSER TO信息

```
MariaDB [(none)]> CHANGE MASTER TO MASTER_HOST='192.168.73.110', MASTER_USER='repluser',MASTER_PASSWORD='centos',MASTER_PORT=3306,MASTER_LOG_FILE='mariadb-bin.000001',MASTER_LOG_POS=245;
Query OK, 0 rows affected (0.00 sec)
```

4.启动复制线程

```
MariaDB [(none)]> START SLAVE;
Query OK, 0 rows affected (0.00 sec)
```

5.查看状态

```
MariaDB [(none)]> SHOW SLAVE STATUS\G;
*************************** 1. row ***************************
               Slave_IO_State: Waiting for master to send event
                  Master_Host: 192.168.73.110
                  Master_User: repluser
                  Master_Port: 3306
                Connect_Retry: 60
              Master_Log_File: mariadb-bin.000001
          Read_Master_Log_Pos: 402
               Relay_Log_File: mariadb-relay-bin.000002
                Relay_Log_Pos: 688
        Relay_Master_Log_File: mariadb-bin.000001
             Slave_IO_Running: Yes
            Slave_SQL_Running: Yes
```

#### 测试

1.主节点导入数据库

```
[root@Master ~]# mysql < hellodb_innodb.sql 
[root@Master ~]# mysql -e "SHOW DATABASES;"
+--------------------+
| Database           |
+--------------------+
| information_schema |
| hellodb            |
| mysql              |
| performance_schema |
| test               |
+--------------------+
```

2.从节点查看

```
[root@Slave ~]# mysql -e "SHOW DATABASES;"
+--------------------+
| Database           |
+--------------------+
| information_schema |
| hellodb            |
| mysql              |
| performance_schema |
| test               |
+--------------------+
```

主从复制配置完毕

#### 二、在ProxySQL上配置读写分离

1.在ProxySQL主机上配置yum源

```
[root@ProxySQL ~]# vim /etc/yum.repos.d/proxysql.repo
[proxysql_repo] 
name= ProxySQL YUM repository 
baseurl=http://repo.proxysql.com/ProxySQL/proxysql-1.4.x/centos/\$releasever 
gpgcheck=1
gpgkey=http://repo.proxysql.com/ProxySQL/repo_pub_key 
```

2.安装ProxySQL和mariadb客户端
ProxySQL内置了一个轻量级的数据库，所以需要有MySQL客户端连上去对其进行配置

```
[root@ProxySQL ~]# yum install proxysql mariadb -y
```

3.启动ProxySQL服务

```
[root@ProxySQL ~]# service proxysql start
Starting ProxySQL: 2019-05-08 14:03:07 [INFO] Using config file /etc/proxysql.cnf
DONE!
```

4.连接管理端口

```
[root@ProxySQL ~]# mysql -uadmin -padmin -P6032 -h127.0.0.1
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MySQL connection id is 1
Server version: 5.5.30 (ProxySQL Admin Module)

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.
```

5.将MySQL主从服务器信息添加入mysql_servers表中
先将主从服务器存放在同一组内，等指定好读写规则后，系统会根据配置文件中的read-only值自动将其分别添加至读组和写组。

```
MySQL [(none)]> INSERT INTO mysql_servers(hostgroup_id,hostname,port) VALUES (10,'192.168.73.110',3306);
Query OK, 1 row affected (0.00 sec)

MySQL [(none)]> INSERT INTO mysql_servers(hostgroup_id,hostname,port) VALUES (10,'192.168.73.111',3306);
Query OK, 1 row affected (0.00 sec)

MySQL [(none)]> SELECT * FROM mysql_servers
    -> ;
+--------------+----------------+------+--------+--------+-------------+-----------------+---------------------+---------+----------------+---------+
| hostgroup_id | hostname       | port | status | weight | compression | max_connections | max_replication_lag | use_ssl | max_latency_ms | comment |
+--------------+----------------+------+--------+--------+-------------+-----------------+---------------------+---------+----------------+---------+
| 10           | 192.168.73.110 | 3306 | ONLINE | 1      | 0           | 1000            | 0                   | 0       | 0              |         |
| 10           | 192.168.73.111 | 3306 | ONLINE | 1      | 0           | 1000            | 0                   | 0       | 0              |         |
+--------------+----------------+------+--------+--------+-------------+-----------------+---------------------+---------+----------------+---------+
2 rows in set (0.00 sec)
```

6.在MySQL服务器的主节点上为ProxySQL添加账号用来查看MySQL节点是主还是从

```
[root@Master ~]# mysql -e "GRANT REPLICATION SLAVE ON *.* TO 'monitor'@'192.168.73.%' IDENTIFIED BY 'centos';"
```

7.在Proxy上配置监控账号

```
MySQL [(none)]> SET mysql-monitor_username='monitor';
Query OK, 1 row affected (0.00 sec)

MySQL [(none)]> SET mysql-monitor_password='centos';
Query OK, 1 row affected (0.00 sec)
```

8.将配置加载至内存，将配置保存至磁盘

```
MySQL [(none)]> LOAD MYSQL VARIABLES TO RUNTIME;
Query OK, 0 rows affected (0.00 sec)

MySQL [(none)]> SAVE MYSQL VARIABLES TO DISK;
Query OK, 97 rows affected (0.00 sec)
```

9.测试
9.1查看连接状态

```
MySQL [(none)]> select * from mysql_server_connect_log;
+----------------+------+------------------+-------------------------+-------------------------------------------------------------------------+
| hostname       | port | time_start_us    | connect_success_time_us | connect_error                                                           |
+----------------+------+------------------+-------------------------+-------------------------------------------------------------------------+
| 192.168.73.110 | 3306 | 1557296528658352 | 0                       | Access denied for user 'monitor'@'192.168.73.112' (using password: YES) |
| 192.168.73.111 | 3306 | 1557296648056186 | 0                       | Access denied for user 'monitor'@'192.168.73.112' (using password: YES) |
| 192.168.73.110 | 3306 | 1557296649025169 | 0                       | Access denied for user 'monitor'@'192.168.73.112' (using password: YES) |
| 192.168.73.110 | 3306 | 1557296708057600 | 0                       | Access denied for user 'monitor'@'192.168.73.112' (using password: YES) |
| 192.168.73.111 | 3306 | 1557296708872496 | 0                       | Access denied for user 'monitor'@'192.168.73.112' (using password: YES) |
| 192.168.73.110 | 3306 | 1557296758752550 | 2763                    | NULL                                                                    |  #此前由于没有创建监控账号所以连接一直失败
| 192.168.73.111 | 3306 | 1557296759862679 | 3205                    | NULL                                                                    |
| 192.168.73.110 | 3306 | 1557296818752346 | 1014                    | NULL                                                                    |
| 192.168.73.111 | 3306 | 1557296819498108 | 3120                    | NULL                                                                    |
| 192.168.73.110 | 3306 | 1557296878752978 | 3245                    | NULL                                                                    |
| 192.168.73.111 | 3306 | 1557296879410404 | 3063                    | NULL                                                                    |
+----------------+------+------------------+-------------------------+-------------------------------------------------------------------------+
22 rows in set (0.00 sec)           
```

9.2测试连接ping

```
MySQL [(none)]> select * from mysql_server_ping_log;
+----------------+------+------------------+----------------------+-------------------------------------------------------------------------+
| hostname       | port | time_start_us    | ping_success_time_us | ping_error                                                              |
+----------------+------+------------------+----------------------+-------------------------------------------------------------------------+
| 192.168.73.111 | 3306 | 1557296508118738 | 0                    | Access denied for user 'monitor'@'192.168.73.112' (using password: YES) |
| 192.168.73.110 | 3306 | 1557296508302837 | 0                    | Access denied for user 'monitor'@'192.168.73.112' (using password: YES) |

...中间省略...

| 192.168.73.110 | 3306 | 1557297088874658 | 675                  | NULL                                                                    |
| 192.168.73.111 | 3306 | 1557297089037256 | 435                  | NULL                                                                    |
| 192.168.73.110 | 3306 | 1557297098875954 | 1144                 | NULL                                                                    |
| 192.168.73.111 | 3306 | 1557297099069333 | 1252                 | NULL                                                                    |
+----------------+------+------------------+----------------------+-------------------------------------------------------------------------+
122 rows in set (0.00 sec)
#已经可以联通
```

10.设置读写分组

```
MySQL [(none)]> INSERT INTO mysql_replication_hostgroups VALUES(10,20,"test");
Query OK, 1 row affected (0.00 sec)

MySQL [(none)]> SELECT * FROM mysql_replication_hostgroups;
+------------------+------------------+---------+
| writer_hostgroup | reader_hostgroup | comment |
+------------------+------------------+---------+
| 10               | 20               | test    |
+------------------+------------------+---------+
1 row in set (0.00 sec)
```

11.让读写表生效

```
MySQL [(none)]> LOAD MYSQL SERVERS TO RUNTIME;
Query OK, 0 rows affected (0.00 sec)
```

12.查看mysql_server表此时已经将服务器分组

```
MySQL [(none)]> SELECT * FROM mysql_servers;
+--------------+----------------+------+--------+--------+-------------+-----------------+---------------------+---------+----------------+---------+
| hostgroup_id | hostname       | port | status | weight | compression | max_connections | max_replication_lag | use_ssl | max_latency_ms | comment |
+--------------+----------------+------+--------+--------+-------------+-----------------+---------------------+---------+----------------+---------+
| 10           | 192.168.73.110 | 3306 | ONLINE | 1      | 0           | 1000            | 0                   | 0       | 0              |         |
| 20           | 192.168.73.111 | 3306 | ONLINE | 1      | 0           | 1000            | 0                   | 0       | 0              |         |
+--------------+----------------+------+--------+--------+-------------+-----------------+---------------------+---------+----------------+---------+
2 rows in set (0.00 sec)
```

13.保存配置至磁盘

```
MySQL [(none)]> SAVE MYSQL SERVERS TO DISK;
Query OK, 0 rows affected (0.02 sec)
```

至此读写分离配置完毕，接下来需要定义读写分离的规则

#### 三、定义读写分离规则

1.在主节点上创建一个账户让客户端连接调度器去访问主从服务器（此处授予的权限较大，实际生产中可以根据需要定义指定的那张表）

```
[root@Master ~]# mysql -e "GRANT ALL ON *.* TO 'sqluser'@'192.168.73.%' IDENTIFIED BY 'centos';"
```

2.在ProxySQL服务器上，将sqluser用户添加至mysql_users表中

```
MySQL [(none)]> INSERT INTO mysql_users(username,password,default_hostgroup) VALUES ('sqluser','centos',10);
Query OK, 1 row affected (0.00 sec)
```

3.查看mysql_user表信息

```
MySQL [(none)]> SELECT * FROM mysql_users;
+----------+----------+--------+---------+-------------------+----------------+---------------+------------------------+--------------+---------+----------+-----------------+
| username | password | active | use_ssl | default_hostgroup | default_schema | schema_locked | transaction_persistent | fast_forward | backend | frontend | max_connections |
+----------+----------+--------+---------+-------------------+----------------+---------------+------------------------+--------------+---------+----------+-----------------+
| sqluser  | centos   | 1      | 0       | 10                | NULL           | 0             | 1                      | 0            | 1       | 1        | 10000           |
+----------+----------+--------+---------+-------------------+----------------+---------------+------------------------+--------------+---------+----------+-----------------+
1 row in set (0.00 sec)
```

4.生效存盘

```
MySQL [(none)]> load mysql users to runtime;
Query OK, 0 rows affected (0.00 sec)

MySQL [(none)]> SAVE MYSQL USERS TO DISK;
Query OK, 0 rows affected (0.00 sec)
```

5.测试
目前尚未设置读写路由规则，所有的请求都是发往主节点

```
[root@Client ~]# mysql -usqluser -pcentos -h192.168.73.112 -P6033 -e "SELECT @@server_id;"
+-------------+
| @@server_id |
+-------------+
|           1 |
+-------------+
```

6.在ProxySQL上定义调度规则

```
MySQL [(none)]> INSERT INTO mysql_query_rules(rule_id,active,match_digest,destination_hostgroup,apply) VALUES (1,1,'^SELECT.*FOR UPDATE$',10,1),(2,1,'^SELECT',20,1);
Query OK, 2 rows affected (0.00 sec)
```

7.查看定义规则

```
MySQL [(none)]>  SELECT * FROM mysql_query_rules\G;
*************************** 1. row ***************************
              rule_id: 1
               active: 1
             username: NULL
           schemaname: NULL
               flagIN: 0
          client_addr: NULL
           proxy_addr: NULL
           proxy_port: NULL
               digest: NULL
         match_digest: ^SELECT.*FOR UPDATE$
        match_pattern: NULL
 negate_match_pattern: 0
         re_modifiers: CASELESS
              flagOUT: NULL
      replace_pattern: NULL
destination_hostgroup: 10
            cache_ttl: NULL
            reconnect: NULL
              timeout: NULL
              retries: NULL
                delay: NULL
    next_query_flagIN: NULL
       mirror_flagOUT: NULL
     mirror_hostgroup: NULL
            error_msg: NULL
               OK_msg: NULL
          sticky_conn: NULL
            multiplex: NULL
                  log: NULL
                apply: 1
              comment: NULL
*************************** 2. row ***************************
              rule_id: 2
               active: 1
             username: NULL
           schemaname: NULL
               flagIN: 0
          client_addr: NULL
           proxy_addr: NULL
           proxy_port: NULL
               digest: NULL
         match_digest: ^SELECT
        match_pattern: NULL
 negate_match_pattern: 0
         re_modifiers: CASELESS
              flagOUT: NULL
      replace_pattern: NULL
destination_hostgroup: 20
            cache_ttl: NULL
            reconnect: NULL
              timeout: NULL
              retries: NULL
                delay: NULL
    next_query_flagIN: NULL
       mirror_flagOUT: NULL
     mirror_hostgroup: NULL
            error_msg: NULL
               OK_msg: NULL
          sticky_conn: NULL
            multiplex: NULL
                  log: NULL
                apply: 1
              comment: NULL
2 rows in set (0.00 sec)
```

8.生效存盘

```
MySQL [(none)]> LOAD MYSQL QUERY RULES TO RUNTIME;
Query OK, 0 rows affected (0.00 sec)

MySQL [(none)]> SAVE MYSQL QUERY RULES TO DISK;
Query OK, 0 rows affected (0.00 sec)
```

#### 四、在Client端测试

1.查询操作

```
[root@Client ~]# mysql -usqluser -pcentos -h192.168.73.112 -P6033 -e "SELECT @@server_id;"
+-------------+
| @@server_id |
+-------------+
|           2 |
+-------------+
```

2.写操作

```
[root@Client ~]# mysql -usqluser -pcentos -h192.168.73.112 -P6033 -e "BEGIN;INSERT hellodb.teachers VALUE(5,'Long',30,'M');SELECT @@server_id;commit;"
+-------------+
| @@server_id |
+-------------+
|           1 |
+-------------+
```

Linux公社的RSS地址：https://www.linuxidc.com/rssFeed.aspx

**本文永久更新链接地址**：https://www.linuxidc.com/Linux/2019-05/158644.htm

[![linux](https://www.linuxidc.com/linuxfile/logo.gif)](http://www.linuxidc.com/)