## Zabbix API

官网API 地址

https://www.zabbix.com/documentation/4.0/zh/manual/api

### 登录

```python
#!/usr/bin/env python
import urllib2
import json
#定义URL账户密码
url = 'http://zabbixip/zabbix/api_jsonrpc.php'
username = 'admin'
password = 'password'
#定义通过HTTP方式访问API地址的函数，后面每次请求API的各个方法都会调用这个函数
def requestJson(url,values):        
    data = json.dumps(values)
    req = urllib2.Request(url, data, {'Content-Type': 'application/json-rpc'})
    response = urllib2.urlopen(req, data)
    output = json.loads(response.read())
#   print output
    try:
        message = output['result']
    except:
        message = output['error']['data']
        print message
        quit()

    return output['result']

#API接口认证的函数，登录成功会返回一个Token
def authenticate(url, username, password):
    values = {'jsonrpc': '2.0',
              'method': 'user.login',
              'params': {
                  'user': username,
                  'password': password
              },
              'id': '0'
              }
    idvalue = requestJson(url,values)
    return idvalue
```

### 操作

```python
#!/usr/bin/env python
#coding=utf-8 
import sys
import argparse
import urllib2
import json

#定义更新action函数
def mediatypeupdate(mediatypeid,status,auth):
    values = {'jsonrpc': '2.0',
              'method': 'mediatype.update',
              'params': {
                  "mediatypeid": mediatypeid,
                  "status": status
              },
              'auth': auth,
              'id': '1'
              }
    output = requestJson(url,values)
#定义读取状态函数
def triggerget(auth):
    values = {'jsonrpc': '2.0',
           "method":"trigger.get",
               "params": {
                        "output": [
                        "triggerid",
                        "description",
                        "priority"
                        ],
              "filter": {
                         "value": 1
                         },
              "expandData":"hostname",
              "sortfield": "priority",
              "sortorder": "DESC"
            },
              'auth': auth,
              'id': '2'
              }
    output = requestJson(url,values)
    return output

#定义通过ip获取主机id的函数
def ipgetHostsid(ip,url,auth):
    values = {'jsonrpc': '2.0',
              'method': 'host.get',
              'params': {
                  'output': [ "host" ], 
                  'filter': {
                      'ip': ip
                  },
              },
              'auth': auth,
              'id': '3'
              }
    output = requestJson(url,values)
    return output
    
#定义通过主机id获取开启关闭监控函数
def idupdatehost(status,hostid,url,auth):
    values = {'jsonrpc': '2.0',
              'method': 'host.update',
              'params': {
                  "hostid": hostid, 
                  "status": status
              },
              'auth': auth,
              'id': '4'
              }
    output = requestJson(url,values)
    return output
#定义通过项目hostid获取itemid函数
def getHostsitemsid(hostid,itemsname,url,auth):
    values = {'jsonrpc': '2.0',
              'method': "item.get",
              "params": {
                    "output": ["itemids"],
                    "hostids": hostid,
            "filter":{
                    "key_": itemsname,
                },
                },
            
              'auth': auth,
              'id': '5'
              }
    output = requestJson(url,values)
    if len(output)==0:
        return output
    else:
        return output[0]['itemid']


#定义通过项目id获取监控项目最近值信息的函数
def getHostsitemsvalue(itemid,url,auth):
    values = {'jsonrpc': '2.0',
              'method': "history.get",
              "params": {
                    "output": "extend",
                    "history":3,
                    "itemids":itemid,
                    "sortfield": "clock",
                    "sortorder": "DESC",
                    "limit":1,
                },
            
              'auth': auth,
              'id': '6'
              }
    output = requestJson(url,values)
    if len(output)==0:
        return output
    else:
        return output[0]["value"]
        
#定义更新读取状态action函数
def mediatypeget(mediatypeid,auth):
    values = {'jsonrpc': '2.0',
              'method': 'mediatype.get',
              'params': {
                "output": "extend",

              "filter": {
                        "mediatypeid":mediatypeid,
                         },
              },

              'auth': auth,
              'id': '7'
              }
    output = requestJson(url,values)
    if len(output)==0:
        return output
    else:
        return output[0]['status']

        
#定义maintenance维修模式host函数
def maintenancecreate(maintenancename,active_since,active_till,hostid,auth):
    values = {'jsonrpc': '2.0',
              'method': 'maintenance.create',
              'params': {
              "name": maintenancename,
              "active_since": active_since,
              "active_till": active_till,
              "hostids": [
                    hostid
                ],
                "timeperiods": [
                            {
                "timeperiod_type": 0,
                "every": 1,
                "dayofweek": 64,
                "start_time": 64800,
                "period": 3600
                            }
                                ]
              },
              'auth': auth,
              'id': '8'
              }
    output = requestJson(url,values)
    
#定义通过模糊获取关闭主机信息函数
def disabledhostget(url,auth):
    values = {'jsonrpc': '2.0',
              'method': 'host.get',
            "params": {
                "output": ["host"],
                'selectInterfaces': [ "ip" ],
                "filter": {
                    "status":1
        }
    },
              'auth': auth,
              'id': '9'
              }
    output = requestJson(url,values)
    return output

#定义maintenance维修模式group函数
def maintenancecreategroup(maintenancename,active_since,active_till,groupid,auth):
    values = {'jsonrpc': '2.0',
              'method': 'maintenance.create',
              'params': {
              "name": maintenancename,
              "active_since": active_since,
              "active_till": active_till,
              "groupids": [
                    groupid
                ],
                "timeperiods": [
                            {
                "timeperiod_type": 0,
                "every": 1,
                "dayofweek": 64,
                "start_time": 64800,
                "period": 3600
                            }
                                ]
              },
              'auth': auth,
              'id': '10'
              }
    output = requestJson(url,values)

#定义通过host groups named 获取groupid
def groupnameGroupid(groupname,auth):
    values = {'jsonrpc': '2.0',
              'method': 'hostgroup.get',
              "params": {
                    "output": "extend",
                    "filter": {
                        "name": [
                            groupname
                        ]
                    }
                },
              'auth': auth,
              'id': '11'
              }
    output = requestJson(url,values)
    return output

#定义模糊查询维护主机
def maintenanceget(url,auth):
    values = {'jsonrpc': '2.0',
              'method': 'maintenance.get',
              "params": {
                    "output": "extend",
                },
              'auth': auth,
              'id': '12'
              }
    output = requestJson(url,values)
    return output

#定义批量恢复处于维护主机
def maintenancedelete(maintenanceid,url,auth):
    values = {'jsonrpc': '2.0',
              'method': 'maintenance.delete',
              "params": [
                    maintenanceid
                ],
              'auth': auth,
              'id': '13'
              }
    output = requestJson(url,values)
    return output

#定义通过hostid获取graphid的函数
def getgraphid(hostid,graphname,url,auth):
        values = {'jsonrpc': '2.0',
                          'method': 'graph.get',
                          'params': {
                                  "output": "name",
                                  "hostids": hostid,
                                  "sortfield": "name",
                          'filter': {
                                        "name": graphname
                                  },

                          },
                          'auth': auth,
                          'id': '14'
                          }
        output = requestJson(url,values)
        return output
```

### 关闭、启用 主机监控

```
#!/usr/bin/env python
#coding=utf-8
import urllib2
import sys
import json
import argparse
from login import *
from function import *
#登陆zabbix获取auth
auth = authenticate(url, username, password)
#状态0是启用监控，1是禁用监控
status=1
#定义操作ip
hostip='192.168.1.100'
#通过hostip获取zabbix hostid
hostids=ipgetHostsid(hostip,url,auth)
hostid=hostids[0]['hostid']
#通过主机id开启关闭监控
idupdatehost(status,hostid,url,auth)
```

\###添加维护周期

```python
#!/usr/bin/env python
#coding=utf-8

import urllib2
import sys
import json
import argparse
import time
from login import *
from function import *

def timetostamp(strtime):
    timeArrary = time.strptime(strtime, "%Y-%m-%d %H:%M")
    return int(time.mktime(timeArrary))

'''
if __name__ == '__main__':
__name__ 是当前模块名，当模块被直接运行时模块名为 __main__ 。
这句话的意思就是，当模块被直接运行时，以下代码块将被运行，当模块是被导入时，代码块不被运行。
在你import别的py文件时，那个py文件会被存一份pyc加速下次装载。而主文件因为只需要装载一次就没有存pyc
'''

#登陆zabbix获取auth
auth = authenticate(url, username, password)

hostip='10.10.10.10'
groupname='Zabbix Agent'

#通过hostip获取zabbix hostid
hostids=ipgetHostsid(hostip,url,auth)
hostid=hostids[0]['hostid']

#通过groupname获取zabbix groupid
groupids=groupnameGroupid(groupname,auth)
groupid=groupids[0]['groupid']


# 名称，描述，注意name不能重复
name='Zabbix Agent group更新维护'
desc = "这是一次全服更新维护，请悉知！"

# 维护时间
dt_since = '2018-01-18 11:25'
dt_till = '2018-01-18 13:25'
active_since = timetostamp(dt_since)
active_till = timetostamp(dt_till)

# 开始生效时间
dt_start = '2018-01-18 12:30'
start_date = timetostamp(dt_start)

# 持续时间，单位秒
period = 600
print 'period=%ds' % period

if __name__ == '__main__':
    maintenancecreate(name,active_since,active_till,desc,hostid,start_date,period,auth)
    maintenancecreategroup(name,active_since,active_till,desc,groupid,start_date,period,auth)
```