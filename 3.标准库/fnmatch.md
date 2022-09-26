## Python标准库: fnmatch

-Author: bavdu

-Email: bavduer@163.com

-GitHub: https://github.com/bavdu

---



大多数情况下, 使用字符串查找文件能够满足基本需求, 但是如果需要更加灵活的字符串匹配, 我们可以使用fnmatch标准库, 它支持使用通配符进行字符串匹配. fnmatch库只有四个函数.

- fnmatch: 判断文件名是否符合特定的模式
- fnmatchcase: 判断文件名是否符合特定的模式, 强制区分大小写
- filter: 返回输入列表中, 符合特定模式的文件名列表
- translate: 将通配符模式转换成正则表达式

```python
import fnmatch
import os

for names in os.listdir("fileAll"):
    if fnmatch.fnmatch(names, "*.jpg"):
        print(names)
```

```python
import fnmatch
import os

images = ['*.jpg', '*.png', '*.jpeg', '*.tif', '*.tiff']

for names in os.listdir('fileAll'):
    for image in images:
        if fnmatch.fnmatch(names, image):
            print(names)
```

```python
files = fnmatch.filter(os.listdir('directory'), '*jpeg')
print(files)
```

