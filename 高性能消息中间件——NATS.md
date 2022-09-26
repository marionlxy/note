# 高性能消息中间件——NATS

[![img](https://upload.jianshu.io/users/upload_avatars/14110732/1b5bbda6-2ceb-407a-a18d-42cbe6acabb3.jpg?imageMogr2/auto-orient/strip|imageView2/1/w/96/h/96/format/webp)](https://www.jianshu.com/u/fd963f762f12)

[Java架构_师](https://www.jianshu.com/u/fd963f762f12)关注

0.8682018.10.27 14:05:43字数 2,435阅读 10,165

前 言

这段时间我的主要工作内容是将公司系统中使用的RabbitMQ替换成NATS，而此之前我对Nats一无所知。经过一段时间紧张的学习和开发之后我顺利的完成了任务,并对消息中间件有了更深的了解。在此感谢同事钟亮在此过程中对我的帮助。NATS属于比较小众的一款中间件产品，中文资料基本上是没有的，故写以记之，为想学习Nats的同学提供一点帮助。

原创作者：万里

**在介绍NATS之前先了解下什么是分布式系统和消息中间件**

对于分布式系统的定义，一直以来我都没有找到或者想到特别简练而又合适的定义，这里引用一下Distributed System Concepts and Design (Thrid Edition)中的一句话A distributed system is one in which components located at networked computers communicate and coordinate their actions only by passing messages,从这句话我们可以看到几个重点，一是组件分布在网络计算机上，二是组件之间仅仅通过消息传递来通信并协调行动。消息中间件维基百科给出的定义为Message-oriented middleware(MOM) is software infrastructure focused on sending and receiving messages between distrubuted systems,意思就是面向消息的系统（消息中间件）是在分布式系统中完成消息的发送和接收的基础软件

![img](https://upload-images.jianshu.io/upload_images/14110732-eef23f510609911e.png!web?imageMogr2/auto-orient/strip|imageView2/2/w/494/format/webp)

消息中间件常被提及的好处即异步和解耦，市面上常常被使用到的中间件有RabbitMQ, ActiveMQ, Kafka等，他们的关注度和使用率都非常的高，并且使用起来也非常的方便。公司的WiseCloud产品就集成了RabbitMQ。而在下一个版本的更新中将会使用NATS来替换RabbitMQ。使用NATS的好处比较多首先就是其性能非常好，下面引用官网的性能对比图：

![img](https://upload-images.jianshu.io/upload_images/14110732-c677991f725e1298.png!web?imageMogr2/auto-orient/strip|imageView2/2/w/550/format/webp)

**NATS介绍**

NATS是一个开源、轻量级、高性能的分布式消息中间件，实现了高可伸缩性和优雅的Publish/Subscribe模型，使用Golang语言开发。NATS的开发哲学认为高质量的QoS应该在客户端构建，故只建立了Request-Reply，不提供 1.持久化 2.事务处理 3.增强的交付模式 4.企业级队列。

**NATS消息传递模型**

NATS支持各种消息传递模型，包括：

**发布订阅**（Publish Subscribe）

**请求回复**（Request Reply）

**队列订阅**（Queue Subscribers )

**提供的功能：**

**纯粹的发布订阅模型**（Pure pub-sub）

**服务器集群**（Cluster mode server）

**自动精简订阅者**（Auto-pruning of subscribers)

**基于文本协议**（Text-based protocol）

**多服务质量保证**（Multiple qualities of service - QoS）

**发布订阅**（Publish Subscribe）

NATS将publish/subscribe消息分发模型实现为一对多通信，发布者在Subject上发送消息，并且监听该Subject在任何活动的订阅者都会收到该消息

![img](https://upload-images.jianshu.io/upload_images/14110732-6cb83b9c69488c1f.png!web?imageMogr2/auto-orient/strip|imageView2/2/w/487/format/webp)

java:

```java
//publish

Connection nc = Nats.connect("nats://127.0.0.1:4222");

nc.publish("subject", "hello world".getBytes(StandardCharsets.UTF_8));

//subscribe

Subscription sub = nc.subscribe("subject");

Message msg = sub.nextMessage(Duration.ofMillis(500));

String response = new String(msg.getData(), StandardCharsets.

UTF_8);

或者是基于回调的**subscribe**

//subscribe

Dispatcher d = nc.createDispatcher(msg - >{

String response = new String(msg.getData(), StandardCharsets.UTF_8)

//do something

})

d.subscribe("subject");
```



**请求响应**（Request Reply）

NATS支持两种请求响应消息：点对点或多对多。点对点涉及最快或首先响应。在一对多的消息交换中，需要限制请求响应的限制

在Request Reply过程中，发布请求发布带有响应主题的消息，期望对该subject做出响应操作

![img](https://upload-images.jianshu.io/upload_images/14110732-3590a39c5fc2db0d.png!web?imageMogr2/auto-orient/strip|imageView2/2/w/487/format/webp)

java:

```java
// publish

Connection connection = Nats.connect("nats://127.0.0.1:4222");

String reply = "replyMsg";

//请求回应方法回调

Dispatcher d = connection.createDispatcher(msg -> 

System.out.println("reply: " + JSON.toJSONString(msg));

})

d.unsubscribe(repl , 1);

//订阅请求

d.subscribe(reply);

//发布请求

connection.publish("requestSub", reply, "request".getBytes(StandardCharsets.

UTF_8));

//subscribe

Connection nc = Nats.connect("nats://127.0.0.1:4222");

//注册订阅

Dispatcher dispatcher = nc.createDispatcher(msg -> {

System.out.println(JSON.toJSONString(msg));

nc.publish(msg.getReplyTo(), "this is reply".getBytes(StandardCharsets.UTF_8));

});

dispatcher.subscribe("requestSub");
```







**队列订阅&分享工作**（Queue Subscribers & Sharing Work）

NATS提供称为队列订阅的负载均衡功能，虽然名字为queue(队列)但是并不是我们所认为的那样。他的主要功能是将具有相同queue名字的subject进行负载均衡。使用队列订阅功能消息发布者不需要做任何改动，消息接受者需要具有相同的对列名欢迎工作一到五年的Java工程师朋友们加入Java架构交流：874811168 群内提供免费的Java架构学习资料

![img](https://upload-images.jianshu.io/upload_images/14110732-cda9857404465f15.png!web?imageMogr2/auto-orient/strip|imageView2/2/w/521/format/webp)

```JAVA
// Subscribe

Connection nc = Nats.connect();

Dispatcher d = nc.createDispatcher(msg -> {

//do something

System.out.println("msg: " + new String(msg.getData(),StandardCharsets.UTF_8));

});

d.subscribe("queSub", "queName");
```



**Nats-Spring集成**

NATS虽说是一个性能非常好的消息中间键，但是和Spring的集成不是很好。这里提供两个集成的思路

**CloudFoundry-Community/java-nats**

**Wanlinus/nats-spring**

**java-nats**

这是一个由CloudFoundry主导的一个NATS java客户端。提供了区别于官方的nats客户端，支持注解配置，对Spring有比较好的支持，但是此项目已经有1年多没有更新且不支持NATS Streaming。相应用法参考Github,这里不做详细讲解. 

**nats-spring**

由于开源社区只提供一个简单的NATS Client,缺少对注解和Spring的支持,所以我基于官方jnats客户端写了一个SpringBoot的兼容插件.主要是为了兼容spring boot amqp开发模式，尽量使用注解解决问题开发出来的，所以使用方法类似于在代码中使用@RabbitListener.具体使用方法如下

```java
{{git clonehttps://github.com/wanlinus/nats-spring.git

cd nats-spring

mvn clean install}}}

<dependency>

<groupId>cn.wanlinus</groupId>

<artifactId>nats-spring</artifactId>

<version>1.0.0.RELEASE</version>

</dependency>

application.yml

spring:

nats:

urls:

\- nats://127.0.0.1:4222

@EnableNats

@SpringBootApplication

public class NatsDemo2Application {

public static void main(String[] args) {

  欢迎Java工程师朋友们加入Java架构交流：874811168

 SpringApplication.run(NatsDemo2Application.class, args);



}

}

@Component

public class Foo{

@NatsSubscribe("haha")

public void message(Message message) {

System.out.println(message.getSubject() + " : " + new String(message.getData()));

}

}
```



**NATS Streaming介绍**

NATS由于不能保证消息的投递正确性和存在其他的缺点,NATS Streaming就孕育而生.他是一个由NATS提供支持的数据流系统,采用Go语言编写,NATS Streaming与核心NATS平台无缝嵌入，扩展和互操作.除了核心NATS平台的功能外,他还提供了以下功能:

**NATS Streaming特征**

**增强消息协议**(Enhanced message protocol)

**消息/事件持久化**(Message/event persistence)

**至少一次数据传输**(At-least-once-delivery)

**Publisher限速(**Publisher rate limiting)

**Subscriber速率匹配**(Rate matching/limiting per subscriber)

**按主题重发消息**(Historical message replay by subject)

**持续订阅**(Durable subscriptions)

**基本用法**

在使用NATS Streaming之前首先要启动服务器,在这里我选择使用docker容器

\# 4222 client默认连接端口

8222 Web端口

6222 集群通信端口

```SH
$ docker run -d -p 4222:4222 -p 8222:8222 -p 6222:6222 nats-streaming
```



STREAM: Starting nats-streaming-server[test-cluster] version 0.11.0

STREAM: ServerID: bzkKJL3jI4KW9Hqb0bC1Ae

STREAM: Go version: go1.11

Starting nats-server version 1.3.0

Git commit [not set]

Starting http monitor on 0.0.0.0:8222

Listening for client connections on 0.0.0.0:4222

Server is ready

STREAM: Recovering the state...

STREAM: No recovered state

STREAM: Message store is MEMORY

STREAM: ---------- Store Limits ----------

STREAM: Channels:         100 *

STREAM: --------- Channels Limits --------

STREAM:  Subscriptions:     1000 *

STREAM:  Messages   :    1000000 *

STREAM:  Bytes    :   976.56 MB *

STREAM:  Age     :   unlimited *

STREAM:  Inactivity  :   unlimited *

STREAM: ----------------------------------

java:

```JAVA
// 第一个参数表示clusterId,在启动NATS Streaming容器的时候确定

// 第二个参数表示clientID,连接客户端的唯一标识符

StreamingConnectionFactory cf = new StreamingConnectionFactory

("test-cluster", "bar");

//设置Nats服务器地址和端口,默认是nats://127.0.0.1:4222

cf.setNatsConnection(Nats.connect("nats://127.0.0.1:4222"));

StreamingConnection sc = cf.createConnection();

Publish: sc.publish("foo", "Hello World".getBytes());

Subscribe:

sc.subscribe("foo", msg -> {

System.out.println(new String(msg.getData(), StandardCharsets.UTF_8));

}, new SubscriptionOptions.Builder()

​    .durableName("aa")

​    .deliverAllAvailable().build());
```



在使用NATS Streaming的时候需要注意订阅主题不支持通配符,在订阅消息时传入MessageHandler函数是接口实现和SubscriptionOptions对象.MessageHandler提供消息回调处理, SubscriptionOptions用于设置订阅选项,比如设置Queue, durableName, ack等。

**Streaming-Spring集成**

作为一款优秀的消息中间件,却没有对Spring做集成,这是非常的可惜的事情.所以为了在工作中方便的使用他,我开发了一个很小的插件.虽然还有很大的改进空间，不过在公司的项目中却能够很好的运行.他开发思路和nats-spring差不多，所以使用方式也是大同小异，具体如下：

```JAVA
{{git clone[https://github.com/wanlinus/na ... g.git](https://github.com/wanlinus/nats-streaming-spring.git)

cd nats-streaming-spring

mvn clean install}}}

<dependency>

<groupId>cn.wanlinus</groupId>

<artifactId>nats-streaming-spring</artifactId>

欢迎Java工程师朋友们加入Java架构交流：874811168

群内提供免费的Java架构学习资料

<version>1.0.0-SNAPSHOT</version>

</dependency>

application.yml

spring:

nats:

streaming:

nats-url: nats://127.0.0.1:4222

cluster-id: test-cluster

@EnableNatsStreaming

@SpringBootApplication

public class StreamingDemoApplication {

public static void main(String[] args) {

 SpringApplication.run(StreamingDemoApplication.class, args);

}

//发布消息只需要注入StreamingConnection

@Autowired

private StreamingConnection sc;

public void sendMsg(){

 sc.publish("foo", "publish message".getBytes())

}

}

@Service

public class A {

@Subscribe(value = "foo", durableName = "dname", queue = "queue")

public void asd(Message message) throws IOException {

 System.out.println(new String(message.getData(), StandardCharsets.UTF_8));

}

}


```



两个插件由于是为了结合项目所写的，所以里面有些部分并不通用。后续的开发中我将会继续进行抽象和改进。