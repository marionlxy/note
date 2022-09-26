# 路由配置(URLconf)

每一个URL都会对应一个视图函数，当一个用户请求访问Django站点的一个页面时，然后就由Django路由系统（URL配置文件）去决定要执行哪个视图函数使用的算法。这个路由系统我们也称之为url控制器，一般是项目目录和应用目录里的urls.py文件。

URLconf是所有整个Django的入口，我们想要访问什么，想要去什么地方，都取决于URLconf，所以我们需要充分理解URLconf的用法。

一般情况下，一个URL，我们是这样写的：

```
urlpatterns = [
    path(正则表达式, views视图函数，参数，别名),
]
参数说明：
1、一个正则表达式字符串
2、一个可调用对象，通常为一个视图函数或一个指定视图函数路径的字符串
3、可选的要传递给视图函数的默认参数（字典形式）
4、一个可选的name参数(别名)
```

下面是一个简单的URLconf例子:

```
from django.urls import path
from . import views
urlpatterns = [
    path('articles/2003/', views.special_case_2003),
    path('articles/<int:year>/', views.year_archive),
    path('articles/<int:year>/<int:month>/', views.month_archive),
    path('articles/<int:year>/<int:month>/<slug:slug>/', views.article_detail),
    ]
```

**注意：**

1. 要捕获一段url中的值，需要使用尖括号，而不是之前的圆括号；
2. 可以转换捕获到的值为指定类型，比如例子中的`<int:name>`。默认情况下，捕获到的结果保存为字符串类型，不包含**/**这个特殊字符；
3. 规则的前面不需要添加**/**，因为默认情况下，每个url都带一个最前面的**/**。比如：articles, 不能写成 /articles。

**匹配例子：**

1、/articles/2005/03/ 将匹配第三条，并调用views.month_archive(request, year=2005, month=3)；

2、/articles/2003/匹配第一条，并调用views.special_case_2003(request)；

3、/articles/2003将一条都匹配不上，因为它最后少了一个斜杠，而列表中的所有模式中都以斜杠结尾；

4、/articles/2003/03/building-a-django-site/ 将匹配最后一个，并调用views.article_detail(request, year=2003, month=3, slug="building-a-django-site"

### 一、path转换器

Django默认情况下内置下面的路径转换器：

1、str：匹配任何非空字符串，但不含斜杠/，如果你没有专门指定转换器，那么这个是默认使用的；
2、int：匹配0和正整数，返回一个int类型
3、slug：可理解为注释、后缀、附属等概念，是url拖在最后的一部分解释性字符。该转换器匹配任何ASCII字符以及连接符和下划线，比如’ building-your-1st-django-site‘；
4、uuid：匹配一个uuid格式的对象。为了防止冲突，规定必须使用破折号，所有字母必须小写，例如’075194d3-6885-417e-a8a8-6c931e272f00‘ 。返回一个UUID对象；
5、path：匹配任何非空字符串，重点是可以包含路径分隔符’/‘。这个转换器可以帮助你匹配整个url而不是一段一段的url字符串。

### 二、注册自定义路径转换器

对于更复杂的匹配需求，您可以定义自己的路径转换器。自定义，就是单独写一个类，它包含下面的内容：
1、类属性regex：一个字符串形式的正则表达式属性；
2、to_python(self, value) 方法：一个用来将匹配到的字符串转换为你想要的那个数据类型，并传递给视图函数。如果不能转换给定的值，则会引发ValueError。

3、to_url(self, value)方法：将Python数据类型转换为一段url的方法，上面方法的反向操作。

例如：

```
class FourDigitYearConverter:
    regex = '[0-9]{4}'
    def to_python(self, value):
        return int(value)
    def to_url(self, value):
        return '%04d' % value
```

在URLconf中注册自定义转换器类，并使用它:

```
from django.urls import path, register_converter
from . import converters, 
viewsregister_converter(converters.FourDigitYearConverter, 'yyyy')
urlpatterns = [
    path('articles/2003/', views.special_case_2003),
    path('articles/<yyyy:year>/', views.year_archive),
    ...
    ]
```

### 三、使用正则表达式

如果路径和转换器语法不足以定义URL模式，也可以使用正则表达式。这时我们就需要使用re_path()而不是path()。

在Python正则表达式中，命名正则表达式组的语法是 (?P<name>pattern)，其中name是组的名称，pattern是需要匹配的规则。

前面的URLconf示例，如果使用正则表达式重写，是这样子的:

```
from django.urls import path, re_path
from . import views
urlpatterns = [
    path('articles/2003/', views.special_case_2003),
    #表示articles/2003/这个路径映射views模块的special_case_2003函数
    re_path(r'^articles/(?P<year>[0-9]{4})/$', views.year_archive),
    #表示匹配4个0-9的任意数字
    re_path(r'^articles/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$', views.month_archive),
    re_path(r'^articles/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<slug>[\w-]+)/$', views.article_detail),
    ]
#注意:上面匹配都加了小括号，这些括号里面的值会当作参数传递到后面的视图函数中
```

re_path与path()不同的主要在于两点：
1、year中匹配不到10000等非四位数字，这是正则表达式决定的
2、传递给视图的所有参数都是字符串类型。而不像path()方法中可以指定转换成某种类型。

### 四、指定视图参数的默认值

有一个方便的小技巧是指定视图参数的默认值。 下面是一个URLconf 和视图的示例：

```
# URLconf
from django.urls import path
from . import views
urlpatterns = [
    path('blog/', views.page),
    path('blog/page<int:num>/', views.page),
    ]

# View (in blog/views.py)
def page(request, num=1):
# Output the appropriate page of blog entries, according to num.
...
```

在上面的例子中，两个URL模式指向同一个视图views.page —— 但是第一个模式不会从URL 中捕获任何值。如果第一个模式匹配，page() 函数将使用num参数的默认值"1"。如果第二个模式匹配，page() 将使用正则表达式捕获的num 值。

### 五、URLconf匹配请求URL中的哪些部分

请求的URL被看做是一个普通的Python字符串，URLconf在其上查找并匹配。进行匹配时将不包括GET或POST请求方式的参数以及域名。
例如，在https://www.example.com/myapp/的请求中，URLconf将查找myapp/。
在https://www.example.com/myapp/?page=3的请求中，URLconf也将查找myapp/。
URLconf不检查使用何种HTTP请求方法，所有请求方法POST、GET、HEAD等都将路由到同一个URL的同一个视图。在视图中，才根据具体请求方法的不同，进行不同的处理。

### 六、错误页面处理

当Django找不到与请求匹配的URL时，或者当抛出一个异常时，将调用一个错误处理视图。错误视图包括400、403、404和500，分别表示请求错误、拒绝服务、页面不存在和服务器错误。它们分别位于：

- handler400 —— django.conf.urls.handler400。
- handler403 —— django.conf.urls.handler403。
- handler404 —— django.conf.urls.handler404。
- handler500 —— django.conf.urls.handler500。

这些值可以在根URLconf中设置。在其它app中的二级URLconf中设置这些变量无效。

Django有内置的HTML模版，用于返回错误页面给用户，但是这些403，404页面实在丑陋，通常我们都自定义错误页面。

首先，在根URLconf中额外增加下面的条目：

```
# urls.py
from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^blog/$', views.page),
    url(r'^blog/page(?P<num>[0-9]+)/$', views.page),
]
# 增加的条目
handler400 = views.bad_request
handler403 = views.permission_denied
handler404 = views.page_not_found
handler500 = views.page_error
```

然后在，views.py文件中增加四个处理视图：

```
def page_not_found(request):
    return render(request, '404.html')
    
def page_error(request):
    return render(request, '500.html')
    
def permission_denied(request):
    return render(request, '403.html')
    
def bad_request(request):
    return render(request, '400.html')
```

再根据自己的需求，创建404.html、400.html等四个页面文件，就可以了。

### 七、urls分层模块化（路由分发）

通常，我们会在每个app里，各自创建一个urls.py路由模块，然后从根路由出发，将app所属的url请求，全部转发到相应的urls.py模块中。

例如，下面是Django网站本身的URLconf节选。 它包含许多其它URLconf：

```
from django.urls import include, path
urlpatterns = [
    # ... snip ...
    path('community/', include('aggregator.urls')),
    path('contact/', include('contact.urls')),
    # ... snip ...
]
```

路由转发使用的是include()方法，需要提前导入，它的参数是转发目的地路径的字符串，路径以圆点分割。

注意，这个例子中的正则表达式没有包含$（字符串结束匹配符），但是包含一个末尾的斜杠。 每当Django 遇到`include()`（来自`django.conf.urls.include()`）时，它会去掉URL中匹配的部分并将剩下的字符串发送给include的URLconf做进一步处理，也就是转发到二级路由去。

另外一种转发其它URL模式的方式是使用一个url()实例的列表。 例如，下面的URLconf：

```
from django.urls import include, path
from apps.main import views as main_views
from credit import views as credit_views
extra_patterns = [
    path('reports/', credit_views.report),
    path('reports/<int:id>/', credit_views.report),
    path('charge/', credit_views.charge),
]
urlpatterns = [
    path('', main_views.homepage),
    path('help/', include('apps.help.urls')),
    path('credit/', include(extra_patterns)),
]
```

在这个例子中， /credit/reports/ URL将被 credit.views.report() 这个Django 视图处理。
上面这种方法可以用来去除URLconf 中的冗余，其中某个模式前缀被重复使用。例如，下面这个例子:

```
from django.urls import path
from . import views
urlpatterns = [
    path('<page_slug>-<page_id>/history/', views.history),
    path('<page_slug>-<page_id>/edit/', views.edit),
    path('<page_slug>-<page_id>/discuss/', views.discuss),
    path('<page_slug>-<page_id>/permissions/', views.permissions),
]
```

我们可以改进它，通过只声明共同的路径前缀一次并将后面的部分分组转发:

```
from django.urls import include, path
from . import views
urlpatterns = [
    path('<page_slug>-<page_id>/', include([
        path('history/', views.history),
        path('edit/', views.edit),
        path('discuss/', views.discuss),
        path('permissions/', views.permissions),
    ])),
]
```

### 八、捕获参数

被转发的URLconf会收到来自父URLconf捕获的所有参数，看下面的例子：

```
# In settings/urls/main.py
from django.urls import include, path
urlpatterns = [
    path('<username>/blog/', include('foo.urls.blog')),
]
# In foo/urls/blog.py
from django.urls import path
from . import views
urlpatterns = [
    path('', views.blog.index),
    path('archive/', views.blog.archive),
]
```

在上面的例子中，捕获的"username"变量将被传递给include()指向的URLconf，再进一步传递给对应的视图。

### 九、嵌套参数

正则表达式允许嵌套参数，Django将解析它们并传递给视图。当反查时，Django将尝试填满所有外围捕获的参数，并忽略嵌套捕获的参数。 考虑下面的URL模式，它带有一个可选的page参数：

```
from django.urls import re_path
urlpatterns = [
    re_path(r'^blog/(page-(\d+)/)?$', blog_articles),   # bad
    re_path(r'^comments/(?:page-(?P<page_number>\d+)/)?$', comments),  # good
```

两个模式都使用嵌套的参数，其解析方式是：例如`blog/page-2/`将匹配`page-2/`并带有两个位置参数`blog_articles`和2。第二个comments的模式将匹配`page_number`并带有一个值为2的关键字参数`comments/page-2/`。这个例子中外围参数是一个不捕获的参数(?:...)。

`blog_articles`视图需要最外层捕获的参数来反查，在这个例子中是comments或者没有参数，而`page-2/`可以不带参数或者用一个`page_number`值来反查。

### 十、向视图传递额外的参数

URLconfs具有一个钩子（hook），允许你传递一个Python字典作为额外的关键字参数给视图函数。

像这样：

```
from django.urls import path
from . import views
urlpatterns = [
    path('blog/<int:year>/', views.year_archive, {'foo': 'bar'}),
]
```

在上面的例子中，对于`/blog/2005/`请求，Django将调`用views.year_archive(request, year='2005', foo='bar')`。理论上，你可以在这个字典里传递任何你想要的传递的东西。但是要注意，URL模式捕获的命名关键字参数和在字典中传递的额外参数有可能具有相同的名称，这会发生冲突，要避免。

### 十一、传递额外的参数给include()

类似上面，也可以传递额外的参数给include()。参数会传递给include指向的urlconf中的每一行。

例如，下面两种URLconf配置方式在功能上完全相同：

配置一：

```
# main.py
from django.urls import include, path
urlpatterns = [
    path('blog/', include('inner'), {'blog_id': 3}),
]
# inner.py
from django.urls import path
from mysite import views
urlpatterns = [
    path('archive/', views.archive),
    path('about/', views.about),
]
```

配置二：

```
# main.py
from django.urls import include, path
from mysite import views
urlpatterns = [
    path('blog/', include('inner')),
]
# inner.py
from django.urls import path
urlpatterns = [
    path('archive/', views.archive, {'blog_id': 3}),
    path('about/', views.about, {'blog_id': 3}),
]
```

注意，只有当你确定被include的URLconf中的每个视图都接收你传递给它们的额外的参数时才有意义，否则其中一个以上视图不接收该参数都将导致错误异常。

### 十二、url的反向解析

在实际的Django项目中，经常需要获取某条URL，为生成的内容配置URL链接。

比如，我要在页面上展示一列文章列表，每个条目都是个超级链接，点击就进入该文章的详细页面。

现在我们的urlconf是这么配置的：`^post/(?P<id>\d+)`。

在前端中，这就需要为HTML的`<a>`标签的href属性提供一个诸如`http://www.xxx.com/post/3`的值。其中的域名部分，Django会帮你自动添加无须关心，我们关注的是`post/3`。

此时，一定不能硬编码URL为`post/3`，那样费时、不可伸缩，而且容易出错。试想，如果哪天，因为某种原因，需要将urlconf中的正则改成`^entry/(?P<id>\d+)`，为了让链接正常工作，必须修改对应的herf属性值，于是你去项目里将所有的`post/3`都改成`entry/3`吗？显然这是不行的！

我们需要一种安全、可靠、自适应的机制，当修改URLconf中的代码后，无需在项目源码中大范围搜索、替换失效的硬编码URL。

为了解决这个问题，Django提供了一种解决方案，只需在URL中提供一个name参数，并赋值一个你自定义的、好记的、直观的字符串。

通过这个name参数，可以反向解析URL、反向URL匹配、反向URL查询或者简单的URL反查。

在需要解析URL的地方，对于不同层级，Django提供了不同的工具用于URL反查：

- 在模板语言中：使用`url`模板标签。(也就是写前端网页时）
- 在Python代码中：使用`reverse()`函数。（也就是写视图函数等情况时）
- 在更高层的与处理Django模型实例相关的代码中：使用`get_absolute_url()`方法。(也就是在模型model中)

**示例：**

```
from django.urls import path
from . import views
urlpatterns = [
    #...
    path('articles/<int:year>/', views.year_archive, name='news-year-archive'),
    #...
]
```

某一年nnnn对应的归档的URL是`/articles/nnnn/`。

可以在模板的代码中使用下面的方法获得它们：

```
<a  >2012 Archive</a>
{# Or with the year in a template context variable: #}
<ul>
{% for yearvar in year_list %}
<li><a  >{{ yearvar }} Archive</a></li>
{% endfor %}
</ul>
```

在Python代码中，这样使用：

```
from django.http import HttpResponseRedirect
from django.urls import reverse
def redirect_to_year(request):
    # ...
    year = 2006
    # ...
    return HttpResponseRedirect(reverse('news-year-archive', args=(year,)))
```

其中，起到核心作用的是我们通过`name='news-year-archive'`为那条url起了一个可以被引用的名称。

URL名称name使用的字符串可以包含任何你喜欢的字符，但是过度的放纵有可能带来重名的冲突，比如两个不同的app，在各自的urlconf中为某一条url取了相同的name，这就会带来麻烦。为了解决这个问题，又引出了下面命名的URL模式。

### 十三、命名的URL模式（URL别名）

URL别名可以保证反查到唯一的URL，即使不同的app使用相同的URL名称。

第三方应用始终使用带命名空间的URL是一个很好的做法。

类似地，它还允许你在一个应用有多个实例部署的情况下反查URL。 换句话讲，因为一个应用的多个实例共享相同的命名URL，命名空间提供了一种区分这些命名URL 的方法。

实现命名空间的做法很简单，在urlconf文件中添加`app_name = 'polls'`和`namespace='author-polls'`这种类似的定义。

**范例**：

以两个实例为例子：'publisher-polls' 和'author-polls'。

假设我们已经在创建和显示投票时考虑了实例命名空间的问题，代码如下：

urls.py

```
from django.urls import include, path
urlpatterns = [
    path('author-polls/', include('polls.urls', namespace='author-polls')),
    path('publisher-polls/', include('polls.urls', namespace='publisher-polls')),
]
```

polls/urls.py

```
from django.urls import path
from . import views
app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    ...
]
```

如果当前的app实例是其中的一个，例如我们正在渲染实例'author-polls'中的detail视图，'polls:index'将解析到'author-polls'实例的index视图。

根据以上设置，可以使用下面的查询：

在基于类的视图的方法中：

```
reverse('polls:index', current_app=self.request.resolver_match.namespace)
```

和在模板中：

```
{% url 'polls:index' %}
```

如果没有当前app实例，例如如果我们在站点的其它地方渲染一个页面，'polls:index'将解析到polls注册的最后一个app实例空间。 因为没有默认的实例（命名空间为'polls'的实例），将使用注册的polls 的最后一个实例。 这将是'publisher-polls'，因为它是在urlpatterns中最后一个声明的。

### 十四、URL命名空间和include的URLconf

可以通过两种方式指定include的URLconf的应用名称空间。

**第一种**

在include的URLconf模块中设置与urlpatterns属性相同级别的`app_name`属性。必须将实际模块或模块的字符串引用传递到include()，而不是urlpatterns本身的列表。

```
polls/urls.py

from django.urls import path
from . import views
app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    ...
]

urls.py
from django.urls import include, path
urlpatterns = [
    path('polls/', include('polls.urls')),
]
```

此时，polls.urls中定义的URL将具有应用名称空间polls。

**第二种**

include一个包含嵌套命名空间数据的对象。如果你include()一个url()实例的列表，那么该对象中包含的URL将添加到全局命名空间。 但是，你也可以include()一个2元组，其中包含：

```
(<list of path()/re_path() instances>, <application namespace>)
```

例如：

```
from django.urls import include, path
from . import views
polls_patterns = ([
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
], 'polls')
urlpatterns = [
    path('polls/', include(polls_patterns)),
]f
```

这将include指定的URL模式到给定的app命名空间。

可以使用include()的namespace参数指定app实例命名空间。如果未指定，则app实例命名空间默认为URLconf的app命名空间。