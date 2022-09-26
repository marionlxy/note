# model update常规用法

假如我们的表结构是这样的

```python
class User(models.Model):
    username = models.CharField(max_length=255, unique=True, verbose_name='用户名')
    is_active = models.BooleanField(default=False, verbose_name='激活状态')
```

那么我们修改用户名和状态可以使用如下两种方法：

方法一：

```
User.objects.filter(id=1).update(username='nick',is_active=True)
```

方法二：

```python
_t = User.objects.get(id=1)
_t.username='nick'
_t.is_active=True
_t.save()
```

方法一适合更新一批数据，类似于mysql语句`update user set username='nick' where id = 1`

方法二适合更新一条数据，也只能更新一条数据，当只有一条数据更新时推荐使用此方法，另外此方法还有一个好处，我们接着往下看

# 具有auto_now属性字段的更新

我们通常会给表添加三个默认字段

- 自增ID，这个django已经默认加了，就像上边的建表语句，虽然只写了username和is_active两个字段，但表建好后也会有一个默认的自增id字段
- 创建时间，用来标识这条记录的创建时间，具有`auto_now_add`属性，创建记录时会自动填充当前时间到此字段
- 修改时间，用来标识这条记录最后一次的修改时间，具有`auto_now`属性，当记录发生变化时填充当前时间到此字段

就像下边这样的表结构

```python
class User(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    username = models.CharField(max_length=255, unique=True, verbose_name='用户名')
    is_active = models.BooleanField(default=False, verbose_name='激活状态')
```

**当表有字段具有auto_now属性且你希望他能自动更新时，必须使用上边方法二的更新，不然auto_now字段不会更新**，也就是：

```python
_t = User.objects.get(id=1)
_t.username='nick'
_t.is_active=True
_t.save()
```

# json/dict类型数据更新字段

目前主流的web开放方式都讲究前后端分离，分离之后前后端交互的数据格式大都用通用的json型，那么如何用最少的代码方便的更新json格式数据到数据库呢？同样可以使用如下两种方法：

方法一：

```python
data = {'username':'nick','is_active':'0'}
User.objects.filter(id=1).update(**data)
```

- 同样这种方法不能自动更新具有`auto_now`属性字段的值
- 通常我们再变量前加一个星号(*)表示这个变量是元组/列表，加两个星号表示这个参数是字典

方法二：

```python
data = {'username':'nick','is_active':'0'}
_t = User.objects.get(id=1)
_t.__dict__.update(**data)
_t.save()
```

- 方法二和方法一同样无法自动更新`auto_now`字段的值
- 注意这里使用到了一个`**dict**`方法

方法三：

```python
_t = User.objects.get(id=1)
_t.role=Role.objects.get(id=3)
_t.save()
```

# ForeignKey字段更新

假如我们的表中有Foreignkey外键时，该如何更新呢？

```python
class User(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    username = models.CharField(max_length=255, unique=True, verbose_name='用户名')
    is_active = models.BooleanField(default=False, verbose_name='激活状态')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, verbose_name='角色')
```

方法一：

```
User.objects.filter(id=1).update(role=2)
```

- 最简单的方法，直接让给role字段设置为一个id即可
- 当然也可以用dict作为参数更新：

```python
User.objects.filter(id=1).update(**{'username':'nick','role':3})
```

方法二：

```python
_role = Role.objects.get(id=2)
User.objects.filter(id=1).update(role=_role)
```

- 也可以赋值一个实例给role
- 当然也可以用dict作为参数更新：

```python
_role = Role.objects.get(id=1)
User.objects.filter(id=1).update(**{'username':'nick','role':_role})
```

方法三：

```python
_t = User.objects.get(id=1)
_t.role=Role.objects.get(id=3)
_t.save()
```

- 注意：**这里的role必须赋值为一个对象，不能写id**，不然会报错`"User.role" must be a "Role" instance`
- 当使用dict作为参数更新时又有一点不同，如下代码：

```python
_t = User.objects.get(id=1)
_t.__dict__.update(**{'username':'nick','role_id':2})
_t.save()
```

- **Foreignkey外键必须加上_id**，例如：{'role_id':3}
- role_id后边必须跟一个id（int或str类型都可），不能跟role实例

# ManyToManyField字段更新

假如我们的表中有ManyToManyField字段时更新又有什么影响呢？

```python
class User(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    username = models.CharField(max_length=255, unique=True, verbose_name='用户名')
    is_active = models.BooleanField(default=False, verbose_name='激活状态')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, verbose_name='角色')
    groups = models.ManyToManyField(Group, null=True, verbose_name='组')
```

m2m更新：m2m字段没有直接更新的方法，只能通过清空再添加的方法更新了

```python
_t = User.objects.get(id=1)
_t.groups.clear()
_t.groups.add(*[1,3,5])
_t.save()
```

- `add()`：m2m字段添加一个值，当有多个值的时候可用列表，参照上边例子
- - _t.groups.add(2)
  - _t.groups.add(Group.objects.get(id=2))
- `remove()`：m2m字段移除一个值，，当有多个值的时候可用列表，参照上边例子
- - _t.groups.remove(2)
  - _t.groups.remove(Group.objects.get(id=2))
- `clear()`：清空m2m字段的值

## Django model select的各种用法详解

# 基本操作

```python
# 获取所有数据，对应SQL：select * from User
User.objects.all()

# 匹配，对应SQL：select * from User where name = '千锋云计算'
User.objects.filter(name='千锋云计算')

# 不匹配，对应SQL：select * from User where name != '千锋云计算'
User.objects.exclude(name='千锋云计算')

# 获取单条数据（有且仅有一条，id唯一），对应SQL：select * from User where id = 724
User.objects.get(id=123)
```

# 常用操作

```python
# 获取总数，对应SQL：select count(1) from User
User.objects.count()

# 获取总数，对应SQL：select count(1) from User where name = '千锋云计算'
User.objects.filter(name='千锋云计算').count()

# 大于，>，对应SQL：select * from User where id > 724
User.objects.filter(id__gt=724)

# 大于等于，>=，对应SQL：select * from User where id >= 724
User.objects.filter(id__gte=724)

# 小于，<，对应SQL：select * from User where id < 724
User.objects.filter(id__lt=724)

# 小于等于，<=，对应SQL：select * from User where id <= 724
User.objects.filter(id__lte=724)

# 同时大于和小于， 1 < id < 10，对应SQL：select * from User where id > 1 and id < 10
User.objects.filter(id__gt=1, id__lt=10)

# 包含，in，对应SQL：select * from User where id in (11,22,33)
User.objects.filter(id__in=[11, 22, 33])

# 不包含，not in，对应SQL：select * from User where id not in (11,22,33)
User.objects.exclude(id__in=[11, 22, 33])

# 为空：isnull=True，对应SQL：select * from User where pub_date is null
User.objects.filter(pub_date__isnull=True)

# 不为空：isnull=False，对应SQL：select * from User where pub_date is not null
User.objects.filter(pub_date__isnull=True)

# 匹配，like，大小写敏感，对应SQL：select * from User where name like '%sre%'，SQL中大小写不敏感
User.objects.filter(name__contains="sre")

# 匹配，like，大小写不敏感，对应SQL：select * from User where name like '%sre%'，SQL中大小写不敏感
User.objects.filter(name__icontains="sre")

# 不匹配，大小写敏感，对应SQL：select * from User where name not like '%sre%'，SQL中大小写不敏感
User.objects.exclude(name__contains="sre")

# 不匹配，大小写不敏感，对应SQL：select * from User where name not like '%sre%'，SQL中大小写不敏感
User.objects.exclude(name__icontains="sre")

# 范围，between and，对应SQL：select * from User where id between 3 and 8
User.objects.filter(id__range=[3, 8])

# 以什么开头，大小写敏感，对应SQL：select * from User where name like 'sh%'，SQL中大小写不敏感
User.objects.filter(name__startswith='sre')

# 以什么开头，大小写不敏感，对应SQL：select * from User where name like 'sh%'，SQL中大小写不敏感
User.objects.filter(name__istartswith='sre')

# 以什么结尾，大小写敏感，对应SQL：select * from User where name like '%sre'，SQL中大小写不敏感
User.objects.filter(name__endswith='sre')

# 以什么结尾，大小写不敏感，对应SQL：select * from User where name like '%sre'，SQL中大小写不敏感
User.objects.filter(name__iendswith='sre')

# 排序，order by，正序，对应SQL：select * from User where name = '千锋云计算' order by id
User.objects.filter(name='千锋云计算').order_by('id')

# 多级排序，order by，先按name进行正序排列，如果name一致则再按照id倒叙排列
User.objects.filter(name='千锋云计算').order_by('name','-id')

# 排序，order by，倒序，对应SQL：select * from User where name = '千锋云计算' order by id desc
User.objects.filter(name='千锋云计算').order_by('-id')
```

# 进阶操作

```python
# limit，对应SQL：select * from User limit 3;
User.objects.all()[:3]

# limit，取第三条以后的数据，没有对应的SQL，类似的如：select * from User limit 3,10000000，从第3条开始取数据，取10000000条（10000000大于表中数据条数）
User.objects.all()[3:]

# offset，取出结果的第10-20条数据（不包含10，包含20）,也没有对应SQL，参考上边的SQL写法
User.objects.all()[10:20]

# 分组，group by，对应SQL：select username,count(1) from User group by username;
from django.db.models import Count
User.objects.values_list('username').annotate(Count('id'))

# 去重distinct，对应SQL：select distinct(username) from User
User.objects.values('username').distinct().count()

# filter多列、查询多列，对应SQL：select username,fullname from accounts_user
User.objects.values_list('username', 'fullname')

# filter单列、查询单列，正常values_list给出的结果是个列表，里边里边的每条数据对应一个元组，当只查询一列时，可以使用flat标签去掉元组，将每条数据的结果以字符串的形式存储在列表中，从而避免解析元组的麻烦
User.objects.values_list('username', flat=True)

# int字段取最大值、最小值、综合、平均数
from django.db.models import Sum,Count,Max,Min,Avg

User.objects.aggregate(Count(‘id’))
User.objects.aggregate(Sum(‘age’))
```

# 时间字段

```python
# 匹配日期，date
User.objects.filter(create_time__date=datetime.date(2018, 8, 1))
User.objects.filter(create_time__date__gt=datetime.date(2018, 8, 2))

# 匹配年，year
User.objects.filter(create_time__year=2018)
User.objects.filter(create_time__year__gte=2018)

# 匹配月，month
User.objects.filter(create_time__month__gt=7)
User.objects.filter(create_time__month__gte=7)

# 匹配日，day
User.objects.filter(create_time__day=8)
User.objects.filter(create_time__day__gte=8)

# 匹配周，week_day
 User.objects.filter(create_time__week_day=2)
User.objects.filter(create_time__week_day__gte=2)

# 匹配时，hour
User.objects.filter(create_time__hour=9)
User.objects.filter(create_time__hour__gte=9)

# 匹配分，minute
User.objects.filter(create_time__minute=15)
User.objects.filter(create_time__minute_gt=15)

# 匹配秒，second
User.objects.filter(create_time__second=15)
User.objects.filter(create_time__second__gte=15)


# 按天统计归档
today = datetime.date.today()
select = {'day': connection.ops.date_trunc_sql('day', 'create_time')}
deploy_date_count = Task.objects.filter(
    create_time__range=(today - datetime.timedelta(days=7), today)
).extra(select=select).values('day').annotate(number=Count('id'))
```

# Q 的使用

Q对象可以对关键字参数进行封装，从而更好的应用多个查询，可以组合&(and)、|(or)、~(not)操作符。

例如下边的语句

```python
from django.db.models import Q

User.objects.filter(
    Q(role__startswith='sre_'),
    Q(name='好程序员') | Q(name='千锋云计算')
)
```

转换成SQL语句如下：

```python
select * from User where role like 'sre_%' and (name='好程序员' or name='千锋云计算')
```

通常更多的时候我们用Q来做搜索逻辑，比如前台搜索框输入一个字符，后台去数据库中检索标题或内容中是否包含

```python
_s = request.GET.get('search')

_t = Blog.objects.all()
if _s:
    _t = _t.filter(
        Q(title__icontains=_s) |
        Q(content__icontains=_s)
    )

return _t
```

# 外键：ForeignKey

- 表结构：

```python
class Role(models.Model):
    name = models.CharField(max_length=16, unique=True)


class User(models.Model):
    username = models.EmailField(max_length=255, unique=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
```

- 正向查询:

```python
# 查询用户的角色名
_t = User.objects.get(username='运维咖啡吧')
_t.role.name
```

- 反向查询：

```python
# 查询角色下包含的所有用户
_t = Role.objects.get(name='Role03')
_t.user_set.all()
```

- 另一种反向查询的方法：

```python
_t = Role.objects.get(name='Role03')

# 这种方法比上一种_set的方法查询速度要快
User.objects.filter(role=_t)
```

- 第三种反向查询的方法：

如果外键字段有`related_name`属性，例如models如下：

```python
class User(models.Model):
    username = models.EmailField(max_length=255, unique=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE,related_name='roleUsers')
```

那么可以直接用`related_name`属性取到某角色的所有用户

```python
_t = Role.objects.get(name = 'Role03')
_t.roleUsers.all()
```

# M2M：ManyToManyField

- 表结构：

```python
class Group(models.Model):
    name = models.CharField(max_length=16, unique=True)

class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    groups = models.ManyToManyField(Group, related_name='groupUsers')
```

- 正向查询:

```python
# 查询用户隶属组
_t = User.objects.get(username = '好程序员')
_t.groups.all()
```

- 反向查询：

```python
# 查询组包含用户
_t = Group.objects.get(name = 'groupC')
_t.user_set.all()
```

同样M2M字段如果有`related_name`属性，那么可以直接用下边的方式反查

```python
_t = Group.objects.get(name = 'groupC')
_t.groupUsers.all()
```

# get_object_or_404

正常如果我们要去数据库里搜索某一条数据时，通常使用下边的方法：

```python
_t = User.objects.get(id=734)
```

但当`id=724`的数据不存在时，程序将会抛出一个错误

```python
abcer.models.DoesNotExist: User matching query does not exist.
```

为了程序兼容和异常判断，我们可以使用下边两种方式:

- 方式一：`get`改为`filter`

```python
_t = User.objects.filter(id=724)
# 取出_t之后再去判断_t是否存在
```

- 方式二：使用`get_object_or_404`

```python
from django.shortcuts import get_object_or_404

_t = get_object_or_404(User, id=724)
# get_object_or_404方法，它会先调用django的get方法，如果查询的对象不存在的话，则抛出一个Http404的异常
```

实现方法类似于下边这样：

```python
from django.http import Http404

try:
    _t = User.objects.get(id=724)
except User.DoesNotExist:
    raise Http404
```

# get_or_create

顾名思义，查找一个对象如果不存在则创建，如下：

```python
object, created = User.objects.get_or_create(username='千锋云计算')
```

返回一个由object和created组成的元组，其中object就是一个查询到的或者是被创建的对象，created是一个表示是否创建了新对象的布尔值

实现方式类似于下边这样：

```python
try:
    object = User.objects.get(username='千锋云计算')

    created = False
exception User.DoesNoExist:
    object = User(username='千锋云计算')
    object.save()

    created = True

returen object, created
```

# 执行原生SQL

Django中能用ORM的就用它ORM吧，不建议执行原生SQL，可能会有一些安全问题，如果实在是SQL太复杂ORM实现不了，那就看看下边执行原生SQL的方法，跟直接使用pymysql基本一致了

```python
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute('select * from accounts_User')
    row = cursor.fetchall()

return row
```

