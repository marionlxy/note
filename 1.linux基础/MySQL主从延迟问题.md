## MySQL数据库拓展学习

-Author: bavdu

-Email: bavduer@163.com

-Github: https://github.com

---



1. **MySQL数据库主从同步延迟原理**

谈到MySQL数据库主从同步延迟原理,得从mysql的数据库主从复制原理说起,mysql的主从复制都是单线程的操作,主库对所有DDL和 DML产生binlog, binlog是顺序写所以效率很高, slave的Slave_IO_Running线程到主库取日志效率也比较高. 

下一步问题来了, slave的Slave_SQL_Running线程将主库的DDL和DML操作在slave实施. DML和DDL的IO操作是随机的, 不是顺序的, 成本高很多,还可能可slave上的其他查询产生lock争用,由于Slave_SQL_Running也是单线程的,所以一个DDL卡主了,需要执行10分钟, 那么所有之后的DDL会等待这个DDL执行完才会继续执行,这就导致了延时.有同学会问: “主库上那个相同的DDL也需要执行10分钟, 为什么slave会延时？” 答案是master可以并发, Slave_SQL_Running线程却不可以

2. **MySQL数据库主从同步延迟是怎么产生的**

当主库的TPS并发较高时, 产生的DDL数量超过slave一个sql线程所能承受的范围,那么延时就产生了,当然还有就是可能与slave的大型query语句产生了锁等待

3. **MySQL数据库主从同步延迟解决方案**

最简单的减少slave同步延时的方案就是在架构上做优化,尽量让主库的DDL快速执行.还有就是主库是写,对数据安全性较高, 比如 sync_binlog=1、innodb_flush_log_at_trx_commit = 1 之类的设置, 而slave则不需要这么高的数据安全, 完全可以将sync_binlog设置为0或者关闭binlog, innodb_flushlog也可以设置为0来提高sql的执行效率,另外就是使用比主库更好的硬件设备作为slave