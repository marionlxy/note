##Python标准库: subprocess

-Author: bavdu

-Email: bavduer@163.com

-Github: https://github.com/bavdu

---



##### subprocess模块主要用于创建子进程, 并连接它们的输入/输出/错误管道, 获取它们的返回状态. 通俗地说就是通过这个模块, 你可以在Python的代码里执行操作系统级别的命令, 比如“ifconfig”、“du -sh”等等;

```python
import subprocess


# 执行系统shell命令
subprocess.run(['du', '-sh'])
subprocess.run('du -sh', shell=True)

# 获取系统shell命令执行后的结果
result = subprocess.run('du -sh', shell=True, stdout=subprocess.PIPE)
print(result, type(result))
```

subprocess.Popen

- args: 命令,可以是字符串或者可迭代对象(列表/元组)
- bufsize: 缓冲区大小(基本用不到)
- stdin,stdout,stderr: 分别表示程序的标准输入/标准输出/标准错误
- shell: 指定是否使用本地系统shell执行命令(True/False)
- cwd: 用于设置子进程的当前目录
- env: 用于指定子进程的环境变量(默认从父进程继承环境变量)
- universal_newlines: 不同系统的的换行符不同,当该参数设定为True时,则表示使用\n作为换行符

```python
# 在当前目录下创建subtotal目录
subprocess.Popen('mkdir subtotal', shell=True, cwd='Github/pysement')

# 获取命令的输出结果
result = subprocess.Popen(['cat', '/etc/passwd'], stdout=subprocess.PIPE)
print(result.stdout.read())
result.stdout.close()

# 将子程序的输出, 输入到另一个子程序中
child01 = subprocess.Popen('pip list', shell=True, stdout=subprocess.PIPE)
child02 = subprocess.Popen(['grep', 'paramiko'], stdin=child01.stdout, stdout=subprocess.PIPE)
print(child02.stdout.read())
child02.stdout.close()
```



