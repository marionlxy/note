## nginx监控

### 监控原理

### 启用nginx status配置   预编译的时候 添加模块 stub_status

./configure --prefix=/usr/local/nginx --user=nginx --group=nginx  --with-http_stub_status_module

在默认主机里面加上location或者你希望能访问到的主机里面。

```shell
server {
    listen  *:80 default_server;
    server_name _;
    location /ngx_status
    {
        stub_status on;
        access_log off;
        #allow 127.0.0.1;
        #deny all;
    }
}
```

### 打开status页面测试数据

```shell
curl -s http://127.0.0.1/ngx_status
Active connections: 11921
server accepts handled requests
 11989 11989 11991
Reading: 0 Writing: 7 Waiting: 42
```

### nginx status参数详解（面试可能问）

active connections – 活跃的连接数量
server accepts handled requests — 总共处理了11989个连接 , 成功创建11989次握手, 总共处理了11991个请求
reading — 读取客户端的连接数.
writing — 响应数据到客户端的数量
waiting — 开启 keep-alive 的情况下,这个值等于 active – (reading+writing), 意思就是 Nginx 已经处理完正在等候下一次请求指令的驻留连接.

### 具体实施

1. 在zabbix agent 添加自定义监控项
2. nginx.conf

```shell
[root@djangoweb1 zabbix_agentd.d]# cat nginx.conf
UserParameter=nginx.status[*],/etc/zabbix/zabbix_agentd.d/nginx.sh $1
```

1. 创建收集数据脚本
2. nginx.sh      /etc/zabbix/zabbix_agentd.d/nginx.sh  路径下

```shell
HOST="localhost"
PORT="80"
stub_status=nginx_status

function check() {
	if [ -f /sbin/pidof ]; then
	   /sbin/pidof nginx | wc -w
	else
	   ps ax | grep -v "grep" | grep -c "nginx:"
	fi
}

function active() {
	/usr/bin/curl -s "http://$HOST:$PORT/${stub_status}/" 2>/dev/null| grep 'Active' | awk '{print $NF}'
}
function accepts() {
	/usr/bin/curl -s "http://$HOST:$PORT/${stub_status}/" 2>/dev/null| awk NR==3 | awk '{print $1}'
}
function handled() {
	/usr/bin/curl -s "http://$HOST:$PORT/${stub_status}/" 2>/dev/null| awk NR==3 | awk '{print $2}'
}
function requests() {
	/usr/bin/curl -s "http://$HOST:$PORT/${stub_status}/" 2>/dev/null| awk NR==3 | awk '{print $3}'
}
function reading() {
	/usr/bin/curl -s "http://$HOST:$PORT/${stub_status}/" 2>/dev/null| grep 'Reading' | awk '{print $2}'
}
function writing() {
	/usr/bin/curl -s "http://$HOST:$PORT/${stub_status}/" 2>/dev/null| grep 'Writing' | awk '{print $4}'
}
function waiting() {
	/usr/bin/curl -s "http://$HOST:$PORT/${stub_status}/" 2>/dev/null| grep 'Waiting' | awk '{print $6}'
}

case "$1" in
	check)
		check
		;;
	active)
		active
		;;
	accepts)
		accepts
		;;
	handled)
		handled
		;;
	requests)
		requests
		;;
	reading)
		reading
		;;
	writing)
		writing
		;;
	waiting)
		waiting
		;;

	*)
		echo $"Usage $0 {check|active|accepts|handled|requests|reading|writing|waiting}"
		exit
esac
```

1. 重启zabbix agent

```shell
service zabbix-agent restart
```

**如何出现问题，请检查配置文件、查看日志**

1. 检查测试

> 在 zabbix-server端进行测试验证

```shell
zabbix_get -s zabbix_agent_ip -p 10050 -k "nginx.status[active]"
```

1. 创建zabbix web端监控



![img](.\图片\nginx-01.png)





![img](.\图片\nginx-02.png)





![img](.\图片\nginx-03.png)



## grafana



![img](.\图片\nginx-04.png)





![img](.\图片\nginx-05.png)



![img](.\图片\nginx-06.png)



![img](.\图片\nginx-07.png)



![img](.\图片\nginx-08.png)



![img](.\图片\nginx-09.png)



![img](.\图片\nginx-10.png)



### 效果展示



![img](.\图片\nginx-11.png)



![img](.\图片\nginx-12.png)



### grafana 添加数据源



![img](.\图片\nginx-13.png)





![img](.\图片\nginx-14.png)





![img](.\图片\nginx-15.png)



- zabbix 数据源



![img](.\图片\nginx-16.png)





![img](.\图片\nginx-17.png)