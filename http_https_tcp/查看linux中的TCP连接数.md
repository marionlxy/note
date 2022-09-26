# 查看linux中的TCP连接数

## [#](http://www.liuwq.com/views/linux基础/linux_tcp_conntions.html#查看哪些ip连接本机)查看哪些IP连接本机

```
netstat -an
```

## [#](http://www.liuwq.com/views/linux基础/linux_tcp_conntions.html#查看tcp连接数)查看TCP连接数

1. 统计80端口连接数

   `netstat -nat|grep -i "80"|wc -l`

2. 统计httpd协议连接数

   `ps -ef|grep httpd|wc -l`

3. 统计已连接上的，状态为“established

   `netstat -na|grep ESTABLISHED|wc -l`

4. 查出哪个IP地址连接最多,将其封了.

```
netstat -na|grep ESTABLISHED|awk {print $5}|awk -F: {print $1}|sort|uniq -c|sort -r +0n
netstat -na|grep SYN|awk {print $5}|awk -F: {print $1}|sort|uniq -c|sort -r +0n
```

------

1. 查看apache当前并发访问数：

   `netstat -an | grep ESTABLISHED | wc -l`

   对比httpd.conf中MaxClients的数字差距多少。

2. 查看有多少个进程数：

   `ps aux|grep httpd|wc -l`

3. 可以使用如下参数查看数据

   `server-status?auto`

   `ps -ef|grep httpd|wc -l`

   `1388`

统计`httpd进程数`，连个请求会启动一个进程，使用于Apache服务器。 表示Apache能够处理1388个并发请求，这个值Apache可根据负载情况自动调整。

```
netstat -nat|grep -i "80"|wc -l
4341
```

`netstat -an`会打印系统当前网络链接状态，而`grep -i "80"`是用来提取与80端口有关的连接的，`wc -l`进行连接数统计。 最终返回的数字就是当前所有80端口的请求总数。

```
netstat -na|grep ESTABLISHED|wc -l
```

`376` `netstat -an`会打印系统当前网络链接状态，而`grep ESTABLISHED` 提取出已建立连接的信息。 然后`wc -l`统计。

最终返回的数字就是当前所有`80端口`的已建立连接的总数。

`netstat -nat||grep ESTABLISHED|wc -`可查看所有建立连接的详细记录

### [#](http://www.liuwq.com/views/linux基础/linux_tcp_conntions.html#查看apache的并发请求数及其tcp连接状态：)查看Apache的并发请求数及其TCP连接状态：

Linux命令：

```
netstat -n | awk '/^tcp/ {++S[$NF]} END {for(a in S) print a, S[a]}'
```

结果:

`TIME_WAIT 8947` 等待足够的时间以确保远程TCP接收到连接中断请求的确认 `FIN_WAIT1 15` 等待远程TCP连接中断请求，或先前的连接中断请求的确认 `FIN_WAIT2 1` 从远程TCP等待连接中断请求 `ESTABLISHED 55` 代表一个打开的连接 `SYN_RECV 21` 再收到和发送一个连接请求后等待对方对连接请求的确认 `CLOSING 2` 没有任何连接状态 `LAST_ACK 4` 等待原来的发向远程TCP的连接中断请求的确认

### [#](http://www.liuwq.com/views/linux基础/linux_tcp_conntions.html#tcp连接状态详解)TCP连接状态详解

`LISTEN:` 侦听来自远方的TCP端口的连接请求 `SYN-SENT：` 再发送连接请求后等待匹配的连接请求 `SYN-RECEIVED：`再收到和发送一个连接请求后等待对方对连接请求的确认 `ESTABLISHED：` 代表一个打开的连接 `FIN-WAIT-1：` 等待远程TCP连接中断请求，或先前的连接中断请求的确认 `FIN-WAIT-2：` 从远程TCP等待连接中断请求 `CLOSE-WAIT：` 等待从本地用户发来的连接中断请求 `CLOSING：` 等待远程TCP对连接中断的确认 `LAST-ACK：` 等待原来的发向远程TCP的连接中断请求的确认 `TIME-WAIT：` 等待足够的时间以确保远程TCP接收到连接中断请求的确认 `CLOSED：` 没有任何连接状态

**输出结果:**

LAST_ACK 5 SYN_RECV 30 ESTABLISHED 1597 FIN_WAIT1 51 FIN_WAIT2 504 TIME_WAIT 1057

其中的 `SYN_RECV` 表示正在等待处理的请求数； `ESTABLISHED` 表示正常数据传输状态； `TIME_WAIT` 表示处理完毕，等待超时结束的请求数。

------

### [#](http://www.liuwq.com/views/linux基础/linux_tcp_conntions.html#查看apache并发请求数及其tcp连接状态)查看Apache并发请求数及其TCP连接状态

查看`httpd`进程数（即`prefork`模式下`Apache`能够处理的并发请求数）：

Linux命令：

```
ps -ef | grep httpd | wc -l
```

### [#](http://www.liuwq.com/views/linux基础/linux_tcp_conntions.html#如发现系统存在大量time-wait状态的连接，通过调整内核参数解决)如发现系统存在大量TIME_WAIT状态的连接，通过调整内核参数解决

```
vim /etc/sysctl.conf
```

编辑文件，加入以下内容：

```yml
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_tw_recycle = 1
net.ipv4.tcp_fin_timeout = 30
```

然后执行 `/sbin/sysctl -p` 让参数生效。

`net.ipv4.tcp_syncookies = 1` 表示开启`SYN cookies`。当出现SYN等待队列溢出时，启用`cookies`来处理，可防范少量SYN攻击，默认为0，表示关闭； `net.ipv4.tcp_tw_reuse = 1` 表示开启重用。允许将`TIME-WAIT sockets`重新用于新的TCP连接，默认为0，表示关闭； `net.ipv4.tcp_tw_recycle = 1` 表示开启TCP连接中`TIME-WAIT sockets`的快速回收，默认为0，表示关闭。 `net.ipv4.tcp_fin_timeout` 修改系統默认的 `TIMEOUT` 时间

下面附上`TIME_WAIT`状态的意义：

客户端与服务器端建立`TCP/IP`连接后关闭`SOCKET`后，服务器端连接的端口 状态为`TIME_WAIT`

是不是所有执行主动关闭的`socket`都会进入`TIME_WAIT`状态呢？ 有没有什么情况使主动关闭的`socket`直接进入`CLOSED`状态呢？

主动关闭的一方在发送最后一个 `ack`后 就会进入 `TIME_WAIT` 状态 停留`2MSL（max segment lifetime）`时间 这个是`TCP/IP`必不可少的，也就是“解决”不了的。

> 也就是TCP/IP设计者本来是这么设计的

**主要有两个原因**

1. 防止上一次连接中的包，迷路后重新出现，影响新连接

（经过2MSL，上一次连接中所有的重复包都会消失）

1. 可靠的关闭TCP连接

在主动关闭方发送的最后一个 `ack(fin)` ，有可能丢失，这时被动方会重新发 fin, 如果这时主动方处于 `CLOSED` 状态 ，就会响应 rst 而不是 ack。所以 主动方要处于 `TIME_WAIT` 状态，而不能是 `CLOSED` 。

`TIME_WAIT` 并不会占用很大资源的，除非受到攻击。

还有，如果一方 `send` 或 `recv` 超时，就会直接进入 `CLOSED` 状态

如何合理设置`apache httpd`的最大连接数？

手头有一个网站在线人数增多，访问时很慢。初步认为是服务器资源不足了，但经反复测试，一旦连接上，不断点击同一个页面上不同的链接，都能迅速打开，这种 现象就是说明apache最大连接数已经满了，新的访客只能排队等待有空闲的链接，而如果一旦连接上，在keeyalive 的存活时间内（KeepAliveTimeout，默认5秒）都不用重新打开连接，因此解决的方法就是加大apache的最大连接数。