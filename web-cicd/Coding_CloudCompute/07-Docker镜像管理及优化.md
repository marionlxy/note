## Docker镜像管理及优化

-Author: bavdu

-Mail: bavduer@163.com

-Github: https://github.com/bavdu

---



镜像是部署应用的基石, 前期会花费不少时间来制作镜像和管理, 这块是重点, 因此我们进一步熟悉掌握.



**/* 镜像是什么？*/**

- 一个分层存储文件: 优点-易于扩展、优化内存及存储空间
- 一个软件的环境
- 一个镜像可以创建N个容器
- 一种标准化的交付



**/* 镜像工作原理 */**

镜像不是一个单一的文件, 而是有多层构成, 可以通过docker history \<ID/NAME\>查看镜像中各层内容及大小, 每层对应着Dockerfile中的一个指令, Docker镜像默认存储在/var/lib/docker/\<storage-driver\>如下:

```shell
[root@docker ~]# docker history nginx
IMAGE          CREATED       CREATED BY                                      SIZE  COMMENT
be1f31be9a87   8 days ago    /bin/sh -c #(nop)  CMD ["nginx" "-g" "daemon…   0B
<missing>      8 days ago    /bin/sh -c #(nop)  STOPSIGNAL [SIGTERM]         0B
<missing>      8 days ago    /bin/sh -c #(nop)  EXPOSE 80/tcp                0B
<missing>      8 days ago    /bin/sh -c ln -sf /dev/stdout /var/log/nginx…   22B
<missing>      8 days ago    /bin/sh -c set -x  && apt-get update  && apt…   53.8MB
<missing>      8 days ago    /bin/sh -c #(nop)  ENV NJS_VERSION=1.15.5.0.…   0B
<missing>      8 days ago    /bin/sh -c #(nop)  ENV NGINX_VERSION=1.15.5-…   0B
<missing>      5 weeks ago   /bin/sh -c #(nop)  LABEL maintainer=NGINX Do…   0B
<missing>      5 weeks ago   /bin/sh -c #(nop)  CMD ["bash"]                 0B
<missing>      5 weeks ago   /bin/sh -c #(nop) ADD file:e6ca98733431f75e9…   55.3MB
[root@docker ~]#
```

容器其实是在镜像的最上层加了一个读写层, 在运行的容器中更改文件时, 会先从镜像中复制目标文件到容器自己的文件系统中, 再在读写层进行修改, 但是如果容器被删除了数据也随之删除。所以无论多少个容器都是共享一个镜像的, 所做的写操作都是从镜像中复制过来的, 并不会修改镜像中的源文件, 这种方式提高磁盘的利用率.

如果想持久保存修改, 可以通过`docker commit`将容器保存成一个镜像



**/* 镜像管理常用指令 */**

- pull-拉取镜像到本地

  ```shell
  Usage:	docker image pull [OPTIONS] NAME[:TAG|@DIGEST]
  $ docker image pull nginx
  ```

- push-上传镜像到仓库

- ```shell
  Usage:	docker image push [OPTIONS] NAME[:TAG]
  $ docker image push nginx:last
  ```

- save-保存一个或多个镜像到一个tar归档文件

- ```shell
  Usage:	docker image save [OPTIONS] IMAGE [IMAGE...]
  $ docker image save name/id > name.tar
  ```

- load-从tar归档或标准输入导入镜像

- ```shell
  Usage:	docker image load [OPTIONS]
  $ docker image load -i name.tar
  $ docker image load < name.tar
  ```

- import-导入tag归档的容器文件系统创建镜像

- ```shell
  Usage:	docker image import [OPTIONS] file|URL|- [REPOSITORY[:TAG]]
  $ docker image import name.tar name:tag
  ```

注: save和load命令用于将一个镜像从一台Docker主机导入到另一台Docker主机



**/* Dockerfile管理 */**

官方仓库虽然有数十万的免费镜像, 但无法满足公司业务需求, 这就需要我们自己构建镜像, Docker可以通过Dockerfile自动构建镜像, Dockerfile是一个文本文档, 其中包含了用户在命令行上所有命令来组合镜像, 使用docker build自动构建。docker通过从一个dockerfile包含所有命令的文本文件中读取指令来构建镜像, 这些command按顺序构建给定镜像. 一个Dockerfile遵循特定的格式和指令集.

官方文档: https://docs.docker.com/engine/reference/builder

| 指令       | 描述                                          |
| :--------- | :-------------------------------------------- |
| FROM       | 构建新镜像是基于那个镜像                      |
| MAINTAINER | 镜像维护者姓名或邮箱地址                      |
| RUN        | 构建镜像时运行的Shell命令                     |
| COPY       | 拷贝文件或目录到镜像中                        |
| ENV        | 设置环境变量                                  |
| USER       | 为RUN、CMD、ENTRYPOINT执行命令指定运行用户    |
| EXPOSE     | 声明容器运行的服务端口                        |
| WORKDIR    | 为RUN、CMD、ENTRYPOINT、COPY和ADD设置工作目录 |
| ENTRYPOINT | 运行容器时执行, 如果有多个CMD指令最后一个生效 |
| CMD        | 运行容器时执行, 如果有多个CMD指令最后一个生效 |

**/* docker build */**

docker build命令是根据上下文自动构建镜像. 构建上下文时指定PATH或文件集URL, PATH是本地文件系统上的目录, URL是一个git仓库地址

建议空目录作为上下文, 并将Dockerfile保存在该目录中, 目录中仅包含构建Dockerfile所需的文件

```shell
Usage:	docker image build [OPTIONS] PATH | URL | - [flags]
$ docker build .
$ docker build -t shykes/myapp .
$ docker build -t shykes/myapp -f /path/Dockerfile /path
$ docker build -t shykes/myapp http://www.example.com/Dockerfile
```



**/* 项目一: 构建PHP网站镜像并部署 */**

准备一个基础镜像, 再构建项目镜像.

部署过PHP网站的同学知道, PHP是一个动态程序, 负责解析的是叫PHP-FPM的服务, 而这个服务不支持静态页面处理, 一般结合Nginx解决这个问题, Nginx本身是一个静态Web服务器, 并不支持解析PHP程序, 但它支持了FastCGI接口来调用动态服务来解析PHP程序

![Screenshot_20181011_114713](T/Screenshot_20181011_114713.jpg)

当客户端请求PHP页面时, Nginx通过fastcgi接口转发给本地9000端口的PHP-FPM子进程处理, 处理完成后返回给Nginx, 所以秉承着一个容器一个服务的原则, 我们要创建两个基础镜像 Nginx和PHP

```shell
##创建项目目录
[root@docker lnmp]# tree
.
├── base
│   ├── Dockerfile-nginx
│   └── Dockerfile-php
└── project
    ├── Dockerfile-nginx
    ├── Dockerfile-php
    └── nginx.conf

2 directories, 5 files
```

```shell
##构建Nginx’s Dockerfile
[root@docker lnmp]# vim base/Dockerfile-nginx
FROM centos:latest
MAINTAINER bavdu<bavduer@163.com>
RUN yum -y install gcc gcc-c++ make \
    openssl-devel zlib-devel pcre-devel gd-devel libxslt-devel \
    iproute net-tools telnet wget curl && \
    yum clean all && \
    rm -rf /var/cache/yum/*
RUN wget http://nginx.org/download/nginx-1.14.0.tar.gz && \
    tar xf nginx-1.14.0.tar.gz && \
    cd nginx-1.14.0 && \
    ./configure --prefix=/usr/local/nginx \
    --with-http_ssl_module \
    --with-http_v2_module \
    --with-http_realip_module \
    --with-http_image_filter_module \
    --with-http_gunzip_module \
    --with-http_gzip_static_module \
    --with-http_secure_link_module \
    --with-http_stub_status_module \
    --with-stream \
    --with-stream_ssl_module && \
    make && make install && \
    mkdir -p /usr/local/nginx/conf/vhost && \
    rm -rf /usr/local/nginx/html/* && \
    echo "ok" >>/usr/local/nginx/html/index.html && \
    cd / && rm -rf nginx-1.14.0*
COPY nginx.conf /usr/local/nginx/conf/nginx.conf
ENV PATH $PATH:/usr/local/nginx/sbin
WORKDIR /usr/local/nginx
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

##构建PHP’s Dockerfile
[root@docker lnmp]# vim base/Dockerfile-php
FROM centos:latest
MAINTAINER bavdu<bavduer@163.com>
RUN yum -y install epel-release && \
    yum -y install gcc gcc-c++ make \
    gd-devel libxml2-devel libcurl-devel libjpeg-devel libpng-devel \
    openssl-devel libmcrypt-devel libxslt-devel libtidy-devel \
    autoconf iproute net-tools telnet wget curl && \
    yum clean all && \
    rm -rf /var/cache/yum/*
RUN wget http://docs.php.net/distributions/php-5.6.36.tar.gz && \
    tar xf php-5.6.36.tar.gz && \
    cd php-5.6.36 && \
    ./configure --prefix=/usr/local/php \
    --with-config-file-path=/usr/local/php/etc \
    --with-config-file-scan-dir=/usr/local/php/etc/php.d \
    --enable-fpm --enable-opcache --enable-statice=no \
    --with-mysql --with-mysqli --with-pdo-mysql \
    --enable-phar --enable-pear --enable-session \
    --enable-sysvshm --with-tidy --with-openssl \
    --with-zlib --with-curl --with-gd --enable-bcmath \
    --with-jpeg-dir --with-png-dir --with-freetype-dir \
    --with-iconv --enable-posix --enable-zip \
    --enable-mbstring --with-mhash --with-mcrypt --enable-hash \
    --enable-xml --enable-libxml --enable-debug=no && \
    make && make install && \
    cp php.ini-production /usr/local/php/etc/php.ini && \
    cp sapi/fpm/php-fpm.conf /usr/local/php/etc/php-fpm.conf && \
    sed -i "90a \daemonize = no" /usr/local/php/etc/php-fpm.conf && \
    mkdir /usr/local/php/log && \
    cd / && rm -rf php* && mkdir -p /usr/local/nginx/html
ENV PATH $PATH:/usr/local/php/sbin
WORKDIR /usr/local/php
EXPOSE 9000
CMD ["php-fpm"]
```

```shell
##开始构建镜像
$ cd base
$ docker build -t nginx14 -f Dockerfile-nginx .
$ docker build -t php56 -f Dockerfile-php .
```

```shell
##创建容器
$ docker network create lnmp
$ mkdir -p /webroot/lnmp

$ docker container run -d --name lnmp-nginx --net lnmp -p 80:80 \
--mount type=bind,src=/webroot/lnmp,dst=/usr/local/nginx/html nginx14

$ docker container run -d --name lnmp-php --net container:lnmp-nginx \
--mount type=bind,src=/webroot/lnmp,dst=/usr/local/nginx/html php56

$ vim /webroot/lnmp/index.php
<?php phpinfo(); ?>
```

