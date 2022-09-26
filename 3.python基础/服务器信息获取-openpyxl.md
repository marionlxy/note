## 项目实战: 服务器信息获取

-Author: bavdu

-Email: bavduer@163.com

-GitHub: https://github.com/bavdu

---



##### Python3邮件发送器

---

在企业环境中我们常用邮件作为**<u>报警信息/服务器健康状态信息</u>**的载体, 而在Python程序中发送邮件也是常常有的需求, 掌握邮件的发送技巧后可以很好的应对企业中的需求

```python
import yagmail


# 建立发送客户端
sendClient = yagmail.SMTP(user='yourname@163.com',
                          password='xxxxxx',
                          host='smtp.163.com')
# 创建邮件正文
contents = [
    'this is test message.',
    'please ~ not use callback.'
]
# 发送邮件并添加附件
sendClient.send(to=['address1', 'address2'],
                subject='[python]Test email send',
                contents=contents,
                attachments=['getinfo.py', 'README.md'])
```



##### 服务器信息采集

---

```python
import psutil
import openpyxl


cpuInfo = psutil.cpu_times_percent(interval=1, percpu=True)
memInfo = psutil.virtual_memory()
diskInfo = psutil.disk_usage('/')

workbook = openpyxl.Workbook()
sheet = workbook.create_sheet(title='cpu', index=0)
sheet.append(('user(%)', 'nice(%)', 'system(%)', 'idle(%)'))
for info in cpuInfo:
    sheet.append(info)

sheet = workbook.create_sheet(title='memory', index=1)
sheet.append(('used(M)', 'free(M)', 'total(M)'))
sheet.append((
        '{:.2f}'.format(memInfo.used/1024/1024),
        '{:.2f}'.format(memInfo.free/1024/1024),
        '{:.2f}'.format(memInfo.total/1024/1024),
))

sheet = workbook.create_sheet(title='disk', index=2)
sheet.append(('used(G)', 'free(G)', 'total(G)'))
sheet.append((
    '{:.2f}'.format(diskInfo.used/1024/1024/1024),
    '{:.2f}'.format(diskInfo.free/1024/1024/1024),
    '{:.2f}'.format(diskInfo.total/1024/1024/1024),
))
workbook.save('monitorInfo.xlsx')
```

##### 通过推送程序来监控远程主机

```python
# 物料准备
#		1. 安装好Python3环境的机器
#		2. 写好的信息获取agent程序(psutil)
#		3. 本地远程控制程序(paramiko)
```

```shell
#!/usr/bin/env bash
#
# usage: deploy python3.7.4 environment
# path: monitor/shellScripts/py3env.sh

if [ $USER != root ];then
	echo "please use root user opera scripts!"
	exit 213
fi
rpm -qa | grep wget
if [ $? -ne 0 ];then
	yum -y install wget
fi
wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tar.xz -O /opt/Python-3.7.4.tar.xz
if [ $? -eq 0 ];then
	tar xf /opt/Python-3.7.4.tar.xz -C /opt/
	
fi

cd /opt/Python-3.7.4
if [ $PWD == /opt/Python-3.7.4 ];then
	./configure --enable-shared && make && make install
fi

echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib' >/etc/profile.d/py3env.sh
echo '/usr/local/lib' >/etc/ld.so.conf.d/py3env.conf
if [ $? -eq 0 ];then
  ldconfig
  source /etc/profile
fi

exit 0
```





##### webserver日志采集

```python
import time
import paramiko


def getLog(user, keypath, ip, port):
    transport = paramiko.Transport((ip, port))
    transport.connect(username=user, pkey=keypath)
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get(remotepath='/var/log/nginx/error.log',
                 localpath='/local/path/error-{}.log'.format(time.strftime('%Y%m%d%H%M%S')))
    finally:
        transport.close()
```

