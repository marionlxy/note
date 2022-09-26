## Nginx负载均衡配置SSL

本实验为配置nginx负载均衡及实现https安全🔐访问,本实验为详细版,**<u>实验环境为CentOS 7.5</u>** 

其中涉及到:

- nignx、tomcat部署
- nginx webserver、tomcat webserver配置
- nginx的负载均衡配置
- CA证书生成
- 测试负载均衡

---

**<u>Nginx Webserver Deploy</u>**

- 准备安装环境

```shell
$ vim /etc/yum.repo.d/nginx.repo
[nginx]
name=nginx repo
baseurl=http://nginx.org/packages/centos/7/$basearch/
gpgcheck=0
enabled=1
```

- 安装nginx webserver、备份默认虚拟主机

```shell
$ yum -y install nginx
$ mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf.bak
```

- 配置webserver虚拟主机`$ vim /etc/nginx/conf.d/web01.conf`

```shell
server {
    listen       10086;
    server_name  web01.server.vip;

    charset koi8-r;
    access_log  /var/log/nginx/host.access.log  main;

    location / {
        root   /usr/share/nginx/html;
        index  index.html index.htm;
    }

    error_page  404              /404.html;

    # redirect server error pages to the static page /50x.html
    #
    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }
}
```

- 测试webserver

```shell
$ sudo echo "This is Nginx Webserver" > /usr/share/nginx/html/index.html
$ curl -I http://10.0.30.213:10086
HTTP/1.1 200 OK
Server: nginx/1.14.0
Date: Fri, 25 May 2018 11:12:13 GMT
Content-Type: text/html; charset=koi8-r
Content-Length: 24
Last-Modified: Fri, 25 May 2018 11:09:11 GMT
Connection: keep-alive
ETag: "5b07eed7-18"
Accept-Ranges: bytes
```



**<u>Tomcat Webserver Deploy</u>**

- 准备安装环境

```shell
# 在官网自行下载jdk源码包
$ tar xf jdk-10.0.1_linux-x64_bin.tar.gz -C /usr/
$ mv /usr/jdk-10.0.1 /usr/java
$ vim /etc/profile
## JAVA PATH Date:2018-5-25 start##
export JAVA_HOME=/usr/java
export JAVA_BIN=$JAVA_HOME/bin
export JAVA_LIB=$JAVA_HOME/lib
export CLASSPATH=.:$JAVA_LIB/tools.jar:$JAVA_LIB/dt.jar
export PATH=$JAVA_BIN:$PATH
## JAVA PATH Date:2018-5-25 end##
$ source /etc/profile
```

- 下载tomcat源码包

```shell
访问官网https://tomcat.apache.org/download-90.cgi
$ wget http://mirrors.tuna.tsinghua.edu.cn/apache/tomcat/tomcat-9/v9.0.8/bin/apache-tomcat-9.0.8.tar.gz
$ tar xf apache-tomcat-9.0.8.tar.gz
$ cp -rf apache-tomcat-9.0.8/* /usr/local/tomcat9/
$ vim /etc/profile
$ source /etc/profile

$ cd /usr/local/tomcat9/
$ vim conf/server.xml
<Connector port="8080" protocol="HTTP/1.1" connectionTimeout="20000" 
redirectPort="8443" />
将其中的 8080 改成 HTTP 协议的默认端口 80，改后的代码如下：
<Connector port="80" protocol="HTTP/1.1" connectionTimeout="20000" 
redirectPort="8443" />

$ vim conf/tomcat-users.xml
在</tomcat-users>上方添加<user username="tomcat" password="tomcat" roles="manager-gui"/>

$ vim bin/catalina.sh
# idea - jdk10.0.1 config start - 2018-05-25
export JAVA_HOME=/usr/java
# idea - jdk-10.0.1 config end - 2018-05-25

$ ./bin/startup.sh
Using CATALINA_BASE:   /usr/local/tomcat9
Using CATALINA_HOME:   /usr/local/tomcat9
Using CATALINA_TMPDIR: /usr/local/tomcat9/temp
Using JRE_HOME:        /jre
Using CLASSPATH:       /usr/local/tomcat9/bin/bootstrap.jar:/usr/local/tomcat9/bin/tomcat-juli.jar
Tomcat started.

浏览器访问http://10.0.30.212看到小猫代表成功.
```

- 测试webserver

```shell
修改server.xml文件中的网页目录为/usr/share/tomcat/
$ echo "This is Tomcat webserver" > /usr/share/tomcat/docs/index.html
重新启动tomcat再次访问首页
```



**<u>Nginx Upstream Deploy</u>**

- 下载nginx源码包,并安装

```shell
# 采用源码编译安装,相关参数请参阅 ·http://nginx.org/en/docs/configure.html
$ wget http://nginx.org/download/nginx-1.14.0.tar.gz
$ tar xf nginx-1.14.0.tar.gz
$ cd nginx-1.14.0

$ yum -y install pcre pcre-devel openssl openssl-devel zlib zlib-devel

$ ./configure --prefix=/usr/local/nginx \
--sbin-path=/usr/bin/nginx \
--http-log-path=/var/log/nginx/access.log \
--error-log-path=/var/log/nginx/error.log \
--user=nginx \
--group=nginx \
--with-http_ssl_module \
--with-pcre

$ make && make install
```

- 配置负载均衡

```nginx
$ vim /usr/local/nginx/conf/nginx.conf
user  nginx;
worker_processes  auto;
error_log  /var/log/nginx/error.log;

events {
    use epoll;
    worker_connections  1024;
}


http {
    include       mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    keepalive_timeout  65;

    gzip  on;
    gzip_min_length 1K;
    gzip_buffers 4 8K;
    gzip_comp_level 5;
    gzip_types text/plain text/css text/javascript application/x-javascript;


    upstream webservers {
        server 10.0.30.212:80 weight 2;
        server 10.0.30.213:10086 weight 1;
    }

    include /usr/local/nginx/conf.d/*.conf;
}

$ nginx -s reload
```

- 配置server模块

```nginx
$ vim /usr/local/nginx/conf.d/upstream.conf
server {
        listen  80;
        listen  443;
        server_name     bavdu.com www.bavdu.com;
        if ($scheme != https) {
                rewrite ^(.*)$  https://$host$1 permanent;
        }

        error_page      404             /nginx_upstream/error_page/404.html;
        error_page      500 502 503 504 /nginx_upstream/error_page/50x.html;

        location ^~ /nginx_upstream/ {
                root    /usr/local/nginx;
                index   index.html index.htm;

                add_header      X-Header-Name value;
                chunked_transfer_encoding on;
                expires 1d;
                gzip on;
        }

        location / {
                proxy_pass      http://webservers;
                proxy_set_header Host $host;
                proxy_set_header Connection close;
                proxy_connect_timeout 100ms;
                expires 30d;
        }

        # https configure.
        ssl_certificate      /usr/local/nginx/nginx_upstream/ssl/nginx.crt;
        ssl_certificate_key  /usr/local/nginx/nginx_upstream/ssl/nginx.key;
        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
        ssl_ciphers   HIGH:!aNULL:!MD5;
}

$ mkdir -p /usr/local/nginx/nginx_upstream/error_page
$ mkdir -p /usr/local/nginx/nginx_upstream/ssl
```



**<u>Config Public Key On Server</u>**

- 生成CA私钥

```shell
[root@localhost ~]# ls /etc/pki/
CA  ca-trust  java  nssdb  nss-legacy  rpm-gpg  rsyslog  tls
[root@localhost ~]# ls /etc/pki/tls
cert.pem  certs  misc  openssl.cnf  private
[root@localhost ~]# vim /etc/pki/tls/openssl.cnf 
[root@localhost ~]# cd /etc/pki/CA/
[root@localhost CA]# ls
certs  crl  newcerts  private
[root@localhost CA]# > index.txt 
[root@localhost CA]# > serial 
[root@localhost CA]# echo 01 > serial 
[root@localhost CA]# ls
certs  crl  index.txt  newcerts  private  serial
[root@localhost CA]# ls private/
[root@localhost CA]# (umask 077; openssl genrsa -out private/ca.key 2048)
Generating RSA private key, 2048 bit long modulus
.......................................................+++
..................+++
e is 65537 (0x10001)
```

- 生成CA证书

```shell
[root@localhost CA]# openssl req -new -x509 -key private/ca.key -out cacert.crt -days 3650
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
Country Name (2 letter code) [XX]: CN
State or Province Name (full name) []:BJ
Locality Name (eg, city) [Default City]: BJ
Organization Name (eg, company) [Default Company Ltd]: bavduer
Organizational Unit Name (eg, section) []: bavdu
Common Name (eg, your name or your server's hostname) []: ca.bavdu.com
Email Address []:
```

- 生成NGINX 的私钥、申请文件、CA颁发证书

```shell
[root@localhost CA]# 
[root@localhost CA]# ls
cacert.crt  certs  crl  index.txt  newcerts  private  serial
[root@localhost CA]# cd
[root@localhost ~]# 
[root@localhost ~]# cd /etc/nginx/
[root@localhost nginx]# mkdir ssl
[root@localhost nginx]# cd ssl/
[root@localhost ssl]# (umask 077; openssl genrsa -out nginx.key 2048)
Generating RSA private key, 2048 bit long modulus
............+++
.................................................+++
e is 65537 (0x10001)
[root@localhost ssl]# ls
nginx.key
[root@localhost ssl]# openssl req -new -key nginx.key -out nginx.csr 
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,

## If you enter '.', the field will be left blank.

Country Name (2 letter code) [XX]:CN
State or Province Name (full name) []:BJ
Locality Name (eg, city) [Default City]:BJ
Organization Name (eg, company) [Default Company Ltd]:bavduer
Organizational Unit Name (eg, section) []:bavdu
Common Name (eg, your name or your server's hostname) []:www.bavdu.com
Email Address []:

Please enter the following 'extra' attributes
to be sent with your certificate request
A challenge password []:
An optional company name []:
[root@localhost ssl]# 
[root@localhost ssl]# ls
nginx.csr  nginx.key
[root@localhost ssl]# cp nginx.csr /etc/pki/CA/
[root@localhost ssl]# cd /etc/pki/CA/
[root@localhost CA]# ls
cacert.crt  certs  crl  index.txt  newcerts  nginx.csr  private  serial
[root@localhost CA]# openssl ca -in nginx.csr -out nginx.crt -days 365
Using configuration from /etc/pki/tls/openssl.cnf
Check that the request matches the signature
Signature ok
Certificate Details:
        Serial Number: 1 (0x1)
        Validity
            Not Before: Mar 29 15:59:54 2018 GMT
            Not After : Mar 29 15:59:54 2019 GMT
        Subject:
            countryName               = CN
            stateOrProvinceName       = BJ
            organizationName          = bavduer
            organizationalUnitName    = bavdu
            commonName                = www.bavdu.com
        X509v3 extensions:
            X509v3 Basic Constraints: 
                CA:FALSE
            Netscape Comment: 
                OpenSSL Generated Certificate
            X509v3 Subject Key Identifier: 
                48:B2:9C:A4:B6:EE:40:79:6B:70:E5:34:BD:A9:AC:73:27:7E:7B:27
            X509v3 Authority Key Identifier: 
                keyid:70:78:6D:C8:A8:71:9F:61:CB:2A:48:92:55:AD:8C:77:58:C0:8D:5C

Certificate is to be certified until Mar 29 15:59:54 2019 GMT (365 days)
Sign the certificate? [y/n]:y

1 out of 1 certificate requests certified, commit? [y/n]y
Write out database with 1 new entries
Data Base Updated
[root@localhost CA]# 
```



*打开浏览器访问 http://www.bavdu.com是否能够实现负载均衡*