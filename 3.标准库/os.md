## Python标准库: os

-Author: bavdu

-Email: bavduer@163.com

-GitHub: https://github.com/bavdu

---



```python
import os

os.listdir(dirname)										-列出dirname下的目录和文件(返回对象列表) 
os.getcwd()														-获得当前工作目录  

os.chdir(dirname)											-改变工作目录到dirname 
os.path.isdir(name)										-判断name是不是一个目录,name不是目录就返回false  
os.path.isfile(name)									-判断name是不是一个文件,不存在name也返回false  
os.path.exists(name)									-判断是否存在文件或目录name  
os.path.getsize(name)									-获得文件大小,如果name是目录返回0L
os.path.abspath(name)									-获得绝对路径  
  
os.path.split(name)										-分割文件名与目录
(事实上如果你完全使用目录,它也会将最后一个目录作为文件名而分离,同时它不会判断文件或目录是否存在)

os.path.splitext()										-分离文件名与扩展名  
os.path.join(path,name)								-连接目录与文件名或目录

os.path.basename(path)								-返回文件名  
os.path.dirname(path)									-返回文件路径

os.remove(dir) 												-dir为要删除的文件夹或者文件路径  
os.rmdir(path) 												-path要删除的目录的路径.
																			需要说明的是,使用os.rmdir删除的目录必须为空目录,否则函数出错
```





在实际工作过程中, 我们经常会遇到的是查找某个目录及其子目录下的所有文件. 比如: 查找某个目录及其子目录下所有的图片文件、查找某个目录及其子目录下最大的十个文件. 可以使用os.walk(), walk函数可以遍历当前目录及其子目录下所有的文件, walk()会返回一个三元组(dirpath, dirnames, filenames). 

- dirpath: 保存的当前目录
- dirnames: 当前目录下的子目录列表
- filenames: 当前目录下的文件列表

```python
import fnmatch
import os

images = ['*.jpg', '*.png', '*.jpeg', '*.tif', '*.tiff']
matches = []
for dirPath, dirNames, fileNames in os.walk("fileAll"):
    for picture in images:
        for filename in fnmatch.filter(fileNames, picture):
            matches.append(os.path.join(dirPath, filename))
    print(matches)
```

