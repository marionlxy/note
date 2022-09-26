### elastalert rules 调整

[官网手册地址](https://app.yinxiang.com/OutboundRedirect.action?dest=https%3A%2F%2Felastalert.readthedocs.io%2Fen%2Flatest%2Frunning_elastalert.html)

#### 环境需求

- python3.6
- centos7
- git

#### 安装部署

```shell
## git clone 程序代码
git clone https://github.com/Yelp/elastalert.git
## 程序需要环境
$ pip3 install "setuptools>=11.3"
$ python3 setup.py install
## 使用qq上传的python3 虚拟环境即可
```

- 创建所需要的es index

```shell
source 虚拟环境路径

elastalert-create-index

(elastalert) [root@new ~]# elastalert-create-index
Enter Elasticsearch host: 10.36.145.187 ##填写es地址
Enter Elasticsearch port: 9200 ## 添加es 端口
Use SSL? t/f: ## 后面全部回车即可
Enter optional basic-auth username (or leave blank): 
Enter optional basic-auth password (or leave blank): 
Enter optional Elasticsearch URL prefix (prepends a string to the URL of every request): 
New index name? (Default elastalert_status) 
New alias name? (Default elastalert_alerts) 
Name of existing index to copy? (Default None) 
Elastic Version: 7.2.0
Reading Elastic 6 index mappings:
Reading index mapping 'es_mappings/6/silence.json'
Reading index mapping 'es_mappings/6/elastalert_status.json'
Reading index mapping 'es_mappings/6/elastalert.json'
Reading index mapping 'es_mappings/6/past_elastalert.json'
Reading index mapping 'es_mappings/6/elastalert_error.json'
New index elastalert_status created
Done!
```

- 修改配置文件

```shell
/opt/elastalert

cp config.yaml.example config.yaml
vi config.yaml
文件内容修改
run_every:
  minutes: 1

buffer_time:
  minutes: 15

es_host: log.example.com ## es地址

es_port: 9200 ## es端口

use_ssl: True

es_send_get_body_as: GET

es_username: es_admin

es_password: es_password

writeback_index: elastalert_status

alert_time_limit:
  days: 2
```

- 配置报警规则

```shell
cd example_rules/

sudo cp example_frequency.yaml my_rule.yaml

sudo vi my_rule.yaml
```

- 创建报警规则文件

```yaml
es_host: log.example.com
es_port: 9200
use_ssl: True
es_username: es_admin
es_password: es_password
#name属性要求唯一，这里最好能标示自己的产品
name: My-Product Exception Alert
#类型，我选择任何匹配的条件都发送邮件警告
type: any
#需要监控的索引，支持通配
index: logstash-*
#下面两个随意配置
num_events: 50
timeframe:
  hours: 4
#根据条件进行过滤查询（这里我只要出现异常的日志，并且排除业务异常（自定义异常））
filter:
- query:
    query_string:
      query: "message:"
#email的警告方式
alert:
- "email"

#增加邮件内容，这里我附加一个日志访问路径
alert_text: "Ref Log https://log.example.com:5601/app/kibana"
#SMTP协议的邮件服务器相关配置（我这里是腾讯企业邮箱）
smtp_host: smtp.exmail.qq.com
smtp_port: 25
#用户认证文件，需要user和password两个属性
smtp_auth_file: smtp_auth_file.yaml
email_reply_to: no-reply@example.com
from_addr: no-reply@example.com

#需要接受邮件的邮箱地址列表
email:
- "user1@example.com"
- "user1@example.com"
```

- mysql慢日志 利用 query_time 大于报警

报警的 rules

```yaml
vim /opt/elastalert/example_rules/my_rule.yaml
# Alert when the rate of events exceeds a threshold

# (Optional)
# Elasticsearch host
es_host: 172.16.249.101

# (Optional)
# Elasticsearch port
es_port: 9200

# (OptionaL) Connect with SSL to Elasticsearch
#use_ssl: True

# (Optional) basic-auth username and password for Elasticsearch
#es_username: someusername
#es_password: somepassword

# (Required)
# Rule name, must be unique
name: mysql-slow

# (Required)
# Type of alert.
# the frequency rule type alerts when num_events events occur with timeframe time
type: frequency

# (Required)
# Index to search, wildcard supported
index: mysql-slow-*

# (Required, frequency specific)
# Alert when this many documents matching the query occur within a timeframe
num_events: 1

# (Required, frequency specific)
# num_events must occur within this amount of time to trigger an alert
timeframe:
  hours: 4

# (Required)
# A list of Elasticsearch filters used for find events
# These filters are joined with AND and nested in a filtered query
# For more info: http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/query-dsl.html
filter:
- query_string:
    query: "query_time >=0.5"  ## mysql slow  大于0.5s 报警。
#- term:
#    some_field: "some_value"

# (Required)
# The alert is use when a match is found
alert:
- "email"

#增加邮件内容，这里我附加一个日志访问路径
alert_text: "Ref Log https://log.example.com:5601/app/kibana"
#SMTP协议的邮件服务器相关配置（我这里是腾讯企业邮箱）
smtp_host: smtp.163.com
smtp_port: 25
#用户认证文件，需要user和password两个属性
smtp_auth_file: ../smtp_auth_file.yaml ##创建相应的文件
email_reply_to: liuwenqi7011@163.com
from_addr: liuwenqi7011@163.com

# (required, email specific)
# a list of email addresses to send alerts to
email:
- "liuwenqi7011@163.com"
```

- 邮箱账户和密码

```yaml
vim /opt/elastalert/smtp_auth_file.yaml
user: "liuwenqi7011@163.com"
password: "xxxxxx"
```

- 启动

```shell
cd /opt/elastalert
## 测试rule 报警规则是否有问题
elastalert-test-rule example_rules/my_rule.yaml
## 启动报警
python3 -m elastalert.elastalert --verbose --rule example_rules/my_rule.yaml
## 放入后台

nohup python3 -m elastalert.elastalert --verbose --rule example_rules/my_rule.yaml&

## 启用多个报警
nohup python3 -m elastalert.elastalert --verbose --rule example_rules/mysql_slow.yaml&
nohup python3 -m elastalert.elastalert --verbose --rule example_rules/nginx_http_code.yaml&
```

- 报错信息日志

```shell
python3 -m elastalert.elastalert --verbose --rule example_rules/my_rule.yaml
```

**执行报警rules报错信息**

```shell
(elastalert) [root@new ~]# python3 -m elastalert.elastalert --verbose --rule example_rules/my_rule.yaml
Traceback (most recent call last):
  File "/usr/local/python3/lib/python3.7/runpy.py", line 193, in _run_module_as_main
    "__main__", mod_spec)
  File "/usr/local/python3/lib/python3.7/runpy.py", line 85, in _run_code
    exec(code, run_globals)
  File "/data/env/elastalert/lib/python3.7/site-packages/elastalert-0.2.1-py3.7.egg/elastalert/elastalert.py", line 31, in <module>
    from .alerts import DebugAlerter
  File "/data/env/elastalert/lib/python3.7/site-packages/elastalert-0.2.1-py3.7.egg/elastalert/alerts.py", line 26, in <module>
    from jira.client import JIRA
  File "/data/env/elastalert/lib/python3.7/site-packages/jira/__init__.py", line 10, in <module>
    from jira.client import Comment  # noqa: E402
  File "/data/env/elastalert/lib/python3.7/site-packages/jira/client.py", line 225
    validate=False, get_server_info=True, async=False, logging=True, max_retries=3, proxies=None,
                                              ^
SyntaxError: invalid syntax
```

**解决方案**

```shell
cd /data/env/elastalert/lib/python3.7/site-packages/
mv jira jira.bak
INFO:elastalert:Queried rule mysql-slow from 2019-11-09 16:46 CST to 2019-11-09 16:50 CST: 3 / 3 hits
ERROR:root:Traceback (most recent call last):
  File "/opt/elastalert/elastalert/elastalert.py", line 1451, in alert
    return self.send_alert(matches, rule, alert_time=alert_time, retried=retried)
  File "/opt/elastalert/elastalert/elastalert.py", line 1545, in send_alert
    alert.alert(matches)
  File "/opt/elastalert/elastalert/alerts.py", line 491, in alert
    self.smtp.sendmail(self.from_addr, to_addr, email_msg.as_string())
  File "/usr/local/python3/lib/python3.7/smtplib.py", line 867, in sendmail
    raise SMTPSenderRefused(code, resp, from_addr)
smtplib.SMTPSenderRefused: (553, b'Mail from must equal authorized user', 'mysql-slow@liuwenqi.com')
```

**上面报错信息为 smtp 配置问题**

```shell
INFO:elastalert:Queried rule mysql-slow from 2019-11-09 16:50 CST to 2019-11-09 16:53 CST: 1 / 1 hits
INFO:elastalert:Sent email to ['liuwenqi7011@163.com']
INFO:elastalert:Ran mysql-slow from 2019-11-09 16:50 CST to 2019-11-09 16:53 CST: 1 query hits (0 already seen), 1 matches, 1 alerts sent
```

**成功发送标识**

