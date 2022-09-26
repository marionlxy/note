## Python三方模块: psutil

-Author: bavdu

-Email: bavduer@163.com

-GitHub: https://github.com/bavdu

---



##### psutil模块简介及安装

---

psutil是用来获取系统信息的第三方模块; 可以用来监控CPU/Memory/Disk/Network, 并且返回的信息很容易被调用, 常常用来作为系统监控信息的来源API库. 使用起来相当简洁; 搭配*paramiko*模块可以获取远程的主机信息

- 检测psutil是否安装在了系统中

  ```python
  $ pip list | grep psutil
  $ echo $?
  # 若返回值是非0数,则证明未安装,执行下列命令进行安装
  $ pip install --upgrade pip
  $ pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
  $ pip install psutil
  ```



##### psutil获取cpu信息

---

使用psutil获取CPU信息有以下函数:

- `cpu_count(logical=True)` - 获取*cpu*逻辑核心数
- `cpu_percent(interval=1, percpu=True)` - 获取*cpu*整体占用情况
- `cpu_times(percpu=True)` - 获取*cpu*时间占用信息
- `cpu_times_percent(interval=1, percpu=True)` - 获取*cpu*各个部分占用百分比情况

```python
import psutil

# logical=True/False[True:逻辑核心数;False:物理核心数;]
print('CPU的核心数为: {}'.format(psutil.cpu_count(logical=True)))

# interval=[(values > 0.0):间隔起始和间隔结束的cpu时间进行比较;(percpu=True):对每个cpu进行单独统计]
print('CPU的整体占用情况: {}'.format(psutil.cpu_percent(interval=1, percpu=False)))
print('CPU的单核占用情况: {}'.format(psutil.cpu_percent(interval=1, percpu=True)))

# percpu=True/False[True:每个cpu的时间占用时间情况;False:整体cpu的时间占用时间情况]
print('CPU的整体占用情况: {}'.format(psutil.cpu_times(percpu=False)))
print('CPU的单核占用情况: {}'.format(psutil.cpu_times(percpu=True)))

# interval=[(values > 0.0):间隔起始和间隔结束的cpu时间进行比较;(percpu=True):对每个cpu进行单独统计]
print('CPU的整体各部分占比情况: {}'.format(psutil.cpu_times_percent(interval=1, percpu=False)))
print('CPU的单核各部分占比情况: {}'.format(psutil.cpu_times_percent(interval=1, percpu=True)))
```



采集*cpu*信息后注入数据模板中,方便json格式化,传递到前端; 在实际开发的场景中需要按照前端规定的数据格式制定数据模板; 可以根据*interval*规定的时长来获取某时段内的*cpu*的变化值; 可以使用*pyecharts*库来实现数据可视化

```json
import json
import time
import psutil

date = time.strftime('%Y%m%d%H%M%S', time.localtime())
data = [{
  date: {
    'user': cpuInfo.user,
    'system': cpuInfo.system,
    'iowait': cpuInfo.iowait,
    'idle': cpuInfo.idle
  }}]

sendData = json.dumps(data)
...
```

```python
import pyecharts
import psutil


def cpuInfo(timeLong):
    cpu = psutil.cpu_times_percent(interval=timeLong)
    data, cpus = [], {'user': cpu.user, 'system': cpu.system, 'iowait': cpu.iowait, 'idle': cpu.idle}
    for element in cpus.items():
        data.append(element)
    return data


print(cpuInfo(1))
picture = pyecharts.charts.Pie()
picture.add(
    series_name='cpu:ipAddress',
    data_pair=cpuInfo(10),
    is_clockwise=True
)
picture.render()
```



##### psutil获取Memory信息

---

使用psutil获取memory信息有如下函数:

- `virtual_memory()` - 查看物理内存的信息
- `swap_memory()` - 查看交换分区的信息

```python
import psutil


print(psutil.virtual_memory())

		total              - 物理内存总容量(bit)
    available          - 不需要进行内存交换(swap)可直接分配给进程的内存容量
    used               - 已用内存(仅供参考) total-free不一定等于used
    free               - 没有被使用的内存,不代表实际可用内存
    active(UNIX)       - 使用中或最近使用的内存
    inactive(UNIX)     - 被标记为未被使用的内存
    buffers(Linux BSD) - 用于文件系统等元数据的缓存
    cached(Linux BSD)  - 当做各种情况下的缓存
    shared(Linux BSD)  - 可被多个进程同时访问的内存
    slab(Linux)        - 内核数据结构缓存
```

```python
import psutil


print(psutil.swap_memory())

		total   - 以bytes表示的交换内存总容量
    used    - 以bytes表示的已使用的交换内存总容量
    free    - 以bytes表示的空间交换内存容量
    percent - 交换内存使用率
    sin     - 以bytes表示的从磁盘交换到内存的容量(累积的),Windows上为0    
    sout    - 以bytes表示的从内存交换到磁盘的容量(累积的),Windows上为0
```



##### psutil获取disk信息

---

使用psutil获取disk信息有如下函数:

- `psutil.disk_partitions()` -  获取磁盘整体情况
- `psutil.disk_usage('/')` -  获取指定分区的使用情况

```python
import psutil


print(psutil.disk_partitions())

		device     - 设备
    mountpoint - 挂载点
    fstype     - 文件系统类型
    opts       - 其它选项
```

```python
import psutil


print(psutil.disk_usage('/'))

		total - 分区总容量(bytes)
    used  - 分区已用容量(bytes)
    free  - 分区空闲容量(bytes)
    percentage - 分区使用百分比
```



##### psutil获取Network信息

---

使用psutil获取Network有如下函数:

- `net_io_counters(pernic=False, nowrap=True)` - 返回系统级别的网络*I/O*统计信息
- `net_connections(kind='inet')` - 返回系统的*socket*连接信息
- `net_if_stats()` - 返回每块网卡的状态信息

```python
import psutil


print(psutil.net_io_counters())

			bytes_sent   - 发送字节数
      bytes_recv   - 接收字节数
      packets_sent - 发送packet数量
      packets_recv - 接收packet数量
      errin        - 接收错误数
      errout       - 发送错误数
      dropin       - 接收丢包数
      dropout      - 发送丢包数
```

```python
import psutil


print(psutil.net_connections(kind='inet'))

			fd     - socket描述符
      family - 地址族
      type   - 地址类型
      laddr  - 本地地址(ip,port)或AF_UNIX路径
      raddr  - 远端地址(ip,port)或UNIX sockets绝对路径
      satus  - TCP连接状态
      pid		 - 开启socket的进程的进程ID(pid)
      
	kind:
       "inet"          IPv4 and IPv6
       "inet4"         IPv4
       "inet6"         IPv6
       "tcp"           TCP
       "tcp4"          TCP of IPv4
       "tcp6"          TCP of IPv6
       "udp"           UDP
       "udp4"          UDP of IPv4
       "udp6"          UDP of IPv6
```

```python
import psutil


print(psutil.net_if_stats())

			 isup   - 网卡是否启动并运行
       duplex - NIC_DUPLEX_FULL(全双工) NIC_DUPLEX_HALF(半双工) NIC_DUPLEX_UNKNOWN(未知)
       speed  - 网络速度(MB),如果不能获取则被设置为0
       mtu    - 以bytes表示的最大传输单元
```



##### psutil获取pid信息

---

psutil模块使用`psutil.pids()`方法获取所有进程*PID*, 使用`psutil.Process()`方法获取单个进程的名称、路径、状态、系统资源利用率等信息

```python
import psutil


allPid = psutil.pids()
# print(allPid)
process = psutil.Process(25766)
print(process.name())               # 获取进程名字
print(process.exe())                # 获取进程执行路径
print(process.status())             # 获取进程状态
print(process.num_threads())        # 获取进程开启的线程数
print(process.create_time())        # 获取进程创建时间
print(process.cpu_times())          # 获取user、system两个 CPU 时间
print(process.memory_percent())     # 获取进程内存利用率
print(process.memory_info())        # 获取进程内存rss、vms信息
print(process.io_counters())        # 进程IO信息,包括读写IO数及字节数
```

