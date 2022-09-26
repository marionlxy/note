## Ansible执行速度优化

-Author: bavdu

-Mail: bavduer@163.com

-Github: https://github.com/bavdu

---



**/* *优化一: 开启SSH长连接* */**

Ansible模式是使用SSH和远程主机进行通信, 所以Ansible对SSH的依赖性非常强, 在OpenSSH 5.6版本以后SSH就支持了Multiplexing, 关于这个特性我们可以参考 [Multiplexing手册](https://en.wikibooks.org/wiki/OpenSSH/Cookbook/Multiplexing). 所以如果Ansible中控机的SSH -V版本高于5.6时, 我们可以直接在ansible.cfg文件中设置SSH长连接, 设置参数如下:

`ssh_args = -C -o ControlMaster=auto -o ControlPersist=5d`

ConrolPersist=5d, 这个参数是设置整个长连接保持时间为5天.

开启此参数后, 通过SSH连接过的设备都会在当前ansible/cp/目录下生成一个socket文件. 也可以通过netstat命令查看, 会发现有一个ESTABLISHED状态的连接一直与远程设备进行着TCP连接

`netstat -anptu `



**/* *优化二: 开启Pipelining* */**

pipelining也是OpenSSH的一个特性, 在Ansible的整个执行流程中, 把生成好的本地python脚本PUT到远程服务器. **如果开启了pipelining, 这个过程将在SSH会话中进行, 这样可以大大提高整个执行效率.** 当然开启pipelining, 需要被控机/etc/sudoers文件编辑当前Ansible SSH用户的配置为requiretty. 否则在执行Ansible的时候会提示报错.

```shell
bavdu@ansible:~$ sudo vim /etc/ansible/ansible.cfg
pipelining = True
```

这样开启了pipelining之后, ansible执行的整个流程就少了一个PUT脚本去远程服务端的流程



 **/* *优化三: 开启accelerate模式* */**

Ansible还有一个accelerate模式, 这和前面的Multiplexing有点类似, 因为都依赖Ansible中控机跟远程机器有一个长连接. 但是accelerate是使用python程序在远程机器上运行一个守护进程, 然后Ansible会通过这个守护进程监听的端口进行通信. 开启accelerate模式很简单, 只要在playbook中配置accelerate: true即可. 

但是需要注意的是: 如果开启accelerate模式, 则需要在Ansible中控机与远程机器都安装python-keyczar软件包. 下面是在ansible.cfg文件中定义一些accelerate参数, 当然也可以在写playbook的时候再定义

> [accelerate]
>
> accelerate_port = 5099
>
> accelerate_timeout = 30
>
> accelerate_connect_timeout = 5.0



**/* *优化四: 设置facts缓存* */**

如果细心的话, 就会发现执行playbook的时候, 默认第一个task都是GATHERING FACTS, 这个过程就是Ansible在收集每台主机的facts信息. 方便我们在playbook中直接饮用facts里的信息. 当然如果你的playbook中不需要facts信息, 可以在playbook中设置gather_facts: False来提高playbook效率. 

但是如果我们既想在每次执行playbook的时候都能收集facts, 又想加速这个收集过程, 那么就需要配置facts缓存了. 目前Ansible支持使用json文件存储facts信息. 如下设置示例:/etc/ansible/ansible.cfg

> gathering = smart
>
> fact_caching_timeout = 86400
>
> fact_caching = jsonfile
>
> fact_caching_connection = /dev/shm/ansible_fact_cache
