###  Ansible自动化运维工具

下载印象笔记

### Ansible自动化运维工具

### Ansible运维

#### 第1章Ansible介绍及安装

##### 1.1介绍

```
    Ansible 是一个 IT 自动化工具。它能配置系统、部署软件、编排更复杂的 IT 任务，如连续部署或零停机时间滚动更新。Ansible 用 Python 编写，尽管市面上已经有很多可供选择的配置管理解决方案（例如 Salt、Puppet、Chef等),但它们各有优劣，而Ansible的特点在于它的简洁。让 Ansible 在主流的配置管理系统中与众不同的一点便是，它并不需要你在想要配置的每个节点上安装自己的组件。同时提供的另一个优点，如果需要的话，你可以在不止一个地方控制你的整个基础架构。
```

##### 1.2工作原理

![img](http://img.liuwenqi.com/blog/2019-10-21-QQ20180304-112411%402x.png)

```
1、在ANSIBLE 管理体系中，存在"管理节点" 和 "被管理节点" 两种角色。
2、被管理节点通常被称为"资产"
3、在管理节点上，Ansible将 AdHoc 或 PlayBook 转换为Python脚本。并通过SSH将这些Python 脚本传递到
   被管理服务器上。在被管理服务器上依次执行，并实时的将结果返回给管理节点。
```

##### 1.3如何安装

![img](http://img.liuwenqi.com/blog/2019-10-21-QQ20180304-112731%402x.png)
**管理决策**

```shell
确保存在OpenSSH
确保Python 版本 >= 2.6
确保安装ansible
```

**被管理官员**

```shell
确保存在OpenSSH
确保Python 版本 >= 2.4 //若为2.4 版本，确保安装了python-samplesjson 扩展
不需要安装ansible
```

**安装Ansible**

```shell
# pip install ansible   // 确保最新版本ansible 或者 pip3 install ansible

# yum -y install ansible  // 不一定是最新版本ansible
```

**确保管理基线与被管理中断之间的SSH信任关系**

```shell
// 生成公私钥对
# ssh-keygen -t rsa
# cd ~/.ssh && ls 
id_rsa  id_rsa.pub
// 将公钥 id_rsa.pub copy 到 被管理服务器上 authorized_keys 文件中， 确保文件的权限为 0600
// managedhost 为被管理服务器，copy的过程中需要用户名及密码
# ssh-copy-id root@managedhost
```

##### 1.4快速入门

**场景假设**

```shell
管理节点:
192.168.122.130

被管理节点(资产):
192.168.122.129
192.168.122.131

且管理节点 和 被管理节点之间的节点已经打通 SSH 信任关系。
```

**场景一**

```shell
在管理节点上，确保同所有被管理节点的网络连通性。
# ansible all -i 192.168.122.129,192.168.122.131 -m ping
// 注意 -i 参数后面接的是一个列表(List)。因此当为一个被管理节点时，我们后面一定要加一个逗号(,)告知是List
# ansible all -i 192.168.122.129, -m ping
```

**场景二**

```shell
在管理节点上，确保文件/tmp/a.conf 发布到所有被管理节点
# ansible all -i 192.168.122.129,192.168.122.131 -m copy -a "src=/tmp/a.conf dest=/tmp/a.conf"
```

**参数解释**

```shell
-i  // 指定Ansible 的资产，也就是被管理服务器。
-m  // 指定要运行的模块,比如这里的 ping 模块和 copy 模块
-a  // 指定模块的参数, 这里模块 ping 没有指定参数。 模块 copy 指定了 src 和 dest 参数
all // ansible 中， 将其叫做pattern , 即匹配。我通常称它为资产选择器。
    // 就是匹配资产(-i 参数指定) 中的一部分。这里的 all 是匹配所有指定的所有资产。
    // 在资产的章节中，我们将详细阐述。
```

#### 第2章Ansible资产

```
在快速入门的场景中，我们一共管理了两台服务器。但是在实际场景中，我们要管理的服务器往往要多得多。难道依然要在Ansible 的 -i 参数后面一个个追加IP指定吗? 这显然不合乎常理。因此这一节我们主要去介绍一下Ansible的资产。Ansible 的资产分为静态资产和动态资产，下面我们将围绕这两部分分别介绍。
```

##### 1.1静态资产

```shell
顾名思义它本身是一个文本文件，一个格式类似INI的文件。默认情况下，Ansible的资产文件位于 /ect/ansible/hosts。我们这里给出一个自定义的静态资产实例，然后再具体解释其含义。
# cat inventory
1.1.1.1
2.2.2.2
3.3.3.[1:15]
test01.qfedu.com
test03.qfedu.com
test[05:09].qfedu.com

[web-servers]
192.168.1.2
192.168.1.3
192.168.1.5

[db-servers]
192.168.2.2
192.168.2.3
192.168.1.5

[all-servers]
[all-servers:children]
db-servers
web-servers
1、Ansible 的资产文件中，可以以IP地址的形式或者主机名的形式存在
2、Ansible 的资产若连续，可以使用[stat:end] 的形式去表达
3、可以将服务器按照业务场景定义成组，比如db-servers 和 web-servers
4、组和组之间可以存在继承关系，比如db-servers 和 web-servers 同时继承all-servers 组
```

**如何使用自定义资产**

```shell
// 通过 -i 参数指定自定义资产的位置即可(可以是全路径，也可以是相对路径)。
# ansible all -i inventory.ini ... // 伪指令，不可执行
```

**如何验证自定义资产**

```shell
// 假如我们刚刚定义的资产为 inventory.ini
// 列举出所有资产
# ansible all -i inventory.ini  --list-hosts

// 列举出选定资产，比如这里列举出web-servers
// 注意这里使用的了资产选择器(pattern)，我们将会在下面对他进行详细的阐述
# ansible web-servers -i inventory.ini --list-hosts

// 以上指令，若能列举出我们在资产中定义的服务器，那么你的自定义资产也就生效了。
```

##### 1.2动态资产

```shell
动态资产, -i 参数后面接的是一个可运行的脚本。脚本的结果为一个 Ansible 可理解的 JSON 格式字符串。

为什么要存在动态资产呢? 往往我们在使用 Ansible 管理服务器前，公司中有可能已经将服务器信息存储在了特定位置,比如 CMDB, 数据库等系统。
此时若我们再使用静态资产去管理服务器，势必会造成资产管理入口不统一的问题。

因此我们只能抛弃原先的静态资产，通过脚本从已存在的系统中获取要管理的节点，并按照特定的形式传给 Ansible。这样既解决了公司资产统一入口， 也解决了Ansible 的服务器管理来源。
```

**动态资产实例**

```shell
{
  "_meta": {
    "hostvars": {
      "192.168.100.10": {
        "host_var": "hoge"
      },
      "192.168.100.20": {
        "host_var": "fuga"
      }
    }
  },
  "sample-servers": {
    "hosts": [
      "192.168.100.10",
      "192.168.100.20"
    ],
    "vars": {
      "group_var": "hogefuga"
    }
  }
}
```

##### 1.3资产选择器

```
有时操作者希望只对资产中的一部分服务器进行操作，而不是资产中列举的所有服务器。此时我们该如何选择呢？
这里我们将学习 Ansible 的资产选择器 PATTERN，通过资产选择器，我们可以灵活的选择想要操作的服务器。
```

**格式**

```shell
# ansible PATTERN -i inventory -m module -a argument  // 伪代码，勿执行
```

**选择一台或者几台服务器**

```shell
# ansible 1.1.1.1 -i inventory.ini --list-hosts
# ansible test01.qfedu.com -i inventory.ini --list-hosts
# ansible 1.1.1.1,2.2.2.2 -i inventory.ini --list-hosts
```

**选择所有服务器**

```
# ansible '*' -i  inventory.ini --list-hosts
# ansible all -i inventory.ini --list-hosts
```

**选择一组服务器**

```
# ansible web-servers -i inventory.ini --list-hosts
```

**使用\*匹配**

```
# ansible 3.3.3.* -i inventory.ini --list-hosts
```

**使用逻辑匹配**

```shell
// web-servers 和 db-servers 的并集
# ansible 'web-servers:db-servers' -i inventory.ini --list-hosts
// web-servers 和 db-servers 的交集
# ansible 'web-servers:&db-servers' -i inventory.ini --list-hosts
// 在 web-servers 中， 但不在 db-servers 的服务器
# ansible 'web-servers:!db-servers' -i inventory.ini --list-hosts
```

#### 第3章Ansible Ad-Hoc

##### 3.1命令格式

```shell
我们在快速入门中执行的Ansible 命令，类似于我们的批处理命令。在Ansible 中统称为Ansible Ad-Hoc。
其命令语法格式如下:
ansible pattern [-i inventory] -m module -a argument
pattern, 资产选择器
-i , 指定资产的位置
-m , 指定本次Ansible ad-hoc 要执行的模块。可以类别成SHELL 中的命令。
-a , 模块的参数. 可以类比成SHELL 中的命令参数
```

**例**

```shell
// 快速入门的实例
# ansible all -i 192.168.122.129,192.168.122.131 -m copy -a "src=/tmp/a.conf dest=/tmp/a.conf"
```

##### 3.2模块类型

```shell
Ansible 模块分三种类型: 核心模块(core module)、附加模块(extra module)及用户自定义模块(consume module)。
核心模块是由Ansible 的官方团队提供的。
附加模块是由各个社区提供的。例如: OPENSTACK 社区、DOCKER 社区等等。
当核心模块和附加模块都无法满足你的需求时，用户可以自定义模块。

默认情况下，在安装Ansible 的时候， 核心模块和附加模块都已经安装而无需用户干预。
```

##### 3.3联机帮助

```
Ansible 的核心模块和附加模块，数量有1000+ 。这样庞大的模块数量，对于任何一个接触Ansible 的人都不可能将其完全记住、掌握使用。 因此能够顺利使用Ansible 的帮助文档，对我们来说是很有必要的。Ansible 的帮助文档，由
它本身提供的命令 ansible-doc 实现。
```

**常用帮助参数**

```shell
// 列举出所有的核心模块和附加模块
# ansible-doc -l
// 查询某个模块的使用方法
# ansible-doc modulename
// 查询某个模块的使用方法，比较简洁的信息
# ansible-doc -s modulename

// Example
# ansible-doc yum
# ansible-doc -s yum
```

##### 3.4常用模块

**命令和shell模块**

```shell
两个模块都是在远程服务器上去执行命令。但command模块是ad-hoc的默认模块,在执行ad-hoc时,若不指定模块的名字则默认使用此模块.常用参数如下:
command & shell 
- chdir       在运行命令之前，切换到此目录。
- executable  更改用于执行命令的shell(bash，sh)，需要是可执行文件的绝对路径。
```

**例**

```shell
// ad-hoc 默认在不指定 -m 参数的时候， 使用了默认的command 模块
# ansible all -i inventory -a "ls /root"
# ansible all -i inventory -m command -a "ls /root" //等同第一个命令
# ansible all -i inventory -m shell -a "ls /root"
两个模块功能类似的模块又存在的必要吗? 他们之间的差异在哪里?
shell   模块可以执行SHELL 的内置命令
command 模块无法执行SHELL 的内置命令
如何检测那些命令是shell 的 内置命令呢?
# type -a set        // set 为SHELL内置命令
set is a shell builtin
# type -a env        // env 非内置命令
env is /bin/env
env is /usr/bin/env
```

**例**

```shell
# ansible all -i localhost, -c local -a "set" 
localhost | FAILED | rc=2 >>
[Errno 2] 没有那个文件或目录
// -c local 表示以本地的方式执行，不使用 SSH 连接的方式
# ansible all -i localhost, -c local -m shell -a "set"
localhost | SUCCESS | rc=0 >>
BASH=/bin/sh
BASHOPTS=cmdhist:extquote:force_fignore:hostcomplete:interactive_comments:progcomp:promptvars:sourcepath
BASH_ALIASES=()
BASH_ARGC=()
BASH_ARGV=()
BASH_CMDS=()
BASH_EXECUTION_STRING=set
BASH_LINENO=()
BASH_SOURCE=()
BASH_VERSINFO=([0]="4" [1]="1" [2]="2" [3]="1" [4]="release" [5]="x86_64-redhat-linux-gnu")
BASH_VERSION='4.1.2(1)-release'
DIRSTACK=()
......
......
```

**脚本模块**

```
将管理节点上的脚本传递到远程服务器上进行执行，理论上此模块的执行完全不需要被管理服务器上有Python。
```

**例**

```shell
// 管理节点上的一个脚本
# cat /root/a.sh
#/bin/bash
touch /tmp/testfile
# ansible all -i inventory -m script -a "/root/a.sh"
```

**复制模块**

```yaml
copy 模块的主要用于管理节点和被管理节点之间的文件拷贝。经常使用到的参数如下:
- src    指定拷贝文件的源地址
- dest   指定拷贝文件的目标地址
- backup 拷贝文件前，若原始文件发生变化，则对目标文件进行备份
- woner  指定新拷贝文件的所有者
- group  指定新拷贝文件的所有组
- mode   指定新拷贝文件的权限
```

**例**

```
// copy 管理节点上的/tmp/a.conf 到被管理节点上
# ansible all -i inventory -m copy -a "src=/tmp/a.conf dest=/tmp/a.conf"
// copy 前， 在被管理节点上对原文件进行备份
# ansible all -i inventory -m copy -a "src=/tmp/a.conf dest=/tmp/a.conf backup=yes"
// copy 文件的同时对文件进行用户及用户组设置
# ansible all -i inventory -m copy -a "src=/tmp/a.conf dest=/tmp/a.conf owner=nobody group=nobody"
// copy 文件的同时对文件进行权限设置
# ansible all -i inventory -m copy -a "src=/tmp/a.conf dest=/tmp/a.conf mode=0755"
```

**服务模块**

```
管理远程节点上的服务。类似于Linux上的service命令。常用参数如下:
– enabled  是否开机启动 yes|no 
– name     必选项，服务名称 
– runlevel 运行级别 
– sleep    如果执行了restarted，在则stop和start之间沉睡几秒钟 
– state    对当前服务执行启动，停止、重启、重新加载等操作(started,stopped,restarted,reloaded)

注意:
使用 service 模块时, enabled 和 state 参数至少要指定一个。
使用 service 模块管理的服务，必须在系统中存在 /etc/init.d/XXX 对应的服务。
比如若管理Nginx 服务，则应该存在 /etc/init.d/nginx
```

**例**

```
// 启动 Nginx 服务
# ansible all -i inventory -m service -a "name=nginx state=started"
// 关闭 Nginx 服务
# ansible all -i inventory -m service -a "name=nginx state=stopped"
// 重启 Nginx 服务
# ansible all -i inventory -m service -a "name=nginx state=restarted"
// 重新加载 Nginx 服务
# ansible all -i inventory -m service -a "name=nginx state=reloaded"
// 加 Nginx 服务设置开机自启动
# ansible all -i inventory -m service -a "name=nginx enabled=yes"
```

**systemd模块**

```
管理远程节点上的 systemd 服务，就是由 systemd 所管理的服务。常用参数如下：
- daemon_reload  重新载入 systemd，扫描新的或有变动的单元
– enabled  是否开机启动 yes|no 
– name     必选项，服务名称 
– state    对当前服务执行启动，停止、重启、重新加载等操作(started,stopped,restarted,reloaded)
```

**例**

```shell
// 重新加载 systemd
# ansible all -i inventory -m systemd -a "daemon_reload=yes"
// 启动 Mariadb 服务
# ansible all -i inventory -m systemd -a "name=mariadb state=started"
// 关闭 Mariadb 服务
# ansible all -i inventory -m systemd -a "name=mariadb state=stopped"
// 重启 Mariadb 服务
# ansible all -i inventory -m systemd -a "name=mariadb state=restarted"
// 重新加载 Mariadb 服务
# ansible all -i inventory -m systemd -a "name=mariadb state=reloaded"
// 将 Mariadb 服务设置开机自启动
# ansible all -i inventory -m systemd -a "name=mariadb enabled=yes"
```

**yum模块**

```
等同于 Linux 上的YUM 命令， 对远程服务器上RPM包进行管理。常用参数如下:
- name    要安装的软件包名， 多个软件包以逗号(,) 隔开
- state   对当前指定的软件安装、拆卸操作(present installed latest absent removed)
          安装参数 present installed latest
          拆卸参数 absent removed
```

**例**

```shell
// 安装一个软件包
# ansible all -i inventory -m yum -a "name=nginx state=present"
# ansible all -i inventory -m yum -a "name=nginx state=latest"
# ansible all -i inventory -m yum -a "name=nginx state=installed"
// 拆卸一个软件包
# ansible all -i inventory -m yum -a "name=nginx state=absent"
# ansible all -i inventory -m yum -a "name=nginx state=removed"
// 安装一个软件包组
# ansible all -i inventory -m yum -a "name='@Development tools' state=present"
```

**组模块**

```shell
在被管理节点上，对组进行管理。 常用参数如下:
- name     组名称， 必须的
- system   是否为系统组, yes/no
```

**例**

```shell
// 创建普通组 db_admin
# ansible all -i 172.16.153.160, -m group -a "name=db_admin"
```

**用户模块**

```
用于在被管理节点上对用户进行管理。常用参数如下：
- name  必须的参数， 指定用户名
- password    设置用户的密码，这里接受的是一个加密的值，因为会直接存到 shadow
- update_password  假如设置的密码不同于原密码，则会更新密码. 在 1.3 中被加入
- home        指定用户的家目录
- shell       设置用户的 shell
- uid         指定用户的 UID
- comment	  用户的描述信息
- create_home 在创建用户时，是否创建其家目录。默认创建，假如不创建，设置为 no。2.5版本之前 
              使用 createhome
              
- group       设置用户的主组
- groups      将用户加入到多个组中，多个用逗号隔开，也可以是个列表
- system      设置为 yes 时，将会创建一个系统账号
- expires     设置用户的过期时间，值为时间戳,会转为为天数后，放在 shadow 的最后一个字段里
- generate_ssh_key	设置为 yes 将会为用户生成密钥，这不会覆盖原来的密钥
- ssh_key_type 指定用户的密钥类型， 默认 rsa, 具体的类型取决于被管理节点

- remove       当与 state=absent 一起使用，删除一个用户及其家目录，可选的值为: yes/no
```

**例**

```shell
// 生成加密的密码
# echo test |openssl passwd -1 -stdin
// 创建一个用户 nginx, 指定其 shell 为 nologin
# ansible all -i inventory -m user  -a "name=nginx shell=/sbin/nologin"
// 创建用户 yangge, 并且为其创建密钥对，并且密钥类型为: ecdsa
# ansible all -i inventory -m user -a "name=yangge generate_ssh_key=yes ssh_key_type=ecdsa"

// 创建用 tom, 并且设置其有效期到 2019年8月16日, 加入到组 db_admin 中
# timestamp=$(date +%s -d 20180725)
// 或者
# timestamp=$(python -c 'import time;print(time.mktime(time.strptime("2019-08-16", "%Y-%m-%d")))')
# ansible all -i 172.16.153.160, -m user -a "name=tom expires=$timestamp"

// 修改已有用户 tom 在 31 天后过期
# ansible all -i 172.16.153.160, -m user -a "name=tom expires=$(echo $((86400 * 31))) groups=db_admin,"
```

日期命令说明

```shell
// 计算 3 小时之后是几点几分
# date +%T -d '3 hours'
// 任意日期的前 N 天，后 N 天的具体日期
# date +%F -d "20190910 1 day"
# date +%F -d "20190910 -1 day"

// 计算两个日期相差天数, 比如计算生日距离现在还有多少天
# d1=$(date +%s -d 20180728)
# d2=$(date +%s -d 20180726)
# echo $(((d1-d2)/86400))
```

**文件模块**

```shell
file 模块主要用于远程主机上的文件操作，经常使用的模块参数如下: 
- group  定义文件/目录的属组 
- mode   定义文件/目录的权限 
- owner  定义文件/目录的属主 
- path   必选项，定义文件/目录的路径 
- recurse  递归的设置文件的属性，只对目录有效 
- src    要被链接(软/硬)的源文件的路径，只应用于state=link的情况 
- dest   被链接到的路径，只应用于state=link的情况 
- state 
   directory  如果目录不存在，创建目录 
   file       文件不存在，则不会被创建，存在则返回文件的信息，常用于检查文件是否存在。 
   link       创建软链接 
   hard       创建硬链接 
   touch      如果文件不存在，则会创建一个新的文件，如果文件或目录已存在，则更新其最后修改时间 
   absent     删除目录、文件或者取消链接文件
```

**例**

```shell
// 创建一个文件
# ansible all -i inventory -m file -a "path=/tmp/foo.conf state=touch"
// 改变文件所有者及权限
# ansible all -i inventory -m file -a "path=/tmp/foo.conf owner=nobody group=nobody mode=0644"
// 创建一个软连接
# ansible all -i inventory -m file -a "src=/tmp/foo.conf dest=/tmp/link.conf state=link"
// 创建一个目录
# ansible all -i inventory -m file -a "path=/tmp/testdir state=directory"
// 取消一个连接
# ansible all -i inventory -m file -a "path=/tmp/link.conf state=absent"
// 删除一个文件
# ansible all -i inventory -m file -a "path=/tmp/foo.conf state=absent"
```

**cron模块**

```shell
管理远程节点的CRON 服务。等同于Linux 中的CRON。 常用命令如下:
- name   指定一个cron job 的名字。一定要指定，便于日之后删除。
- minute 指定分钟，可以设置成(0-59, *, */2 等)格式。 默认是 * , 也就是每分钟。
- hour   指定小时，可以设置成(0-23, *, */2 等)格式。 默认是 * , 也就是每小时。
- day    指定天，  可以设置成(1-31, *, */2 等)格式。 默认是 * , 也就是每天。
- month  指定月份， 可以设置成(1-12, *, */2 等)格式。 默认是 * , 也就是每周。
- weekday 指定星期， 可以设置成(0-6 for Sunday-Saturday, * 等)格式。默认是 *，也就是每星期。
- job    指定要执行的内容，通常可以写个脚本，或者一段内容。
- state  指定这个job的状态，可以是新增(present)或者是删除(absent)。 默认为新增(present)
```

**例**

```
// 新建一个 CRON JOB 任务
# ansible all -i inventory -m cron -a "name='create new job' minute='0' job='ls -alh > /dev/null'"
// 删除一个 CRON JOB 任务，删除时，一定要正确指定job 的name参数，以免误删除。
# ansible all -i inventory -m cron -a "name='create new job' state=absent" 
```

登录任何一台管理机验证cron

```
# crontab -l
#Ansible: create new job
0 * * * * ls -alh > /dev/null
```

**调试模块**

```
debug 模块主要用于PlayBook调试时使用，通常的作用是将一个变量的结果打印出来。常用参数如下:
- var 直接打印一个指定的变量值
- msg 打印一段可以格式化的字符串
```

**例**

```
// 这里引入了变量，我们只需了解 debug 模板的使用即可。在学习变量、剧本时，我们会对它有更深刻的理解。
# ansible all -i inventory -m debug -a "var=role" -e "role=web"
# ansible all -i inventory -m debug -a "msg='role is {{role}} '" -e "role=web"
```

**模板** 模块

```
template 模块使用了Jinjia2格式作为文件模版，可以进行文档内变量的替换。
         它的每次使用都会被ansible标记为”changed”状态。文件以 .j2 结尾
         模块常用参数如下：
- backup 创建一个包含时间戳信息的备份文件，这样如果您以某种方式错误地破坏了原始文件，
         就可以将其恢复原状。yes/no
- force  默认值是yes，当内容与源不同时，它将替换远程文件。如果no，仅在目标不存在时才传输文件。
- src    指定 Ansible 控制端的 文件路径
- dest   指定 Ansible 被控端的 文件路径
- owner  指定文件的属主
- group  指定文件的属组
- mode   指定文件的权限

- newline_sequence 指定新文件的换行符; \n，\r, 或 \r\n

内置变量
ansible_managed - 包含一个字符串，可用于描述模板名称，主机，模板文件的修改时间和所有者的uid
template_host - 包含模板机器的节点名称
template_uid - 所有者的uid
template_path - 模版路径
template_fullpath - 模版的绝对路径
template_run_date - 模版呈现的时间
```

**例**

```
// 把本地的当前目录下的 jinja2 模板文件 foo.j2 传送到目标机器上，并指定属主为 shark, 属组 为 wheel, 权限为 0644
# ansible all -i 172.16.153.160, -m template -a "src=./foo.j2 dest=/tmp/foo.conf owner=shark group=wheel mode=0644"
// 上面的用法其实和 copy 模块一样，下面我们就来介绍 template 模块的强大之处
1. 建立一个 template 文件, 名为 hello_world.j2
# cat hello_world.j2
Hello {{var}} !

2. 执行命令，并且设置变量 var 的值为 world
# ansible all -i 172.16.153.160, -m template -a "src=hello_world.j2 dest=/tmp/hello_world.world" -e "var=world"

3. 在被控主机上验证
# cat /tmp/hello_world.world
Hello world !
```

所有模块列表https://docs.ansible.com/ansible/latest/modules/list_of_all_modules.html

模块按照首字母排序

#### 第4章Ansible剧本

```
通过对 AD-HOC 的学习，我们发现 AD-HOC 每次只能在被管理节点上执行简单的命令。而日常工作中，我们往往面临的是一系列的复杂操作，例如我们有可能需要安装软件、更新配置、启动服务等等一系列操作的结合。此时再通过 AD-HOC 去完成任务就有些力不从心了。在这种场景下，Ansible引进了 PLAYBOOK 来帮忙我们解决这样复杂问题。
```

##### 4.1 PlayBook是什么

```
Playbook 也通常被大家翻译成剧本。可以认为它是Ansible 自定义的一门语言(可以将 Playbook 比作 Linux 中的 shell，而 Ansible 中的 Module 可以比作为 Linux 中的各种命令。通过这样的类比，我们对PlayBook就有了一个更形象的认识了)。既然 Playbook 是一门语言，那么它遵循什么样的语法格式? 有哪些语言呢性? 我们将通过下面的学习逐步了解。
```

##### 4.2 YAML学习

```
PlayBook遵循YAML 的语法格式。 因此在学习PlayBook之前，我们必须要先弄明白YAML 相关知识点。
```

**YAML特点**

```
YAML 文件以 # 为注释符
YAML 文件以 .yml 或者.yaml 结尾
YAML 文件以 --- 开始 , 以 ... 结束, 但开始和结束标志都是可选的
```

**基本语法**

```
大小写敏感
使用缩进表示层级关系
缩进时是使用Tab键还是使用空格一定要达到统一，建议使用空格。
相同层级的元素必须左侧对齐即可
YAML 支持的数据结构有三种: 字符串、列表、字典。
```

**弦乐**

```
---
# YAML 中的字符串可以不使用引号，即使里面存在空格的时候，当然了使用单引号和双引号也没有错。
this is a string
'this is a string'
"this is a string"
# YAML 中若一行写不下你要表述的内容，可以进行折行。写法如下:
long_line: | 
		Example 1
		Example 2
		Example 3
# 或者
long_line: >
		Example 1
		Example 2
		Example 3	
...
```

**清单**

```
---
# 若熟悉 Python 的话， 可以认为它就是Python中的List ,若熟悉 C 语言的话， 可以认为它是 C 中的数组。
# 如何定义: 以短横线开头 + 空格 + 具体的值
- red
- green
- blue

# 以上的值假如转换成 python 的 List 会是这样：
# ['red', 'green', 'blue']
...
```

**字典**

```
---
# 若熟悉Python 的话， 可以认为它就是Python中的 Dict
# 如何定义: key + 冒号(:) + 空格 + 值(value), 即 key: value

name: Using Ansible
code: D1234

# 转换为 python 的 Dict
# {'name': 'Using Ansibel', 'code': 'D1234'}
...
```

**混合结构**

```
以上,针对YAML 的所有基础知识点就介绍完了。但在日常生活中，往往需要的数据结构会特别复杂，有可能会是字符串、列表、字典的组合形式。 这里举一个小例子:
所有人都上过学，都知道到学校里是以班级为单位。我们去使用列表和字典的形式去描述一个班级的组成。
---
class:
  - name: stu1
    num: 001
  - name: stu2
    num: 002
  - name: stu3
    num: 003
# {'class': [{'name': 'stu1', 'num': 1},{'name': 'stu2', 'num': 2},...]}
...
```

**验证YAML语法**

```
// 将YAML文件，通过Python 的YAML 模块验证， 若不正确则报错。若正确则会输出YAML 里的内容。
// 注意使用时，一定确保安装了yaml 软件包。
python -c 'import yaml,sys; print yaml.load(sys.stdin)' < myyaml.yml
python3 -c 'import yaml,sys; print(yaml.load(sys.stdin))' < myyaml.yml
```

**例**

```
// 正确的情况
# cat myyaml.yml
---
- red
- green
- blue
...
# python -c 'import yaml,sys; print yaml.load(sys.stdin)' < myyaml.yml
['red', 'green', 'blue']

// 错误的情况， 将YAML文件写错
# cat myyaml.yml
---
- red
- green
-blue
...
# python -c 'import yaml,sys; print yaml.load(sys.stdin)' < myyaml.yml
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/usr/local/lib/python2.7/site-packages/yaml/__init__.py", line 71, in load
    return loader.get_single_data()
  File "/usr/local/lib/python2.7/site-packages/yaml/constructor.py", line 37, in get_single_data
    node = self.get_single_node()
...
...
```

##### 4.3播放定义

```
由于Playbook 是由一个或者多个Play组成,那么如果我们熟悉Play 的写法，就自然掌握了我们这章的PlayBook。

那如何定义一个Play呢
1、每一个Play 都是以短横杠开始的
2、每一个Play 都是一个YAML 字典格式
```

根据上面两条播放的规则，一个假想的

```
---
- key1: value1
  key2: value2
  key3: value3
...
```

由于一个Playbook是由一个或多个Play构成，那么一个包含多个Play的Playbook结构上应该是如下的样子

```
---
# 一个含有3个Play 的伪PlayBook构成
- key1: value1
  key2: value2
  key3: value3
- key4: value1
  key5: value2
  key6: value3
- key1: value1
  key2: value2
  key3: value3
...
```

##### 4.4播放属性

```
以上一小节中的Play为基础, Play中的每一个key, key1、key2、key3等；这些key在PlayBook中被定义为Play的属性。这些属性都具有特殊的意义,我们不能随意的自定义Play 的属性。那么Ansible本身都支持哪些Play属性呢
```

**常用属性**

```
(1)、name 属性， 每个play的名字
(2)、hosts 属性, 每个play 涉及的被管理服务器，同ad hoc 中的patten
(3)、tasks 属性, 每个play 中具体要完成的任务，以列表的形式表达
(4)、become 属性，如果需要提权，则加上become 相关属性
(5)、become_user 属性, 若提权的话，提权到哪个用户上
(6)、remote_user属性，指定连接用户。若不指定，则默认使用当前执行 ansible Playbook 的用户
```

##### 4.5一个完整剧本

根据上一小节中介绍的真实的属性，一个包含一个Play的Playbook应该是如下的样子

```yaml
---
- name: the first play example
  hosts: all
  remote_user: root
  tasks:
    - name: install nginx package
      yum: name=nginx state=present
    - name: copy nginx.conf to remote server
      copy: src=nginx.conf dest=/etc/nginx/nginx.conf
    - name: start nginx server
      service:
        name: nginx
        enabled: true
        state: started
```

**任务属性中任务的多种写法**

```
# 以启动 nginx 服务，并增加开机启动为例
# 一行的形式:
service: name=nginx enabled=true state=started

# 多行的形式:
service: name=nginx
         enabled=true
         state=started

# 多行写成字典的形式:
service:
  name: nginx
  enabled: true
  state: started
```

**具有多个Play的Playbook**

```yaml
---
- name: manage web servers
  hosts: web-servers
  remote_user: root
  tasks:
    - name: install nginx package
      yum: name=nginx state=present
    - name: copy nginx.conf to remote server
      copy: src=nginx.conf dest=/etc/nginx/nginx.conf
    - name: start nginx server
      service:
        name: nginx
        enabled: true
        state: started
- name: manager db servers
  hosts: db-servers
  tasks:
    - name: update database confg
      copy: src=my.cnf dest=/etc/my.cnf        
```

**如何对Playbook进行语法验证**

```
// 因为PlayBook 属于YAML 格式， 我们同样可以使用检查YAML的语法格式的方法进行检查PlayBook的语法正确性。
// 此形式的校验，只能校验PlayBook是否正确，而不能校验YAML文件是否语法正确。
# ansible-playbook myplaybook.yml --syntax-check
```

**如何运行PlayBook**

```
# ansible-playbook myplaybook.yml
```

**如何单步跟从调试PlayBook**

```
// 执行Task中的任务，需要手动确认是否往下执行。
# ansible-playbook myplaybook.yml --step
```

**如何测试运行PlayBook**

```
// 会执行完整个PlayBook ,但是所有Task中的行为都不会在远程服务器上执行，所有执行都是模拟行为。
# ansible-playbook myplaybook.yml -C
// -C 为大写的字母 C
```

#### 第 5 章 Ansible 变量

```
我们在PlayBook一节中，将PlayBook类比成了Linux中的shell。那么它作为一门Ansible特殊的语言，肯定要涉及到变量定义、控制结构的使用等特性。在这一节中主要讨论变量的定义和使用。
```

##### 变量命名规则

**变量的名字由字母、下划线和数字组成，以字母开头。**

```
如下变量命名为正确:
good_a  OK
ok_b    OK
如下变量命名为错误:
_aaa    FAIL
2_bb    FAIL
```

**保留关键字不能作为变量名称**

```
add, append, as_integer_ratio, bit_length, capitalize, center, clear, conjugate, copy, count, decode, denominator, difference, difference_update, discard, encode, endswith, expandtabs, extend, find, format, fromhex, fromkeys, get, has_key, hex, imag, index, insert, intersection, intersection_update, isalnum, isalpha, isdecimal, isdigit, isdisjoint, is_integer, islower, isnumeric, isspace, issubset, issuperset, istitle, isupper, items, iteritems, iterkeys, itervalues, join, keys, ljust, lower, lstrip, numerator, partition, pop, popitem, real, remove, replace, reverse, rfind, rindex, rjust, rpartition, rsplit, rstrip, setdefault, sort, split, splitlines, startswith, strip, swapcase, symmetric_difference, symmetric_difference_update, title, translate, union, update, upper, values, viewitems, viewkeys, viewvalues, zfill
```

##### 变量类型

```
根据变量的作用范围大体的将变量分为: 全局变量、剧本变量、资产变量。但只是一个比较粗糙的划分，不能囊括Ansible 中的所有变量。下面将分别从这三种变量入手，去介绍变量的使用
```

##### 全局变量

```
全局变量，是我们使用ansible 或使用ansible-playbook 时，手动通过 -e 参数传递给Ansible 的变量。
通过ansible 或 ansible-playbook 的 help 帮助, 可以获取具体格式使用方式:
# ansible -h |grep var
  -e EXTRA_VARS, --extra-vars=EXTRA_VARS
                        set additional variables as key=value or YAML/JSON

# ansible-playbook  -h |grep var
  -e EXTRA_VARS, --extra-vars=EXTRA_VARS
                        set additional variables as key=value or YAML/JSON
```

**Example**

传递普通的key=value 的形式

```
# ansible all -i localhost, -m debug -a "msg='my key is {{ key }}'" -e "key=value"
```

传递一个YAML/JSON 的形式(注意不管是YAML还是JSON，它们的最终格式一定要是一个字典)

```
# cat a.json
{"name":"qfedu","type":"school"}
# ansible all -i localhost, -m debug -a "msg='name is {{ name  }}, type is {{ type }}'" -e @a.json
# cat a.yml
---
name: qfedu
type: school
...
# ansible all -i localhost, -m debug -a "msg='name is {{ name  }}, type is {{ type }}'" -e @a.yml
```

##### 剧本变量

```
此种变量和PlayBook 有关，定义在PlayBook中的。它的定义方式有多种，我们这里介绍两种最常用的定义方式。
```

**通过PLAY 属性 vars 定义**

```yaml
---
- name: test play vars 
  hosts: all
  vars:
    user: lilei
    home: /home/lilei
```

**通过PLAY 属性 vars_files 定义**

```yaml
# 当通过vars属性定义的变量很多时，这个Play就会感觉特别臃肿。此时我们可以将变量单独从Play中抽离出来，
# 形成单独的YAML 文件。
---
- name: test play vars
  hosts: all
  vars_files:
    - vars/users.yml
# cat vars/users.yml
---
user: lilei
home: /home/lilei
```

**如何在PlayBook中使用这些变量**

在PlayBook中使用变量时，使用 **{{ 变量名 }}** 来使用变量

```yaml
---
- name: test play vars 
  hosts: all
  vars:
    user: lilei
    home: /home/lilei
  tasks:
    - name: create the user {{ user }}
      user:
        name: "{{ user }}"
        home: "{{ home }}"
```

**在PlayBook中使用变量的注意点**

```yaml
---
# 这里我们将上面的Playbook中引用变量的部分进行修改，去掉了双引号。
- name: test play vars 
  hosts: all
  vars:
    user: lilei
    home: /home/lilei
  tasks:
    - name: create the user {{ user }}
      user:
        # 注意这里将 "{{ user }}" 改成了 {{ user }}
        name: {{ user }}
        home: "{{ home }}”
```

执行以上的PlayBook 时，会出现以下错误

```
The offending line appears to be:

      user:
        name: {{ user }}
               ^ here
We could be wrong, but this one looks like it might be an issue with
missing quotes.  Always quote template expression brackets when they
start a value. For instance:

    with_items:
      - {{ foo }}

Should be written as:

    with_items:
      - "{{ foo }}"
这样错误的主要原因是PlayBook 是YAML 的文件格式， 当Ansible 分析YAML 文件时，有可能会误认为类似
name: {{ user }} 是一个字典的开始。因此加针对变量的使用，加上了双引号，避免Ansible错误解析。
```

##### 资产变量

```
在第二章中我们学习了资产。资产共分为静态资产和动态资产。这一节中学习的资产变量，就是和资产紧密相关的一种变量。资产变量分为主机变量和组变量，分别针对资产中的单个主机和组。
```

**主机变量**

以下资产中，定义了一个主机变量 lilei ，此变量只针对 192.168.122.129 这台服务器有效。

```
# cat inventoryandhostvars
[web-servers]
192.168.122.129 user=lilei
192.168.122.131
```

**验证**

```
// 获取定义的变量值
# ansible 192.168.122.129  -i inventoryandhostvars  -m debug -a "var=user"
192.168.122.129 | SUCCESS => {
    "user": "lilei"
}

// 未获取到定义的变量值，因为 lilei 这个变量针对 192.168.122.131 主机无效。
# ansible 192.168.122.131  -i inventoryandhostvars  -m debug -a "var=user"
192.168.122.131 | SUCCESS => {
    "user": "VARIABLE IS NOT DEFINED!"
}
```

**组变量**

以下资产中，定义了一个组变量home ，此变量将针对web-servers 这个主机组中的所有服务器有效

```
# cat inventoryandgroupvars
[web-servers]
192.168.122.129 user=lilei
192.168.122.131

[web-servers:vars]
home="/home/lilei"
```

**验证**

```
// user 在资产中定义的是主机变量， 所有在主机 192.168.122.131 中未获取到变量user 值
# ansible web-servers  -i inventoryandgroupvars  -m debug -a "var=user"
192.168.122.129 | SUCCESS => {
    "user": "lilei"
}
192.168.122.131 | SUCCESS => {
    "user": "VARIABLE IS NOT DEFINED!"
}
// home 是 web-servers 的组变量，会针对这个组内的所有服务器生效。
# ansible web-servers  -i inventoryandgroupvars  -m debug -a "var=home"
192.168.122.129 | SUCCESS => {
    "home": "/home/lilei"
}
192.168.122.131 | SUCCESS => {
    "home": "/home/lilei"
}
```

**主机变量 VS 组变量**

当主机变量和组变量在同一个资产中发生重名的情况，会有什么效果呢?

```
# cat inventory_v2
[web-servers]
192.168.122.129 user=lilei
192.168.122.131

[web-servers:vars]
user=cat
```

**验证**

```
// 在资产中定义了主机变量和组变量 user, 此时发现 192.168.122.129 这台机器的主机变量 user 的优先级
// 优先于 组变量user 使用。
# ansible web-servers  -i inventory_v2  -m debug -a "var=user"
192.168.122.129 | SUCCESS => {
    "user": "lilei"
}
192.168.122.131 | SUCCESS => {
    "user": "cat"
}
```

**变量继承**

在介绍资产时说过资产的继承，那么变量是否也存在继承关系呢?

```
# cat inventory_v3
[web-servers]
192.168.122.129

[db-servers]
192.168.122.131

[all-servers]
[all-servers:children]
db-servers
web-servers

[all-servers:vars]
user=lilei
```

**验证**

```
// 在资产继承的同时，对应的变量也发生了继承
# ansible all-servers  -i inventory_v3  -m debug -a "var=user"
192.168.122.131 | SUCCESS => {
    "user": "lilei"
}
192.168.122.129 | SUCCESS => {
    "user": "lilei"
}
# ansible db-servers  -i inventory_v3  -m debug -a "var=user"
192.168.122.131 | SUCCESS => {
    "user": "lilei"
}
# ansible web-servers  -i inventory_v3  -m debug -a "var=user"
192.168.122.129 | SUCCESS => {
    "user": "lilei"
}
```

##### Facts变量

```
Facts变量不包含在前文中介绍的全局变量、剧本变量及资产变量之内。Facts变量不需要我们人为去声明变量名及赋值。它的声明和赋值完全有Ansible 中的Facts模块帮我们完成。类似于资产变量中的主机变量，它收集了有关被管理服务器的操作系统的版本、服务器的IP地址、主机名，磁盘的使用情况、CPU个数、内存大小等等有关被管理服务器的私有信息。假如我们足够细心的话，在每次PlayBook运行的时候都会发现在PlayBook执行前都会有一个Gathering Facts的过程。这个过程就是收集被管理服务器的Facts信息过程。
```

**手动收集Facts 变量**

```shell
# ansible all -i localhost, -c local -m setup
localhost | SUCCESS => {
    "ansible_facts": {
        "ansible_all_ipv4_addresses": [
            "192.168.122.130"
        ],
        "ansible_all_ipv6_addresses": [
            "fe80::20c:29ff:fede:b5b"
        ],
        "ansible_apparmor": {
            "status": "disabled"
        },
        "ansible_architecture": "x86_64",
        "ansible_bios_date": "07/02/2015",
        "ansible_bios_version": "6.00",
        "ansible_cmdline": {
            "KEYBOARDTYPE": "pc",
            "KEYTABLE": "us",
            "LANG": "en_US.UTF-8",
            "SYSFONT": "latarcyrheb-sun16",
            "nomodeset": true,
            "quiet": true,
            "rd_LVM_LV": "vg_mouse00/lv_root",
            "rd_NO_DM": true,
            "rd_NO_LUKS": true,
            "rd_NO_MD": true,
            "rhgb": true,
            "ro": true,
            "root": "/dev/mapper/vg_mouse00-lv_root"
        },
    ...
    ...
    ...
```

**过滤Facts**

```shell
通过刚刚的手动收集Facts，我们发现facts 信息量很大。 能不能有针对性的显示我们想要的信息呢?
可以通过使用Facts 模块中的filter参数去过滤我们想要的信息。
// 比如我想要服务器的内存情况信息
# ansible all -i localhost, -m setup -a "filter=*memory*" -c local
localhost | SUCCESS => {
    "ansible_facts": {
        "ansible_memory_mb": {
            "nocache": {
                "free": 508,
                "used": 473
            },
            "real": {
                "free": 59,
                "total": 981,
                "used": 922
            },
            "swap": {
                "cached": 0,
                "free": 1981,
                "total": 1983,
                "used": 2
            }
        }
    },
    "changed": false
}
// 比如想要服务器的磁盘挂载情况
# ansible all -i localhost, -m setup -a "filter=*mount*" -c local
localhost | SUCCESS => {
    "ansible_facts": {
        "ansible_mounts": [
            {
                "device": "/dev/mapper/vg_mouse00-lv_root",
                "fstype": "ext4",
                "mount": "/",
                "options": "rw",
                "size_available": 5795786752,
                "size_total": 18435350528,
                "uuid": "N/A"
            },
            {
                "device": "/dev/sda1",
                "fstype": "ext4",
                "mount": "/boot",
                "options": "rw",
                "size_available": 442216448,
                "size_total": 499355648,
                "uuid": "N/A"
            }
        ]
    },
    "changed": false
}
```

**如何在PlayBook中去使用Facts 变量**

默认情况下，在执行PlayBook的时候，它会去自动的获取每台被管理服务器的facts信息。

```yaml
---
- name: a play example
  hosts: all
  remote_user: root
  tasks:
    - name: install nginx package
      yum: name=nginx state=present
    - name: copy nginx.conf to remote server
      copy: src=nginx.conf dest=/etc/nginx/nginx.conf
    - name: start nginx server
      service:
        name: nginx
        enabled: true
        state: started
```

**执行**

```
# ansible-playbook   myplaybook.yml

PLAY [a play example] ***************************************************************************************************************************************************************
# 执行PLAYBOOK时，自动收集facts 信息
TASK [Gathering Facts] **************************************************************************************************************************************************************
ok: [192.168.122.131]
ok: [192.168.122.129]

TASK [install nginx package] ********************************************************************************************************************************************************
ok: [192.168.122.129]
ok: [192.168.122.131]
......
......
```

可以像使用其他变量一样，去使用facts 变量

```yaml
---
- name: print facts variable
  hosts: all
  tasks:
   - name: print facts variable
     debug:
       msg: "The default IPV4 address is {{ ansible_default_ipv4.address }}"
```

**如何在PlayBook中去关闭Facts 变量的获取**

```yaml
若在整个PlayBook 的执行过程中，完全未使用过Facts 变量，此时我们可以将其关闭，以加快PlayBook的执行速度。
---
- name: a play example
  hosts: all
  # 关闭 facts 变量收集功能
  gather_facts: no
  remote_user: root
  tasks:
    - name: install nginx package
      yum: name=nginx state=present
    - name: copy nginx.conf to remote server
      copy: src=nginx.conf dest=/etc/nginx/nginx.conf
    - name: start nginx server
      service:
        name: nginx
        enabled: true
        state: started
```

**执行**

```
# ansible-playbook   myplaybook2.yml

PLAY [a play example] ***************************************************************************************************************************************************************

TASK [install nginx package] ********************************************************************************************************************************************************
ok: [192.168.122.129]
ok: [192.168.122.131]

TASK [copy nginx.conf to remote server] *********************************************************************************************************************************************
ok: [192.168.122.131]
ok: [192.168.122.129]

TASK [start nginx server] ***********************************************************************************************************************************************************
ok: [192.168.122.131]
```

##### 注册变量

```yaml
往往用于保存一个task任务的执行结果, 以便于debug时使用。或者将此次task任务的结果作为条件，去判断是否去执行其他task任务。注册变量在PlayBook中通过register关键字去实现。
---
- name: install a package and print the result
  hosts: all
  remote_user: root
  tasks:
    - name: install nginx package
      yum: name=nginx state=present
      register: install_result
    - name: print result
      debug: var=install_result
```

**执行**

```
# ansible-playbook  myplaybook3.yml

PLAY [a play example] ***************************************************************************************************************************************************************

TASK [Gathering Facts] **************************************************************************************************************************************************************
ok: [192.168.122.131]
ok: [192.168.122.129]

TASK [install nginx package] ********************************************************************************************************************************************************
ok: [192.168.122.129]
ok: [192.168.122.131]
// 打印软件包安装结果
TASK [print result] *****************************************************************************************************************************************************************
ok: [192.168.122.129] => {
    "install_result": {
        "changed": false,
        "msg": "",
        "rc": 0,
        "results": [
            "nginx-1.12.1-1.el6.ngx.x86_64 providing nginx is already installed"
        ]
    }
}
ok: [192.168.122.131] => {
    "install_result": {
        "changed": false,
        "msg": "",
        "rc": 0,
        "results": [
            "nginx-1.12.2-1.el6.ngx.x86_64 providing nginx is already installed"
        ]
    }
}

PLAY RECAP **************************************************************************************************************************************************************************
192.168.122.129            : ok=3    changed=0    unreachable=0    failed=0
192.168.122.131            : ok=3    changed=0    unreachable=0    failed=0
```

##### 变量优先级

```
目前介绍了全局变量、剧本变量、资产变量、Facts变量及注册变量。其中Facts变量不需要人为去声明、赋值；注册变量只需通过关键字register去声明，而不需要赋值。而全局变量、剧本变量及资产变量则完全需要人为的去声明、赋值。变量的优先权讨论，也将着重从这三类变量去分析。
假如在使用过程中，我们同时在全局变量、剧本变量及资产变量声明了同一个变量名，那么哪一个优先级最高呢?
下面我们将以实验的形式去验证变量的优先级
```

**环境准备**

1、定义一份资产、且定义了资产变量user

```
[web-servers]
192.168.122.129
192.168.122.131

[web-servers:vars]
user=tomcat
```

2、编写一份PlayBook、同样定义剧本变量user

```
---
- name: test variable priority
  hosts: all
  remote_user: root
  vars:
    user: mysql
  tasks:
    - name: print the user value
      debug: msg='the user value is {{ user }}'
```

**验证测试**

**同时使用全局变量、剧本变量、资产变量**

```
当变量user同时定义在全局变量、剧本变量及资产变量中时，全局变量的优先级最高。
# ansible-playbook priority.yml -e "user=www"

PLAY [a play example] ***************************************************************************************************************************************************************

TASK [Gathering Facts] **************************************************************************************************************************************************************
ok: [192.168.122.131]
ok: [192.168.122.129]

// 打印的 user 值 为www , 全局变量生效
TASK [print the user value] *********************************************************************************************************************************************************
ok: [192.168.122.129] => {
    "msg": "the user value is www"
}
ok: [192.168.122.131] => {
    "msg": "the user value is www"
}

PLAY RECAP **************************************************************************************************************************************************************************
192.168.122.129            : ok=2    changed=0    unreachable=0    failed=0
192.168.122.131            : ok=2    changed=0    unreachable=0    failed=0
```

**同时使用剧本变量和资产变量**

```
取消全局变量，发现剧本变量的优先级要高于资产变量的优先级。
# ansible-playbook priority.yml

PLAY [a play example] ***************************************************************************************************************************************************************

TASK [Gathering Facts] **************************************************************************************************************************************************************
ok: [192.168.122.129]
ok: [192.168.122.131]
// 打印的 user 值 为mysql , 剧本变量生效
TASK [print the user value] *********************************************************************************************************************************************************
ok: [192.168.122.129] => {
    "msg": "the user value is mysql"
}
ok: [192.168.122.131] => {
    "msg": "the user value is mysql"
}

PLAY RECAP **************************************************************************************************************************************************************************
192.168.122.129            : ok=2    changed=0    unreachable=0    failed=0
192.168.122.131            : ok=2    changed=0    unreachable=0    failed=0
```

**只是用资产变量的情况**

```
不使用全局变量、且注释掉剧本变量后，资产变量才最终生效。
---
- name: test variable priority
  hosts: all
  remote_user: root
  #vars:
  #  user: mysql
  tasks:
    - name: print the user value
      debug: msg='the user value is {{ user }}'
# ansible-playbook priority.yml

PLAY [a play example] ***************************************************************************************************************************************************************

TASK [Gathering Facts] **************************************************************************************************************************************************************
ok: [192.168.122.129]
ok: [192.168.122.131]

// 打印的 user 值 为tomcat , 资产变量生效。
TASK [print the user value] *********************************************************************************************************************************************************
ok: [192.168.122.129] => {
    "msg": "the user value is tomcat"
}
ok: [192.168.122.131] => {
    "msg": "the user value is tomcat"
}

PLAY RECAP **************************************************************************************************************************************************************************
192.168.122.129            : ok=2    changed=0    unreachable=0    failed=0
192.168.122.131            : ok=2    changed=0    unreachable=0    failed=0
```

**变量优先级结论**

```
当一个变量同时在全局变量、剧本变量和资产变量中定义时，优先级最高的是全局变量；其次是剧本变量；最后才是资产变量。
```

#### 第 6 章 Ansible 任务控制

```shell
这里主要来介绍PlayBook中的任务控制，任务控制类似于编程语言中的if ... 、for ... 等逻辑控制语句。这里我们给出一个实际场景应用案例去说明在PlayBook中，任务控制如何应用。
在下面的PlayBook中，我们创建了 tomcat、www 和 mysql 三个用户。安装了Nginx 软件包、并同时更新了 Nginx 主配置文件和虚拟主机配置文件，最后让Nginx 服务处于启动状态。整个PlayBook从语法上没有任何问题，但从逻辑和写法上仍然有一些地方需要我们去注意及优化:
1、Nginx启动逻辑欠缺考虑。若Nginx的配置文件语法错误则会导致启动Nginx失败，以至于PlayBook执行失败。
2、批量创建用户，通过指令的罗列过于死板。如果再创建若干个用户，将难以收场。
---
- name: task control playbook example
  hosts: web-servers
  tasks:
    - name: create tomcat user
      user: name=tomcat state=present

    - name: create www user
      user: name=www state=present

    - name: create mysql user
      user: name=mysql state=present

    - name: yum nginx webserver
      yum: name=nginx state=present

    - name: update nginx main config
      copy: src=nginx.conf dest=/etc/nginx/

    - name: add virtualhost config
      copy: src=www.qfedu.com.conf dest=/etc/nginx/conf.d/

    - name: start nginx server
      service: name=nginx state=started
# cat nginx.conf
user  www;
worker_processes 2;

error_log  /var/log/nginx/error.log;
pid        /var/run/nginx.pid;

events {
    worker_connections  1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    sendfile        on;
    tcp_nopush     on;

    keepalive_timeout  0;

    gzip on;
    gzip_min_length  1k;
    gzip_buffers     8 64k;
    gzip_http_version 1.0;
    gzip_comp_level 5;
    gzip_types   text/plain application/x-javascript text/css application/json application/xml application/x-shockwave-flash application/javascript image/svg+xml image/x-icon;
    gzip_vary on;

    include /etc/nginx/conf.d/*.conf;
}
# cat www.qfedu.com.conf
server {
    listen 80;
    server_name www.qfedu.com;
    root /usr/share/nginx/html;
    access_log /var/log/nginx/www.qfedu.com-access_log main;
    error_log  /var/log/nginx/www.qfedu.com-error_log;

    add_header Access-Control-Allow-Origin *;

    location ~ .*\.(gif|jpg|jpeg|png|bmp|swf)$ {
            expires      1d;
    }

    location ~ .*\.(js|css)?$ {
            expires      1d;
    }
}
我们下面将以解决一个个问题的形式去优化上例中的PlayBook。通过问题的解决，来达到我们学习任务控制的目的。
```

##### 条件判断

**解决第一个问题**

```
Nginx启动逻辑欠缺考虑。若Nginx的配置文件语法错误则会导致启动Nginx失败，以至于PlayBook执行失败。
如果我们能够在启动之前去对Nginx的配置文件语法做正确性的校验，只有当校验通过的时候我们才去启动或者重启Nginx；否则则跳过启动Nginx的过程。这样就会避免Nginx 配置文件语法问题而导致的无法启动的风险。 
```

**Nginx 语法校验**

```yaml
- name: check nginx syntax
  shell: /usr/sbin/nginx -t
那如何将Nginx语法检查的TASK同Nginx启动的TASK关联起来呢?
如果我们能够获得语法检查的TASK的结果，根据这个结果去判断“启动NGINX的TASK”是否执行，这将是一个很好的方案。
如何和获取到语法检查TASK的结果呢? 此时就可以使用Ansible中的注册变量。
```

**获取Task任务结果**

```yaml
- name: check nginx syntax
  shell: /usr/sbin/nginx -t
  register: nginxsyntax
此时有可能还有疑问，我获取到任务结果，但是结果里面的内容是个什么样子， 我如何在后续的PlayBook中使用呢?
```

**通过debug模块去确认返回结果的数据结构**

```yaml
- name: print nginx syntax result
  debug: var=nginxsyntax
```

通过debug 模块，打印出来的返回结果。 当nginxsyntax.rc 为 0 时语法校验正确。

```yaml
"nginxsyntax": {
        "changed": true,
        "cmd": "/usr/sbin/nginx -t",
        "delta": "0:00:00.012045",
        "end": "2017-08-12 20:19:04.650718",
        "rc": 0,
        "start": "2017-08-12 20:19:04.638673",
        "stderr": "nginx: the configuration file /etc/nginx/nginx.conf syntax is ok\nnginx: configuration file /etc/nginx/nginx.conf test is successful",
        "stderr_lines": [
            "nginx: the configuration file /etc/nginx/nginx.conf syntax is ok",
            "nginx: configuration file /etc/nginx/nginx.conf test is successful"
        ],
        "stdout": "",
        "stdout_lines": []
    }
```

**通过条件判断(when) 指令去使用语法校验的结果**

```yaml
    - name: check nginx syntax
      shell: /usr/sbin/nginx -t
      register: nginxsyntax

    - name: print nginx syntax
      debug: var=nginxsyntax
      
    - name: start nginx server
      service: name=nginx state=started
      when: nginxsyntax.rc == 0
```

**改进后的PlayBook**

```yaml
---
- name: task control playbook example
  hosts: web-servers
  tasks:
    - name: create tomcat user
      user: name=tomcat state=present

    - name: create www user
      user: name=www state=present

    - name: create mysql user
      user: name=mysql state=present

    - name: yum nginx webserver
      yum: name=nginx state=present

    - name: update nginx main config
      copy: src=nginx.conf dest=/etc/nginx/

    - name: add virtualhost config
      copy: src=www.qfedu.com.conf dest=/etc/nginx/conf.d/

    - name: check nginx syntax
      shell: /usr/sbin/nginx -t
      register: nginxsyntax

    - name: print nginx syntax
      debug: var=nginxsyntax
      
    - name: start nginx server
      service: name=nginx state=started
      when: nginxsyntax.rc == 0
以上的逻辑，只要语法检查通过都会去执行 "start nginx server"这个TASK。当反复执行这个PlayBook 的，除了第一次外，其他"start nginx server" 的TASK是没有必要的执行的。能否避免这样的问题呢?
我们在判断"start nginx server" 这个TASK任务是否启动的条件基础上再加一个条件。只有当语法校验正确、且Nginx 服务没有启动的时候再去启动服务。
---
- name: task control playbook example
  hosts: web-servers
  tasks:
    - name: create tomcat user
      user: name=tomcat state=present

    - name: create www user
      user: name=www state=present

    - name: create mysql user
      user: name=mysql state=present

    - name: yum nginx webserver
      yum: name=nginx state=present

    - name: update nginx main config
      copy: src=nginx.conf dest=/etc/nginx/

    - name: add virtualhost config
      copy: src=www.qfedu.com.conf dest=/etc/nginx/conf.d/

    - name: check nginx syntax
      shell: /usr/sbin/nginx -t
      register: nginxsyntax
      
    - name: check nginx running
      stat: path=/var/lock/subsys/nginx
      register: nginxrunning
      
    - name: print nginx syntax
      debug: var=nginxsyntax
    # 只有当Nginx 的语法校验正确、且Nginx 没有启动的情况下才会去启动Nginx 。
    # 再次执行PlayBook 时，会发现"start nginx server" 的TASK被 skipping 了。
    - name: start nginx server
      service: name=nginx state=started
      when: nginxsyntax.rc == 0 and nginxrunning.stat.exists == false
在这个问题的解决里，我们学习了when条件判断和注册变量的结合使用。学习了when条件判断中是可以支持复杂逻辑的。比如现在用到的逻辑运算符 and。 

另外when 支持如下运算符:
==
!=
> >=
< <=
is defined
is not defined
true
false
支持逻辑运算符: and or
```

##### 循环控制

**解决第二个问题**

```
批量创建用户，通过指令的罗列过于死板。如果再创建若干个用户，将难以收场。
如果在创建用户时,抛开PlayBook的实现不说, 单纯的使用shell去批量的创建一些用户。通常会怎么写呢?
#! /bin/bash
createuser="tomcat mysql www"
for i in `echo $createuser`
do
   useradd $i
done
那么如果PlayBook中也存在这样的循环控制，我们也可以像写shell一样简单的去完成多用户创建工作。
在PlayBook中使用with_items 去实现循环控制，且循环时的中间变量(上面shell循环中的 $i 变量)只能是
关键字 item ，而不能随意自定义。
```

**上面的基础上，改进的PlayBook**

```yaml
在这里使用定义了剧本变量 createuser(一个列表) ，然后通过 with_items 循环遍历变量这个变量来达到创建用户的目的。
- name: variable playbook example
  hosts: webservers
  vars:
    createuser:
      - tomcat
      - www
      - mysql
  tasks:
    - name: create user
      user: name={{ item }} state=present
      with_items: "{{ createuser }}"

    - name: yum nginx webserver
      yum: name=nginx state=present

    - name: update nginx main config
      copy: src=nginx.conf dest=/etc/nginx/

    - name: add virtualhost config
      copy: src=www.qfedu.com.conf dest=/etc/nginx/conf.d/

    - name: check nginx syntax
      shell: /usr/sbin/nginx -t
      register: nginxsyntax

    - name: check nginx running
      stat: path=/var/lock/subsys/nginx
      register: nginxrunning
      
    - name: print nginx syntax
      debug: var=nginxsyntax

    - name: start nginx server
      service: name=nginx state=started
      when: nginxsyntax.rc == 0 and nginxrunning.stat.exists == false
解决了以上问题，整个PlayBook已经有了很大的改进。但我们在生产环境中验证时发现还是不够灵活。
若更新了Nginx 的配置文件后，我们需要通过PlayBook将新的配置发布到生产服务器上，然后再重新加载我们的Nginx 服务。但以现在的PlayBook来说，每次更改Nginx 配置文件后虽然可以通过它发布到生产，但整个PlayBook都要执行一次，这样无形中扩大了变更范围和变更风险。
```

##### Tags属性

```
我们可以通过Play中的tags 属性，去解决目前PlayBook变更而导致的扩大变更范围和变更风险的问题。
在改进的PlayBook中，我们针对文件发布TASK 任务 "update nginx main config" 和 "add virtualhost config" 新增了属性 tags ，属性值为updateconfig。另外我们新增"reload nginx server" TASK任务。当配置文件更新后，去reload Nginx 服务。这样对配置文件更新的操作将很完美。
```

**改进PlayBook**

```yaml
- name: tags playbook example
  hosts: web-servers
  vars:
    createuser:
      - tomcat
      - www
      - mysql
  tasks:
    - name: create user
      user: name={{ item }} state=present
      with_items: "{{ createuser }}"

    - name: yum nginx webserver
      yum: name=nginx state=present

    - name: update nginx main config
      copy: src=nginx.conf dest=/etc/nginx/
      tags: updateconfig

    - name: add virtualhost config
      copy: src=www.qfedu.com.conf dest=/etc/nginx/conf.d/
      tags: updateconfig

    - name: check nginx syntax
      shell: /usr/sbin/nginx -t
      register: nginxsyntax
      tags: updateconfig

    - name: check nginx running
      stat: path=/var/lock/subsys/nginx
      register: nginxrunning
      tags: updateconfig

    - name: print nginx syntax
      debug: var=nginxsyntax

    - name: reload nginx server
      service: name=nginx state=started
      when: nginxsyntax.rc == 0 and nginxrunning.stat.exists == true
      tags: updateconfig

    - name: start nginx server
      service: name=nginx state=started
      when: nginxsyntax.rc == 0 and nginxrunning.stat.exists == false
```

**指定tags 去执行PlayBook**

```
// 执行时一定要指定tags，这样再执行的过程中只会执行task 任务上打上tag 标记为 updateconfig 的任务
# ansible-playbook site.yml -t updateconfig
但反复执行此PlayBook依然存在问题。当我的配置文件没有发生变化时，每次依然都会去触发TASK "reload nginx server"。如何能做到只有配置文件发生变化的时候才去触发TASK "reload nginx server"，这样的处理才是最完美的实现。此时可以使用handlers 属性。
```

##### Handlers属性

```
在改进的PlayBook中，我们针对文件发布TASK 任务 "update nginx main config" 和 "add virtualhost config" 增加了新属性 notify, 值为 "reload nginx server"。它的意思是说，针对这两个文件发布的TASK,
设置一个通知机制，当Ansible 认为文件的内容发生了变化(文件MD5发生变化了)，它就会发送一个通知信号 handlers 中的任务。具体发送到handlers中的哪个任务，由notify 的值"reload nginx server"决定。通知发出后handlers 会根据发送的通知，在handlers中相关的任务中寻找名称为"reload nginx server" 的任务。当发现存在这样名字的TASK，就会执行它。若没有找到，则什么也不做。若我们要实现这样的机制，千万要注意notify属性设置的值，一定要确保能和handlers中的TASK 名称对应上。
```

**改进PlayBook**

```yaml
- name: handlers playbook example
  hosts: web-servers
  vars:
    createuser:
      - tomcat
      - www
      - mysql
  tasks:
    - name: create user
      user: name={{ item }} state=present
      with_items: "{{ createuser }}"

    - name: yum nginx webserver
      yum: name=nginx state=present

    - name: update nginx main config
      copy: src=nginx.conf dest=/etc/nginx/
      tags: updateconfig
      notify: reload nginx server

    - name: add virtualhost config
      copy: src=www.qfedu.com.conf dest=/etc/nginx/conf.d/
      tags: updateconfig
      notify: reload nginx server

    - name: check nginx syntax
      shell: /usr/sbin/nginx -t
      register: nginxsyntax
      tags: updateconfig

    - name: check nginx running
      stat: path=/var/lock/subsys/nginx
      register: nginxrunning
      tags: updateconfig

    - name: print nginx syntax
      debug: var=nginxsyntax

    - name: start nginx server
      service: name=nginx state=started
      when: nginxsyntax.rc == 0 and nginxrunning.stat.exists == false
  handlers:
    - name: reload nginx server
      service: name=nginx state=reload
      when: nginxsyntax.rc == 0 and nginxrunning.stat.exists == true
```

**执行**

```
// 首次执行，若配置文件没有发生变化。发现根本就没有触发handlers 中TASK任务
# ansible-playbook site.yml -t updateconfig
// 人为对Nginx 配置文件稍作修改，只要MD5校验值发生变化即可。此时再执行，发现触发了handlers 中的TASK任务
# ansible-playbook site.yml -t updateconfig
```

#### 第 7 章 Ansible Jinja2模板

```
目前Nginx的配置文件在所有的服务器上都是相同的,但我希望能根据每一台服务器的性能去定制服务的启动进程。
同时定制每一台Nginx服务的响应头，以便于当某台服务出现问题时能快速定位到具体的服务器。
要做这样的定制势必会导致一个问题，Nginx 在每台物理服务器上的配置文件都不一样，这样的配置文件如何管理呢?
再使用copy 模块去做管理显然已经不合适。此时使用Ansible 提供的另一个模板(template) 功能，它可以帮助我们完美的解决问题。
```

##### JinJa2 模板

```
要学会Ansible 中的模板(template)使用，前提我们必须要学会JinJa2模板。学会了它，就相当于我们学会了Ansible 模板。
```

**JinJa2 是什么**

```
Jinja2是基于Python书写的模板引擎。功能比较类似于PHP的smarty模板。
```

**JinJa2 必知必会**

```
1、jinja2 文件以 .j2 为后缀， 也可以不写后缀。
2、jinja2 中存在 三种定界符
   注释:    {# #}
   变量引用:  {{}}
   逻辑表达:  {%%}
```

**JinJa2 逻辑控制**

**条件表达**

```
{% if %}
...
...
{% endif %}
```

**Example**

```
{# 如果定义了 idc 变量， 则输出 #}
{% if idc is defined %}
{{idc}}
{% endif %}
```

**循环控制**

```
{% for %}
...
...
{% endfor %}
```

**Example**

```shell
{# 列举出 db-servers 这个 group 中的所有主机 #}
{% for host in groups['db-servers'] %}
{{ host }}
{% endfor %}
{#与Python 语法不通，模板中的循环内不能break或continue。但你可以在迭代中过滤序列来跳过某些项#}
{#打印db-servers 组中的所有主机，但是不打印1.1.1.1 这台主机#}
{% for host in groups['db-servers'] if host != "1.1.1.1" %}
{{host}}
{% endfor %}
```

##### 如何使用模块

**一个基于Facts的Jinja2 实例**

```shell
# cat config.j2
{# use variable example #}
wlecome host {{ ansible_hostname }}, os is {{ ansible_os_family }}

{# use condition example #}
{% if ansible_processor_vcpus > 1 %}
OS CPU more than one core
{% endif %}

{% for m in ansible_mounts if m['mount'] != "/" %}
mount {{ m['mount'] }}, total size is {{m['size_total']}}, free size is {{m['size_available']}}
{% endfor %}

{# use variables example #}
welcome host {{ ansible_hostname   }},it's os is {{ ansible_os_family  }}
today is {{ ansible_date_time.date  }}
cpucore numbers {{ ansible_processor_vcpus  }}

{# use condition example #}
{% if ansible_processor_vcpus > 1 %}
OS CPU more than one core
{% endif %}

{# use loop exampe #}
{% for m in ansible_mounts %}
mount {{ m['mount']  }} , total size is {{ m['size_total']  }}, free size is {{m['size_available']}}
{% endfor %}
```

**如何在Ansible 中使用模板**

```shell
---
- name: a template example
  hosts: all
  remote_user: root
  tasks:
    - name: update jinja2 config
      template: src=config.j2 dest=/tmp/config.conf
Jinja2 模板以及如何在Ansible中使用模板，已经介绍完了。那么如何去实现我们的需求呢? 
# cat nginx.conf.j2
user              www;
{# start process equal cpu cores #}
worker_processes {{ ansible_processor_vcpus }};

error_log  /var/log/nginx/error.log;
pid        /var/run/nginx.pid;

events {
    worker_connections  1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    sendfile        on;
    tcp_nopush     on;

    keepalive_timeout  0;

    gzip on;
    gzip_min_length  1k;
    gzip_buffers     8 64k;
    gzip_http_version 1.0;
    gzip_comp_level 5;
    gzip_types   text/plain application/x-javascript text/css application/json application/xml application/x-shockwave-flash application/javascript image/svg+xml image/x-icon;
    gzip_vary on;
    {# add_header {{ ansible_hostname }}; #}
    add_header x-hostname {{ ansible_hostname  }};

    include /etc/nginx/conf.d/*.conf;
}
```

**继续优化我们的PlayBook, 让它支持模板**

```yaml
- name: template playbook example
  hosts: web-servers
  vars:
    createuser:
      - tomcat
      - www
      - mysql
  tasks:
    - name: create user
      user: name={{ item }} state=present
      with_items: "{{ createuser }}"

    - name: yum nginx webserver
      yum: name=nginx state=present

      # use ansible template
    - name: update nginx main config
      template: src=nginx.conf.j2 dest=/etc/nginx/
      tags: updateconfig
      notify: reload nginx server
      
    - name: add virtualhost config
      copy: src=www.qfedu.com.conf dest=/etc/nginx/conf.d/
      tags: updateconfig
      notify: reload nginx server
      
    - name: check nginx syntax
      shell: /usr/sbin/nginx -t
      register: nginxsyntax
      tags: updateconfig
      
    - name: check nginx running
      stat: path=/var/lock/subsys/nginx
      register: nginxrunning
      tags: updateconfig
        
    - name: print nginx syntax
      debug: var=nginxsyntax
      
    - name: start nginx server
      service: name=nginx state=started
      when: nginxsyntax.rc == 0 and nginxrunning.stat.exists == false
  handlers:
    - name: reload nginx server
      service: name=nginx state=started
      when: nginxsyntax.rc == 0 and nginxrunning.stat.exists == true
```

#### 第 8 章 Ansible Roles

```
一个数据中心有可能存在好多类型的服务器。比如WEB类型、DB类型、开发人员使用的开发类型、QA使用的测试类型等等。如果每个类型的服务器的初始化行为都不一致，那要在一个PlayBook中将这些动作完成，这个PlayBook将变得臃肿、庞大，且难以后续维护和更新。如果能够针对每个类型的服务器单独编写PlayBook，最后通过某种方式整合这PlayBook， 在管理方式上就又会变得简单。Ansible中提供了类似的概念，也就是Role。它允许管理员将他们复杂的PlayBook分解成一个个小的逻辑单元, 以便于维护和管理。
```

##### Roles 结构

**ROLE 是什么呢**

```
从表面上看，它就是一个目录。目录的名字也就是role的名字。进到这个role名字的目录里，会发现好多子目录。
tasks:     存放 task 任务
handlers:  存放 handlers 任务
files:     存放 task 中引用的文件
templages: 存放 task 中引用的模板
meta:      存在 role 的依赖role(这个role 执行前，要先执行那个role)
vars:      存放 role 的变量
defaults:  存在 role 的默认变量
```

**那么一个真正的Role 的目录结构应该如下**

```shell
user.example/
├── defaults
│   └── main.yml
├── files
├── handlers
│   └── main.yml
├── meta
│   └── main.yml
├── tasks
│   └── main.yml
├── templates
└── vars
    └── main.yml
role 的名字叫做 user.example。
其中 tasks 、handlers 、meta、 vars、defaults 目录的入口文件必须是main.yml，不能别配置为其他。
```

##### 制作一个Role

```
我们将上文经过最终优化的PlayBook，分解成一个Role。 那么应该如何操作呢?
```

**最终优化的PlayBook**

```yaml
- name: template playbook example
  hosts: web-servers
  vars:
    createuser:
      - tomcat
      - www
      - mysql
  tasks:
    - name: create user
      user: name={{ item }} state=present
      with_items: "{{ createuser }}"

    - name: yum nginx webserver
      yum: name=nginx state=present

      # use ansible template
    - name: update nginx main config
      template: src=nginx.conf.j2 dest=/etc/nginx/
      tags: updateconfig
      notify: reload nginx server
      
    - name: add virtualhost config
      copy: src=www.qfedu.com.conf dest=/etc/nginx/conf.d/
      tags: updateconfig
      notify: reload nginx server
      
    - name: check nginx syntax
      shell: /usr/sbin/nginx -t
      register: nginxsyntax
      tags: updateconfig
      
    - name: check nginx running
      stat: path=/var/lock/subsys/nginx
      register: nginxrunning
      tags: updateconfig
        
    - name: print nginx syntax
      debug: var=nginxsyntax
      
    - name: start nginx server
      service: name=nginx state=started
      when: nginxsyntax.rc == 0 and nginxrunning.stat.exists == false
  handlers:
    - name: reload nginx server
      service: name=nginx state=started
      when: nginxsyntax.rc == 0 and nginxrunning.stat.exists == true
```

**分解这个PlayBook，命名role 的名字为 nginx**

```shell
nginx/
│
├── files
├── handlers
│   └── main.yml
├── tasks
│   └── main.yml
├── templates
└── vars
    └── main.yml
```

**files 文件夹存放文件**

```
存放 www.qfedu.com.conf 配置文件
```

**handlers 文件夹中的main.yml 文件**

```yaml
---
- name: reload nginx server
  service: name=nginx state=started
  when: nginxsyntax.rc == 0 and nginxrunning.stat.exists == true
```

**tasks 文件夹中的 main.yml 文件**

```yaml
---
- name: create user
  user: name={{ item }} state=present
  with_items: "{{ createuser }}"

- name: yum nginx webserver
  yum: name=nginx state=present

  # use ansible template
- name: update nginx main config
  template: src=nginx.conf.j2 dest=/etc/nginx/
  tags: updateconfig
  notify: reload nginx server
      
- name: add virtualhost config
  copy: src=www.qfedu.com.conf dest=/etc/nginx/conf.d/
  tags: updateconfig
  notify: reload nginx server
      
- name: check nginx syntax
  shell: /usr/sbin/nginx -t
  register: nginxsyntax
  tags: updateconfig
      
- name: check nginx running
  stat: path=/var/lock/subsys/nginx
  register: nginxrunning
  tags: updateconfig
        
- name: print nginx syntax
  debug: var=nginxsyntax
      
- name: start nginx server
  service: name=nginx state=started
  when: nginxsyntax.rc == 0 and nginxrunning.stat.exists == false
```

**templates 文件夹存放模板**

```
存放 nginx.conf.j2 模板
```

**vars 文件夹中的 main.yml 文件**

```yaml
---
createuser:
  - tomcat
  - www
  - mysql
经过以上对PlayBook 的拆分，就形成了一个nginx 的 ROLE。
回到本章开始的问题，当一个数据中心存在多种类型的服务器时，我们可以针对每个类型去单独写一个ROLE，这些ROLE 有可能分给不同的人去开发，这样不但使开发的逻辑变得简单，且开发效率也随着人员的增加而提升。
```

##### 如何在PlayBook中使用 Role

```yaml
Role 本身不能被直接执行，还是需要借助PlayBook进行间接的调用。
- name: a playbook used role
  hosts: all
  roles:
    - nginx
```

##### 如何使用 Galaxy

```
Ansible的galaxy 工具，类似程序员使用的github。运维人员可以将自己编写的Role通过galaxy这个平台进行分享。同样，我们也可以通过galaxy 这个平台去获取一些我们想要的role。官网为:https://galaxy.ansible.com
而ansible-galaxy 则是一个使用 galaxy 命令行的工具。它使我们不用访问galaxy 的网站而获取到需要的内容。
接下来我们将通过 ansible-galaxy 这个命令行去学习galaxy的使用。
```

**获取帮助**

```shell
# ansible-galaxy  --help
Usage: ansible-galaxy [delete|import|info|init|install|list|login|remove|search|setup] [--help] [options] ...

Options:
  -h, --help     show this help message and exit
  -v, --verbose  verbose mode (-vvv for more, -vvvv to enable connection
                 debugging)
  --version      show program's version number and exit
```

**获取具体某个子指令的帮助**

```shell
在 ansible-galaxy  --help 中可以看到子指令
子指令包含: delete|import|info|init|install|list|login|remove|search|setup
ansible-galaxy delete|import|info|init|install|list|login|remove|search|setup --help
# ansible-galaxy install --help
Usage: ansible-galaxy install [options] [-r FILE | role_name(s)[,version] | scm+role_repo_url[,version] | tar_file(s)]

Options:
  -f, --force           Force overwriting an existing role
  -h, --help            show this help message and exit
  -c, --ignore-certs    Ignore SSL certificate validation errors.
  -i, --ignore-errors   Ignore errors and continue with the next specified
                        role.
  -n, --no-deps         Don't download roles listed as dependencies
  -r ROLE_FILE, --role-file=ROLE_FILE
                        A file containing a list of roles to be imported
  -p ROLES_PATH, --roles-path=ROLES_PATH
                        The path to the directory containing your roles. The
                        default is the roles_path configured in your
                        ansible.cfg file (/etc/ansible/roles if not
                        configured)
  -s API_SERVER, --server=API_SERVER
                        The API server destination
  -v, --verbose         verbose mode (-vvv for more, -vvvv to enable
                        connection debugging)
  --version             show program's version number and exit
```

**常用指令**

```shell
// 在galaxy 上搜索共享的ROLE
# ansible-galaxy search
// 安装 galaxy 上共享的 ROLE
# ansible-galaxy install
// 列举已经通过 ansible-galaxy 工具安装的ROLE
# ansible-galaxy list
// 创建一个ROLE 的空目录架构, 这样我们在开发一个ROLE的时候，就不需要手动创建目录了。
# ansible-galaxy init --offline
```

**Example**

```shell
// 创建了名字为testrole的空ROLE目录结构，默认在执行命令的目录生产。
# ansible-galaxy init --offline testrole
# tree testrole/
testrole/
├── defaults
│   └── main.yml
├── handlers
│   └── main.yml
├── meta
│   └── main.yml
├── README.md
├── tasks
│   └── main.yml
├── tests
│   ├── inventory
│   └── test.yml
└── vars
    └── main.yml
```

保存到我的笔记

如