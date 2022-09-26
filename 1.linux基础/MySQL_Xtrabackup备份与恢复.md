# [MySQL入门篇（七）之Xtrabackup备份与恢复](https://www.cnblogs.com/linuxk/p/9372990.html)

- ### **一、Xtrabackup介绍**

　　MySQL冷备、mysqldump、MySQL热拷贝都无法实现对数据库进行增量备份。在实际生产环境中增量备份是非常实用的，如果数据大于50G或100G，存储空间足够的情况下，可以每天进行完整备份，如果每天产生的数据量较大，需要定制数据备份策略。例如每周实用完整备份，周一到周六实用增量备份。而Percona-Xtrabackup就是为了实现增量备份而出现的一款主流备份工具，xtrabakackup有2个工具，分别是xtrabakup、innobakupe。

　　Percona-xtrabackup是 Percona公司开发的一个用于MySQL数据库物理热备的备份工具，支持MySQL、Percona server和MariaDB，开源免费，是目前较为受欢迎的主流备份工具。xtrabackup只能备份innoDB和xtraDB两种数据引擎的表，而不能备份MyISAM数据表。

- ### **二、Xtrabackup优点**

（1）备份速度快，物理备份可靠

（2）备份过程不会打断正在执行的事务（无需锁表）

（3）能够基于压缩等功能节约磁盘空间和流量

（4）自动备份校验

（5）还原速度快

（6）可以流传将备份传输到另外一台机器上

（7）在不增加服务器负载的情况备份数据

- ### **三、Xtrabackup备份原理**

**Xtrabackup备份流程图：**

 ![img](https://images2018.cnblogs.com/blog/1349539/201807/1349539-20180727165438283-1118004015.png)

（1）innobackupex启动后，会先fork一个进程，用于启动xtrabackup，然后等待xtrabackup备份ibd数据文件；

（2）xtrabackup在备份innoDB数据是，有2种线程：redo拷贝线程和ibd数据拷贝线程。xtrabackup进程开始执行后，会启动一个redo拷贝的线程，用于从最新的checkpoint点开始顺序拷贝redo.log；再启动ibd数据拷贝线程，进行拷贝ibd数据。这里是先启动redo拷贝线程的。在此阶段，innobackupex进行处于等待状态（等待文件被创建）

（4）xtrabackup拷贝完成ibd数据文件后，会通知innobackupex（通过创建文件），同时xtrabackup进入等待状态（redo线程依旧在拷贝redo.log）

（5）innobackupex收到xtrabackup通知后哦，执行FLUSH TABLES WITH READ LOCK（FTWRL），取得一致性位点，然后开始备份非InnoDB文件（如frm、MYD、MYI、CSV、opt、par等格式的文件），在拷贝非InnoDB文件的过程当中，数据库处于全局只读状态。

（6）当innobackup拷贝完所有的非InnoDB文件后，会通知xtrabackup，通知完成后，进入等待状态；

（7）xtrabackup收到innobackupex备份完成的通知后，会停止redo拷贝线程，然后通知innobackupex，redo.log文件拷贝完成；

（8）innobackupex收到redo.log备份完成后，就进行解锁操作，执行：UNLOCK TABLES；

（9）最后innbackupex和xtrabackup进程各自释放资源，写备份元数据信息等，innobackupex等xtrabackup子进程结束后退出。

- ### **四、xtrabackup的安装部署以及备份恢复实现**

- ### **1、xtrabackup的安装**

#### 下载地址：https://www.percona.com/downloads/XtraBackup/LATEST/

可以选择rpm包方式安装，也可以下载源码包编译安装，这里直接采用rpm包的方式进行安装

```shell
[root@master tools]# wget https://www.percona.com/downloads/XtraBackup/Percona-XtraBackup-2.4.9/binary/redhat/7/x86_64/percona-xtrabackup-24-2.4.9-1.el7.x86_64.rpm
[root@master tools]# yum install -y percona-xtrabackup-24-2.4.9-1.el7.x86_64.rpm 
[root@master ~]# rpm -qa |grep xtrabackup
percona-xtrabackup-24-2.4.9-1.el7.x86_64

Xtrabackup中主要包含两个工具：
xtrabackup：是用于热备innodb，xtradb表中数据的工具，不能备份其他类型的表，也不能备份数据表结构；
innobackupex：是将xtrabackup进行封装的perl脚本，提供了备份myisam表的能力。
常用选项:  
   --host     指定主机
   --user     指定用户名
   --password    指定密码
   --port     指定端口
   --databases     指定数据库
   --incremental    创建增量备份
   --incremental-basedir   指定包含完全备份的目录
   --incremental-dir      指定包含增量备份的目录   
   --apply-log        对备份进行预处理操作             
     一般情况下，在备份完成后，数据尚且不能用于恢复操作，因为备份的数据中可能会包含尚未提交的事务或已经提交但尚未同步至数据文件中的事务。因此，此时数据文件仍处理不一致状态。“准备”的主要作用正是通过回滚未提交的事务及同步已经提交的事务至数据文件也使得数据文件处于一致性状态。
   --redo-only      不回滚未提交事务
   --copy-back     恢复备份目录
```

使用innobackupex备份时，其会调用xtrabackup备份所有的InnoDB表，复制所有关于表结构定义的相关文件(.frm)、以及MyISAM、MERGE、CSV和ARCHIVE表的相关文件，同时还会备份触发器和数据库配置信息相关的文件，这些文件会被保存到一个以时间命名的目录当中。在备份的同时，innobackupex还会在备份目录中创建如下文件：

```reStructuredText
(1)xtrabackup_checkpoints -- 备份类型(如完全或增量)、备份状态(如是否已经为prepared状态)和LSN(日志序列号)范围信息：

每个InnoDB页(通常为16k大小)
都会包含一个日志序列号，即LSN，LSN是整个数据库系统的系统版本号，每个页面相关的LSN能够表明此页面最近是如何发生改变的。

(2)xtrabackup_binlog_info  --  mysql服务器当前正在使用的二进制日志文件及备份这一刻位置二进制日志时间的位置。

(3)xtrabackup_binlog_pos_innodb  --  二进制日志文件及用于InnoDB或XtraDB表的二进制日志文件的当前position。

(4)xtrabackup_binary  --  备份中用到的xtrabackup的可执行文件；

(5)backup-my.cnf  --  备份命令用到的配置选项信息：

在使用innobackupex进行备份时，还可以使用--no-timestamp选项来阻止命令自动创建一个以时间命名的目录：如此一来，innobackupex命令将会创建一个BACKUP-DIR目录来存储备份数据。
```

如果要使用一个最小权限的用户进行备份，则可基于如下命令创建此类用户：如果要使用一个最小权限的用户进行备份，则可基于如下命令创建此类用户：

 

```sql
mysql> CREATE USER 'bkpuser'@'localhost' IDENTIFIED BY '123456';　　#创建用户
mysql> REVOKE ALL PRIVILEGES,GRANT OPTION FROM 'bkpuser';　　#回收此用户所有权限
mysql> GRANT RELOAD,LOCK TABLES,RELICATION CLIENT ON *.* TO 'bkpuser'@'localhost';　　#授权刷新、锁定表、用户查看服务器状态
mysql> FLUSH PRIVILEGES;　　#刷新授权表
```

 

***\*注意：备份时需启动MySQL,恢复时需关闭MySQL,清空mysql数据目录且不能重新初始化,恢复数据后应该立即进行一次完全备份\****

- ### **2、xtrabackup全量备份与恢复**

 

 

```sh
备份：
innobackupex --user=DBUSER --password=DBUSERPASS --defaults-file=/etc/my.cnf /path/to/BACKUP-DIR/

恢复：
innobackupex --apply-log /backups/2018-07-30_11-04-55/
innobackupex --copy-back --defaults-file=/etc/my.cnf  /backups/2018-07-30_11-04-55/
```

 

**（1）准备(prepare)一个完全备份**

一般情况下，在备份完成后，数据尚且不能用于恢复操作，因为备份的数据中可能会包含尚未提交的事务或者已经提交但尚未同步至数据文件中的事务。因此，此时数据文件仍处于不一致状态。"准备"的主要作用正是通过回滚未提交的事务及同步已经提交的事务至数据文件也使用得数据文件处于一致性状态。

innobackupex命令的--apply-log选项可用于实现上述功能，如下面的命令：

```sh
# innobackupex --apply-log /path/to/BACKUP-DIR
如果执行正确，其最后输出的几行信息通常如下：

120407 09:01:04 innobackupex: completed OK!
```

 在实现"准备"的过程中，innobackupex通常还可以使用--user-memory选项来指定其可以使用的内存的大小，默认为100M.如果有足够的内存空间可用，可以多划分一些内存给prepare的过程，以提高其完成备份的速度。

**（2）从一个完全备份中恢复数据**

注意：恢复不用启动MySQL

innobackupex命令的--copy-back选项用于恢复操作，其通过复制所有数据相关的文件至mysql服务器DATADIR目录中来执行恢复过程。innobackupex通过backup-my.cnf来获取DATADIR目录的相关信息。

```sh
# innobackupex --copy-back /path/to/BACKUP-DIR
```

当数据恢复至DATADIR目录以后，还需要确保所有的数据文件的属主和属组均为正确的用户，如mysql，否则，在启动mysqld之前还需要事先修改数据文件的属主和属组。如：

```sh
# chown -R mysql.mysql /mydata/data/
```

**（3）实战练习**

```shell
（1）全量备份
[root@master backups]#  innobackupex --user=root --password=123456 --host=127.0.0.1 /backups/　　#在master上进行全库备份#语法解释说明：#--user=root 指定备份用户#--password=123456  指定备份用户密码#--host　　指定主机#/backups　　指定备份目录
[root@master backups]# ll
total 0
drwxr-x--- 7 root root 232 Jul 30 11:01 2018-07-30_11-01-37
[root@master backups]# ll 2018-07-30_11-01-37/　　#查看备份数据
total 77856
-rw-r----- 1 root root      418 Jul 30 11:01 backup-my.cnf　　#备份用到的配置选项信息文件
-rw-r----- 1 root root 79691776 Jul 30 11:01 ibdata1　　#数据文件
drwxr-x--- 2 root root       20 Jul 30 11:01 kim
drwxr-x--- 2 root root     4096 Jul 30 11:01 mysql
drwxr-x--- 2 root root     4096 Jul 30 11:01 performance_schema
drwxr-x--- 2 root root       20 Jul 30 11:01 repppp
drwxr-x--- 2 root root     4096 Jul 30 11:01 wordpress
-rw-r----- 1 root root       21 Jul 30 11:01 xtrabackup_binlog_info　　#mysql服务器当前正在使用的二进制日志文件和此时二进制日志时间的位置信息文件
-rw-r----- 1 root root      113 Jul 30 11:01 xtrabackup_checkpoints　　#备份的类型、状态和LSN状态信息文件
-rw-r----- 1 root root      482 Jul 30 11:01 xtrabackup_info
-rw-r----- 1 root root     2560 Jul 30 11:01 xtrabackup_logfile　　　　#备份的日志文件

（2）恢复
[root@slave ~]# /etc/init.d/mysqld stop　　#停止slave上的mysql
Shutting down MySQL.. SUCCESS! 

[root@slave tools]# yum install -y percona-xtrabackup-24-2.4.9-1.el7.x86_64.rpm 　　#安装xtrabackup
[root@master backups]# scp -r 2018-07-30_11-01-37/ root@192.168.56.12:/backups/　　 #从master上拷贝备份数据
[root@slave tools]# innobackupex --apply-log /backups/2018-07-30_11-01-37/　　　　　 #合并数据，使数据文件处于一致性的状态
180729 23:18:23 innobackupex: Starting the apply-log operation

IMPORTANT: Please check that the apply-log run completes successfully.
           At the end of a successful apply-log run innobackupex
           prints "completed OK!".

innobackupex version 2.4.9 based on MySQL server 5.7.13 Linux (x86_64) (revision id: a467167cdd4)
xtrabackup: cd to /backups/2018-07-30_11-01-37/
xtrabackup: This target seems to be not prepared yet.
InnoDB: Number of pools: 1
xtrabackup: xtrabackup_logfile detected: size=8388608, start_lsn=(3127097)
......
InnoDB: FTS optimize thread exiting.
InnoDB: Starting shutdown...
InnoDB: Shutdown completed; log sequence number 3129915
180729 23:18:30 completed OK!
[root@slave ~]# rm -rf /usr/local/mysql/data/　　#在slave上删除原有的数据
[root@slave ~]# vim /etc/my.cnf　　#配置my.cnf的数据目录路径，否则会报错，要和master一致
datadir=/usr/local/mysql/data
[root@slave ~]# innobackupex --copy-back /backups/2018-07-30_11-01-37/　　#在slave上数据恢复
180729 23:32:03 innobackupex: Starting the copy-back operation

IMPORTANT: Please check that the copy-back run completes successfully.
           At the end of a successful copy-back run innobackupex
           prints "completed OK!".
......
180729 23:32:08 completed OK!　　#看到completed OK就是恢复正常了
[root@slave ~]# ll /usr/local/mysql/data/　　#slave上查看数据目录，可以看到数据已经恢复，但是属主会有问题，需要进行修改，所以一般使用mysql的运行用户进行恢复，否则需要进行修改属主和属组信息
total 188432
-rw-r----- 1 root root 79691776 Jul 29 23:32 ibdata1
-rw-r----- 1 root root 50331648 Jul 29 23:32 ib_logfile0
-rw-r----- 1 root root 50331648 Jul 29 23:32 ib_logfile1
-rw-r----- 1 root root 12582912 Jul 29 23:32 ibtmp1
drwxr-x--- 2 root root       20 Jul 29 23:32 kim
drwxr-x--- 2 root root     4096 Jul 29 23:32 mysql
drwxr-x--- 2 root root     4096 Jul 29 23:32 performance_schema
drwxr-x--- 2 root root       20 Jul 29 23:32 repppp
drwxr-x--- 2 root root     4096 Jul 29 23:32 wordpress
-rw-r----- 1 root root      482 Jul 29 23:32 xtrabackup_info
[root@slave ~]# chown -R mysql.mysql /usr/local/mysql/data/　　#修改属主属组
[root@slave ~]# /etc/init.d/mysqld start　　#启动mysql
Starting MySQL. SUCCESS! 
[root@slave ~]# mysql -uroot -p -e "show databases;"　　#查看数据，是否恢复
Enter password: 
+--------------------+
| Database           |
+--------------------+
| information_schema |
| kim                |
| mysql              |
| performance_schema |
| repppp             |
| wordpress          |
+--------------------+
```

总结全库备份与恢复三步曲：

a.　innobackupex全量备份，并指定备份目录路径；

b.　在恢复前，需要使用--apply-log参数先进行合并数据文件，确保数据的一致性要求；

c.　恢复时，直接使用--copy-back参数进行恢复，需要注意的是，在my.cnf中要指定数据文件目录的路径。

- ### **3、xtrabackup增量备份与恢复**

　　使用innobackupex进行增量备份，每个InnoDB的页面都会包含一个LSN信息，每当相关的数据发生改变，相关的页面的LSN就会自动增长。这正是InnoDB表可以进行增量备份的基础，即innobackupex通过备份上次完全备份之后发生改变的页面来实现。在进行增量备份时，首先要进行一次全量备份，第一次增量备份是基于全备的，之后的增量备份都是基于上一次的增量备份的，以此类推。

要实现第一次增量备份，可以使用下面的命令进行：

```reStructuredText
基于全量备份的增量备份与恢复
做一次增量备份（基于当前最新的全量备份）
innobackupex --user=root --password=root --defaults-file=/etc/my.cnf --incremental /backups/ --incremental-basedir=/backups/2018-07-30_11-01-37
1. 准备基于全量
innobackupex --user=root --password=root --defaults-file=/etc/my.cnf --apply-log --redo-only /backups/2018-07-30_11-01-37
2. 准备基于增量
innobackupex --user=root --password=root --defaults-file=/etc/my.cnf --apply-log --redo-only /backups/2018-07-30_11-01-37 --incremental-dir=/backups/2018-07-30_13-51-47/3. 恢复
innobackupex --copy-back --defaults-file=/etc/my.cnf /opt/2017-01-05_11-04-55/
解释：
1. 2018-07-30_11-01-37指的是完全备份所在的目录。2. 2018-07-30_13-51-47指定是第一次基于2018-07-30_11-01-37增量备份的目录，其他类似以此类推，即如果有多次增量备份。每一次都要执行如上操作。
```

需要注意的是，增量备份仅能应用于InnoDB或XtraDB表，对于MyISAM表而言，执行增量备份时其实进行的是完全备份。

"准备"(prepare)增量备份与整理完全备份有着一些不同，尤其要注意的是：
①需要在每个备份 (包括完全和各个增量备份)上，将已经提交的事务进行"重放"。"重放"之后，所有的备份数据将合并到完全备份上。
②基于所有的备份将未提交的事务进行"回滚"

**（1）增量备份演示**

```sh
[root@master backups]# innobackupex --user=root --password=123456 --host=127.0.0.1 /backups/   #全备数据[root@master ~]# mysql -uroot -p　　#在master上创建student库并创建testtb表插入若干数据Enter password: 
mysql> create database student;
Query OK, 1 row affected (0.03 sec)

mysql> use student;
Database changed
mysql> create table testtb(id int);
Query OK, 0 rows affected (0.07 sec)

mysql> insert into testtb values(1),(10),(99);
Query OK, 3 rows affected (0.04 sec)
Records: 3  Duplicates: 0  Warnings: 0

mysql> select * from testtb;
+------+
| id   |
+------+
|    1 |
|   10 |
|   99 |
+------+
3 rows in set (0.00 sec)

mysql> quit;
Bye
#使用innobackupex进行增量备份[root@master backups]# innobackupex --user=root --password=123456 --host=127.0.0.1 --incremental /backups/ --incremental-basedir=/backups/2018-07-30_11-01-37/
......
180730 13:51:50 Executing UNLOCK TABLES
180730 13:51:50 All tables unlocked
180730 13:51:50 Backup created in directory '/backups/2018-07-30_13-51-47/'
MySQL binlog position: filename 'mysql-bin.000005', position '664'
180730 13:51:50 [00] Writing /backups/2018-07-30_13-51-47/backup-my.cnf
180730 13:51:50 [00]        ...done
180730 13:51:50 [00] Writing /backups/2018-07-30_13-51-47/xtrabackup_info
180730 13:51:50 [00]        ...done
xtrabackup: Transaction log of lsn (3158741) to (3158741) was copied.
180730 13:51:50 completed OK!
[root@master backups]# ll　　#查看备份数据
total 0
drwxr-x--- 7 root root 232 Jul 30 11:01 2018-07-30_11-01-37　　#全量备份数据目录
drwxr-x--- 8 root root 273 Jul 30 13:51 2018-07-30_13-51-47　　#增量备份数据目录
[root@master 2018-07-30_11-01-37]# cat xtrabackup_checkpoints #查看全量备份的xtrabackup_checkpoints
backup_type = full-backuped　　#备份类型为全量备份
from_lsn = 0　　#lsn从0开始
to_lsn = 3127097　　#lsn到3127097结束
last_lsn = 3127097
compact = 0
recover_binlog_info = 0

[root@master 2018-07-30_13-51-47]# cat xtrabackup_checkpoints 　　#查看增量备份的xtrabackup_checkpoints
backup_type = incremental　　#备份类型为增量备份
from_lsn = 3127097　　#lsn从3127097开始
to_lsn = 3158741　　  #lsn到啊3158741结束
last_lsn = 3158741　　
compact = 0
recover_binlog_info = 0
```

**（2）增量备份后数据恢复演示**

```sh
（1）模拟mysql故障，删除数据目录所有数据[root@master ~]# /etc/init.d/mysqld stop　　#模拟mysql故障，停止mysql
Shutting down MySQL.. SUCCESS! 
[root@master ~]# rm -rf /usr/local/mysql/data/*　　#删除数据目录中的所有数据（2）合并全备数据目录，确保数据的一致性
[root@master ~]# innobackupex --apply-log --redo-only /backups/2018-07-30_11-01-37/
180730 14:05:27 innobackupex: Starting the apply-log operation

IMPORTANT: Please check that the apply-log run completes successfully.
           At the end of a successful apply-log run innobackupex
           prints "completed OK!".

innobackupex version 2.4.9 based on MySQL server 5.7.13 Linux (x86_64) (revision id: a467167cdd4)
xtrabackup: cd to /backups/2018-07-30_11-01-37/
......
......
xtrabackup: starting shutdown with innodb_fast_shutdown = 1
InnoDB: Starting shutdown...
InnoDB: Shutdown completed; log sequence number 3127106
InnoDB: Number of pools: 1
180730 14:05:29 completed OK!（3）将增量备份数据合并到全备数据目录当中
[root@master ~]# innobackupex --apply-log --redo-only /backups/2018-07-30_11-01-37/ --incremental-dir=/backups/2018-07-30_13-51-47/
180730 14:06:42 innobackupex: Starting the apply-log operation

IMPORTANT: Please check that the apply-log run completes successfully.
           At the end of a successful apply-log run innobackupex
           prints "completed OK!".
......
......
180730 14:06:44 [00]        ...done
180730 14:06:44 completed OK!
[root@master ~]# cat /backups/2018-07-30_11-01-37/xtrabackup_checkpoints 
backup_type = log-applied　　#查看到数据备份类型是增加
from_lsn = 0　　#lsn从0开始
to_lsn = 3158741　　#lsn结束号为最新的lsn
last_lsn = 3158741
compact = 0
recover_binlog_info = 0（4）恢复数据
[root@master ~]# innobackupex --copy-back /backups/2018-07-30_11-01-37/
180730 14:07:51 innobackupex: Starting the copy-back operation

IMPORTANT: Please check that the copy-back run completes successfully.
           At the end of a successful copy-back run innobackupex
           prints "completed OK!".
.......
.......
180730 14:08:17 [01]        ...done
180730 14:08:17 completed OK!
[root@master ~]# ll /usr/local/mysql/data/
total 77844
-rw-r----- 1 root root 79691776 Jul 30 14:08 ibdata1
drwxr-x--- 2 root root       20 Jul 30 14:08 kim
drwxr-x--- 2 root root     4096 Jul 30 14:08 mysql
drwxr-x--- 2 root root     4096 Jul 30 14:08 performance_schema
drwxr-x--- 2 root root       20 Jul 30 14:08 repppp
drwxr-x--- 2 root root       56 Jul 30 14:08 student
drwxr-x--- 2 root root     4096 Jul 30 14:08 wordpress
-rw-r----- 1 root root       21 Jul 30 14:08 xtrabackup_binlog_pos_innodb
-rw-r----- 1 root root      554 Jul 30 14:08 xtrabackup_info
[root@master ~]# chown -R mysql.mysql /usr/local/mysql/data　　#更改数据的属主属组
[root@master ~]# /etc/init.d/mysqld start　　#启动mysql
Starting MySQL.Logging to '/usr/local/mysql/data/master.err'.
.. SUCCESS! 
[root@master ~]# mysql -uroot -p -e "show databases;"　　#查看数据是否恢复
Enter password: 
+--------------------+
| Database           |
+--------------------+
| information_schema |
| kim                |
| mysql              |
| performance_schema |
| repppp             |
| student            |
| wordpress          |
+--------------------+
```

 总结：

（1）增量备份需要使用参数--incremental指定需要备份到哪个目录，使用incremental-dir指定全备目录；

（2）进行数据备份时，需要使用参数--apply-log redo-only先合并全备数据目录数据，确保全备数据目录数据的一致性；

（3）再将增量备份数据使用参数--incremental-dir合并到全备数据当中；

（4）最后通过最后的全备数据进行恢复数据，注意，如果有多个增量备份，需要逐一合并到全备数据当中，再进行恢复。

 

 

\#1. --user=root 指定备份的用户

\#2. --password=root指定备份用户的密码

\#3. --defaults-file=/etc/my.cnf 指定的备份数据的配置文件

\#4. /opt/ 指定备份后的数据保存路径