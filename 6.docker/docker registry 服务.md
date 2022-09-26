# docker registry 服务

## 在本地搭建registry服务

docker run -d -p 5000:5000 --name registry registry:2

## 将本地镜像推送到本地的registry服务，分2步

1. 将本地镜像重现打tag，目的是让镜像名中包含注册中心服务地址

   docker tag centos:7 localhost:5000/centos:7

2. docker push

   docker push localhost:5000/centos:7

## 如果是外部的服务器会有https的报错，例如`docker push 10.36.145.100:5000/hello-world`

## 需要更改本地docker服务端的设置，允许访问不安全的注册服务器

vi /etc/docker/daemon.json

```json
{
  "insecure-registries" : ["10.36.145.100:5000"]
}
```



然后重启docker服务端，再次尝试推送镜像

docker push 10.36.145.100:5000/hello-world

## 删除本地的 `10.36.145.100:5000/hello-world`镜像以进行拉取测试

## 从本地registry拉取刚推送的镜像

docker pull 10.36.145.100:5000/hello-world

## 查看镜像仓库内的镜像名：

curl 10.36.145.100:5000/v2/_catalog |python -m json.tool

返回结果例如：

```json
{
    "repositories": [
        "centos",
        "centos_tmp",
        "cgq_centos",
        "cgq_python",
        "hello-world",
        "lijinwangcentos",
        "liuyishou",
        "python",
        "yan_centos"
    ]
}
```



## 查看镜像仓库内镜像名的TAG

curl 10.36.145.100:5000/v2/python/tags/list |python -m json.tool

查询上面列举出的python镜像的版本：

返回结果例如：

```json
{
    "name": "python",
    "tags": [
        "3.7.4",
        "3.6.4"
    ]
}
```

