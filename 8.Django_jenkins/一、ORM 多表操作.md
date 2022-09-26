# 一、ORM 多表操作

**假设场景：**

我们现在要对机房里的服务器进行管理：

1. 一个机房可以 存放多个机柜。
2. 一个机柜可以放置多台服务器。
3. 机房有：城市、地址、楼层。
4. 机柜有：品牌、机柜的型号、几 U、机柜编号、所属机房。
5. 服务器有：主机名、管理 IP、所属机柜等。

以上的内容需要以下表来存储管理这些信息：

**机房表**

| id   | 名称     | 城市 | 地址 |
| :--- | :------- | :--- | :--- |
| 1    | 亦庄机房 | 北京 | 亦庄 |

**机柜表**

| id   | 品牌   | 型号       | 自编号  | U    | 机房 id |
| :--- | :----- | :--------- | :------ | :--- | :------ |
| 1    | 国普达 | GP-ZN61042 | Y-S-001 | 42   | 1       |
| 2    | 国普达 | GP-36A22   | Y-S-002 | 22   | 1       |

**服务器表**

| Id   | 主机名     | 管理 IP      | 所属机柜 |
| :--- | :--------- | :----------- | :------- |
| 1    | appserver1 | 192.168.1.10 | 1        |
| 2    | appserver2 | 192.168.1.11 | 1        |
| 3    | Dbserver1  | 192.168.1.12 | 2        |

# 二、Django Model 如何表示表之间的关系

- 模型之间的三种关系：一对一，多对一，多对多。

  ```python
  一对一：实质就是在主外键（author_id就是foreign key）的关系基础上，给外键加了一个UNIQUE＝True的属性；
     
  多对一：就是主外键关系；（foreign key）
     
  多对多：(ManyToManyField) 自动创建第三张表(当然我们也可以自己创建第三张表：两个foreign key)
  ```

```python
# 一对一：
models.OneToOneField(OtherModel)

# 多对一：
models.ForeignKey(OtherModel, on_delete=models.CASCADE)

# 多对多：
models.ManyToManyField(OtherModel)
```

> Django2.x 的 多对一表关系设置时，外键需要添加 `on_delete=models.CASCADE`。
> 表示当删除表中的数据的时候，执行级联删除动作。

# 三 编写 Model (模型)

```python
class Asset(models.Model):
    """
    资产信息表，所有资产公共信息（交换机，服务器，防火墙等）
    """
    device_type_choices = (
        (1, '服务器'),
        (2, '路由器'),
        (3, '交换机'),
        (4, '防火墙'),
    )
    device_status_choices = (
        (1, '上架'),
        (2, '在线'),
        (3, '离线'),
        (4, '下架'),
    )

    device_type_id = models.IntegerField(choices=device_type_choices, default=1)
    device_status_id = models.IntegerField(choices=device_status_choices, default=1)

    # 多个资产可以放在一个机柜中，也就是多对一，
    # 即：此字段会有相同的值
    cabinet_id = models.ForeignKey('Cabinet', verbose_name='所属机柜', max_length=30, null=True, blank=True, on_delete=models.CASCADE)

    latest_date = models.DateField(verbose_name='更新时间', null=True, blank=True)
    create_at = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    """
    auto_now=True 每次更新，日期自动存为当前时间，并且在 Admin 管理中，此字段将不支持修改
    default
    """
 
    class Meta:
        verbose_name = "资产表"
        verbose_name_plural = verbose_name
        db_table = 'asset'

    def __str__(self):
        return "{}-{}-{}".format(self.idc.name, self.cabinet_num, self.cabinet_order)

    

class IDC(models.Model):
    name = models.CharField(verbose_name='机房', max_length=128)
    city = models.CharField(verbose_name='城市', max_length=32)
    address = models.CharField(verbose_name='地址', max_length=256)

    class Meta:
        verbose_name_plural = '机房表'
        db_table = "idc"

    def __str__(self):
        return self.name


class Cabinet(models.Model):
    name = models.CharField(verbose_name='机柜编号', max_length=128)
    cab_lever = models.CharField(verbose_name='U 数', max_length=2)  # 机柜总共几层
    idc = models.ForeignKey('IDC', verbose_name='所属机房', null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '机柜表'
        db_table = "cabinet"

    def __str__(self):
        return self.name

    
class Server(models.Model):
    # 每个服务器都和资产表一一对应
    asset = models.OneToOneField('Asset', verbose_name='对应资产', on_delete=models.CASCADE)

    hostname = models.CharField(verbose_name='主机名', max_length=128, unique=True)
    sn = models.CharField(verbose_name='SN号', max_length=64, db_index=True)  # 为此字段创建索引
    manage_ip = models.GenericIPAddressField(verbose_name='管理IP', null=True, blank=True)
    latest_date = models.DateTimeField(verbose_name='更新时间', default=timezone.now, null=True)
    create_at = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

   class Meta:
        verbose_name = "服务器表"
        verbose_name_plural = verbose_name
        db_table = 'server'

    def __str__(self):
        return self.hostname
```

##### 同步数据库

```python
python3 manage.py makemigrations
python3 manage.py migrate
```

##### `__str__()`

- `Model.__str__()`

`__str__()` 方法在每当你对一个对象调用`str()` 时候。 Django在许多地方使用`str(obj)`。 最明显的是在Django 的Admin 站点显示一个对象和在模板中插入对象的值的时候。 所以，你应该始终让`__str__()` 方法返回模型的一个友好的、人类可读的形式。

像这样：

```python
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible  # only if you need to support Python 2
class Person(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
  
return '%s %s' % (self.first_name, self.last_name)
```

如果你希望与Python 2兼容，则可以使用`python_2_unicode_compatible()`来装饰模型类，如上所示。

#### ORM 进阶操作

##### `OneToOneFiel`

```python
# 一对一

# 添加数据


引入 models

from cmdb.models import IDC,Cabinet,Asset  # 引入机房、机柜、资产 模型

obj = IDC.objects.create(name="兆维机房",city="北京",address="北京路")

Cabinet.objects.create(name="BJ-S-003", cab_lever="42", idc=obj)


zw_dic = IDC.objects.filter(name="兆维机房").values("id")[0]
f_id = zw_dic['id']

Cabinet.objects.create(name="BJ-S-003",
                              cab_lever="42",
                              idc_id=f_id)

Cabinet.objects.all().values()

Cabinet.objects.all().values("name")

Cabinet.objects.filter(name='BJ-S-003')

obj = Cabinet.objects.filter(name='BJ-S-003').last()

obj.name

obj.name="BJ-S-004"
obj.name

obj.save()
Cabinet.objects.all().values("name")
```

##### `ForeignKey`

**添加数据**

```python
# 方式1：
# 由于绑定多对一的字段,比如 Cabinet 表的 idc 字段, 存到数据库中的字段名会是 idc_id 所以可以直接给这个字段设定对应值:
Cabinet.objects.create(name="Y-S-01",
                              cab_lever="42",
                              idc_id=1)

# 方式2:
# 选获取到需要关联的对象，就是多对一中那个 一
idc_obj = IDC.objects.filter(id=1)[0]
cab_dic = dict(name="Y-S-02",cab_lever="22",idc=idc_obj)
models.Cabinet.objects.create(**cab_dic)
```

##### 更新数据

```python
Cabinet.objects.filter(name="Y-S-02"
                             ).update(name="Y-S-002")
```

##### 查询数据

- 获取 `QuerySet` 对象时，使用 `.` 连接
- 获取字段值时，使用 `__` 连接

**使用 . 查对象**

```python
# 正向查，就是查我属于谁
# 使用 Frenkey 的字段名，进行连表查询
qst = Cabinet.objects.first()
qst.name
Out[43]: 'Y-S-01'
qst.idc.name
Out[44]: '亦庄'

# 反向查，就是查谁属于我
# 使用小写的表名加 _set,进行连表查询
qst = IDC.objects.last()
qst.cabinet_set.all()
```

**基于双下划线，直接查询字段的值**

```python
# 正向，就是从含有 ForeignKey 字段的表开始查
# 先获取到一个 QueySet 对象
qst = Cabinet.objects.filter(id=1)

# 再用 QuerySet 对象查询字段的值
# 结果是字典
qst.values("name","idc__name")
Out[53]: <QuerySet [{'name': 'Y-S-01', 'idc__name': '亦庄'}]>

# 结果是元组
qst.values_list("name","idc__name")
Out[54]: <QuerySet [('Y-S-01', '亦庄')]>
    
###############################################

# 反向查，表的映射类名称的小写
qst = IDC.objects.filter(id=1)

# 结果是字典
qst.values("name", "cabinet__name")
Out[58]: <QuerySet [{'name': '亦庄', 'cabinet__name': 'Y-S-01'}, {'name': '亦庄', 'cabinet__name': 'Y-S-002'}]>

# 结果是元组 
qst.values_list("name", "cabinet__name")
Out[60]: <QuerySet [('亦庄', 'Y-S-01'), ('亦庄', 'Y-S-002')]>
```

##### 优化

假如你想查询到机柜表里的的所有数据，并且得到每条数据所关联的表中的字段的值。

那可能需要先得到机柜表里所有的数据，之后在循环每条数据时，用 `ForeignKey`字段名进行跨表查询，这样的话就会进行多次跨表查询。

像下面这样：

```python
qst_all_obj = models.Cabinet.objects.all()

for obj in qst_all_obj:
    print(obj.idc.city)
```

解决方案一：

```python
qst_all_dic = Cabinet.objects.all().values("idc__city")

# QuerySet[{},{}]
# 通过字典的方法取值
```

解决方案二：

适用于数据量相对较少，并且查询的频率低的情况。

```python
qst_all_obj = Cabinet.objects.all().select_related("idc")


# Django 内部会用 inner join IDC 进行主动跨表查询
# 一次查询到所有关联的数据
# 通过面向对象的方法取值，即用 obj.city 的方式取值
# 但是，只要连表查询，就会影响效率
```

解决方案三：

适用于数据量相对大 ，并且查询频率高的情况。

```python
qst_all_obj = Cabinet.objects.all().prefetch_related("idc")

# 不做跨表查询，进行多次(两个表两次)单表查询

"""
1. select * from cabinet;
2. Django 内部：
    # 把外键的值进行去重
    idc_id = set(qst_all_obj.idc_id)
    
    # 比如 idc_id 的值是 [2, 3]
    
    # 通过条件查询到 IDC 机房表里的数据
    select * from IDC where id in idc_id;
    
    这样的话，所需要的结果集都会在内存中了
    再次循环查询相应的值时，就不会再次进行跨表查询了，而是去内存的结果集中查找了。
"""

for obj in qst_all_obj:
    print(obj.city)
```

##### `ManyToManyField`

示例 models

```python
class SysUsers(models.Model):
    user_type_choice = (
        ('1', "超级管理员"),
        ('2', "sudo 用户"),
        ('3', "普通用户"),
    )
    name = models.CharField("用户名", max_length=16)
    user_type = models.CharField("用户类型", choices=user_type_choice, max_length=1, default='3')

    class Meta:
        verbose_name = '用户表'
        verbose_name_plural = verbose_name
        db_table = "sys_users"

    def __str__(self):
        return self.name

class Servers(models.Model):

    hostname = models.CharField("主机名", max_length=128)
    sysusers = models.ManyToManyField(
        SysUsers,
        verbose_name="用户",
        related_name="servers")
    class Meta:
        verbose_name = '服务器表'
        verbose_name_plural = verbose_name
        db_table = "servers"

    def __str__(self):
        return self.hostname
```

#### 参考官方文档自修 [官方文档连接](https://app.yinxiang.com/OutboundRedirect.action?dest=https%3A%2F%2Fdocs.djangoproject.com%2Fzh-hans%2F2.2%2Ftopics%2Fdb%2Fexamples%2Fmany_to_many%2F)

**注意：**

查单个的时候用`.values()`或者 `.values_list()`

不管是多对一，还是多对多，查询的目标假如是多的一方，就得用`.all()`

#### ORM 查询 API 总结

```python
# 查询相关API：

#  <1>filter(**kwargs):      它包含了与所给筛选条件相匹配的对象

#  <2>all():                 查询所有结果

#  <3>get(**kwargs):         返回与所给筛选条件相匹配的对象，返回结果有且只有一个，如果符合筛选条件的对象超过一个或者没有都会抛出错误。

#-----------下面的方法都是对查询的结果再进行处理:比如 objects.filter.values()--------

#  <4>values(*field):        返回一个ValueQuerySet——一个特殊的QuerySet，运行后得到的并不是一系列 model的实例化对象，而是一个可迭代的字典序列
                                     
#  <5>exclude(**kwargs):     它包含了与所给筛选条件不匹配的对象

#  <6>order_by(*field):      对查询结果排序

#  <7>reverse():             对查询结果反向排序

#  <8>distinct():            从返回结果中剔除重复纪录

#  <9>values_list(*field):   它与values()非常相似，它返回的是一个元组序列，values返回的是一个字典序列

#  <10>count():              返回数据库中匹配查询(QuerySet)的对象数量。

#  <11>first():               返回第一条记录

#  <12>last():                返回最后一条记录

#  <13>exists():             如果QuerySet包含数据，就返回True，否则返回False
```

#### 关于 QuerySet

Foo.objects.all()或者.filter()等都只是返回了一个QuerySet（查询结果集对象），它并不会马上执行sql，而是当调用QuerySet的时候才执行。

- 可以进行切片操作
- 是可迭代对象
- 有缓存机制

```python
简单的使用if语句进行判断也会完全执行整个queryset并且把数据放入cache，虽然你并不需要这些
     数据！为了避免这个，可以用exists()方法来检查是否有数据：
    if qst.exists():
        print("QuerSet 中有数据")
```

**总结:**
​ queryset的cache是用于减少程序对数据库的查询，在通常的使用下, 会保证只有在需要的时候才会查询数据库。
使用 `exists()` 和 `iterator()` 方法可以优化程序对内存的使用。不过，由于它们并不会生成 **queryset cache**，可能会造成额外的数据库查询。

#### ORM 扩展知识

##### 事务

```python
import traceback
from django.db.transaction import atomic


def func(request):
    try:
        with atomic():
            models.users.objects.create(**dict)
    except Exception as e:
        print(traceback.format_exc())
```

##### Q 查询

```python
# Q
Q(id__gt=10)
Q(id=8) | Q(id__gt=10)
Q(Q(id=8) | Q(id__gt=10)) & Q(username='root')

# 执行原生SQL
from django.db import connection, connections
cursor = connection.cursor()  
# cursor = connections['default'].cursor()

cursor.execute("""SELECT * from db_usersprofile where id = %s""", [1])
result_row = cursor.fetchone()
```

# 分组查询

```python
>>> str(models.SalaryOfDay.objects.filter(date__month='07').values('name_id').annotate(total=Sum('wages')).values('name_id', 'total').query)
'SELECT "salary_of_day"."name_id", CAST(SUM("salary_of_day"."wages") AS NUMERIC) AS "total" FROM "salary_of_day" WHERE django_date_extract(\'month\', "salary_of_day"."date") = 7 GROUP BY "salary_of_day"."name_id"'
```

> 注意上面的 `values('name_id)` 需要放在前面。
> 假如不放在前面的结果会是如下的样子:

```python
str(models.SalaryOfDay.objects.filter(date__month='07').annotate(total=Sum('wages')).values('name_id', 'total').query)
'SELECT "salary_of_day"."name_id", CAST(SUM("salary_of_day"."wages") AS NUMERIC) AS "total" FROM "salary_of_day" WHERE django_date_extract(\'month\', "salary_of_day"."date") = 7 GROUP BY "salary_of_day"."id", "salary_of_day"."name_id", "salary_of_day"."date", "salary_of_day"."wages", "salary_of_day"."other"'
```

> 需要注意 SQL 语句最后的 `group by` 语句

## 批量插入数据

批量插入数据时，只需先生成个一要传入的Product数据的列表，然后调用bulk_create方法一次性将列表中的数据插入数据库。

```python
product_list_to_insert = list()
for x in range(10):
    product_list_to_insert.append(Product(name='product name ' + str(x), price=x))
Product.objects.bulk_create(product_list_to_insert)
```

## 给字段起别名

```python
from django.db.models import F

MyModel.objects.annotate(renamed_value=F('cryptic_value_name')).values('renamed_value')
```

# 聚合查询

### [参考官方文档](https://app.yinxiang.com/OutboundRedirect.action?dest=https%3A%2F%2Fdocs.djangoproject.com%2Fzh-hans%2F2.1%2Ftopics%2Fdb%2Faggregation%2F)

# 关于多表继承和代理模型

### [点击 参考官方文档](https://app.yinxiang.com/OutboundRedirect.action?dest=https%3A%2F%2Fdocs.djangoproject.com%2Fzh-hans%2F2.2%2Ftopics%2Fdb%2Fmodels%2F%23multi-table-inheritance)