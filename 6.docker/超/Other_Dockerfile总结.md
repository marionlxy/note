## Dockerfile总结

-Author: bavdu

-Email: bavduer@163.com

-Github: https://github.com/bavdu

---



**/* FROM \[:\]\[AS\] 设置基础镜像 */**

`FROM centos:latest`



**/* RUN \["executable", "param1", "param2"\] 运行命令 */** 

执行shell脚本, 应当尽量少的执行RUN命令, 因为每次执行都会使docker增加一层只读层, 例子如下:

```dockerfile
Example:
RUN /bin/bash -c 'source $HOME/.bashrc; echo $HOME'

Example Other01:
RUN source $HOME/.bashrc \
echo $HOME

Example Other02:
RUN ["/bin/bash", "-c", "source $HOME/.bashrc; echo $HOME"]
```



**/* CMD \["executable", "param1", "param2"] 启动容器后执行的默认命令 */ **

Dockerfile中最好只设置一个CMD命令, 大于一个的时候只执行最后一个CMD, 最好放在Dockerfile的最后一行, 作为启动后的默认命令

```dockerfile
CMD ["catalina.sh", "run"]
```



**/* LABEL = =... 镜像标签 */**

```dockerfile
LABEL version="1.0"
LABEL description="This text illustrates that label-values can span multiple lines."
```



**/* EXPOSE \[\] 暴露容器端口 */**

```dockerfile
EXPOSE 80/tcp
EXPOSE 80/udp
```



**/* ENV \ =: 设置容器环境变量 */**

```dockerfile
ENV myName John Doe
ENV myDog Rex The Dog
ENV myCat fluffy
```



**/* ADD [--chown=:] ... \ \[--chown=:\]\["",... ""\]拷贝文件到镜像 */**

拷贝一个新文件、文件夹、远程文件的URLS, 把他们添加到镜像的文件系统中. 路径书写为绝对路径或者由WORKDIR定义的相对路径. ADD命令和COPY的方法相同, 但当本地文件夹内的文件形式为压缩包的时候, 传输到镜像里面时会自动的解压缩再拷贝, ADD还支持从URL中获取文件但是不支持自动的解压缩.

```dockerfile
ADD hom* /mydir/			# 添加所有以"hom"开头的文件到/mydir中
ADD hom?.txt /mydir/        # ?替换任何单个的字符, “e.g.”, "home.txt"

ADD test relativeDir/       # 添加"test"到 `WORKDIR`/relativeDir/
ADD test /absoluteDir/      # 添加"test"到 /absoluteDir/

ENV cpath /home/zb			# 配合ENV及WORKDIR进行拷贝
ENV zbpath=/home/lala
WORKDIR $cpath
ADD **.jpg $cpath
ADD **.jpg $zbpath

# 通过--chown指定添加文件或者文件夹的用户名和组名
# ADD [--chown=<user/uid>:<group/gid>] ["<src>",... "<dest>"]
ADD [--chown=55:mygroup] ["files*", "/somedir/"]
```

