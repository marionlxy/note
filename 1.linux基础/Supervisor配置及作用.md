## Supervisor配置及作用

Author：bavdu

Email：bavduer@163.com

---

**原理解析**

supervisor管理进程，是通过fork/exec的方式将这些被管理的进程当作supervisor的子进程来启动，所以我们只需要将要管理进程的可执行文件的路径添加到supervisor的配置文件中就好了。此时被管理进程被视为supervisor的子进程，若该子进程异常中断，则父进程可以准确的获取子进程异常中断的信息，通过在配置文件中设置autostart=ture，可以实现对异常中断的子进程的自动重启



**部署过程**

1. 安装supervisor

```shell
$ sudo pip install supervisor
```

2. 查看配置文件内容

```shell
$ sudo echo_supervisor_conf
$ sudo vim /etc/supervisord.conf

; Sample supervisor config file.

[unix_http_server]
file=/var/run/supervisor/supervisor.sock   ; (the path to the socket file)
;chmod=0700                 ; sockef file mode (default 0700)
;chown=nobody:nogroup       ; socket file uid:gid owner
;username=user              ; (default is no username (open server))
;password=123               ; (default is no password (open server))

;[inet_http_server]         ; inet (TCP) server disabled by default
;port=127.0.0.1:9001        ; (ip_address:port specifier, *:port for all iface)
;username=user              ; (default is no username (open server))
;password=123               ; (default is no password (open server))

[supervisord]
logfile=/var/log/supervisor/supervisord.log  
							; (main log file;default $CWD/supervisord.log)
logfile_maxbytes=50MB       ; (max main logfile bytes b4 rotation;default 50MB)
logfile_backups=10          ; (num of main logfile rotation backups;default 10)
loglevel=info               ; (log level;default info; others: debug,warn,trace)
pidfile=/var/run/supervisord.pid ; (supervisord pidfile;default supervisord.pid)
nodaemon=false              ; (start in foreground if true;default false)
minfds=1024                 ; (min. avail startup file descriptors;default 1024)
minprocs=200                ; (min. avail process descriptors;default 200)
;umask=022                  ; (process file creation umask;default 022)
;user=chrism                 ; (default is current user, required if root)
;identifier=supervisor       ; (supervisord identifier, default is 'supervisor')
;directory=/tmp              ; (default is not to cd during start)
;nocleanup=true              ; (don't clean up tempfiles at start;default false)
;childlogdir=/tmp            ; ('AUTO' child log dir, default $TEMP)
;environment=KEY=value       ; (key value pairs to add to environment)
;strip_ansi=false            ; (strip ansi escape codes in logs; def. false)
......
```

- \[unix_http_server\]这部分设置HTTP服务器监听的UNIX domain socket
  - file: 指向UNIX domain socket，即file=/var/run/supervisor.sock
  - chmod：启动时改变supervisor.sock的权限
- \[supervisord\] 与supervisord有关的全局配置需要在这部分设置
  - logfile: 指向记录supervisord进程的log文件
  - pidfile：pidfile保存子进程的路径
  - childlogdir：子进程log目录设为AUTO的log目录
- \[supervisorctl\]
  - serverurl：进入supervisord的URL， 对于UNIX domain sockets, 应设为 unix:///absolute/path/to/file.sock
- \[include\] 如果配置文件包含该部分, 则该部分必须包含一个files键
  - files：包含一个或多个文件，这里包含了/etc/supervisor/conf.d/目录下所有的.conf文件，可以在该目录下增加我们自己的配置文件，在该配置文件中增加[program:x]部分，用来运行我们自己的程序
- \[program:x\] 配置文件必须包括至少一个program, x是program名称, 必须写上, 不能为空
  - command：包含一个命令，当这个program启动时执行
  - directroy：执行子进程时supervisord暂时切换到该目录
  - user：账户名
  - startsecs：进程从STARING状态转换到RUNNING状态program所需要保持运行的时间（单位：秒）
  - redirect_stderr：如果是true，则进程的stderr输出被发送回其stdout文件描述符上的supervisord
  - stdout_logfile：将进程stdout输出到指定文件
  - stdout_logfile_maxbytes：stdout_logfile指定日志文件最大字节数，默认为50MB，可以加KB、MB或GB等单位
  - stdout_logfile_backups：要保存的stdout_logfile备份的数量



3. 配置一个program

```shell
$ wget https://nginx.org/downloads/nginx-1.14.0.tar.gz
$ sudo yum -y install openssl-devel pcre-devel zlib-devel gcc gcc-c++
$ sudo tar xf nginx-1.14.0.tar.gz -C /opt/
$ sudo useradd nginx
$ sudo ./configure --prefix=/usr/local/nginx --user=nginx --group=nginx
$ sudo make && sudo make install

$ sudo /usr/local/nginx/sbin/nginx
访问浏览器是否能够访问到nginx欢迎页！
```

```shell
$ sudo vim /etc/supervisord.d/nginx_program.conf
;/etc/supervisord.d/nginx_program.conf

[program:nginx]

command     = /usr/local/nginx/sbin/nginx
directory   = /usr/local/nginx/sbin
user        = nginx
startsecs   = 3

redirect_stderr         = true
stdout_logfile_maxbytes = 50MB
stdout_logfile_backups  = 10
stdout_logfile          = /var/log/nginx/nginx_error.log
```



手动关闭nginx，测试supervisor