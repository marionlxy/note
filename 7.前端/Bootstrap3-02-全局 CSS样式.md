# 一、全局样式
## 布局容器
Bootstrap 需要为页面内容和栅格系统包裹一个 `.container` 容器。
提供了两个作此用处的类。注意，由于 `padding` 等属性的原因，这两种 容器类不能互相嵌套。

`.container` 类用于固定宽度并支持响应式布局的容器。

```html
<div class="container">
  ...
</div>
```

`.container-fluid` 类用于 100% 宽度，占据全部视口（viewport）的容器。

```html
<div class="container-fluid">
  ...
</div>
```

# [](https://v3.bootcss.com/css/#grid)

 Bootstrap  提供了大量的全局样式，大部分的  HTML 元素都可以通过添加不同的类，来设置元素的样式。

![image.png](https://upload-images.jianshu.io/upload_images/11414906-a00d1ad95b5352b7.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![image.png](https://upload-images.jianshu.io/upload_images/11414906-d5b9c6ad128aef8c.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

## 1. 大标题小标题
![image.png](https://upload-images.jianshu.io/upload_images/11414906-989f03fead352994.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


![image.png](https://upload-images.jianshu.io/upload_images/11414906-5747c737247df8ba.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


## 2. 文本

### 段落
***网页中的字体默认大小是 16 px***
![image.png](https://upload-images.jianshu.io/upload_images/11414906-903fc8ac53a923b4.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![image.png](https://upload-images.jianshu.io/upload_images/11414906-fc7aa6a3c9bb8a07.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)



### 排版对齐方式
![image.png](https://upload-images.jianshu.io/upload_images/11414906-edc30cf2ec5f012e.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

### 排版大小写
![image.png](https://upload-images.jianshu.io/upload_images/11414906-eaf9240270f6a186.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


## 3. 表格

![image.png](https://upload-images.jianshu.io/upload_images/11414906-52837b0786b33d69.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

### a. 基本实例

```html
        <table class="table">
                <caption>Optional table caption.</caption>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>First Name</th>
                    <th>Last Name</th>
                    <th>Username</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <th scope="row">1</th>
                    <td>Mark</td>
                    <td>Otto</td>
                    <td>@mdo</td>
                  </tr>
                  <tr>
                    <th scope="row">2</th>
                    <td>Jacob</td>
                    <td>Thornton</td>
                    <td>@fat</td>
                  </tr>
                </tbody>
        </table>
```

效果图
![image.png](https://upload-images.jianshu.io/upload_images/11414906-679c3dedc22ced9c.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

### b. 条纹状表格
通过 `.table-striped` 类可以给 `<tbody>` 之内的每一行增加斑马条纹样式。

![image.png](https://upload-images.jianshu.io/upload_images/11414906-5d806dcdad969681.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


```html
<table class="table  table-striped">
    ...
<table>
```

### c. 带边框的表格
添加 `.table-bordered` 类为表格和其中的每个单元格增加边框。
![千锋云计算](https://upload-images.jianshu.io/upload_images/11414906-8293644e37d03540.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```html
<table class="table table-bordered">
  ...
</table>
```

### d. 鼠标悬停效果
通过添加 `.table-hover` 类可以让 `<tbody>` 中的每一行对鼠标悬停状态作出响应。

![image.png](https://upload-images.jianshu.io/upload_images/11414906-1328e5234efa73d2.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```html
<table class="table table-hover">
  ...
</table>
```

### e. 紧缩表格
通过添加 `.table-condensed` 类可以让表格更加紧凑，单元格中的内补（padding）均会减半.
![image.png](https://upload-images.jianshu.io/upload_images/11414906-d6d14ee5ebffdb68.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```html
<table class="table table-condensed">
  ...
</table>
```

### f. 带状态条的表格

![image.png](https://upload-images.jianshu.io/upload_images/11414906-e46045ffe88b58e2.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)



```
<table class="table">
    <!-- On rows -->
    <tr class="active"><td>1...</td><td>2...</td><td>3...</td><td>4...</td><td>5...</td></tr>
    <tr class="success"><td>...</td><td>...</td><td>...</td><td>...</td><td>...</td></tr>
    <tr class="warning"><td>...</td><td>...</td><td>...</td><td>...</td><td>...</td></tr>
    <tr class="danger"><td>...</td><td>...</td><td>...</td><td>...</td><td>...</td></tr>
    <tr class="info"><td>...</td><td>...</td><td>...</td><td>...</td><td>...</td></tr>
    
    
    <tr class="active"><td>我</td><td>是</td><td>分</td><td>割</td><td>行</td></tr>

    <!-- On cells (`td` or `th`) -->

    <tr>
    <td class="active">...</td>
    <td class="success">...</td>
    <td class="warning">...</td>
    <td class="danger">...</td>
    <td class="info">...</td>
    </tr>
</table>
```

### g. 响应式表格
将任何 `.table` 元素包裹在 `.table-responsive` 元素内，即可创建响应式表格，其会在小屏幕设备上（小于768px）水平滚动。当屏幕大于 768px 宽度时，水平滚动条消失。

```
<div class="table-responsive">
    <table class="table">
            <tr class="active"><td>1...</td><td>2...2...2...2...2...2...2...2...2...2...2...</td><td>3...</td><td>4...</td><td>5...</td></tr>

    </table>
</div>
```

之前
![之前](https://upload-images.jianshu.io/upload_images/11414906-11c38031dc2d5322.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

之后

![之后](https://upload-images.jianshu.io/upload_images/11414906-35e03d83dc87b9a4.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


## 4. 表单
### a. 基本实例
单独的表单控件会被自动赋予一些全局样式。
所有设置了 `.form-control` 类的 `<input>`、`<textarea>` 和 `<select>` 元素都将被默认设置宽度属性为 width: 100%;。 将 `label` 元素和前面提到的控件包裹在 `.form-group` 中可以获得最好的排列。

![image.png](https://upload-images.jianshu.io/upload_images/11414906-eae9a3180636639f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```html
<form>
    <div class="form-group">
        <label for="inputName">姓名</label>
        <input type="text" class="form-control" id="inputName" placeholder="姓名">
    </div>
    <div class="form-group">
        <label for="inputPassword">密码</label>
        <input type="password" class="form-control" id="inputPassword" placeholder="密码">
    </div>
    <div class="form-group">
        <label for="inputFile">上传文件</label>
        <input type="file" id="inputFile">
        <p class="help-block">在这里上传文件.</p>
    </div>
    <div class="checkbox">
        <label>
        <input type="checkbox"> Check me out
        </label>
    </div>
    <button type="submit" class="btn btn-default">提交</button>
</form>
```

> #### 不要将表单组和输入框组混合使用
>
>不要将表单组直接和[输入框组](https://v3.bootcss.com/components/#input-groups)混合使用。建议将输入框组嵌套到表单组中使用。

### b. 内联表单
为 `<form>` 元素添加 `.form-inline` 类可使其内容左对齐并且表现为 `inline-block` 级别的控件。
只适用于视口（viewport）至少在 768px 宽度时（视口宽度再小的话就会使表单折叠）。


![image.png](https://upload-images.jianshu.io/upload_images/11414906-e1fa7a4e4725a9db.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
```html
<form class="form-inline">
    <div class="form-group">
        <label for="inputName">姓名</label>
        <input type="text" class="form-control" id="inputName" placeholder="姓名">
    </div>
    <div class="form-group">
        <label for="inputPassword">密码</label>
        <input type="password" class="form-control" id="inputPassword" placeholder="密码">
    </div>
    <button type="submit" class="btn btn-default">提交</button>
</form>
```

![image.png](https://upload-images.jianshu.io/upload_images/11414906-2b6a0d0430901036.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```html
<form class="form-inline">
    <div class="form-group">
        <label class="sr-only" for="exampleInputAmount">Amount (in dollars)</label>
        <div class="input-group">
        <div class="input-group-addon">$</div>
        <input type="text" class="form-control" id="exampleInputAmount" placeholder="Amount">
        <div class="input-group-addon">.00</div>
        </div>
    </div>
    <button type="submit" class="btn btn-primary">转账金额</button>
</form>
```



### c. 水平排列的表单
通过为表单添加 .form-horizontal 类，并联合使用 Bootstrap 预置的栅格类，可以将 label 标签和控件组水平并排布局。这样做将改变 .form-group 的行为，使其表现为栅格系统中的行（row），因此就无需再额外添加 .row 了。
![image.png](https://upload-images.jianshu.io/upload_images/11414906-014e8aa181e09117.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
```html
<form class="form-horizontal">
    <div class="form-group">
        <label for="inputName" class="col-sm-2 control-label">姓名</label>
        <div class="col-sm-10">
        <input type="text" class="form-control" id="inputName" placeholder="姓名">
        </div>
    </div>
    <div class="form-group">
        <label for="inputPassword" class="col-sm-2 control-label">密码</label>
        <div class="col-sm-10">
        <input type="password" class="form-control" id="inputPassword" placeholder="密码">
        </div>
    </div>
    <div class="form-group">
        <div class="col-sm-offset-2 col-sm-10">
        <div class="checkbox">
            <label>
            <input type="checkbox"> 记住我
            </label>
        </div>
        </div>
    </div>
    <div class="form-group">
        <div class="col-sm-offset-2 col-sm-10">
        <button type="submit" class="btn btn-default">注册</button>
        </div>
    </div>
</form>
```




### d.  被支持的控件
输入框
包括大部分表单控件、文本输入域控件，还支持所有 HTML5 类型的输入控件： `text、password、datetime、datetime-local、date、month、time、week、number、email、url、search、tel` 和 `color`。



### e. 文本域
支持多行文本的表单控件。可根据需要改变 rows 属性。

![image.png](https://upload-images.jianshu.io/upload_images/11414906-eda19623d8bbc677.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```html
<textarea class="form-control" rows="3"></textarea>
```

### f. 多选和单选框
多选框（checkbox）用于选择列表中的一个或多个选项，而单选框（radio）用于从多个选项中只选择一个。
#### 普通堆叠在一起
![image.png](https://upload-images.jianshu.io/upload_images/11414906-be8e62f6ec24a1db.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


```html
<form class="form-horizontal">
    <div class="checkbox">
        <label>
        <input type="checkbox" value="">
        多选项
        </label>
    </div>
    <div class="checkbox">
            <label>
            <input type="checkbox" value="">
            多选项
            </label>
        </div>
    <div class="checkbox disabled">
    <label>
        <input type="checkbox" value="" disabled>
        这个选项被禁用
    </label>
    </div>
    
    <div class="radio">
    <label>
        <input type="radio" name="optionsRadios" id="optionsRadios1" value="option1" checked>
        这个选项是互斥选项，只能选择选项中的一个
    </label>
    </div>
    <div class="radio">
    <label>
        <input type="radio" name="optionsRadios" id="optionsRadios2" value="option2">
        这个选项是互斥选项，只能选择选项中的一个
    </label>
    </div>
    <div class="radio disabled">
    <label>
        <input type="radio" name="optionsRadios" id="optionsRadios3" value="option3" disabled>
        这个选项被禁用
    </label>
    </div>
</form>
```

#### 内联单选和多选框
通过将 .checkbox-inline 或 .radio-inline 类应用到一系列的多选框（checkbox）或单选框（radio）控件上，可以使这些控件排列在一行。

![image.png](https://upload-images.jianshu.io/upload_images/11414906-cb1603c495f404f0.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```html
<label class="checkbox-inline">
  <input type="checkbox" id="inlineCheckbox1" value="option1"> 1
</label>
<label class="checkbox-inline">
  <input type="checkbox" id="inlineCheckbox2" value="option2"> 2
</label>
<label class="checkbox-inline">
  <input type="checkbox" id="inlineCheckbox3" value="option3"> 3
</label>

<label class="radio-inline">
  <input type="radio" name="inlineRadioOptions" id="inlineRadio1" value="option1"> 1
</label>
<label class="radio-inline">
  <input type="radio" name="inlineRadioOptions" id="inlineRadio2" value="option2"> 2
</label>
<label class="radio-inline">
  <input type="radio" name="inlineRadioOptions" id="inlineRadio3" value="option3"> 3
</label>
```

### g. 下拉列表（select）
注意，很多原生选择菜单 - 即在 Safari 和 Chrome 中 - 的圆角是无法通过修改 border-radius 属性来改变的。

![image.png](https://upload-images.jianshu.io/upload_images/11414906-826e8ca0284d74cc.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


```html
<select class="form-control">
  <option>1</option>
  <option>2</option>
  <option>3</option>
  <option>4</option>
  <option>5</option>
</select>
```
![image.png](https://upload-images.jianshu.io/upload_images/11414906-0f3bba3b282755a5.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

### h. 控件尺寸
通过给控件的标签添加 .input-lg 类似的类可以为控件设置高度，通过 .col-lg-* 类似的类可以为控件设置宽度。

```
<input class="form-control input-lg " type="text" placeholder=".input-lg"> 
```
###  i. 添加校验状态（就是给输入控件的边框添加颜色）
Bootstrap 对表单控件的校验状态，如 error、warning 和 success 状态，都定义了样式。
使用时，添加 `.has-warning、.has-error` 或` .has-success` 类到这些控件的***父元素***即可。任何包含在此元素之内的 .control-label、.form-control 和 .help-block 元素都将接受这些校验状态的样式。
![image.png](https://upload-images.jianshu.io/upload_images/11414906-1a4c6dbabb40cca9.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```html
<div class="form-group has-success">
        <label class="control-label" for="inputSuccess1">输入成功</label>
        <input type="text" class="form-control" id="inputSuccess1" aria-describedby="helpBlock2">
        <span id="helpBlock2" class="help-block">一段帮助文字，可以是多行</span>
</div>
```

### 调整宽度
用栅格系统中的列（column）包裹输入框或其任何父元素，都可很容易的为其设置宽度。
![image.png](https://upload-images.jianshu.io/upload_images/11414906-9cf927845315d99c.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```html
<div class="row">
  <div class="col-xs-2">
    <input type="text" class="form-control" placeholder=".col-xs-2">
  </div>
  <div class="col-xs-3">
    <input type="text" class="form-control" placeholder=".col-xs-3">
  </div>
  <div class="col-xs-4">
    <input type="text" class="form-control" placeholder=".col-xs-4">
  </div>
</div>
```


## 5. 按钮
![image.png](https://upload-images.jianshu.io/upload_images/11414906-a2bd5a1e0e4051c3.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```html
<button type="button" class="btn btn-default">（默认样式）class="btn btn-default"</button>
<button type="button" class="btn btn-primary">（首选项）class="btn btn-primary"</button>
<div>
    <button type="button" class="btn btn-success">（成功）class="btn btn-success"</button>
    <button type="button" class="btn btn-info">（一般信息）class="btn btn-info"</button>
</div>
<button type="button" class="btn btn-warning">（警告）class="btn btn-warning"</button>
<button type="button" class="btn btn-danger">（危险）class="btn btn-danger"</button>
<button type="button" class="btn btn-link">（链接）class="btn btn-link"</button>
```

### 控制大小

使用 `.btn-lg、.btn-sm` 或 `.btn-xs` 就可以获得不同尺寸的按钮。

通过给按钮添加 `.btn-block` 类可以将其拉伸至父元素100%的宽度，而且按钮也变为了块级（block）元素。
![image.png](https://upload-images.jianshu.io/upload_images/11414906-b8fd87bd07769c1f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```html
<button type="button" class="btn btn-success btn-xs">（成功）</button>
<button type="button" class="btn btn-success btn-sm">（成功）</button>
<button type="button" class="btn btn-success btn-lg">（成功）</button>
<button type="button" class="btn btn-success btn-block">（成功）</button>
```

### 激活状态
当按钮处于激活状态时，其表现为被按压下去（底色更深、边框夜色更深、向内投射阴影）。
![image.png](https://upload-images.jianshu.io/upload_images/11414906-fd6d2f3fa3ee0e8e.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)



```html
<button type="button" class="btn btn-success active">（成功）class="btn btn-success active"</button>
<button type="button" class="btn btn-success">（成功）class="btn btn-success"</button>
```

### 禁用的按钮
为 `<button>`元素添加 `disabled` 属性，使其表现出禁用状态。

为 `<a>` 元素添加 `.disabled` 类，也会实现同样的效果

![image.png](https://upload-images.jianshu.io/upload_images/11414906-10a07f772d2470c0.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```html
<button type="button" class="btn btn-success btn-xs">（成功）</button>
<button type="button" class="btn btn-success btn-sm" disabled>（成功）</button>
<a href="#" class="btn btn-default btn-lg disabled" role="button">Link</a>
```

### 关闭按钮
通过使用一个象征关闭的图标，可以让模态框和警告框消失。
![image.png](https://upload-images.jianshu.io/upload_images/11414906-9d2e1ccca9c9a99e.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```html
<button type="button" class="close" aria-label="Close"><span aria-hidden="true">&times;</span></button>
```

## 6. 图片

### a. 响应式图片
在 Bootstrap 版本 3 中，通过为图片添加 `.img-responsive` 类可以让图片支持响应式布局。

其实质是为图片设置了 `max-width: 100%`;、 `height: auto`; 和 `display: block`; 属性，从而让图片在其父元素中更好的缩放。

如果需要让使用了 `.img-responsive` 类的图片水平居中，请使用 `.center-block` 类，不要用 `.text-center`

> SVG 图像和 IE 8-10
在 Internet Explorer 8-10 中，设置为 .img-responsive 的 SVG 图像显示出的尺寸不匀称。为了解决这个问题，在出问题的地方添加 width: 100% \9; 即可。Bootstrap 并没有自动为所有图像元素设置这一属性，因为这会导致其他图像格式出现错乱。

```html
<img src="..." class="img-responsive" alt="Responsive image">
```

### b. 图片形状
通过为 <img> 元素添加以下相应的类，可以让图片呈现不同的形状。

>跨浏览器兼容性
时刻牢记：Internet Explorer 8 不支持 CSS3 中的圆角属性。

![image.png](https://upload-images.jianshu.io/upload_images/11414906-633a2b246b6cbe4a.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```html
<img src="..." alt="..." class="img-rounded">
<img src="..." alt="..." class="img-circle">
<img src="..." alt="..." class="img-thumbnail">
```


## 7. 辅助类
### a. 字体颜色
通过颜色来展示意图，Bootstrap 提供了一组工具类。这些类可以应用于链接，并且在鼠标经过时颜色可以还可以加深，就像默认的链接一样。

![image.png](https://upload-images.jianshu.io/upload_images/11414906-330b6afaf5c57f05.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


```html
<p class="text-muted">此生如若有你，何惧岁月老去。</p>
<p class="text-primary">何处的风景美如画，却抵不过你笑如花。</p>
<p class="text-success">我喜欢你，笨拙而热烈，一无所有却又倾尽所有。</p>
<p class="text-info">"猜猜我的心在哪边?" "左边？" "错了，在你那边。"</p>
<p class="text-warning">别替我遮风，别替我挡雨，因为我怕身边突然没有你。</p>
<p class="text-danger">"我们合作一下吧！" "合作什么？" "以后的余生。"</p>

<a href="#" class="text-success>"半途而废可不好。" "所以我建议你。" "陪我一直到老。"</a>
```

### b. 文字背景色
和文本颜色类一样，使用任意情境背景色类就可以设置元素的背景。链接组件在鼠标经过时颜色会加深，就像上面所讲的情境文本颜色类一样。

![image.png](https://upload-images.jianshu.io/upload_images/11414906-9d02c934679f5d7f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```
<p class="bg-primary">我愿与你一房两人三餐四季，四海三山二心一生。</p>
<p class="bg-success">“你见过凌晨两点的太阳吗？”“我见过，噩梦醒来身旁你熟睡的脸。”</p>
<p class="bg-info">愿我能陪你度过每个春夏秋冬，就算终须一别也不辜负你我相遇。</p>
<p class="bg-warning">假如你爱上一个人，那个人没回绝也没接受，只是在享用你的付出，那么你就要懂得恰到好处。</p>
<p class="bg-danger">假如你爱上一个人，那个人也对你有意，只是因为实际的一些原因，没能走到一起，那么只能顺其天然</p>

<a href="#" class="bg-success">一行泪流下，是因为瓦解了脆弱；一段话入心，是因为触碰了心灵！</a>
```
### c. 快速浮动
通过添加一个类，可以将任意元素向左或向右浮动。!important 被用来明确 CSS 样式的优先级。

![image.png](https://upload-images.jianshu.io/upload_images/11414906-778978675cc41bd6.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```html
<div class="pull-left">
    时间，珍惜了就是黄金，虚度了就是荒芜；人生，尽心了就是精彩，敷衍了就是惋惜；
</div>
<div class="pull-right">家庭，有爱就是幸福，无爱就是牢笼。</div>
```

>不能用于导航条组件中
排列导航条中的组件时可以使用这些工具类：`.navbar-left` 或 `.navbar-right` 。

### 内容居中
为任意元素设置 `.center-block` 类，就是使其居中。
这会给其设置 `display: block` 和 `margin` 等相关属性。

```html
<div class="center-block">...</div>
```

### 清除浮动
通过为父元素添加 .clearfix 类可以很容易地清除浮动（float）。

```html
<div class="clearfix">...</div>
```

### 显示或隐藏内容
.show 和 .hidden 类可以强制任意元素显示或隐藏(对于屏幕阅读器也能起效)。
![image.png](https://upload-images.jianshu.io/upload_images/11414906-4089e0e558443e23.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```html
<div class="pull-left hidden">
    时间，珍惜了就是黄金，虚度了就是荒芜；人生，尽心了就是精彩，敷衍了就是惋惜；
</div>
<div class="center-block">家庭，有爱就是幸福，无爱就是牢笼。</div>
```

另外，.invisible 类可以被用来仅仅影响元素的可见性，也就是说，元素的 display 属性不被改变，并且这个元素仍然能够影响文档流的排布。

![image.png](https://upload-images.jianshu.io/upload_images/11414906-faedf55a9cab58c6.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```html
<div class="pull-left invisible">
    时间，珍惜了就是黄金，虚度了就是荒芜；人生，尽心了就是精彩，敷衍了就是惋惜；
</div>
<div class="center-block">家庭，有爱就是幸福，无爱就是牢笼。</div>
```

### 三角符号
通过使用三角符号可以指示某个元素具有下拉菜单的功能。

![image.png](https://upload-images.jianshu.io/upload_images/11414906-909f0309cc9c3f84.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

其方向默认是向下。
当其处于上拉菜单中，方向会自动随之调整为向上。

