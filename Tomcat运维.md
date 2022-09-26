###  Tomcat运维

下载印象笔记

### Tomcat运维

### Tomcat运维

#### JVM虚拟机常识

##### 两个常识问题

作为了解JVM虚拟机的开始。我们很有必要弄明白以下两个问题。

**1.什么是JAVA虚拟机**

```
所谓虚拟机，就是一台虚拟的计算机。他是一款软件，用来执行一系列虚拟计算机指令。大体上，虚拟机可以分为系统虚拟机和程序虚拟机。大名鼎鼎的VisualBox、VMware就属于系统虚拟机。他们完全是对物理计算机的仿真。提供了一个可以运行完整操作系统的软件平台。
程序虚拟机的典型代表就是Java虚拟机，它专门为执行单个计算机程序而设计，在Java虚拟机中执行的指令我们称为Java字节码指令。无论是系统虚拟机还是程序虚拟机，在上面运行的软件都呗限制于虚拟机提供的资源中。
```

**2.JAVA如何做到跨平台**

```
同一个JAVA程序(JAVA字节码的集合)，通过JAVA虚拟机(JVM)运行于各大主流操作系统平台
比如Windows、CentOS、Ubuntu等。程序以虚拟机为中介，来实现跨平台。
```

![img](http://img.liuwenqi.com/blog/2019-09-09-034835.jpg)

##### 虚拟机基本结构

我们要对JVM虚拟机的结构有一个感性的认知。毕竟我们不是编程人员，认知程度达不到那么深刻。

![img](http://img.liuwenqi.com/blog/2019-09-09-034847.jpg)

```
1、类加载子系统
负责从文件系统或者网络中加载Class信息，加载的类信息存放于一块称为方法区的内存空间。除了类信息外，方法区中可能还会存放运行时常量池信息，包括字符串字面量和数字量。

2、Java堆
在虚拟机启动的时候建立，它是Java程序最主要的内存工作区域。几乎所有的Java对象实例都放Java堆中。堆空间是所有线程共享的，这是一块与Java应用密切相关的内存区间。

3、Java的NIO库(直接内存)
允许Java程序使用直接内存。直接内存是在Java堆外的、直接向系统申请的内存区间。通常访问直接内存的速度会优于Java堆。因此出于性能考虑，读写频繁的场合可能会考虑使用直接内存。由于直接内存在Java堆外，因此它的大小不会受限于Xmx指定的最大堆大小。但是系统内存是有限的，Java堆和直接内存的总和依然受限于操作系统能给出的最大内存。

4、垃圾回收系统
垃圾回收系统是Java虚拟机的重要组成部分，垃圾回收器可以对方法区、Java堆和直接内存进行回收。

5、Java栈
每一个Java虚拟机线程都有一个私有的Java栈。一个线程的Java栈在线程创建的时候被创建。Java保存着帧信息，Java栈中保存着局部变量、方法参数，同时和Java方法的调用、返回密切相关。

6、本地方法
与Java栈非常类似，最大的不同在于Java栈用于Java方法的调用，而本地方法栈用于本地方法调用。作为Java虚拟机的重要扩展，Java虚拟机运行Java程序直接调用本地方法（通常使用C编写）。

7、PC寄存器
每个线程私有的空间，Java虚拟机会为每一个Java线程创建PC寄存器。在任意时刻，一个Java线程总是在执行一个方法，这个正在被执行的方法称为当前方法。如果当前方法不是本地方法，PC寄存器就会指向当前正在被执行的指令。如果当前方法是本地方法，那么PC寄存的值就是undefined.

8、执行引擎
是Java虚拟机最核心组件之一，它负责执行虚拟机的字节码。现代虚拟机为了提高执行效率。会使用即时编译技术将方法编译成机器码后再执行。
```

##### 虚拟机堆内存结构

![img](http://img.liuwenqi.com/blog/2019-09-09-034853.jpg)

JVM中堆空间可以划分三个大区，年轻代，老年代，永久代（方法区）。

**年轻代**

```
所有新生成的对象首先都是放在年轻代的。年轻代的目标就是尽可能快速的收集掉那些生命周期短的对象。年轻代分为三个区域：EDEN、Survivor0(简称S0,也通常称为from区)、Survivor1(简称S1，也通常称为to区)。其中S0与S1的大小是相同等大的，三者所占年轻代的比例大致为8:1:1，S0与S1就像"孪生兄弟"一样，我们大家不必去纠结此比例(可以通过修改JVM某些动态参数来调整)的大小.只需谨记三点就好：
1.S0与S1相同大小。
2.EDEN区远比S(S0+S1)区大,EDEN占了整个年轻代的大致70%至80%左右。 
3.年轻代分为2个区(EDEN区、Survivor区)、3个板块(EDEN、S0、S1)。
```

**老年代**

```
在年轻代中经历了N次垃圾回收后仍然存活的对象，就会被放到年老代中。因此，可以认为年老代中存放的都是一些生命周期较长的对象。
那一个对象到底要经过多少次垃圾回收才能从年轻代进入老年代呢?
我们通常认为在新生代中的对象，每经历过一次GC,如果它没有被回收，它的年龄就会被加1， 虚拟机提供了一个参数来可控制新生代对象的最大年龄:MaxTenuringThreshold。默认情况下，这个参数是15。 也就是说，在新生代的对象最多经历15次GC，就可以进入老年代。
假如存在一种这样的情况，一个新生代对象，占用新生代空间特别大。在GC时若不回收，新生代空间将不足。但是若要回收，程序还没有使用完。此时就不会依据这个对象的 MaxTenuringThreshold 参数。而是直接晋升到老年代。所以说
MaxTenuringThreshold 参数是晋升老年代的充分非必要条件。
```

**永久代（方法区）**

```
也通常被叫做方法区。是一块所有线程共享的内存区域。用于保存系统的类信息，比如类的字段、方法、常量池。
```

##### 常用虚拟机参数

JVM虚拟机提供了三种类型参数

**标准参数**

```
标准参数中包括功能和输出的参数都是很稳定的，很可能在将来的JVM版本中不会改变。你可以用 java 命令（或者是用 java -help）检索出所有标准参数。
```

**X类型参数**

```
非标准化的参数，在将来的版本中可能会改变。所有的这类参数都以 -X 开始，并且可以用 java -X 来检索。
注意，不能保证所有参数都可以被检索出来，其中就没有 -Xcomp 。
```

**XX类型参数**

```
非标准化的参数（到目前为止最多的），它们同样不是标准的，甚至很长一段时间内不被列出来。然而，在实际情况中 X 参数和 XX 参数并没有什么不同。X 参数的功能是十分稳定的，然而很多 XX 参数仍在实验当中（主要是 JVM 的开发者用于 debugging 和调优 JVM 自身的实现）。

用一句话来说明 XX 参数的语法。所有的 XX 参数都以"-XX:"开始，但是随后的语法不同，取决于参数的类型：
1）对于布尔类型的参数，我们有"+"或"-"，然后才设置 JVM 选项的实际名称。
   例如，-XX:+ 用于激活选项，而 -XX:- 用于注销选项。
   Example:
   开启GC日志的参数: -XX:+PrintGC
2) 对于需要非布尔值的参数，如 string 或者 integer，我们先写参数的名称，后面加上"="，最后赋值。
   例如: -XX:MaxPermSize=2048m
```

以上介绍完了JVM的三类参数类型，接下来我们主要聊聊常用的JVM参数。

**跟踪JAVA虚拟机的垃圾回收**

JVM的GC日志已替换的方式（>）写入的，而不是追加（>>），如果下次写入到同一个文件中的话，以前的GC内容会被清空。这导致我们重启了JAVA服务后，历史的GC日志将会丢失。

```
-XX:+PrintGC 
-XX:+PrintGCDetails
-XX:+PrintGCTimeStamps
-Xloggc:filename
```

**例**

初期写法，会导致JAVA服务重启后，GC日志丢失

```
-XX:+PrintGCDetails -XX:+PrintGCTimeStamps -Xloggc:/data0/logs/gc.log
```

在这里GC日志支持％p和％t两个参数：

- ％p将会被替换为对应的进度PID
- ％t将会被替代为时间字符串，格式为：YYYY-MM-DD_HH-MM-SS

彻底写法，无论如何重启，GC历史日志将不会丢失

```
-XX:+PrintGCDetails -XX:+PrintGCDateStamps -Xloggc:/data0/logs/gc-%t.log"
```

**配置JAVA虚拟机的堆空间**

```
-Xms:初始堆大小
-Xmx:最大堆大小
实际生产环境中， 我们通常将初四化堆(-Xms) 和 最大堆(-Xmx) 设置为一样大。以避免程序频繁的申请堆空间。

-Xmn: 设置年轻代大小
-XX:NewRatio=老年代/新生代 //设置年轻代和年老代的比值
-XX:SurvivorRatio=eden/from=eden/to //年轻代中Eden区与两个Survivor区的比值
```

例：

```
-Xmn1m -XX:SurvivorRatio=2
// 这里的eden 于from(to) 的比值为2:1 ，因此在新生代为1m的区间里， eden 区为 512KB, from 和 to 分别为 256KB. 而新生代总大小为 512KB + 256KB + 256KB = 1MB
-Xms20M -Xmx20M -XX:NewRatio=2
// 这里 老年代和新生代的比值为2:1 ， 因此在堆大小为20MB的区间里， 新生代大小为: 20MB * 1/3 = 6MB左右
// 老年代为 13MB 左右。
```

**配置JAVA虚拟机的永久区（方法区）**

```
-XX:PermSize=n    //设置初始化值
-XX:MaxPermSize=n //设置持久代大小
```

**配置JAVA虚拟机的栈**

```
-Xss128k 设置每个线程的堆栈大小
```

##### 常用垃圾回收算法

**引用计数法**

```
引用计数法是最经典的一种垃圾回收算法。其实现很简单，对于一个A对象，只要有任何一个对象引用了A，则A的引用计算器就加1，当引用失效时，引用计数器减1.只要A的引用计数器值为0，则对象A就不可能再被使用。
       
虽然其思想实现都很简单（为每一个对象配备一个整型的计数器），但是该算法却存在两个严重的问题：
1）无法处理循环引用的问题，因此在Java的垃圾回收器中，没有使用该算法。
2）引用计数器要求在每次因引用产生和消除的时候，需要伴随一个加法操作和减法操作，对系统性能会有一定的影响。

一个简单的循环引用问题描述:
对象A和对象B，对象A中含有对象B的引用，对象B中含有对象A的引用。此时对象A和B的引用计数器都不为0，但是系统中却不存在任何第三个对象引用A和B。也就是说A和B是应该被回收的垃圾对象，但由于垃圾对象间的互相引用使得垃圾回收器无法识别，从而引起内存泄漏（由于某种原因不能回收垃圾对象占用的内存空间）。

如下图：不可达对象出现循环引用，它的引用计数器不为0
```

![img](http://img.liuwenqi.com/blog/2019-09-09-034902.jpg)

```
注意：由于引用计数器算法存在循环引用以及性能的问题，java虚拟机并未使用此算法作为垃圾回收算法。
【可达对象】通过根对象的进行引用搜索，最终可以到达的对象。
【不可达对象】通过根对象进行引用搜索，最终没有被引用到的对象。
```

**标记清除法**

```
标记-清除算法是现代垃圾回收算法的思想基础。标记-清除算法将垃圾回收分为两个阶段：标记阶段和清除阶段。一种可行的实现是，在标记阶段，首先通过根节点，标记所有从根节点开始的可达对象。因此，未被标记的对象就是未被引用的垃圾对象。然后，在清除阶段，清除所有未被标记的对象。
缺陷:
①.效率问题：标记清除过程效率都不高。 
②.空间问题：标记清除之后会产生大量的不连续的内存碎片
```

![img](http://img.liuwenqi.com/blog/2019-09-09-034908.jpg)

**标记压缩法**

```
标记-压缩算法适合用于存活对象较多的场合，如老年代。它在标记-清除算法的基础上做了一些优化。和标记-清除算法一样，标记-压缩算法也首先需要从根节点开始，对所有可达对象做一次标记。但之后，它并不简单的清理未标记的对象，而是将所有的存活对象压缩到内存的一端。之后，清理边界外所有的空间。
标记-压缩算法的最终效果等同于标记-清除算法执行完成之后，再进行一次内存碎片的整理。基于此，这种算法也解决了内存碎片问题。
```

![img](http://img.liuwenqi.com/blog/2019-09-09-034913.jpg)

**复制算法**

```
与标记-清除算法相比，复制算法是一种相对高效的回收方法。但不适用于存活对象较多的场合，如老年代。它将原有的内存空间分为两块，每次只使用其中一块，在垃圾回收时，将正在使用的内存中的存活对象复制到未使用的内存块中，之后，清除正在使用的内存块中的所有对象，交换两个内存的角色，完成垃圾回收
缺陷： 
空间浪费，浪费了50%的内存空间。
```

![img](http://img.liuwenqi.com/blog/2019-09-09-034917.jpg)

```
我们前文介绍的JVM 的新生代，分为Eden 及 S0 和 S1 ， 其中S0 和 S1 是两个容量相等的区域。其实在JVM 的垃圾回收中, S0 和 S1 就使用了复制算法作为它们的垃圾回收算法。
# 使用JDK 自带的jmap 工具，打印一个JVM 虚拟机的堆信息. 
# 其中 187136 为JVM 的PID

[root@java00 ~]# jmap -heap 187136
Attaching to process ID 187136, please wait...
Debugger attached successfully.
Server compiler detected.
JVM version is 24.80-b11

using parallel threads in the new generation.
using thread-local object allocation.
Concurrent Mark-Sweep GC

Heap Configuration:
   MinHeapFreeRatio = 40
   MaxHeapFreeRatio = 70
   MaxHeapSize      = 4294967296 (4096.0MB)
   NewSize          = 1431633920 (1365.3125MB)
   MaxNewSize       = 1431633920 (1365.3125MB)
   OldSize          = 2863267840 (2730.625MB)
   NewRatio         = 2
   SurvivorRatio    = 8
   PermSize         = 1073741824 (1024.0MB)
   MaxPermSize      = 2147483648 (2048.0MB)
   G1HeapRegionSize = 0 (0.0MB)

Heap Usage:
New Generation (Eden + 1 Survivor Space):
   capacity = 1288503296 (1228.8125MB)
   used     = 570069688 (543.6608200073242MB)
   free     = 718433608 (685.1516799926758MB)
   44.242780734027704% used
Eden Space:
   capacity = 1145372672 (1092.3125MB)
   used     = 561190696 (535.1931533813477MB)
   free     = 584181976 (557.1193466186523MB)
   48.99634064256773% used
From Space:
   capacity = 143130624 (136.5MB)
   used     = 8878992 (8.467666625976562MB)
   free     = 134251632 (128.03233337402344MB)
   6.2034187736092035% used
To Space:
   capacity = 143130624 (136.5MB)
   used     = 0 (0.0MB)
   free     = 143130624 (136.5MB)
   0.0% used
concurrent mark-sweep generation:
   capacity = 2863333376 (2730.6875MB)
   used     = 46529976 (44.37444305419922MB)
   free     = 2816803400 (2686.313056945801MB)
   1.6250282412102892% used
Perm Generation:
   capacity = 1073741824 (1024.0MB)
   used     = 47940496 (45.71961975097656MB)
   free     = 1025801328 (978.2803802490234MB)
   4.464806616306305% used

20796 interned Strings occupying 2411488 bytes.
# 截取部分信息如下: From(S0) 和 To(S1) 区间采用了复制算法，不论什么时候执行jmap 区间，都会发现
# 有一个区间的使用用于都是 0.0% used
From Space:
   capacity = 143130624 (136.5MB)
   used     = 8878992 (8.467666625976562MB)
   free     = 134251632 (128.03233337402344MB)
   6.2034187736092035% used
To Space:
   capacity = 143130624 (136.5MB)
   used     = 0 (0.0MB)
   free     = 143130624 (136.5MB)
   0.0% used
```

**分代算法**

```
    前文介绍了复制、标记清除、标记压缩等垃圾回收算法。在所有的算法中，并没有一种算法可以完全取代其他算法，它们都具有自己独特的优势和特点。因此，根据垃圾回收对象的特性，使用合适的算法回收，才是明智的选择。分代算法就是基于这种思想，它将内存区间根据对象的特点分成几块，根据每块内存区间的特点，使用不同的回收算法，以提高垃圾回收的效率。
    一般来说，Java虚拟机会将所有的新建对象都放到称为新生代的区域中，新生代的特点是对象朝生夕灭，大约90%的新建对象会被回收，因此新生代比较适合使用复制算法。当一个对象经过几次回收后依然存活，对象就会被放到称为老年代的内存空间。在老年代中，几乎所有对象都经过几次垃圾回收后依然得以存活的。因此可以认为对象在一段时期内，甚至在应用程序的整个生命周期中，将是常驻内存的。
    在极端情况下，老年代对象的存活率可以达到100%。如果依然使用复制算法回收老年代，将需要复制大量对象。再加上老年代的回收性价比也要低于新生代，因此这种做法是不可取的。根据分代的思想，可以对老年代的回收使用与新生代不通的标记压缩或者标记清除算法，以提高垃圾回收效率。
```

![img](http://img.liuwenqi.com/blog/2019-09-09-034923.jpg)

#### JVM运维实用排障工具

##### jps

```
用来查看Java进程的具体状态, 包括进程ID，进程启动的路径及启动参数等等，与unix上的ps类似，只不过jps是用来显示java进程，可以把jps理解为ps的一个子集。
常用参数如下:
-q：忽略输出的类名、Jar名以及传递给main方法的参数，只输出pid
-m：输出传递给main方法的参数，如果是内嵌的JVM则输出为null
-l：输出完全的包名，应用主类名，jar的完全路径名
-v：输出传给jvm的参数

注意: 使用jps 时的运行账户要和JVM 虚拟机启动的账户一致。若启动JVM虚拟机是运行的账户为www，那使用jps指令时，也要使用www 用户去指定。 sudo -u www jps
```

例

```
// 查看已经运行的JVM 进程的实际启动参数
[root@mouse03 bin]# jps  -v
38372 Jps -Dapplication.home=/usr/local/jdk -Xms8m
38360 Bootstrap -Djava.util.logging.config.file=/data0/tomcat/conf/logging.properties -Djava.util.logging.manager=org.apache.juli.ClassLoaderLogManager -Xms4096m -Xmx4096m -XX:PermSize=1024m -XX:MaxPermSize=2048m -Djdk.tls.ephemeralDHKeySize=2048 -Djava.protocol.handler.pkgs=org.apache.catalina.webresources -Dignore.endorsed.dirs= -Dcatalina.base=/data0/tomcat -Dcatalina.home=/data0/tomcat -Djava.io.tmpdir=/data0/tomcat/temp
```

##### jstack

```
jstack用于打印出给定的java进程ID或core file或远程调试服务的Java堆栈信息。如果现在运行的java程序呈现hung的状态，jstack是非常有用的。此信息通常在运维的过程中被保存起来(保存故障现场)，以供RD们去分析故障。
常用参数如下:
jstack <pid>
jstack [-l] <pid> //长列表. 打印关于锁的附加信息
jstack [-F] <pid> //当’jstack [-l] pid’没有响应的时候强制打印栈信息
```

例

```
// 打印JVM 的堆栈信息，以供问题排查
[root@mouse03 ~]# jstack -F 38360 > /tmp/jstack.log
```

##### 资讯

```
可以查看或修改运行时的JVM进程的参数。
常用参数:
jinfo [option] pid
    
where <option> is one of:
    -flag <name>         to print the value of the named VM flag
    -flag [+|-]<name>    to enable or disable the named VM flag
    -flag <name>=<value> to set the named VM flag to the given value
    -flags               to print VM flags
```

例

```
// 根据 PID 查看目前分配的最大堆栈
[root@mouse03 ~]# jinfo -flag MaxHeapSize 38360
-XX:MaxHeapSize=4294967296
// 动态更改 JVM 的最大堆栈值
[root@mouse03 ~]# jinfo -flag MaxHeapSize=4294967296  38360
Exception in thread "main" com.sun.tools.attach.AttachOperationFailedException: flag 'MaxHeapSize' cannot be changed

	at sun.tools.attach.LinuxVirtualMachine.execute(LinuxVirtualMachine.java:229)
	at sun.tools.attach.HotSpotVirtualMachine.executeCommand(HotSpotVirtualMachine.java:261)
	at sun.tools.attach.HotSpotVirtualMachine.setFlag(HotSpotVirtualMachine.java:234)
	at sun.tools.jinfo.JInfo.flag(JInfo.java:134)
	at sun.tools.jinfo.JInfo.main(JInfo.java:81)

// jinfo 并不能动态的改变所有的JVM 参数。 那到底有哪些参数能够被动态的改变呢?
// java -XX:+PrintFlagsFinal -version 答应JVM 的所有参数
// java -XX:+PrintFlagsFinal -version | grep manageable

[root@mouse03 ~]# java -XX:+PrintFlagsFinal -version | grep manageable
     intx CMSAbortablePrecleanWaitMillis            = 100                                 {manageable}
     intx CMSTriggerInterval                        = -1                                  {manageable}
     intx CMSWaitDuration                           = 2000                                {manageable}
     bool HeapDumpAfterFullGC                       = false                               {manageable}
     bool HeapDumpBeforeFullGC                      = false                               {manageable}
     bool HeapDumpOnOutOfMemoryError                = false                               {manageable}
    ccstr HeapDumpPath                              =                                     {manageable}
    uintx MaxHeapFreeRatio                          = 70                                  {manageable}
    uintx MinHeapFreeRatio                          = 40                                  {manageable}
     bool PrintClassHistogram                       = false                               {manageable}
     bool PrintClassHistogramAfterFullGC            = false                               {manageable}
     bool PrintClassHistogramBeforeFullGC           = false                               {manageable}
     bool PrintConcurrentLocks                      = false                               {manageable}
     bool PrintGC                                   = false                               {manageable}
     bool PrintGCDateStamps                         = false                               {manageable}
     bool PrintGCDetails                            = false                               {manageable}
     bool PrintGCID                                 = false                               {manageable}
     bool PrintGCTimeStamps                         = false                               {manageable}
     
// 也只有以上这些值才能够动态的被改变
[root@mouse03 ~]# jinfo -flag CMSWaitDuration=1900  38360
# 查看， jinfo -flags 查看 JVM 的 flags 
[root@mouse03 ~]# jinfo -flags 38360
Attaching to process ID 38360, please wait...
Debugger attached successfully.
Server compiler detected.
JVM version is 25.91-b14
Non-default VM flags: -XX:CICompilerCount=2 -XX:CMSWaitDuration=1900 -XX:InitialHeapSize=4294967296 -XX:MaxHeapSize=4294967296 -XX:MaxNewSize=1431633920 -XX:MinHeapDeltaBytes=196608 -XX:NewSize=1431633920 -XX:OldSize=2863333376 -XX:+UseCompressedClassPointers -XX:+UseCompressedOops -XX:+UseFastUnorderedTimeStamps
Command line:  -Djava.util.logging.config.file=/data0/tomcat/conf/logging.properties -Djava.util.logging.manager=org.apache.juli.ClassLoaderLogManager -Xms4096m -Xmx4096m -XX:PermSize=1024m -XX:MaxPermSize=2048m -Djdk.tls.ephemeralDHKeySize=2048 -Djava.protocol.handler.pkgs=org.apache.catalina.webresources -Dignore.endorsed.dirs= -Dcatalina.base=/data0/tomcat -Dcatalina.home=/data0/tomcat -Djava.io.tmpdir=/data0/tomcat/temp
```

##### 统计

```
// 监控JVM 的状态，常用指令:
# jstat -gc 113059 1000 10 // 打印PID 为 113059 JVM 状态，一共打印10次，每次间隔时间为1s(1000ms)
// 注 jstat 的用法超级强大， 我们这里只是列举出列其中一个简单的应用。
```

例

```
# jstat -gc 113059 1000 10
 S0C    S1C    S0U    S1U      EC       EU        OC         OU       PC     PU    YGC     YGCT    FGC    FGCT     GCT
195904.0 195904.0  0.0   21610.3 1567680.0 1516721.9 8526272.0  3557507.8  1048576.0 163148.4   2577   92.033   0      0.000   92.033
195904.0 195904.0 23600.9  0.0   1567680.0 142541.6 8526272.0  3558435.8  1048576.0 163148.4   2578   92.060   0      0.000   92.060
195904.0 195904.0 23600.9  0.0   1567680.0 266338.1 8526272.0  3558435.8  1048576.0 163148.4   2578   92.060   0      0.000   92.060
195904.0 195904.0 23600.9  0.0   1567680.0 413941.8 8526272.0  3558435.8  1048576.0 163148.4   2578   92.060   0      0.000   92.060
195904.0 195904.0 23600.9  0.0   1567680.0 642390.6 8526272.0  3558435.8  1048576.0 163148.4   2578   92.060   0      0.000   92.060
195904.0 195904.0 23600.9  0.0   1567680.0 813957.3 8526272.0  3558435.8  1048576.0 163148.4   2578   92.060   0      0.000   92.060
195904.0 195904.0 23600.9  0.0   1567680.0 984223.2 8526272.0  3558435.8  1048576.0 163148.4   2578   92.060   0      0.000   92.060
195904.0 195904.0 23600.9  0.0   1567680.0 1155472.7 8526272.0  3558435.8  1048576.0 163148.4   2578   92.060   0      0.000   92.060
195904.0 195904.0 23600.9  0.0   1567680.0 1399228.5 8526272.0  3558435.8  1048576.0 163148.4   2578   92.060   0      0.000   92.060
195904.0 195904.0  0.0   23866.6 1567680.0 38005.6  8526272.0  3559196.7  1048576.0 163148.4   2579   92.092   0      0.000   92.092
```

**初步意义如下**

| 列名     | 说明                                                         |
| -------- | ------------------------------------------------------------ |
| S0C      | 新生代中幸存者空间中S0当前容量的大小（KB）                   |
| S1C      | 新生代中幸存者空间中S1当前容量的大小（KB）                   |
| S0U      | 新生代中幸存者空间中S0容量使用的大小（KB）                   |
| S1U      | 新生代中幸存者空间中S1容量使用的大小（KB）                   |
| 欧共体   | 伊甸园空间当前容量的大小（KB）                               |
| 欧盟     | 伊甸空间容量使用的大小（KB）                                 |
| 超频     | 旧空间当前容量的大小（KB）                                   |
| OU       | 旧空间使用容量的大小（KB）                                   |
| 个人电脑 | 永久空间当前容量的大小（KB）                                 |
| 聚氨酯   | 永久空间使用容量的大小（KB）                                 |
| 青年会   | 从应用程序启动到采样时发生Young GC的次数                     |
| 青年会   | 从应用程序启动到采样时Young GC所用的时间（秒）               |
| FGC      | 从应用程序启动到采样时发生                                   |
| FGCT     | 从应用程序启动到采样时Full GC所用的时间（秒）                |
| GCT      | T从应用程序启动到采样时用于垃圾回收的总时间（单位秒），它的值等于YGC + FGC |

##### jvmtop

```
以上介绍的jps、jstack、jinfo等都是安装JDK 时自带的系统分析工具，而jvmtop是一款开源的JVM工具。
它的下载地址如下: https://github.com/patric-r/jvmtop
顾名思义，它是一个只针对JVM的工具，展示的方式和unix的top命令相似.
jvmtop 提供了两个视图，一个是概览视图，可以展示出当前机器的所有的 JVM 的情况. 还有一个视图是详情视图，展示一个 JVM 的详细情况.
```

**概览视图**

```
jvmtop.sh
```

![img](http://img.liuwenqi.com/blog/2019-09-09-034935.jpg)

```
其中，各个字段的意义分别如下：
PID：进程 ID
MAIN-CLASS：main 类的名字
HPCUR：当前被使用的 heap 的大小
HPMAX：最大可用的 heap 的大小
NHCUR：当前被使用的非 heap 大小（比如：perm gen）
NHMAX：最大可用的非 heap 大小
CPU：CPU 的使用情况
GC：消耗在 GC 上的时间比例
VM：JVM 的提供者，大版本号，小版本号，图中的意思是 Apple 提供的 JDK 6U51 版本。
USERNAME：当前的用户名
#T：线程数量
DL：是否有现成发生死锁
```

**详情视图**

```
jvmtop.sh <pid>
```

![img](http://img.liuwenqi.com/blog/2019-09-09-15191835567998.jpg)

```
其中，各个字段的意义如下：
TID：线程 ID
NAME：线程名
STATE：线程状态
CPU：线程当前的 CPU 占用情况
TOTALCPU：从线程被创建开始总体的 CPU 占用情况
BLOCKBY：阻塞这个线程的线程 ID
```

#### JVM运维实用监控工具

##### 虚拟机

```
VisualVM 是一款免费的性能分析工具。它通过 jvmstat、JMX、SA（Serviceability Agent）以及 Attach API 等多种方式从程序运行时获得实时数据，从而进行动态的性能分析。同时，它能自动选择更快更轻量级的技术尽量减少性能分析对应用程序造成的影响，提高性能分析的精度。
```

**安装VisualVM**

```
到官网下载相应操作系统对应的软件.
官网地址: http://visualvm.github.io/
```

**安装VisualVM插件**

```
VisualVM 插件中心提供很多插件以供安装。可以通过 VisualVM 应用程序安装，或者从 VisualVM 插件中心手动下载插件，然后离线安装。
    
    从 VisualVM 插件中心安装插件步骤:
    * 从主菜单中选择“工具”>“插件”。
    * 在“可用插件”标签中，选中该插件的“安装”复选框。单击”安装“。
    * 逐步完成插件安装程序。
    
    离线安装插件步骤:
    * 到插件中心官网: http://visualvm.github.io/pluginscenters.html 下周对应的VisualVM版本的插件
    * 从主菜单中选择“工具”>“插件”。
    * 在“已下载”标签中,点击"添加插件"按钮,选择已下载的插件文件 (以.nbm结尾) 打开。
    * 选中要打开的插件文件，并单击"安装"按钮，逐步完成插件安装程序。
```

**如何监控JVM**

```
那如何通过VisualVM 去分析远程的JVM虚拟机里的信息呢?
首先要在JVM中开启相关配置，以供VisualVM能够从中获取JVM的信息，如何配置JVM呢？ 这里以Tomcat为例:

在Tomcat的 catalina.sh 或者是setenv.sh 脚本中加上如下参数
 -Dcom.sun.management.jmxremote 
 -Dcom.sun.management.jmxremote.port=一个监听端口 
 -Dcom.sun.management.jmxremote.authenticate=false 
 -Dcom.sun.management.jmxremote.ssl=false 
 -Djava.rmi.server.hostname=可解析的主机名称

具体测试参数如下:
 -Dcom.sun.management.jmxremote 
 -Dcom.sun.management.jmxremote.port=11412 
 -Dcom.sun.management.jmxremote.authenticate=false 
 -Dcom.sun.management.jmxremote.ssl=false 
 -Djava.rmi.server.hostname=java01.qfedu.com

 注意这里的java01.qfedu.com 必须是DNS可解析的主机名，11412 为监听端口

 其次在VisualVM 中配置连接到上面配置的服务器加端口的地址上去:
 * 在VisualVM中选择"远程"
 * 在弹出的窗口中选择"添加远程主机"
 * 此时会在远程中，多出一台主机。此时点击多出来的主机
 * 添加连接JVM相关的信息
```

**VisualVM如何监控JVM具体操作截图**

![img](http://img.liuwenqi.com/blog/2019-09-09-061019.jpg)

![img](http://img.liuwenqi.com/blog/2019-09-09-061022.jpg)

![img](http://img.liuwenqi.com/blog/2019-09-09-061028.jpg)

![img](http://img.liuwenqi.com/blog/2019-09-09-061039.jpg)

![img](http://img.liuwenqi.com/blog/2019-09-09-061045.jpg)

##### JmxTrans

JmxTrans是一个可以实时通过JMX查询JVM虚拟机状态的工具，它可以将通过JMX查询到的信息实时的录入到Ganglia，Graphite，Zabbix等。

![img](http://img.liuwenqi.com/blog/2019-09-09-061049.png)

**安装JmxTrans**

```
// 下载 RPM 包，下载地址: http://central.maven.org/maven2/org/jmxtrans/jmxtrans/
// 这里下载的RPM包为: http://central.maven.org/maven2/org/jmxtrans/jmxtrans/266/jmxtrans-266.rpm
# yum -y install java // 由于jmxtrans 打包的原因，安全前必须依赖java软件包。所以安装。
# rpm -ivh jmxtrans-266.rpm // 若无法正常运行，可以试试其他版本
// 安装完成后，
// 有关 jmxtrans 程序安装在 /usr/share/jmxtrans 目录中
// 有关 jmxtrans 程序的启动脚本 /etc/init.d/jmxtrans
// 有关 jmxtrans 程序抓取JMX 的配置存放在 /var/lib/jmxtrans, 且是json文件的格式
// 有关 jmxtrans 程序的配置文件 /etc/jmxtrans/wrapper.conf
// 有关 jmxtrans 程序启动是的错误信息存储在 /var/log/jmxtrans/jmxtrans.log 
```

**使用JmxTrans采集数据**

在/ var / lib / jmxtrans目录下，创建test.json文件。软后重启jmxtrans服务。

由于是测试，我们将收集到的JVM信息保存到了本地的/tmp/output.txt文件中

```
{
  "servers": [
    {
      "numQueryThreads": 3,
      "host": "10.200.16.228", //换成JVM 所在的服务器
      "port": 11415,       // 换成JMX 端口
      "queries": [
        {
          "outputWriters": [
            {
              "@class" : "com.googlecode.jmxtrans.model.output.KeyOutWriter",
              "outputFile" : "/tmp/output.txt"
            }
          ],
          "resultAlias": "heap",
          "obj": "java.lang:type=Memory",
          "attr": [
            "HeapMemoryUsage",
            "NonHeapMemoryUsage"
          ]
        },
        {
          "outputWriters": [
            {
              "@class" : "com.googlecode.jmxtrans.model.output.KeyOutWriter",
              "outputFile" : "/tmp/output.txt"
           }
          ],
          "resultAlias": "thread",
          "obj": "java.lang:type=Threading",
          "attr": [
            "ThreadCount",
            "PeakThreadCount",
            "DaemonThreadCount",
            "CurrentThreadCpuTime",
            "CurrentThreadUserTime",
            "TotalStartedThreadCount"
          ]
        },
        {
          "outputWriters": [
            {
              "@class" : "com.googlecode.jmxtrans.model.output.KeyOutWriter",
              "outputFile" : "/tmp/output.txt"
            }
          ],
          "resultAlias": "operatingsystem",
          "obj": "java.lang:type=OperatingSystem",
          "attr": [
            "ProcessCpuTime",
            "ProcessCpuLoad",
            "SystemCpuLoad",
            "SystemLoadAverage",
            "FreeSwapSpaceSize",
            "TotalSwapSpaceSize",
            "TotalPhysicalMemorySize",
            "CommittedVirtualMemorySize",
            "OpenFileDescriptorCount",
            "AvailableProcessors",
            "MaxFileDescriptorCount",
            "FreePhysicalMemorySize"
          ]
        }
      ]
    }
  ]
}
```

参考输出结果：

```
[root@mouse03 jmxtrans]# cat /tmp/output.txt
10_200_16_228_11415.thread.ThreadCount	418	1518065577329
10_200_16_228_11415.thread.PeakThreadCount	445	1518065577329
10_200_16_228_11415.thread.DaemonThreadCount	417	1518065577329
10_200_16_228_11415.thread.CurrentThreadCpuTime	4065386	1518065577329
10_200_16_228_11415.thread.CurrentThreadUserTime	0	1518065577329
10_200_16_228_11415.thread.TotalStartedThreadCount	53766	1518065577329
10_200_16_228_11415.heap.HeapMemoryUsage_init	4294967296	1518065577343
10_200_16_228_11415.heap.HeapMemoryUsage_committed	4151836672	1518065577343
10_200_16_228_11415.heap.HeapMemoryUsage_max	4151836672	1518065577343
10_200_16_228_11415.heap.HeapMemoryUsage_used	1066173744	1518065577343
10_200_16_228_11415.heap.NonHeapMemoryUsage_init	1076297728	1518065577343
10_200_16_228_11415.heap.NonHeapMemoryUsage_committed	1087897600	1518065577343
10_200_16_228_11415.heap.NonHeapMemoryUsage_max	2197815296	1518065577343
10_200_16_228_11415.heap.NonHeapMemoryUsage_used	99018384	1518065577343
10_200_16_228_11415.operatingsystem.ProcessCpuTime	30701230000000	1518065577381
10_200_16_228_11415.operatingsystem.ProcessCpuLoad	3.976670201484624E-4	1518065577381
10_200_16_228_11415.operatingsystem.SystemCpuLoad	0.060445387062566275	1518065577381
10_200_16_228_11415.operatingsystem.SystemLoadAverage	2.06	1518065577381
10_200_16_228_11415.operatingsystem.FreeSwapSpaceSize	6357475328	1518065577381
10_200_16_228_11415.operatingsystem.TotalSwapSpaceSize	8565813248	1518065577381
10_200_16_228_11415.operatingsystem.TotalPhysicalMemorySize	67266252800	1518065577381
10_200_16_228_11415.operatingsystem.CommittedVirtualMemorySize	25674649600	1518065577381
10_200_16_228_11415.operatingsystem.OpenFileDescriptorCount	1102	1518065577381
10_200_16_228_11415.operatingsystem.AvailableProcessors	32	1518065577381
10_200_16_228_11415.operatingsystem.MaxFileDescriptorCount	65535	1518065577381
10_200_16_228_11415.operatingsystem.FreePhysicalMemorySize	700805120	1518065577381
```

**JmxTrans的配置json文件是怎么写出来的**

这里就要结合上一节提到的VirtualVM + MBeans插件了，我们所有通过JmxTrans获取到的JVM里的信息，

在JVM里被称为Mbeans。

```
        {
          "outputWriters": [
            {
              "@class" : "com.googlecode.jmxtrans.model.output.KeyOutWriter",
              "outputFile" : "/tmp/output.txt"
            }
          ],
          "resultAlias": "heap",
          "obj": "java.lang:type=Memory",
          "attr": [
            "HeapMemoryUsage",
            "NonHeapMemoryUsage"
          ]
        }
          "outputWriters": [
            {
              "@class" : "com.googlecode.jmxtrans.model.output.KeyOutWriter",
              "outputFile" : "/tmp/output.txt"
            }
          ]
//这部分信息标示，采集到的信息存储到哪里，我们这里存储到了本地文件 /tmp/output.txt 中
"resultAlias": "heap",
// 给采集到的堆栈信息和非堆栈信息加了一个类似metric 的前缀，所以我们在输出文件中看到了一下这些内容
10_200_16_228_11415.heap.HeapMemoryUsage_init	4294967296	1518065577343
10_200_16_228_11415.heap.HeapMemoryUsage_committed	4151836672	1518065577343
10_200_16_228_11415.heap.HeapMemoryUsage_max	4151836672	1518065577343
10_200_16_228_11415.heap.HeapMemoryUsage_used	1066173744	1518065577343
10_200_16_228_11415.heap.NonHeapMemoryUsage_init	1076297728	1518065577343
10_200_16_228_11415.heap.NonHeapMemoryUsage_committed	1087897600	1518065577343
10_200_16_228_11415.heap.NonHeapMemoryUsage_max	2197815296	1518065577343
10_200_16_228_11415.heap.NonHeapMemoryUsage_used	99018384	1518065577343
"obj": "java.lang:type=Memory",
// 这一部分的信息获取， 就要结合 VirtualVM + MBeans 了。 找到ObjName ,将里面的Value 原样复制过来就好
// 这是来告诉 JmxTrans 收集 Memory 信息，那到底收集内存里的一些什么东西呢？ 我们继续看下面的解释。
```

![img](http://img.liuwenqi.com/blog/2019-09-09-061100.png)

```
          "attr": [
            "HeapMemoryUsage",
            "NonHeapMemoryUsage"
          ]
// 告诉JmxTrans ， 收集内存里的 HeapMemoryUsage 和  NonHeapMemoryUsage 这两个属性。那 Memory 里
// 都有啥属性，怎么去查看呢？ 这里还是离不开  VirtualVM + MBeans 的帮助。同样，我们将属性名字原样粘
// 贴过来就好
```

![img](http://img.liuwenqi.com/blog/2019-09-09-061445.png)

其实JmxTrans的使用不是很复杂，主要是如何去表达要获取到的属性。我们这里只是列表了最基本，也是最常见的方法。要想详细的了解JmxTrans的使用。可以学习它的官方文档：https ：//github.com/jmxtrans/jmxtrans/wiki

#### Tomcat运维实战

##### Tomcat是什么

```
Tomcat是Apache软件基金会（Apache Software Foundation）的Jakarta 项目中的一个核心项目，是一款轻量级Web应用服务器，是Servlet规范和JSP规范的开源实现。由于Tomcat技术先进、性能稳定，而且免费，因而深受Java爱好者的喜爱并得到了部分软件开发商的认可。这也使它成为目前比较流行的Web应用服务器。

Tomcat最初是由Sun的软件构架师詹姆斯·邓肯·戴维森开发的，由Sun贡献给Apache软件基金会。由于大部分开源项目O'Reilly都会出一本相关的书，并且将其封面设计成某个动物的素描，因此他希望将此项目以一个动物的名字命名。因为他希望这种动物能够自己照顾自己，最终他将其命名为Tomcat（英语公猫或其他雄性猫科动物），Tomcat的Logo兼吉祥物也被设计成了一只公猫。
```

##### 部署Tomcat + Jenkins

```
既然Tomcat是一个WEB应用服务器，这个服务器中运行的程序是什么语言的呢? PHP、PYTHON、JAVA还是ASP等呢？
Tomcat 服务器在生产环境中主要作为JAVA程序的WEB服务器。我们这里以Tomcat + jenkins 的部署为例来运行 jenkins 服。
   1、安装JDK8、并配置JAVA_HOME 等相关信息(新版本jenkins只有jdk8支持)
   JAVA_HOME="/usr/local/jdk"
   CLASSPATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar
   PATH=$PATH:"$JAVA_HOME/bin"
   2、安装Tomcat,启动Tomcat 并访问http://127.0.0.1:8080(这是使用了tomcat8 做测试)
   3、下载jenkins的war包程序
      http://mirrors.shu.edu.cn/jenkins/war/2.108/jenkins.war
   4、将jenksins.war 放到解压后的tomcat 的webapps 目录中
   5、重启tomcat,并访问 http://127.0.0.1/jenkins
```

##### 日志格式配置

```
<Valve className="org.apache.catalina.valves.AccessLogValve" directory="/data0/www/logs"
               prefix="jenkins-" suffix="-access_log"
               pattern="%{X-Real-IP}i - %v %t &quot;%r&quot; - %s %b %T &quot;%{Referer}i&quot; &quot;%{User-Agent}i&quot; %a &quot;-&quot; &quot;-&quot;" >
```

##### JVM参数优化

```
JAVA_OPTS="$JAVA_OPTS -Xms4096m -Xmx4096m -XX:PermSize=1024m -XX:MaxPermSize=2048m"
```

##### 开启GC日志

```
JAVA_OPTS="$JAVA_OPTS -XX:+PrintGCDetails -XX:+PrintGCDateStamps -Xloggc:/data0/logs/gc-%t.log"
```

##### 开启JMX端口便利监控

```
CATALINA_OPTS="$CATALINA_OPTS -Dcom.sun.management.jmxremote 
-Dcom.sun.management.jmxremote.port=10028 
-Dcom.sun.management.jmxremote.authenticate=false 
-Dcom.sun.management.jmxremote.ssl=false 
-Djava.rmi.server.hostname=java69-matrix.zeus.lianjia.com"
```

##### 取消JVM的预设DNS缓存时间

不缓存DNS记录，避免DNS解析更改后要重启JVM虚拟机

```
CATALINA_OPTS="$CATALINA_OPTS -Dsun.net.inetaddr.ttl=0 -Dsun.net.inetaddr.negative.ttl=0
```

保存到我的笔记

如