# 命令行运行Python脚本时传入参数的三种方式

转载[there2belief](https://me.csdn.net/dou3516) 发布于2018-09-30 19:04:34 阅读数 6907 收藏

展开

From:https://blog.csdn.net/weixin_35653315/article/details/72886718

# 三种常用的方式

如果在运行python脚本时需要传入一些参数，例如`gpus`与`batch_size`，可以使用如下三种方式。

```
python script.py 0,1,2 10python script.py -gpus=0,1,2 --batch-size=10python script.py -gpus=0,1,2 --batch_size=10
```

这三种格式对应不同的参数解析方式，分别为`sys.argv`, `argparse`, `tf.app.run`, 前两者是python自带的功能，后者是`tensorflow`提供的便捷方式。

# `sys.argv`

`sys`模块是很常用的模块， 它封装了与python解释器相关的数据，例如`sys.modules`里面有已经加载了的所有模块信息，`sys.path`里面是`PYTHONPATH`的内容，而`sys.argv`则封装了传入的参数数据。
使用`sys.argv`接收上面第一个命令中包含的参数方式如下：

```
import sysgpus = sys.argv[1]#gpus = [int(gpus.split(','))]batch_size = sys.argv[2]print gpusprint batch_size
```

# `argparse`

```
import argparseparser = argparse.ArgumentParser(description='manual to this script')parser.add_argument('--gpus', type=str, default = None)parser.add_argument('--batch-size', type=int, default=32)args = parser.parse_args()print args.gpusprint args.batch_size
```

需要注意的是，脚本运行命令`python script.py -gpus=0,1,2 --batch-size=10`中的`--batch-size`会被自动解析成`batch_size`.
`parser.add_argument` 方法的`type`参数理论上可以是任何合法的类型， 但有些参数传入格式比较麻烦，例如list，所以一般使用`bool`, `int`, `str`, `float`这些基本类型就行了，更复杂的需求可以通过`str`传入，然后手动解析。`bool`类型的解析比较特殊，传入任何值都会被解析成`True`，传入空值时才为`False`

```
python script.py --bool-val=0 # args.bool_val=Truepython script.py --bool-val=False # args.bool_val=Truepython script.py --bool-val=     # args.bool_val=什么都不写False
```

通过这个方法还能指定命令的帮助信息。具体请看API文档：https://docs.python.org/2/library/argparse.html

# `tf.app.run`

tensorflow也提供了一种方便的解析方式。
脚本的执行命令为：

```
python script.py -gpus=0,1,2 --batch_size=10
```

对应的python代码为：

```
import tensorflow as tftf.app.flags.DEFINE_string('gpus', None, 'gpus to use')tf.app.flags.DEFINE_integer('batch_size', 5, 'batch size') FLAGS = tf.app.flags.FLAGS def main(_):    print FLAGS.gpus    print FLAGS.batch_size if __name__=="__main__":    tf.app.run()
```

几点需要注意：

1. `tensorflow`只提供以下几种方法：
   `tf.app.flags.DEFINE_string`，
   `tf.app.flags.DEFINE_integer`,
   `tf.app.flags.DEFINE_boolean`,
   `tf.app.flags.DEFINE_float` 四种方法，分别对应`str`, `int`,`bool`,`float`类型的参数。这里对`bool`的解析比较严格，传入1会被解析成`True`，其余任何值都会被解析成`False`。
2. 脚本中需要定义一个接收一个参数的`main`方法：`def main(_):`，这个传入的参数是脚本名，一般用不到， 所以用下划线接收。
3. 以`batch_size`参数为例，传入这个参数时使用的名称为`--batch_size`，也就是说，中划线不会像在`argparse` 中一样被解析成下划线。
4. `tf.app.run()`会寻找并执行入口脚本的`main`方法。也只有在执行了`tf.app.run()`之后才能从`FLAGS`中取出参数。
   从它的签名来看，它也是可以自己指定需要执行的方法的，不一定非得叫`main`：

```
run(    main=None,    argv=None)
```

5 . `tf.app.flags`只是对`argpars`的简单封装。代码见

https://github.com/tensorflow/tensorflow/blob/r1.2/tensorflow/python/platform/flags.py

 