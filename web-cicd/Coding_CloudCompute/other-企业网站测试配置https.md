## 企业网站测试配置https

-Author: bavdu

-Mail: bavduer@163.com

-Github: https://github.com/bavdu

---



**/* 快速准备网站架构 */**

Nginx:192.168.13.20

```shell
$ sudo vim /etc/yum.repos.d/nginx.repo
[nginx]
name=nginx repo
baseurl=https://nginx.org/packages/centos/7/$basearch
enabled=1
gpgcheck=0

$ sudo yum -y install epel-release
$ sudo yum -y install nginx
$ id nginx
uid=998(nginx) gid=996(nginx) 组=996(nginx)
```

MariDB:192.168.13.21

```shell
$ sudo yum -y install mariadb-server mariadb
$ sudo systemctl start mariadb
$ sudo systemctl enable mariadb
$ sudo mysqladmin -uroot -p password "(QianFeng..1012)"

$ sudo mysql -uroot -p'(QianFeng..1012)'
[MariaDB none]> create database iterm_name;
[MariaDB none]> grant all privileges on iterm_name to 'nginx'@'192.168.13.%' identified by "(QianFeng..1012)";
```

PHP & NFS: 192.168.13.22

```shell
$ sudo yum -y install epel-release
$ sudo yum -y install nfs-utils php php-mbstring php-mcrypt php-gd \
php-mysql php-devel php-xml php-fpm

$ sudo vim /etc/exports
/usr/share/nginx/html		192.168.13.0/24(rw,sync)

$ sudo groupadd -g 996 nginx
$ sudo useradd -u 998 -g nginx -M -s /sbin/nologin nginx

$ sudo vim /etc/php-fpm.d/www.conf
listen = 192.168.13.22:9000
listen.allowed_clients = 192.168.13.20
user = nginx
group = nginx

$ sudo systemctl start nfs php-fpm
$ sudo systemctl enable nfs php-fpm
```



**/* 生成https证书 */**

```shell
Use root User Manager:

$ yum -y install openssl openssl-devel

##自签发TLS证书
$ openssl req \
    -newkey rsa:4096 -nodes -sha256 -keyout ca.key \
    -x509 -days 365 -out ca.crt
Country Name (2 letter code) [XX]:CN
State or Province Name (full name) []:BJ
Locality Name (eg, city) [Default City]:BJ
Organization Name (eg, company) [Default Company Ltd]:qianfeng
Organizational Unit Name (eg, section) []:cloud
Common Name (eg, your name or your server's hostname) []:www.qfcc.com
Email Address []:bavduer@163.com


$ openssl req \
    -newkey rsa:4096 -nodes -sha256 -keyout qfcc.com.key \
    -out qfcc.com.csr
Country Name (2 letter code) [XX]:CN
State or Province Name (full name) []:BJ
Locality Name (eg, city) [Default City]:BJ
Organization Name (eg, company) [Default Company Ltd]:qianfeng
Organizational Unit Name (eg, section) []:cloud
Common Name (eg, your name or your server's hostname) []:www.qfcc.com
Email Address []:bavduer@163.com

Please enter the following 'extra' attributes
to be sent with your certificate request
A challenge password []:
An optional company name []:

$ openssl x509 -req -days 365 -in qfcc.com.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out qfcc.com.crt
```



**/* 配置nginx https加密vhost**

Nginx:192.168.13.20

```shell
$ sudo vim /etc/nginx/conf.d/jump.conf
server {
    listen 80;
    server_name www.qfcc.com;
    
    location = / {
        rewrite ^(.*) https://www.qfcc.com/$1 permanent;
    }
    
    location / {
        rewrite ^(.*) https://www.qfcc.com/$1 permanent;
    }
}

$ sudo vim /etc/nginx/conf.d/qfcc.conf
server {
    listen 443;
    server_name www.qfcc.com;
    
    ssl on;
	  ssl_certificate /etc/nginx/ssl/qfcc.com.crt;
	  ssl_certificate_key /etc/nginx/ssl/qfcc.com.key;
	  ssl_session_timeout 5m;
	  ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
	  ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:HIGH:!aNULL:!MD5:!RC4:!DHE;
	  ssl_prefer_server_ciphers on;
    
    location / {
        root	/usr/share/nginx/html;
        index	index.php index.html index.htm;
    }
    
    location ~ \.php$ {
        root			/usr/share/nginx/html;
        fastcgi_pass	192.168.13.22:9000;
        fastcgi_index	index.php;
        fastcgi_param	SCRIPT_FILENAME	$document_root$fastcgi_script_name;
        include			fastcgi_params;
    }
}
```

访问测试即可