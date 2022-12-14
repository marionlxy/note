# Redis特性和性能调优

## 概要

在分布式里面满足CP （一致性、分区容错性）。

性能：对于单纯只有IO操作来说，单线程可以将速度优势发挥到最大，但是Redis也提供了一些简单的计算功能，比如排序、聚合等，对于这些操作，单线程模型实际会严重影响整体吞吐量，CPU计算过程中，整个IO调度都是被阻塞住的。

## 一 Redis和Memcached对比

1：数据类型：Memcached单个key-value大小有限，一个value最大只支持1MB，而Redis最大支持512MB，支持set，list等类型

2：持久性：Memcached只是个内存缓存，对可靠性无要求；而Redis更倾向于内存数据库，因此对对可靠性方面要求比较高、做了数据持久化

3：数据一致性：redis是单线程模型，保证了数据按顺序提交，Redis提供了事务的功能，可以保证一串 命令的原子性，中间不会被任何操作打断。 memcached需要cas保证数据一致性，在高并发下。性能会受到影响，甚至不如redis。

## 二 数据回收策略

相关知识：redis 内存数据集大小上升到一定大小的时候，就会施行数据淘汰策略（回收策略）。redis 提供 6种数据淘汰策略：

1. volatile-lru：从已设置过期时间的数据集（server.db[i].expires）中挑选最近最少使用的数据淘汰
2. volatile-ttl：从已设置过期时间的数据集（server.db[i].expires）中挑选将要过期的数据淘汰
3. volatile-random：从已设置过期时间的数据集（server.db[i].expires）中任意选择数据淘汰
4. allkeys-lru：从数据集（server.db[i].dict）中挑选最近最少使用的数据淘汰
5. allkeys-random：从数据集（server.db[i].dict）中任意选择数据淘汰
6. no-enviction（驱逐）：禁止驱逐数据

## 三 持久化

*fork**操作都会造成主线程堵塞。这个时候服务是停止的。*

### 3.1 RDB（redis database）

​     rdb为二进制文件，redis在指定的时间内（默认配置3个时间段，1分钟1W次，10分钟10次，15分钟1次），把内存的数据集快照写入到磁盘，恢复的时候是将硬盘中快照文件写入内存。redis 会单独创建（fork）一个子进程去进行持久化，先写入一个临时文件dump.rdb ，待持久化结束了，再替换上次持久化好的文件，整个过程中，主线程是不需要任何io操作的。（子进程保持数据一致性）。运维手段（上报dump.rdb）

​     如果需要大规模恢复，且对数据缺失不是很敏感。那么采用RDB，RDB的方式比AOF更加高效，但是最后一次持久化的数据可能丢失。一般做冷数据备份

​     fork的时候，内存中的数据被克隆了一份，大致2倍的膨胀性需要考虑，当数据集比较大额时候，folk的过程是比较耗时的，可能会导致redis在一些毫秒级不能响应客服端请求

### 3.2 AOF（append only file）

（如果同时rdb和aof同时存在，先加载aof，error才加载rdb）：命令

​    redis也会fork一个子进程，以日志的形式记录每次写操作命令。 AOF持久化以日志的形式记录服务器所处理的每一个写、删除操作，查询操作不会记录，换句话说，恢复的时候，把文件记录命令全部再执行一遍

​    AOF是存放每条写命令的，所以会不断的增大，当大到一定程度时，AOF会做rewrite操作,rewrite操作就是基于当时redis的数据重新构造一个小的AOF文件，然后将大的AOF文件删除。

1. 对于同一份文件AOF文件比RDB数据快照要大。
2. AOF开启后支持写的QPS会比RDB支持的写的QPS低，因为AOF一般会配置成每秒fsync操作，每秒的fsync操作还是很高的
3. 数据恢复比较慢，不适合做冷备。

## 四 事务

*不保证原子性，部分支持事务，但是可以通过watch**实现乐观锁*

开启事务-》放入队列-》执行，本质上是一组命令的集合。一个事务中的所有命令都会被序列化，按照顺序串行地执行而不会被其他命令插入。 

原子性：redis事务不能保证原子性，有一个执行失败，其它依被执行，没有回滚

隔离级别：没有数据那些隔离级别概念，队列里面没有提交之前都不会执行，在执行过程中也不会被其它事务打断。

1. 如果中途命令（编译）出错。那么全部不执行
2. 如果是运行时报错，其他依然执行。出错的不执行：字符串+1

一致性问题：

在事务之前有其他执行，那么数据就有误

*WATCH* *（乐观锁）*

可以监视一个或多个key，一旦其中有任意一个key被修改，那么事务被打断，都不会被执行，返回失败，但是并不能保证其他客户端不修改监控的值，所以当EXEC命令执行失败之后需要手动重新执行整个事务

伪代码：

*exec(WATCH stock:1001);*

*if(exec(HGET stock:1001 state) == "in stock") {*

  *exec(MULTI);*

  *exec(HSET stock:1001 state "sold");*

  *exec(EXEC);*

*}*

## 五 集群

*软件架构不是越复杂越好，尽量减少过度设计，我们用的主从。*

### 5.1 主从复制

info replication —查看集群信息

1. 只有*1*个*Master*，可以有*N*个*slaver*，而且*Slaver*也可以有自己的*Slaver*，由于这种主从的关系决定他们是在配置阶段就要指定他们的上下级关系，而不是*Zookeeper*那种平行关系是自主推优出来的。
2. 读写分离，*Master*只负责写和同步数据给*Slaver*，*Slaver*承担了被读的任务，所以*Slaver*的扩容只能提高读效率不能提高写效率。
3. *Slaver*先将*Master*那边获取到的信息压入磁盘，再*load*进内存，*client*端是从内存中读取信息的，所以*Redis*是内存数据库。
4. 当一个新的*Slaver*加入到这个集群时，会向主服务器发送一个 SYNC 命令，*Master*发现新的小弟后将全量数据（全量是rdb、增量是aof文件）发送给新的*Slaver*，数据量越大性能消耗也就越大，所以尽量避免在运行时做*Slaver*的扩容

*简单总结下主从模式的设计：*

优点：读写分离，通过增加*Slaver*可以提高并发读的能力。

缺点：*Master*写能力是瓶颈。

​     虽然理论上对*Slaver*没有限制但是维护*Slaver*开销总将会变成瓶颈。

​     Master的Disk大小也将会成为整个Redis集群存储容量的瓶颈。

*Sentinel**哨兵模式：*

能够后台监控主机是否故障，如果故障了根据投票数自动将从库转换为主库。

### 5.2 集群分片

哈希Slot [slɒt]:就是分库分表，hash取模

​      Redis Cluster中共有16384个hash slot，Redis会计算每个key的CRC16，将结果与16384取模，来决定该key存储在哪一个hash slot中，同时需要指定Redis Cluster中每个数据分片负责的Slot数。Slot的分配在任何时间点都可以进行重新分配。

![img](https://img-blog.csdn.net/20180817112116961?watermark/2/text/aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2h1OTQ4MTYyOTk5/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70)

 

### 5.3 主从分片

​      想扩展并发读就添加*Slaver*，想扩展并发写就添加*Master*，想扩容也就是添加*Master*，任何一个*Slaver*或者几个*Master*挂了都不会是灾难性的故障。

简单总结下哈希*Slot*的优缺点：

缺点：每个*Node*承担着互相监听、高并发数据写入、高并发数据读出，工作任务繁重

优点：将*Redis*的写操作分摊到了多个节点上，提高写的并发能力，扩容简单。

![img](https://img-blog.csdn.net/20180817112116990?watermark/2/text/aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2h1OTQ4MTYyOTk5/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70)

## 六 缓存穿透、雪崩

## 缓存穿透

一般出现这样的问题，是因为当我们查询一条肯定不存在的数据的时候，缓存中没有，就会透过缓存来查询数据库，数据库也不存在，这样就不会将值保存在缓存中，最后还是缓存和数据库中都没有，如果一直访问这条数据。我们就对数据库进行频繁的查询，给数据库带来压力；

**解决方法：**当查询的时候，如果缓存和数据库中都没有，我们就将这个数据以空的形式存放在缓存中，（或者是给一个false的标示）这样就不用去数据库就可以知道不存在，减少对数据库查询的次数，当我们这个值发生改变的时候，我们在重新进行赋值；

## 并发情况

当我们大量访问都是查询一个缓存中没有的数据时，这样就会都去数据库中进行查询，可能会造成数据库的宕机；

**解决方法：**在查询的时候，我给他添加了一个同步锁，只有第一条数据去数据库中查并且返回到redis中后才能查询，这是数据库中已近存在了值，这样也可以避免；

## 缓存雪崩　

大量数据的缓存时间失效，这样用户就会访问到数据库，第一台数据库崩溃了，访问就会到第二台数据库进行查询，这样会导致第二台的也崩溃；

**解决方法：**就是设置失效时间时，不要一起失效，或者是设置在访问量少的时候，或者设置为永远不失效；

## 缓存击穿

　　是指一个key非常热点，在不停的扛着大并发，大并发集中对这一个点进行访问，当这个key在失效的瞬间，持续的大并发就穿破缓存，直接请求数据库，就像在一个屏障上凿开了一个洞。

　　**解决方法：**对热门访问key早早的做好了准备，让缓存永不过期；





# [redis持久化的几种方式](http://www.cnblogs.com/chenliangcl/p/7240350.html)

# [1、前言](http://www.cnblogs.com/Fairy-02-11/p/6182478.html)

Redis是一种高级key-value数据库。它跟memcached类似，不过数据可以持久化，而且支持的数据类型很丰富。有字符串，链表，集 合和有序集合。支持在服务器端计算集合的并，交和补集(difference)等，还支持多种排序功能。所以Redis也可以被看成是一个数据结构服务 器。
Redis的所有数据都是保存在内存中，然后不定期的通过异步方式保存到磁盘上(这称为“半持久化模式”)；也可以把每一次数据变化都写入到一个append only file(aof)里面(这称为“全持久化模式”)。 

由于Redis的数据都存放在内存中，如果没有配置持久化，redis重启后数据就全丢失了，于是需要开启redis的持久化功能，将数据保存到磁 盘上，当redis重启后，可以从磁盘中恢复数据。redis提供两种方式进行持久化，一种是RDB持久化（原理是将Reids在内存中的数据库记录定时 dump到磁盘上的RDB持久化），另外一种是AOF（append only file）持久化（原理是将Reids的操作日志以追加的方式写入文件）。那么这两种持久化方式有什么区别呢，改如何选择呢？网上看了大多数都是介绍这两 种方式怎么配置，怎么使用，就是没有介绍二者的区别，在什么应用场景下使用。

#### 2、二者的区别

RDB持久化是指在指定的时间间隔内将内存中的数据集快照写入磁盘，实际操作过程是fork一个子进程，先将数据集写入临时文件，写入成功后，再替换之前的文件，用二进制压缩存储。

![img](图片/388326-20170726161552843-904424952.png)

 

AOF持久化以日志的形式记录服务器所处理的每一个写、删除操作，查询操作不会记录，以文本的方式记录，可以打开文件看到详细的操作记录。

![img](图片/388326-20170726161604968-371688235.png)

 

#### 3、二者优缺点

#### RDB存在哪些优势呢？

1). 一旦采用该方式，那么你的整个Redis数据库将只包含一个文件，这对于文件备份而言是非常完美的。比如，你可能打算每个小时归档一次最近24小时的数 据，同时还要每天归档一次最近30天的数据。通过这样的备份策略，一旦系统出现灾难性故障，我们可以非常容易的进行恢复。

2). 对于灾难恢复而言，RDB是非常不错的选择。因为我们可以非常轻松的将一个单独的文件压缩后再转移到其它存储介质上。

3). 性能最大化。对于Redis的服务进程而言，在开始持久化时，它唯一需要做的只是fork出子进程，之后再由子进程完成这些持久化的工作，这样就可以极大的避免服务进程执行IO操作了。

4). 相比于AOF机制，如果数据集很大，RDB的启动效率会更高。

RDB又存在哪些劣势呢？

1). 如果你想保证数据的高可用性，即最大限度的避免数据丢失，那么RDB将不是一个很好的选择。因为系统一旦在定时持久化之前出现宕机现象，此前没有来得及写入磁盘的数据都将丢失。

2). 由于RDB是通过fork子进程来协助完成数据持久化工作的，因此，如果当数据集较大时，可能会导致整个服务器停止服务几百毫秒，甚至是1秒钟。

#### AOF的优势有哪些呢？

1). 该机制可以带来更高的数据安全性，即数据持久性。Redis中提供了3中同步策略，即每秒同步、每修改同步和不同步。事实上，每秒同步也是异步完成的，其 效率也是非常高的，所差的是一旦系统出现宕机现象，那么这一秒钟之内修改的数据将会丢失。而每修改同步，我们可以将其视为同步持久化，即每次发生的数据变 化都会被立即记录到磁盘中。可以预见，这种方式在效率上是最低的。至于无同步，无需多言，我想大家都能正确的理解它。

2). 由于该机制对日志文件的写入操作采用的是append模式，因此在写入过程中即使出现宕机现象，也不会破坏日志文件中已经存在的内容。然而如果我们本次操 作只是写入了一半数据就出现了系统崩溃问题，不用担心，在Redis下一次启动之前，我们可以通过redis-check-aof工具来帮助我们解决数据 一致性的问题。

3). 如果日志过大，Redis可以自动启用rewrite机制。即Redis以append模式不断的将修改数据写入到老的磁盘文件中，同时Redis还会创 建一个新的文件用于记录此期间有哪些修改命令被执行。因此在进行rewrite切换时可以更好的保证数据安全性。

4). AOF包含一个格式清晰、易于理解的日志文件用于记录所有的修改操作。事实上，我们也可以通过该文件完成数据的重建。

AOF的劣势有哪些呢？

1). 对于相同数量的数据集而言，AOF文件通常要大于RDB文件。RDB 在恢复大数据集时的速度比 AOF 的恢复速度要快。

2). 根据同步策略的不同，AOF在运行效率上往往会慢于RDB。总之，每秒同步策略的效率是比较高的，同步禁用策略的效率和RDB一样高效。

二者选择的标准，就是看系统是愿意牺牲一些性能，换取更高的缓存一致性（aof），还是愿意写操作频繁的时候，不启用备份来换取更高的性能，待手动运行save的时候，再做备份（rdb）。rdb这个就更有些 eventually consistent的意思了。

#### 4、常用配置

#### RDB持久化配置

Redis会将数据集的快照dump到dump.rdb文件中。此外，我们也可以通过配置文件来修改Redis服务器dump快照的频率，在打开6379.conf文件之后，我们搜索save，可以看到下面的配置信息：

save 900 1       #在900秒(15分钟)之后，如果至少有1个key发生变化，则dump内存快照。

save 300 10      #在300秒(5分钟)之后，如果至少有10个key发生变化，则dump内存快照。

save 60 10000    #在60秒(1分钟)之后，如果至少有10000个key发生变化，则dump内存快照。

#### AOF持久化配置

在Redis的配置文件中存在三种同步方式，它们分别是：

appendfsync always   #每次有数据修改发生时都会写入AOF文件。

appendfsync everysec #每秒钟同步一次，该策略为AOF的缺省策略。

appendfsync no     #从不同步。高效但是数据不会被持久化。