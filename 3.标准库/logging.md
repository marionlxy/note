## Python标准库: logging

-Author: bavdu

-Email: bavduer@163.com

-GitHub: https://github.com/bavdu

---





```python
import logging

# 定义日志输出的位置/级别/格式/增加规则
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(pathname)s - %(message)s',
  	datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.WARNING,
    filename='./example.log',
    filemode='a'
)

try:
    var01, var02 = 'hello', 18
    print(var01 + var02)
except Exception as error:
    logging.error(error)
finally:
    pass

print('go on ...')
```



- logger日志记录器, 暴露给应用使用的接口
- handlers日志处理器, 发送日志记录到指定的位置
- formatters日志格式化, 日志记录格式

```python
import logging.handlers


# 设置日志的记录格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 设置日志处理器,将日志记录器获取的日志放到指定文件
rowHandler = logging.FileHandler(filename='logRecording.log')

# 设置日志处理器,将日志记录器获取的日志放到指定文件,并根据大小进行切割
rotateHandler = logging.handlers.RotatingFileHandler(
    filename='logRotate.log',
    maxBytes=1024 * 1024 * 5,
    backupCount=5
)

# 设置日志处理器,将日志记录器获取的日志文件放到指定文件,并根据时间进行切割
timeHandler = logging.handlers.TimedRotatingFileHandler(
    filename='example.log',
    when='D',
    interval=2,
    backupCount=5
)

# 设置日志处理器处理日志的最低级别
rowHandler.setLevel(logging.WARNING)
# 为日志处理器设置格式化器
rowHandler.setFormatter(formatter)

# 设置日志的记录器,并设置记录器的名字
logger = logging.getLogger('logRecording')
# 设置日志记录器的最低记录级别
logger.setLevel(logging.WARNING)
# 为日志记录器添加处理器
logger.addHandler(rowHandler)


try:
    var01, var02 = 'hello', 18
    print(var01 + var02)
except Exception as error:
    logger.error(error)
finally:
    pass

print('go on ...')
```



- logging.conf 配置文件设置日志

```ini
# @project/logconfig.conf
[formatters]
keys=formatOne
[formatter_formatOne]
format=%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s
datefmt=%a, %Y-%m-%d %H:%M:%S

[handlers]
keys=file,rotateSize
[handler_file]
class=FileHandler
level=DEBUG
formatter=formatOne
args=('logfileName.log', 'a')
[handler_rotateSize]
class=handlers.RotatingFileHandler
level=WARNING
formatter=formatOne
args=('logfileName.log', 'a', 5*1024*1024, 5, None, False)

[loggers]
keys=root,rotate
[logger_root]
handlers=file
[logger_rotate]
handlers=rotateSize
qualname=rotate
propagate =0
```

```python
import logging.config

logging.config.fileConfig('./logconfig.conf')

try:
    var01, var02 = 'hello', 18
    print(var01 + var02)
except Exception as error:
    logger = logging.getLogger('rotateSize')
    logger.error(error)
finally:
    pass

print('go on...')
```

