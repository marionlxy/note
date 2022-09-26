#!/usr/bin/python3

# -*-coding:utf-8 -*-
# @Time    : 2019/11/26 09:43
# @File    : ansible_example.py
# @User    : kame
# !/usr/bin/env python
# 自定义 ansible 执行及返回状态类相关写法
# 使用ansible 模块

import json
import shutil
# 主要作用与拷贝文件用的、删除等
from ansible.module_utils.common.collections import ImmutableDict
# 用于添加选项。比如: 指定远程用户remote_user=None
from ansible.parsing.dataloader import DataLoader
# 读取 json/yaml/ini 格式的文件的数据解析器
from ansible.vars.manager import VariableManager
# 管理主机和主机组的变量管理器
from ansible.inventory.manager import InventoryManager
# 管理资源库的，可以指定一个 inventory 文件等
from ansible.playbook.play import Play
# 用于执行 Ad-hoc 的类 ,需要传入相应的参数
from ansible.executor.task_queue_manager import TaskQueueManager
# ansible 底层用到的任务队列管理器
from ansible.plugins.callback import CallbackBase
# 处理任务执行后返回的状态 可以重写自定义返回状态信息
from ansible import context
# 上下文管理器，他就是用来接收 ImmutableDict 的示例对象 (接受选项值)
import ansible.constants as C


# 用于获取 ansible 产生的临时文档。


class ResultCallback(CallbackBase):
    """
    重写callbackBase类的部分方法
    """

    def __init__(self, *args, **kwargs):
        """
        初始化返回信息，定义返回空字典
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)

        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}
        self.task_ok = {}

    def v2_runner_on_unreachable(self, result):
        """
        runner 不成功返回信息
        :param result:
        :return:
        """
        self.host_unreachable[result._host.get_name()] = result

    def v2_runner_on_ok(self, result, **kwargs):
        """
        runner返回成功结果信息
        :param result:
        :param kwargs:
        :return:
        """
        self.host_ok[result._host.get_name()] = result

    def v2_runner_on_failed(self, result, **kwargs):
        self.host_failed[result._host.get_name()] = result


class MyAnsiable2():
    """
    重写ansible执行类
    """

    # 定义初始化传入参数
    def __init__(self,
                 connection='local',
                 remote_user=None,
                 ack_pass=None,
                 sudo=None, sudo_user=None, ask_sudo_pass=None,
                 module_path=None,
                 become=None,
                 become_method=None,
                 become_user=None,
                 check=False, diff=False,
                 listhosts=None, listtasks=None, listtags=None,
                 verbosity=3,
                 syntax=None,
                 start_at_task=None,
                 inventory=None):
        """

        :param connection: 连接方式 local 本地方式，smart ssh方式
        :param remote_user: 远程用户
        :param ack_pass: 提示输入密码
        :param sudo: 切换用户
        :param sudo_user: sudo用户
        :param ask_sudo_pass: sudo用户的秘钥地址
        :param module_path: 模块路径
        :param become: 是否提权相关
        :param become_method: 提权方式 默认sudo 可以使su
        :param become_user: 提权后，要成为的用户，并非登录用户
        :param check: 检查测试
        :param diff:
        :param listhosts:
        :param listtasks:
        :param listtags:
        :param verbosity:
        :param syntax:
        :param start_at_task:
        :param inventory: ansible hosts地址
        """

        # 函数文档注释
        """
        初始化函数，定义的默认的选项值，
        在初始化的时候可以传参，以便覆盖默认选项的值
        """
        context.CLIARGS = ImmutableDict(
            connection=connection,
            remote_user=remote_user,
            ack_pass=ack_pass,
            sudo=sudo,
            sudo_user=sudo_user,
            ask_sudo_pass=ask_sudo_pass,
            module_path=module_path,
            become=become,
            become_method=become_method,
            become_user=become_user,
            verbosity=verbosity,
            listhosts=listhosts,
            listtasks=listtasks,
            listtags=listtags,
            syntax=syntax,
            start_at_task=start_at_task,
        )

        # 三元表达式，假如没有传递 inventory, 就使用 "localhost,"
        self.inventory = inventory if inventory else "localhost,"

        # 实例化数据解析器
        self.loader = DataLoader()

        # 实例化 资产配置对象
        self.inv_obj = InventoryManager(loader=self.loader, sources=self.inventory)

        # 设置密码，可以为空字典，但必须有此参数
        self.passwords = {}

        # 实例化回调插件对象
        self.results_callback = ResultCallback()

        # 变量管理器
        self.variable_manager = VariableManager(self.loader, self.inv_obj)

    def run(self, hosts='localhost', gether_facts="no", module="ping", args=''):
        """
        执行传入 Ad-hoc 相关信息
        :param hosts: 默认传入localhost
        :param gether_facts: 定义是否获取facts信息
        :param module: 定义传入模块
        :param args: 定义对应模块传入的变量
        :return:
        """
        play_source = dict(
            name="Ad-hoc",
            hosts=hosts,
            gather_facts=gether_facts,
            tasks=[
                # 这里每个 task 就是这个列表中的一个元素，格式是嵌套的字典
                # 也可以作为参数传递过来，这里就简单化了。
                {"action": {"module": module, "args": args}},
            ])

        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)

        tqm = None
        try:
            # ansible内置任务列表
            tqm = TaskQueueManager(
                inventory=self.inv_obj,
                variable_manager=self.variable_manager,
                loader=self.loader,
                passwords=self.passwords,
                stdout_callback=self.results_callback)

            result = tqm.run(play)
        finally:
            if tqm is not None:
                tqm.cleanup()
            shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)
            # 递归删除文件夹下文件

    def playbook(self, playbooks):
        """
        ansible  playbook执行导入函数
        :param playbooks: 传入playbooks是列表信息
        :return:
        """
        from ansible.executor.playbook_executor import PlaybookExecutor

        playbook = PlaybookExecutor(playbooks=playbooks,  # 注意这里是一个列表
                                    inventory=self.inv_obj,
                                    variable_manager=self.variable_manager,
                                    loader=self.loader,
                                    passwords=self.passwords)

        # 使用回调函数
        playbook._tqm._stdout_callback = self.results_callback

        result = playbook.run()

    def get_result(self):
        """
        获取返回状态相关信息
        """
        result_raw = {'success': {}, 'failed': {}, 'unreachable': {}}

        # print(self.results_callback.host_ok)
        for host, result in self.results_callback.host_ok.items():
            result_raw['success'][host] = result._result
        for host, result in self.results_callback.host_failed.items():
            result_raw['failed'][host] = result._result
        for host, result in self.results_callback.host_unreachable.items():
            result_raw['unreachable'][host] = result._result

        # 最终打印结果，并且使用 JSON 继续格式化
        print(json.dumps(result_raw, indent=4))


# 初始化实例
ansible2 = MyAnsiable2(inventory='/etc/ansible/hosts', connection='local')

# 调用类run函数
ansible2.run(hosts='nginx', gether_facts="no", module="shell", args="ls /tmp")

# 调用类 get_result函数获取执行返回结果信息
ansible2.get_result()


