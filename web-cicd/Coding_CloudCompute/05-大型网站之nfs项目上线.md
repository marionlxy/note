## 大型网站 之 NFS项目上线

-Author：bavdu

-Mail：bavduer@163.com

-GitHub：https://github.com/bavdu

---

**/* NFS简介 */**

NFS（Network File System）即网络文件系统, 是FreeBSD支持的文件系统中的一种, 它允许网络中的计算机之间通过TCP/IP网络共享资源. 在NFS的应用中, 本地NFS的客户端应用可以透明地读写位于远端NFS服务器上的文件,就像访问本地文件一样



**/* 环境准备 */**

```shell
[root@example02 ~]# systemctl stop firewalld && systemctl disable firewalld
[root@example02 ~]# setenforce 0
[root@example02 ~]# getenforce
Permissive

[root@example02 ~]# vim /etc/yum.repos.d/nignx.repo
[nginx]
name=nginx repo
baseurl=http://nginx.org/packages/centos/7/$basearch
gpgcheck=0
enabled=1

[root@example02 ~]# yum -y install nginx nfs-utils
[root@example02 ~]# vim /etc/nignx/conf.d/default.conf
server {
    listen 80;
    server_name localhost;
    
    location / {
        root	/usr/share/nginx/html;
        index	index.php index.html index.htm;
    }
    
    location ~ \.php$ {
        root           /usr/share/nginx/html;
        fastcgi_pass   192.168.13.31:9000;
        fastcgi_index  index.php;
        fastcgi_param  SCRIPT_FILENAME  $document_root$fastcgi_script_name;
        include        fastcgi_params;
    }
}

[root@example02 ~]# systemctl restart nginx
[root@example02 ~]# id nginx
uid=998 gid=996 group=nginx
[root@example02 ~]# vim /etc/fstab
192.168.13.31:/usr/share/nginx/html	/usr/share/nginx/html	nfs	defaults	0 0
```



**/* 构建简易NFS网络共享 */**

```shell
[root@example01 ~]# yum -y install utils
[root@example01 ~]# vim /etc/exports
/usr/share/nginx/html	192.168.13.0/24(rw,sync)
[root@example01 ~]# systemctl start nfs

[root@example01 ~]# yum -y install php php-mbstring php-mcrypt php-devel php-gd php-fpm php-mysql php-xml
[root@example01 ~]# sytemctl start php-fpm
[root@example01 ~]# groupadd -g 996 nginx
[root@example01 ~]# useradd -u 998 -g 996 -M -s /sbin/nologin nginx
[root@example01 ~]# vim /etc/php-fpm.d/www.conf
listen=192.168.13.31:9000
listen.allowed.client=192.168.13.32,192.168.13.33
user=nginx
group=nginx
[root@example01 ~]# systemctl restart php-fpm
[root@example01 ~]# vim /usr/share/nginx/html/index.php
<?php phpinfo(); ?>
```



**/* 测试项目上线 */**

```shell
[root@example02 ~]# mount -a
[root@example03 ~]# mount -a

浏览器访问测试！～
```

