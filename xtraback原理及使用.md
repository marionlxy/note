# xtraback原理及使用

------

*kame* *2016/12/23*  24  *mysql xtraback*

# [#](http://www.liuwq.com/views/数据库/xtarback.html#xtrabackup)xtrabackup

> xtrabackup 是 percona 的一个开源项目，可以热备份innodb ，XtraDB,和MyISAM（会锁表）。对MyISAM存储引擎会锁表，也是很郁闷的因为线上使用的是Innodb和MyISAM两种存储引擎，比较头疼！！ Xtrabackup是一个对InnoDB做数据备份的工具，支持在线热备份（备份时不影响数据读写），是商业备份工具InnoDB Hotbackup的一个很好的替代品。

## [#](http://www.liuwq.com/views/数据库/xtarback.html#官方原理)官方原理

> 在InnoDB内部会维护一个redo日志文件，我们也可以叫做事务日志文件。事务日志会存储每一个InnoDB表数据的记录修改。当InnoDB启动时，InnoDB会检查数据文件和事务日志，并执行两个步骤：它应用（前滚）已经提交的事务日志到数据文件，并将修改过但没有提交的数据进行回滚操作。

xtrabackup在启动时会记住log sequence number（LSN），并且复制所有的数据文件。复制过程需要一些时间，所以这期间如果数据文件有改动，那么将会使数据库处于一个不同的时间点。这时，xtrabackup会运行一个后台进程，用于监视事务日志，并从事务日志复制最新的修改。xtrabackup必须持续的做这个操作，是因为事务日志是会轮转重复的写入，并且事务日志可以被重用。所以xtrabackup自启动开始，就不停的将事务日志中每个数据文件的修改都记录下来。

上面就是xtrabackup的备份过程。接下来是准备（prepare）过程。在这个过程中，xtrabackup使用之前复制的事务日志，对各个数据文件执行灾难恢复（就像MySQL刚启动时要做的一样）。当这个过程结束后，数据库就可以做恢复还原了。 以上的过程在xtrabackup的编译二进制程序中实现。程序innobackupex可以允许我们备份MyISAM表和frm文件从而增加了便捷和功能。Innobackupex会启动xtrabackup，直到xtrabackup复制数据文件后，然后执行FLUSH TABLES WITH READ LOCK来阻止新的写入进来并把MyISAM表数据刷到硬盘上，之后复制MyISAM数据文件，最后释放锁。

备份MyISAM和InnoDB表最终会处于一致，在准备（prepare）过程结束后，InnoDB表数据已经前滚到整个备份结束的点，而不是回滚到xtrabackup刚开始时的点。这个时间点与执行FLUSH TABLES WITH READ LOCK的时间点相同，所以MyISAM表数据与InnoDB表数据是同步的。类似Oracle的，InnoDB的prepare过程可以称为recover（恢复），MyISAM的数据复制过程可以称为restore（还原）。

xtrabackup和innobackupex这两个工具都提供了许多前文没有提到的功能特点。手册上有对各个功能都有详细的介绍。简单介绍下，这些工具提供了如流（streaming）备份，增量（incremental）备份等，通过复制数据文件，复制日志文件和提交日志到数据文件（前滚）实现了各种复合备份方式。

xtrabackup只能备份和恢复InnoDB表，而且只有ibd文件，frm文件它不管，恢复时就需要DBA提供frm。innobackupex可以备份和恢复MyISAM表以及frm文件，并且对xtrabackup也做了很好的封装，所以可以使用innobackupex来备份MySQL数据库。还有一个问题，就是innobackupex备份MyISAM表之前要对全库进行加READ LOCK，阻塞写操作，若备份是在从库上进行的话会影响主从同步，造成延迟。对InnoDB表备份不会阻塞读写。

## [#](http://www.liuwq.com/views/数据库/xtarback.html#xtrabackup增量备份的原理是)xtrabackup增量备份的原理是

首先完成一个完全备份，并记录下此时检查点LSN； 2)、然后增量备份时，比较表空间中每个页的LSN是否大于上次备份的LSN，若是则备份该页并记录当前检查点的LSN。

具体来说，首先在logfile中找到并记录最后一个checkpoint（“last checkpoint LSN”），然后开始从LSN的位置开始拷贝InnoDB的logfile到`xtrabackup_logfile`；然后开始拷贝全部的数据文件.ibd；在拷贝全部数据文件结束之后，才停止拷贝logfile。

所以xtrabackuplogfile文件在并发写入很大时也会变得很大，占用很多空间，需要注意。另外当我们使用--stream=tar或者远程备份--remote-host时默认使用/tmp，但最好显示用参数--tmpdir指定，以免把/tmp目录占满影响备份以及系统其它正常服务。 因为logfile里面记录全部的数据修改情况，所以即使在备份过程中数据文件被修改过了，恢复时仍然能够通过解析xtrabackuplogfile保持数据的一致。 xtrabackup的增量备份只能用于InnoDB表，不能用在MyISAM表上。采用增量备份MySQL数据库时xtrabackup会依据上次全备份或增量备份目录对InnoDB表进行增量备份，对MyISAM表会进行全表复制。

流备份（streaming）可以将备份直接保存到远程服务器上。 当执行恢复时，由于复制是不锁表的所以此时数据文件都是不一致的，xtrabackup使用之前保存的redo log对各个数据文件检查是否与事务日志的checkpoint一致，执行恢复： 1)、根据复制数据文件时以及之后已提交事务产生的事务日志进行前滚； 2)、将未提交的事务进行回滚。

这个过程就是MySQL数据库宕机之后执行的crash recovery。

## [#](http://www.liuwq.com/views/数据库/xtarback.html#增量备份)增量备份

在InnoDB中，每个page中都记录LSN信息，每当相关数据发生改变，page的LSN就会自动增加，xtrabackup的增量备份就是依据这一原理进行的。xtrabackup将上次备份（完全备份集或者也是一个增量备份集）以来LSN改变的page进行备份。 所以，要做增量备份第一次就要做一个完全备份（就是将MySQL实例或者说要备份的数据库表做一个完全复制，同时记录LSN），之后可以基于此进行增量备份以及恢复。

### [#](http://www.liuwq.com/views/数据库/xtarback.html#增量备份优点)增量备份优点

1. 数据库太大没有足够的空间全量备份，增量备份能有效节省空间，并且效率高；
2. 支持热备份，备份过程不锁表（针对InnoDB而言），不阻塞数据库的读写；
3. 每日备份只产生少量数据，也可采用远程备份，节省本地空间；
4. 备份恢复基于文件操作，降低直接对数据库操作风险；
5. 备份效率更高，恢复效率更高。

### [#](http://www.liuwq.com/views/数据库/xtarback.html#恢复与还原)恢复与还原

`backup`的恢复过程中包括恢复和还原两个部分。 我们前面已经说了`xtrabackup`只备份`InnoDB`表的`ibd`文件，而`innobackupex`可以备份包括`InnoDB`表在内的其他存储引擎的表的所有数据文件。由于不同引擎表备份时的不同，也会让恢复过程看起来不一样。

先来看看完全备份集的恢复。 在`InnoDB`表的备份或者更直接的说ibd数据文件复制的过程中，数据库处于不一致的状态，所以要将`xtraback_logfile`中尚未提交的事务进行回滚，以及将已经提交的事务进行前滚，使各个数据文件处于一个一致性状态，这个过程叫做“准备(prepare)”。

如果你是在一个从库上执行的备份，那说明你没有东西需要回滚，只是简单的apply redo log就可以了。另外在prepare过程中可以使用参数--use-memory增大使用系统内存量从而提高恢复速度。

之后，我们就可以根据backup-my.cnf中的配置把数据文件复制回对应的目录了，当然你也可以自己复制回去，但innobackupex都会帮我们完成。在这里，对于InnoDB表来说是完成“后准备”动作，我们称之为“恢复(recovery)”，而对于MyISAM表来说由于备份时是采用锁表方式复制的，所以此时只是简单的复制回来，不需要apply log，这个我们称之为“还原(restore)”。 注：本文档里之所以使用恢复和还原，也是和其他数据库比如Oracle看起来一样。

对于增量备份的恢复过程，与完全备份集的恢复类似，只是有少许不同：

- 恢复过程需要使用完全备份集和各个增量备份集，各个备份集的恢复与前面说的一样（前滚和回滚），之后各个增量备份集的redo log都会应用到完全备份集中；
- 对于完全备机集之后产生的新表，要有特殊处理方式，以便恢复后不丢表；
- 要以完全备份集为基础，然后按顺序应用各个增量备份集。

### [#](http://www.liuwq.com/views/数据库/xtarback.html#流备份和压缩)流备份和压缩

提到流备份(streaming)就要说远程备份和备份压缩，先说流备份吧。 流备份是指备份的数据通过标准输出STDOUT传输给tar程序进行归档，而不是单纯的将数据文件保存到指定的备份目录中，参数--stream=tar表示开启流备份功能并打包。同时也可以利用流备份到远程服务器上。 举例来说:

```
$ innobackupex --stream=TAR ${BACKUPDIR}/base | gzip > ${BACKUPDIR}/base.tar.gz $ innobackupex --stream=TAR ${BACKUP_DIR}/base|ssh somebackupaddr “cat > ${DIR}/base.tar”
```

当然了，如果你使用了流备份，那么增量备份也就不能用了，因为增量备份需要参考次备份情况，而上次备份却被打包或者压缩了。 在我们现实使用中，更多的使用增量备份，至于归档压缩我们可以通过脚本自主完成。

### [#](http://www.liuwq.com/views/数据库/xtarback.html#部分备份和恢复)部分备份和恢复

xtrabackup可以只备份/恢复部分库表，可以正则模式匹配或者是你想备份库表的列表，但InnoDB表必须是独立表空间，同时不能使用流备份功能。

- 使用正则模式匹配备份部分库表，需要使用参数--include，语句类似如下:

  `$ innobackupex --include=’^qb.*’ ${BACKUP_DIR}/part-base`

- 使用数据库列表备份部分库，需要使用参数--databases，语句类似如下:

  `$ innobackupex --databases=qb0 qb1 qb2 qb3 ${BACKUP_DIR}/part-base`

- 使用表列表备份部分表，需要使用参数--tables-file，语句类似如下:

  `$ innobackupex --tables-list=${CONFDIR}/tab.conf ${BACKUPDIR}/part-base`

> 注：在我们的现实应用中，很少会只备份集群中部分库表，所以只是了解此功能即可，若有现实需要可以参考percona官方资料以获取更多信息。

能备份部分库表，也就能根据完全备份集进行部分库表的恢复，在现实中很少会用到，但还是说一下吧。 首先在“准备prepare”的过程中，使用参数--export将表导出，这个导出会将每个InnoDB表创建一个以.exp结尾的文件，这些文件为之后的导入过程服务。

```
`$ innobackupex --apply-log --export ${BACKUP_DIR}/base`
```

然后将你需要恢复的表的ibd和exp文件复制到目标机器，在目标机器上执行导入：

```
  mysql> create table t()engine=innodb;
  //此处需要DBA手动创建一个同结构的表或表已存在
  mysql> ALTER TABLE t DISCARD TABLESPACE;
  $ cp t.ibd t.exp ${DATA_DIR}/${DB}/ mysql> ALTER TABLE t IMPORT TABLESPACE; 这样的导出导入就可以保住恢复的表可以与数据库其他表保持一致性了。
```

### [#](http://www.liuwq.com/views/数据库/xtarback.html#并行备份)并行备份

xtrbackup还支持并行备份，默认情况下xtrabackup备份时只会开启一个进程进行数据文件的备份，若配置参数--parallel=N可以让xtrabackup开启N个子进程对多个数据文件进行并发备份，这样可以加快备份的速度。当然服务器的IO处理能力以及对服务器的影响也是要考虑的，所以另一个参数--throttle=IOS会与它同时使用，这个参数用来限制备份过程中每秒读写的IO次数，对服务器的IO是一个保护。

这两个参数xtrabackup和innobackupex都支持，举例如下:

```
$ innobackupex --parallel=4 --throttle=400 ${BACKUP_DIR}/part-base 注意：对同一个数据文件只会有一个进程在备份。
```

### [#](http://www.liuwq.com/views/数据库/xtarback.html#其他)其他

xtrabackup在备份时主要的工作是做数据文件复制，它每次只会读写1MB的数据（即64个page，不能修改），xtrabackup逐页访问1MB数据，使用innodb的bufpageis_corrupted()函数检查此页的数据是否正常，如果数据不正常，就重新读取这一页，最多重新读取10次，如果还是失败，备份就失败了，退出。 在复制事务日志的时候，每次读写512KB的数据，同样不可以配置。 之前我在维护mysql数据库的时候，使用mysqldump来进行备份与恢复，在备份的时候锁住表，然后全部备份，在数据少的时候没问题，但如果数据很多，不允许锁表，同时需要恢复数据块的情况，mysqldump就不适合了，我在恢复一个4G数据文件的数据库的时候，恢复的数据是使用mysqldump的数据，恢复了3个小时还没有反应，造成的影响很严重，所以我开始寻找其他的别发软件来满足以上的需求，幸好找到了，就是使用xtrabackup来进行备份与恢复，恢复4G数据文件的数据库，仅需要14秒，同时在备份的时候不会锁表，而且支持增量备份，所以把我的比较分享给大家，希望对大家有益！

### [#](http://www.liuwq.com/views/数据库/xtarback.html#安装：)安装：

```shell
      yum install perl-Time-HiRes -y
      yum -y install perl-DBD-MySQL.x86_64
      tar xvf percona-xtrabackup-2.1.5-680-Linux-x86_64.tar.gz
      cd percona-xtrabackup-2.1.5-Linux-x86_64/
      cp bin/* /usr/bin/
```

> innobackupex使用参数介绍由于innobackupex能同时备份InnoDB和MyISAM引擎的表，这里重点介绍innobackupex的备份与恢复使用通常一般都直接使用innobackupex，因为它能同时备份InnoDB和MyISAM引擎的表。要注意的是my.cnf里datadir这个参数是必须要指定的，xtrabackup_55是根据它去定位innodb数据文件的位置。

```
innobackupex语法及参数说明innobackup [--sleep=MS] [--compress[=LEVEL]] [--include=REGEXP] [--user=NAME] [--password=WORD] [--port=PORT] [--socket=SOCKET] [--no-timest a mp] [--ibbackup=IBBACKUP-BINARY] [--slave-info] [--stream=tar] [--defaults-file=MY.CNF] [--databases=LIST] [--remote-host=HOSTNAME] BACKUP-ROOT-DIR

innobackup --apply-log [--use-memory=MB] [--uncompress] [--defaults-file=MY.CNF] [--ibbackup=IBBACKUP-BINARY] BACKUP-DIR

innobackup --copy-back [--defaults-file=MY.CNF] BACKUP-DIR
```

#### [#](http://www.liuwq.com/views/数据库/xtarback.html#各参数说明：)各参数说明：

```
--defaults-file指定mysql的配置文件my.cnf的位置，如--defaults-file=/etc/my.cnf如果不该参数，xtrabackup将从依次从以下位置查找配置文件/etc/my.cnf、/etc/mysql/my.cnf、/usr/local/etc/my.cnf、~/.my.cnf，并读取配置文件中的[mysqld]和[xtrabackup]配置段。[mysqld]中只需要指定datadir、innodb_data_home_dir、innodb_data_file_path、innodb_log_group_home_dir、innodb_log_files_in_group、innodb_log_file_size6个参数即可让xtrabackup正常工作--apply-log对xtrabackup的--prepare参数的封装
--copy-back做数据恢复时将备份数据文件拷贝到MySQL服务器的datadir ；
--remote-host=HOSTNAME通过ssh将备份数据存储到进程服务器上,HOSTNAME是远程IP地址；
--stream=[tar]
```

> 备份文件输出格式, tar时使用tar4ibd , 该文件可在XtarBackup binary文件中获得.如果备份时有指定--stream=tar, 则tar4ibd文件所处目录一定要在$PATH中(因为使用的是tar4ibd去压缩, 在XtraBackup的binary包中可获得该文件)。 在使用参数stream=tar备份的时候，你的xtrabackup_logfile可能会临时放在/tmp目录下，如果你备份的时候并发写入较大的话xtrabackup_logfile可能会很大(5G+)，很可能会撑满你的/tmp目录，可以通过参数--tmpdir指定目录来解决这个问题。

```
--tmpdir=DIRECTORY
当有指定--remote-host or --stream时, 事务日志临时存储的目录, 默认采用MySQL配置文件中所指定的临时目录tmpdir
--redo-only --apply-log组,
强制备份日志时只redo ,跳过rollback。这在做增量备份时非常必要。
--use-memory=#
该参数在prepare的时候使用，控制prepare时innodb实例使用的内存量
--throttle=IOS  
同xtrabackup的--throttle参数
--sleep=是给ibbackup使用的，指定每备份1M数据，过程停止拷贝多少毫秒，也是为了在备份时尽量减小对正常业务的影响，具体可以查看ibbackup的手册 ；
--compress[=LEVEL]对备份数据迚行压缩，仅支持ibbackup，xtrabackup还没有实现；
--include=REGEXP对xtrabackup参数--tables的封装，也支持ibbackup。备份包含的库表，例如：--include="test.*"，意思是要备份test库中所有的表。如果需要全备份，则省略这个参数；如果需要备份test库下的2个表：test1和test2,则写成：--include="test.test1|test.test2"。也可以使用通配符，如：--include="test.test*"。
--databases=LIST列出需要备份的databases，如果没有指定该参数，所有包含MyISAM和InnoDB表的database都会被备份；
--uncompress解压备份的数据文件，支持ibbackup，xtrabackup还没有实现该功能；
--slave-info,备份从库, 加上--slave-info备份目录下会多生成一个xtrabackup_slave_info 文件, 这里会保存主日志文件以及偏移, 文件内容类似于:CHANGE MASTER TO MASTER_LOG_FILE='', MASTER_LOG_POS=0
--socket=SOCKET指定mysql.sock所在位置，以便备份进程登录mysql.
```

#### [#](http://www.liuwq.com/views/数据库/xtarback.html#操作：)操作：

对数据库全库备份：

innobackupex --defaults-file=/etc/my.cnf --user=root --password=111111 --port=3306 /tmp/

> 解释：

```
--defaults-file=/etc/my.cnf  #指定my.cnf位置
--user=root  #指定mysql帐号
--password=111111   #指定mysql密码
--port=3306   #指定mysql端口
/tmp/   #指定备份好的文件存放目录，我这放在/tmp/下面，
执行完成后，如下多了个时间为名了的目录，里面就是备份文件了：

[root@drfdai-17 tmp]# ls
2013-10-29_16-06-41
[root@drfdai-17 tmp]# ls 2013-10-29_16-06-41/
aa ibdata1 testxtrabackup_checkpoints
backup-my.cnf  mysql   xtrabackup_binary   xtrabackup_logfile
drfdai performance_schema  xtrabackup_binlog_info
备份drfdai库：

innobackupex --defaults-file=/etc/my.cnf --user=root --password=111111 --port=3306 --database=drfdai /tmp/
```

> 解释：

```
--database=drfdai #指定需要备份的数据库名

  [root@drfdai-17 2013-10-29_16-23-53]# ls
  backup-my.cnf  ibdata1xtrabackup_binlog_info  xtrabackup_logfile
  drfdai xtrabackup_binary  xtrabackup_checkpoints
```

#### [#](http://www.liuwq.com/views/数据库/xtarback.html#备份多个库：)备份多个库：

```
  innobackupex --defaults-file=/etc/my.cnf --user=root --password=111111 --port=3306 --database='drfdai mysql' /tmp/
```

> 解释：

```
  --database='drfdai mysql'  #指定你需要备份的那几个库名，用单引号把这些库名引起来，每个库中间用空格隔开。
  [root@drfdai-17 2013-10-29_16-33-09]# ls
  backup-my.cnf  ibdata1  xtrabackup_binary   xtrabackup_checkpoints
  drfdai mysqlxtrabackup_binlog_info  xtrabackup_logfile
```

#### [#](http://www.liuwq.com/views/数据库/xtarback.html#备份多个表：)备份多个表：

```
  innobackupex --defaults-file=/etc/my.cnf --user=root --password=111111 --port=3306 --database='drfdai.aa1 drfdai.aa2' /tmp/
```

> 解释：

```
--database='drfdai.aa1 drfdai.aa2' #指定备份drfdai库下面的aa1表和aa2表
```

### [#](http://www.liuwq.com/views/数据库/xtarback.html#还原操作：)还原操作：

```
停止mysql数据库并删除欲恢复的数据库文件夹
如我的mysql数据库文件夹是在/data/mysql/data中，所以我删掉这个文件夹
然后重建一个/data/mysql/data/
      rm -rf /data/mysql/data
      mkdir /data/mysql/data
```

#### [#](http://www.liuwq.com/views/数据库/xtarback.html#还原完整备份：)还原完整备份：

```
innobackupex --defaults-file=/etc/my.cnf --user=root --password=111111 --port=3306 --apply-log /tmp/2013-10-29_17-17-47/
这里的--apply-log指明是将日志应用到数据文件上，完成之后将备份文件中的数据恢复到数据库中

innobackupex --defaults-file=/etc/my.cnf --user=root --password=111111 --port=3306 --copy-back /tmp/2013-10-29_17-17-47/
这里的—copy-back指明是进行数据恢复。数据恢复完成之后，需要修改相关文件的权限mysql数据库才能正常启动。

chown -R mysql:mysql /data/mysql/data
```

#### [#](http://www.liuwq.com/views/数据库/xtarback.html#增量备份：)增量备份：

```
次先进行完备： innobackupex --defaults-file=/etc/my.cnf --user=root --password=111111 --port=3306 /tmp/ 备份完后，会生成最新的目录，名为：2013-10-29_17-17-47

进行第一次增量备份：

innobackupex --defaults-file=/etc/my.cnf --user=root --password=111111 --port=3306  --incremental --incremental-basedir=/tmp/2013-10-29_17-17-47 /tmp
备份完成后，会生成最新增量备份，名为：2013-10-29_17-57-21
解释：

--incremental #指定为此次为增量备份
--incremental-basedir=/tmp/2013-10-29_17-17-47  #指定是从哪个备份目录为参考点进行增量备份
进行第二次增量备份：

innobackupex --defaults-file=/etc/my.cnf --user=root --password=111111 --port=3306  --incremental --incremental-basedir=/tmp/2013-10-29_17-57-21/ /tmp
以此类推，第三，第四 ……
```

#### [#](http://www.liuwq.com/views/数据库/xtarback.html#增量备份恢复：)增量备份恢复：

> 增量备份恢复的步骤和完整备份恢复的步骤基本一致，只是应用日志的过程稍有不同。增量备份恢复时，是先将所有的增量备份挨个应用到完整备份的数据文件中，然后再将完整备份中的数据恢复到数据库中。命令如下：

- 应用第一个增量备份

  innobackupex --user=root --password=MySQLPASSWORD --defaults-file=/etc/my.cnf --apply-log /mysqlbackup/full/2011-08-09_14-50-20/ --incremental-dir=/mysqlbackup/trn/2011-08-09_15-12-43/

- 应用第二个增量备份

  innobackupex --user=root --password=MySQLPASSWORD --defaults-file=/etc/my.cnf --apply-log /mysqlbackup/full/2011-08-09_14-50-20/ --incremental-dir=/mysqlbackup/trn/2011-08-05_15-15-47/

- 将完整备份中的数据恢复到数据库中

  innobackupex --user=root --password=MySQLPASSWORD --defaults-file=/etc/my.cnf --copy-back /mysqlbackup/full/2011-08-05_14-50-20/ 其中，--incremental-dir指定要恢复的增量备份的位置。



# xtraback备份脚本



```shell
# xtraback 备份脚本
# author: kame
# mail:liuwenqi7011@.163.com
#!/bin/sh
#percona-xtrabackup全量和增量备份脚本

#usage: 1. full backup  : ./backup.sh full
#       2. incremental backup : ./backup.sh inc


Innobackupex_Path=/usr/bin/innobackupex
Mysql_Client=/usr/bin/mysql
Bak_Time=`date +%Y%m%d_%H%M%S`

#请勿在Incrbackup_Path及下属文件夹创建或写入内容，否则可能导致增量备份不成功
Backup_Dir=/opt/backup   #备份主目录
#Backup_Dir=/opt/backup/data/`data -I`   #按日期生成备份主目录
Fullbackup_Path=$Backup_Dir/full # 全库备份的目录  
Incrbackup_Path=$Backup_Dir/incr # 增量备份的目录  
Log_Path=$Backup_Dir/logs   #日志文件目录
Keep_Fullbackup=5    #保留的全备份数量,此处要加1; 如要保留2个，此处要写3
Mysql_Conf=/etc/my.cnf #mysql配置文件
Mysql_Opts='--socket=/opt/mysql/mysql.sock  --host=localhost --user=root --password=9hb1a$OCinbl'  #mysql的连接配置，按需修改

Error()  
  {  
    echo -e "\e[1;31m$1\e[0m" 1>&2
    exit 1  
  }  
Backup()
  {
    #两个参数为全量备份,第一个参数为备份目录，第二个参数为日志全路径
    if [ $# = 2 ] ; then
        $Innobackupex_Path --defaults-file=$Mysql_Conf $Mysql_Opts  --no-timestamp  $1/full_$Bak_Time>$2 2>&1
    #三个参数为增量备份，第一个为增量备份目录，第二个为上个增量备份目录,第三个为日志全路径
    elif [ $# = 3 ];then
        $Innobackupex_Path --defaults-file=$Mysql_Conf $Mysql_Opts  --no-timestamp --incremental  $1/incr_$Bak_Time  --incremental-basedir $2 >$3 2>&1
    else
    Error "Backup(): 参数不正确"
     fi
  }

#获得某个目录下，最近修改的目录
Lastest_Dir()
  {
    if [ -d $1 ]; then
        path=`ls -t $1 |head -n 1`
        if [  $path ]; then
            echo $path
        else
            Error "Lastest_Diri(): 目录为空,没有最新目录"
        fi
    else
        Error "Latest_Dir(): 目录不存在或者不是目录"
    fi
  }

#进行增量备份
Do_Inc()
  {
    if [ "$(ls -A $Incrbackup_Path)" ] ; then
        #不是第一次增量备份，以最新的增量备份目录为base_dir
        Backup $Incrbackup_Path $Incrbackup_Path/`Lastest_Dir $Incrbackup_Path`  $Log_Path/incr_$Bak_Time.log
      else
        #第一次增量备份要先全量备份
        Backup $Incrbackup_Path  $Log_Path/incr_full_$Bak_Time.log
    fi
  }

#进行全量备份
Do_Full()
  {
    Backup  $Fullbackup_Path $Log_Path/full_$Bak_Time.log
    cd $Fullbackup_Path
    ls -t |tail -n +$Keep_Fullbackup |xargs  rm -rf
  }

#环境和配置检查
Check()
  {
    #检查目录和创建目录
    if [ ! -d $Fullbackup_Path ];then
        mkdir -p $Fullbackup_Path
    fi
    if [ ! -d $Incrbackup_Path ];then
        mkdir -p $Incrbackup_Path
    fi
    if [ ! -d $Log_Path ];then
        mkdir -p $Log_Path
    fi
    #检测所需的软件
    if [ ! -f $Innobackupex_Path ];then
        Error "未安装xtradbbackup或xtradbbackup路径不正确"
    fi
    if [ ! -f $Mysql_Client ];then
        Error "未安装mysql客户端"
    fi
    if [ ! -f $Mysql_Conf ];then
        Error "mysql配置文件路径不正确"
    fi
    #检查mysql的运行状态
    if [ `netstat -tlnp |grep mysqld |wc -l` = 0 ];then
        Error "MySQL没有运行"
    fi
    #验证mysql的用户和密码是否正确
    if  ! `echo 'exit' | $Mysql_Client -s  $Mysql_Opts >/dev/null 2>&1` ; then
        Error "提供的数据库连接配置不正确!"  
    fi
  }
case $1 in
       full)
          Check
          Do_Full
          ;;
        inc)
          Check
          Do_Inc
          ;;
         *)
          echo "full 全量备份"
      echo "inc  增量备份"
      ;;
esac  
```