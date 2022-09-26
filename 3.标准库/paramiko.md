##Python第三方模块: paramiko

-Author: bavdu

-Email: bavduer@163.com

-Github: https://github.com/bavdu

---

paramiko是基于SSH协议用于连接远程服务器并执行相关操作(SSHClient和SFTPClinet,即远程连接/上传下载务)的服务;   使用该模块可以对远程服务器进行命令或文件操作,  ansible内部的远程管理就是使用的paramiko来现实现的;

```python
# 基于用户名和密码连接远程服务器

import paramiko


client = paramiko.SSHClient()		# ssh root@192.168.161.10
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(
    hostname='1.1.1.1',
    port=22,
    username='root',
    password='xxxxxxxx'
)

stdin, stdout, stderr = client.exec_command(command='hostname', timeout=0.03)
print(stdout.read().decode('utf-8'))

client.close()
```

```python
# 基于秘钥对儿连接远程服务器
import paramiko

private = paramiko.RSAKey.from_private_key_file('/Users/chaoliu/.ssh/id_rsa')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(
    hostname='39.100.110.135',
    port=22,
    username='root',
    pkey=private
)

stdin, stdout, stderr = client.exec_command('hostname')
print(stdout.read().decode('utf-8'))

client.close()
```

```python
# 基于加密通道传输
import paramiko

private = paramiko.RSAKey.from_private_key_file('/Users/chaoliu/.ssh/id_rsa')
transport = paramiko.Transport(('39.100.110.135', 22))
transport.connect(username='root', pkey=private)
client = paramiko.SSHClient()
client._transport = transport

stdin, stdout, stderr = client.exec_command('hostname')
print(stdout.read().decode('utf-8'))

transport.close()
```

```python
# 基于加密通道进行上下传文件
import paramiko

private = paramiko.RSAKey.from_private_key_file('/Users/chaoliu/.ssh/id_rsa')
transport = paramiko.Transport(('39.100.110.135', 22))
transport.connect(username='root', pkey=private)

sftp = paramiko.SFTPClient.from_transport(transport)

sftp.put('/Users/chaoliu/Downloads/Books/docker_practice.pdf', '/opt/docker_practice.pdf')
sftp.get('/opt/docker_practice.pdf', './a.pdf')

transport.close()
```



#####思考题: paramiko模块获取远程机器的系统信息

---

```shell
#!/usr/bin/env bash
#
# author: bavdu
# date: 2019/07/27
# usage: monitor cpu status

DATE=$(date +'%Y-%m-%d %H:%M:%S')
IPADDR=$(ifconfig | grep inet | awk 'BEGIN{ FS=" " }NR==1{ print $2 }')
MAIL="bavduer@163.com"

# 检测vmstat命令是否存在
if ! which vmstat &>/dev/null; then
	yum -y install procps-ng &>/dev/null
	if [ $? -eq 0 ];then
		echo "vmstat already installed"
	fi
fi

US=$(vmstat | awk 'BEGIN{ FS=" " }NR==3{ print $13 }')
SY=$(vmstat | awk 'BEGIN{ FS=" " }NR==3{ print $14 }')
ID=$(vmstat | awk 'NR==3{ print $15 }')
WA=$(vmstat | awk 'NR==3{ print $16 }')
ST=$(vmstat | awk 'NR==3{ print $17 }')

useTotal=$( (${US}+${SY}) )
if [[ ${useTotal} -ge 70 ]];then
	echo "
	Date: ${DATE}
	Host: ${HOSTNAME}: ${IPADDR}
	Problem: CPU using rate: ${useTotal}%
	" | mail -s "CPU Monitor Warnning" ${MAIL}
fi
```

```shell
#!/usr/bin/env bash
#
# author: bavdu
# date: 2019/07/27
# usage: monitor memory status

DATE=$(date +'%Y-%m-%d %H:%M:%S')
IPADDR=$(ifconfig | grep inet | awk 'BEGIN{ FS=" " }NR==1{ print $2 }')
MAIL="bavduer@163.com"

TOTAL=$(free -mw | awk 'NR==2{ print $2 }')
USE=$(free -mw | awk 'BEGIN{ FS=" " }NR==2{ print $3 }')
FREE=$(free -mw | awk 'BEGIN{ FS=" " }NR==2{ print $4 }')
CACHE=$(free -mw | awk 'BEGIN{ FS=" " }NR==2{ print $7 }')
useRate=$(echo "((${USE}+${CACHE})/${TOTAL})*100" | bc -ql)
freeRate=$(echo "(${FREE}/${TOTAL})*100" | bc -ql)

if [[ ${FREE} -le 100 ]];then
  echo "
	Date: ${DATE}
	Host: ${HOSTNAME}: ${IPADDR}
	Problem: 
		Memory using rate: ${useRate: 0: 5}%
		Memory free rate: ${freeRate: 0: 5}%
	" | mail -s "CPU Monitor Warnning" ${MAIL}
fi
```

```shell
#!/usr/bin/env bash
#
# author: bavdu
# date: 2019/07/27
# usage: monitor memory status

DATE=$(date +'%Y-%m-%d %H:%M:%S')
IPADDR=$(ifconfig | grep inet | awk 'BEGIN{ FS=" " }NR==1{ print $2 }')
MAIL="bavduer@163.com"

useRate=$(df -Th | awk 'BEGIN{ FS=" " }NR==2{ print $6 }')

if [[ ${useRate: 0: 2} -ge 90 ]];then
	echo "
	Date: ${DATE}
	Host: ${HOSTNAME}: ${IPADDR}
	Problem: 
		Memory using rate: up ${useRate: 0: 2}
	" | mail -s "CPU Monitor Warnning" ${MAIL}
fi
```



