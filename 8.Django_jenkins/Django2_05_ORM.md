###  Django2_05_ORM



#### ORM

[本文链接](https://www.jianshu.com/p/90fcb25f9a64)

##### 基本介绍

关系对象映射（Object Relational Mapping，简称ORM）

##### ORM是如何和数据库映射的

Django规定在models.py文件内创建一个类，然后进行初始化，迁移后，Django将根据该类在数据库中创建相应的表以及表的不同内容。

其对应关系如下：

类名------>数据库中的表名

类的数据属性------>表分区

每一个实例化的对象------>表中的每一条数据

![img](https://upload-images.jianshu.io/upload_images/11414906-65c1e02592672a91.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

表示例：

下面的示例是利用Django自带的用户模型去扩展我们自定义的细分

1. 首先需要在编写自己的模型时继承Django的AbstractUser

> Django的自带的用户中已经有这些字段了：
> `username`，`password`，`email`等

下面增加头像，手机号，性别三个长度

```python
from django.db import models
from django.contrib.auth.models import AbstractUser

class UsersProfile(AbstractUser):
    gender_choice = (
        ('1', "男"),
        ('2', "女")
    )
    mobile = models.CharField('手机', max_length=11)
    gender = models.CharField("性别", choices=gender_choice, default="1", max_length=1)
    avatar = models.ImageField(verbose_name="头像", upload_to='users/%Y/%m/%d/', max_length=128)
```

> `chioces`属性相当于MySQL的中的枚举类型。
> 其值必须是一个嵌套的元组，其中元组中的第一个元素是数据库存储到值，第二个元素是展示在前端的值。
> 比如`('1', "男")`中`'1'`的英文数据库存储到值，`"男"`是前端页面中展示的值。

1. 之后在`settings.py`中添加如下内容，指定我们自己的模型

```python
# 自定义用户表，在 sttings.py 中添加如下配置信息    #users 对应自己的APP名字，记得更换
AUTH_USER_MODEL = 'users.UsersProfile'
```

- 所有的Django模型类都必须继承django.db.models.Model类。它的父类模型包含了所有必要的和数据库交互的方法。并提供了一个简洁的定义数据库语法。
- 每个模型相当于相应的数据库表（多对多关系例外，会多生成一张表关系表），每个模型类的数据属性也是这个表中的变量。属性名就是分段名，它的类型（例如CharField ）相当于数据库的细分类型（例如varchar）。大家可以留意下其他的类型都和数据库里的什么分区对应。
- 通过其中的类属性定义模型变量，模型区段必须是某种模型。XXField类型，需要指定长度的类型，最大长度也是需要指定的。
- 通过模型类中的Meta子类定义模型元数据，类似数据库的表名，数据排序方式等

## 为Django配置数据库引擎

### 初步

```sh
# settings.py
DATABASES = {

    'default': {

        'ENGINE': 'django.db.backends.mysql', 

        'NAME': '',  # 数据库名称，必须先在数据库中创建

        'USER': '',   # 数据库用户名

        'PASSWORD': '',   # 数据库密码

        'HOST': '',       # 数据库主机，留空默认为localhost

        'PORT': '',   # 数据库端口
    }
}
```

### 第二步

![img](https://app.yinxiang.com/FileSharing.action?hash=1/02e61cdd80f2a653ff14de46edbbb95b-42413)

##### 安装数据库模块（MySql）

> 此步骤仅适用于MysqL，使用替代的Sqlite的跳过此步骤。

需要先安装依赖包，切换到项目的环境下安装以下依赖包

由于依赖包需要或者`mariadb-devel`或者`mysql-community-devel`，每个安装任意一个都行。

`mariadb-devel` 应该是CentOS7默认安装的。

假如希望安装 `mysql-community-devel`

执行如下步骤

编辑这个文件`/etc/yum.repos.d/mysql-community.repo`，并添加如下内容：

```sh
[mysql57-community]
name=MySQL 5.7 Community Server
baseurl=http://repo.mysql.com/yum/mysql-5.7-community/el/7/$basearch/
enabled=1
```

之后，在Linux命令行终端中，执行以下的命令

```sh
yum  install mysql-community-devel
```

系统-保证中含有`mariadb-devel`或者`mysql-community-devel`软件包。就可以使用如下命令安装模块`mysqlclient`

```shell
pip3 install mysqlclient 
```

##### 同步数据库

Django根据代码中定义的类来自动生成数据库表。

1. 生成数据移植文件（makemigrations）

```shell
# 在 shell 环境下的项目根目录下执行 
python3 manage.py  makemigrations
```

此命令执行成功后，会在应用app的迁移目录下创建0001_initial.py文件；这个文件是数据库生成的中间文件，通过它可以指定当前的数据库版本。

> > 在makemigrations的过程中，Django会比较models.py中的模型与现有数据库之间的差异，如果没有差异则不做任何操作。

假如对models.py有任何改变，则在执行makemigrations的时候会同步更新到数据移植文件中。

1. 真正改变数据库

```
# 在 shell 环境下的项目根目录下执行 
python3 manage.py migrate  
```

**自增列**

当model中如果没有自增列，则自动会创建一个列名为id的列

- 自定义自增列(了解即可)

```
nid = models.AutoField(primary_key=True)
```

# Field 字段

## 字符串类型相关

### 1. models.CharField(max_length=None)

> 字符串类型 `varchar`, 必须提供max_length参数， max_length表示字符长度

### 2. mdels.TextField(*options)

> 字符串类型 `text` 一个大的文本字段。

### 3. models.EmailField(max_length = 254, **options)

> 字符串类型 `varchar`，检查该值是使用一个有效的电子邮件地址

### 4. models.GenericIPAddressField(protocol='both', **options)

> IPv4或IPv6地址
> protoclol 指定了地址的类型:
>
> - `both` IPv4 或 IPv6
> - `IPv4` 只可以是 IPv4
> - `IPv6` 只可以是 IPv6
>   匹配不区分大小写

### 5. models.SlugField(max_length=50, **options)

> 字母、数字、下划线、连接符（减号）的任意组合

### 5. models.URLField(max_length=200, **options)

> 可以验证 URL 地址

### 6. UUIDField(Field)

> 字符串类型，Django Admin以及ModelForm中提供对UUID格式的验证

## 数字类型

### 1. BooleanField(**options)

> 布尔值类型

### 2. SmallIntegerField()

> 小整数 -32768 ～ 32767

### 3. IntegerField(Field)

> 整数列(有符号的) -2147483648 ～ 2147483647

### 4. PositiveSmallIntegerField()

> 正小整数 0 ～ 32767

### 5. PositiveIntegerField()

> 正整数 0 ～ 2147483647

### 6.FloatField(Field)

> 浮点型

### 7. DecimalField((max_digits=None, decimal_places=None, **options))

> 一个固定精度的十进制数，由Python [`Decimal`](https://docs.python.org/3/library/decimal.html#decimal.Decimal)实例表示。
>
> - 10进制小数
>   - 参数：
>     max_digits，小数总长度
>     decimal_places，小数位长度

### 8. BinaryField(Field)

> 二进制类型

## 关于时间和日期

### 1. DateField(auto_now=False, auto_now_add=False, **options)

> 日期格式 YYYY-MM-DD
>
> `auto_now=True` 每次保存时，更新此字段的值为当前时间，对“最后修改”的时间戳有用，只有调用 Model.save()时，此值才会自动更新。在以其他方式更新其他字段时，不会导致此字段自动更新。比如：Queryset.update() 不会自动更新。不允许在后台修改。
>
> `auto_now_add=True` 首次创建对象时自动将字段设置为现在。可以用于创建时间戳。 并且不支持在后台修改。
>
> `default=date.today` 支持后台修改
> 这三个是互斥的。

### 2. DateTimeField(auto_now=False, auto_now_add=False, **options))

> 日期+时间格式 YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ]
>
> ```python
> fromdjango.utils from timezone`
> `default=timezone.now
> ```

### 3. TimeField(auto_now=False, auto_now_add=False, **options)

> 时间格式 HH:MM[:ss[.uuuuuu]]

## 关于文件和图片

```python
FilePathField(Field)
         选择仅限于文件系统上某个目录中的文件名
        - 字符串，Django Admin以及ModelForm中提供读取文件夹下文件的功能
        - 参数：
                path,                      文件夹路径
                match=None,                正则匹配
                recursive=False,           递归下面的文件夹
                allow_files=True,          允许文件
                allow_folders=False,       允许文件夹

FileField(Field)
        - 字符串，路径保存在数据库，文件上传到指定目录
        - 参数：
            upload_to = ""      上传文件的保存路径
            storage = None      存储组件，默认django.core.files.storage.FileSystemStorage

ImageField(upload_to=None, height_field=None, width_field=None, max_length=100, **options)
        - 字符串，路径保存在数据库，文件上传到指定目录
        - 参数：
            upload_to = ""      上传文件的保存路径
            storage = None      存储组件，默认django.core.files.storage.FileSystemStorage
            width_field=None,   上传图片的高度保存的数据库字段名（字符串）
            height_field=None   上传图片的宽度保存的数据库字段名（字符串）
```

**关于上传文件或图片字段的补充**

```python
在模型中调用FileField 或 ImageField (见下方) 需如下几步：

1. 在你的settings文件中, 你必须要定义 MEDIA_ROOT 作为Django存储上传文件的路径 (从性能上考虑，这些文件不能存在数据库中。) 定义一个 MEDIA_URL 作为基础的URL或者目录。 确保这个目录可以被web server使用的账户写入。

2. 在模型中添加FileField或ImageField字段, 定义upload_to选项来指定MEDIA_ROOT的一个子目录用于存放上传的文件。

3. 数据库中存放的仅是这个文件的路径（相对于MEDIA_ROOT）。 你很可能会想用由Django提供的便利的url属性。 比如说, 如果你的ImageField命名为mug_shot, 你可以在template中用{{ object.mug_shot.url }}获得你照片的绝对路径。
例如，如果你的 MEDIA_ROOT设定为 '/home/media'，并且 upload_to设定为 'photos/%Y/%m/%d'。 upload_to的'%Y/%m/%d'是strftime()格式；'%Y'是四位数年份，'%m'是两位数的月份，'%d'是两位数的天数。 如果你在Jan.15.2007上传了一个文件，它将被保存在/home/media/photos/2007/01/15目录下。

如果要检索上传的文件的磁盘文件名或文件大小，则可以分别使用name和size属性；有关可用属性和方法的更多信息，请参见File类参考和管理文件主题指南。
```

### 字段里可以使用的选项(options)

```python
null               数据库中字段是否可以为空
db_column          数据库中字段的列名
db_tablespace      数据库中表空间
default            数据库中字段的默认值
primary_key        数据库中字段是否为主键
db_index           为数据库中字段建立索引
unique             数据库中字段是否可以建立唯一索引

verbose_name       Admin中显示的字段名称
blank              表单验证时是否允许输入空值
editable           Admin中是否可以编辑
help_text          Admin中该字段的提示信息
choices            一个可迭代的结构(比如，列表或是元组)，用来给
                   这个字段提供选择项
                   如：
                  qf = models.IntegerField(
                       choices=[(0, '服务器'),
                                (1, '交换机'),],
                       default=0)
```

##### Mata

Meta 类的属性名由 Django 预先定义，常用的 Meta 类属性汇总如下：

```python
# 映射的数据库的表名，假如不指定，则 Django 会自动创建，命名格式为：“应用名小写_模型类名的小写”
db_table

# 后台管理显示的表名称
verbose_name

# 复数名称，默认表名后面会加字母 s
verbose_name_plural  

# 联合索引
index_together = [
    ("host_name", "manage_ip"),
]

# 联合唯一
unique_together = (("host_name", "manage_ip"),)
```

##### ORM 基本操作

```python
创建数据
# 增加一条数据，可以接受字典类型数据 **kwargs
# 方式一：
obj = models.UsersProfile(username="山炮",
                          password='1',
                          email="3@3.com",
                          mobile='13733333333')
obj.save()

# 方式二：
# 如果你想只用一条语句创建并保存一个对象，使用create()方法。
user_info_dic = {"username":"王二锤",
                 "password":'1',
                 "email":"2@qf.com",
                 "mobile":'13722222222'}

models.UsersProfile.objects.create(**user_info_dic)

# 方式三一次创建多条数据：
objs = [
models.UsersProfile(**{"username":"王二锤1",   "password": '1',   "email": "2@qf.com",   "mobile": '13722222222'}),
models.UsersProfile(**{"username":"王二锤2",   "password": '1',   "email": "22@qf.com",   "mobile": '13722222223'}),
models.UsersProfile(**{"username":"王二锤3",   "password": '1',   "email": "3@qf.com",   "mobile": '13722222222'}),
]

models.UsersProfile.objects.bulk_create(objs)
简单查询
# 获取到一个表里所有的数据
models.UsersProfile.objects.all()

# 指定条件过滤查询
- 获取到所有字段字典形式
res = models.UsersProfile.objects.filter(username="英雄").values()
res[0]

- 获取到指定字段字典形式，多个用逗号隔开
res = models.UsersProfile.objects.filter(username="英雄").values("id")             
res[0]

- 元组形式的数据
res = models.UsersProfile.objects.filter(username="英雄"
                                        ).values_list()
res[0][0]

res = models.UsersProfile.objects.filter(username="英雄"
                                     ).values_list("id", flat=True)
res[0]
删除数据
# 删除指定条件的数据
models.UsersProfile.objects.filter(id=1).delete()
更新数据
# 将指定条件的数据更新，均支持 **kwargs
models.UsersProfile.objects.filter(
                                username='王二锤'
                               ).update(
                                email="1@qf.com"
                               )  
obj = models.UsersProfile.objects.get(id=1)
obj.email = "1@qf.com"
obj.save()                        
#  get 方法没有则报错
```

##### ORM 高级操作

```python
双下划线查询
from db.models import UsersProfile
# 统计数量
UsersProfile.objects.filter(username='王二锤').count()

### 大于，小于
# 获取 id 大于 1 的数据
UsersProfile.objects.filter(id__gt=1)

# 获取 id 大于等于 1 的数据
UsersProfile.objects.filter(id__gte=1)              

# 获取 id 小于 10 的数据
UsersProfile.objects.filter(id__lt=10)

# 获取 id 小于等于 10 的数据
UsersProfile.objects.filter(id__lte=10)             

# 获取id大于1 且 小于10的值
UsersProfile.objects.filter(id__gt=1, id__lt=10)   

### in
# 获取id等于2、3的数据
UsersProfile.objects.filter(id__in=[2, 3])  

### not in  不等于
UsersProfile.objects.exclude(id__in=[11, 22, 33])  

### isnull
UsersProfile.objects.filter(email__isnull=True)

 
### range
# 范围 bettwen and
models.UsersProfile.objects.filter(id__range=[1, 2])   

# 其他类似
# startswith，istartswith, endswith, iendswith,

### like
# 不区分大小写
models.UsersProfile.objects.filter(username__icontains="山")

### order by
# asc
models.UsersProfile.objects.filter(username='山炮'
                                  ).order_by('id')

# desc  反序
models.UsersProfile.objects.filter(username='山炮'
                                  ).order_by('-id')

### group by
from django.db.models import Count, Min, Max, Sum

models.UsersProfile.objects.filter(id=1).values('id').annotate(c=Count('id'))

### 显示原始语句
str(models.UsersProfile.objects.filter(id=1).values('id').annotate(c=Count('id')).query)

'SELECT `db_usersprofile`.`id`, COUNT(`db_usersprofile`.`id`) AS `c` FROM `db_usersprofile` WHERE `db_usersprofile`.`id` = 1 GROUP BY `db_usersprofile`.`id` ORDER BY NULL'


### limit
models.UsersProfile.objects.all()[1:3]
```

保存到我的笔记

如