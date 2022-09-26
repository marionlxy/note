import logging.config
import pymysql.cursors
import json
import requests


logging.config.fileConfig('cnf/logging.conf')
logger = logging.getLogger('rotate')


def analysis(cpu=85, memory=90, disk=90, logpath='./log/monitor.log'):
    with open(file=logpath, mode='r') as log:
        for lines in log.readlines():
            data = json.loads(lines.split('-')[-1])
            for items in data.items():
                if items[0] == 'cpu':
                    if items[0]['user'] + items[0]['system'] > cpu:
                        logger.warning('cpu usage rate: {}'.format(items[0]['user'] + items[0]['system']))
                elif items[0] == 'memory':
                    if items[0]['percent'] > memory:
                        logger.warning('memory usage rate: {}'.format(items[0]['percent']))
                elif items[0] == 'disk':
                    if items[0]['percent'] > disk:
                        logger.warning('disk usage rate: {}'.format(items[0]['percent']))


def dingtalk(token, logpath='./log/monitor.log'):
    api = 'https://oapi.dingtalk.com/robot/send?access_token={}'.format(token)
    header = {'Content-Type': 'application/json'}

    def info(messages, phone):
        data = {"msgtype": "text", "text": {"content": "{}".format(messages)}, 'at': {'atMobiles': ["{}".format(phone)]}, 'isAtAll': 'false'}
        sendData = json.dumps(data).encode('utf-8')
        return sendData

    with open(file=logpath, mode='r') as log:
        for lines in log.readlines():
            content = json.loads(lines.split('-')[-1])
            for items in content.items():
                if items[0] == 'cpu':
                    if items[0]['user'] + items[0]['system'] > 80:
                        requests.post(url=api, headers=header, data=info(
                            messages='[warning]: cpu rate: {}'.format(items[0]['user'] + items[0]['system']),
                            phone='15222401953'     # 写一个读取排班表格的函数获取返回值
                        ))
                elif items[0] == 'memory':
                    if items[0]['percent'] > 90:
                        requests.post(url=api, headers=header, data=info(
                            messages='[warning]: memory rate: {}'.format(items[0]['percent']),
                            phone='15222401953'
                        ))
                elif items[0] == 'disk':
                    if items[0]['percent'] > 90:
                        requests.post(url=api, headers=header, data=info(
                            messages='[warning]: disk rate: {}'.format(items[0]['percent']),
                            phone='15222401953'
                        ))


def record(serverIP, dbUser, dbPasswd, port=3306, db='monitor', logpath='./log/monitor.log'):
    """
    {
        "cpu": {"user": 1, "system": 0, "idle": 99},
        "memory": {"total": 972, "free": 177, "percent": 80.0},
        "disk": {"percent": "13%"}
    }
    """
    client = pymysql.connect(host=serverIP, user=dbUser, password=dbPasswd, db=db, port=port)
    try:
        with client.cursor() as cursors:
            with open(file=logpath, mode='r') as log:
                for lines in log.readlines():
                    hostname = lines.split('-')[-2]
                    times = int(lines.split('-')[0])
                    content = json.loads(lines.split('-')[-1])
                    for items in content.items():
                        if items[0] == 'cpu':
                            sql = "insert into cpu values ({}, '{}', {}, {}, {});"
                            cursors.execute(sql.format(times, hostname, items[0]['user'], items[0]['system'], items[0]['idle']))
                        elif items[0] == 'memory':
                            sql = "insert into memory values ({}, '{}', {}, {});"
                            cursors.execute(sql.format(times, hostname, items[0]['free'], items[0]['percent']))
                        elif items[0] == 'disk':
                            sql = "insert into memory values ({}, '{}', {});"
                            cursors.execute(sql.format(times, hostname, items[0]['percent']))
    finally:
        client.commit()
        client.close()
