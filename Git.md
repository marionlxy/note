## Git

Author: ***liuchao***

Email: ***bavduer@163.com***



***<u>Git历史</u>***

&emsp;&emsp;很多人都知道,Linus在1991年创建了开源的Linux，从此Linux系统不断发展,已经成为最大的服务器系统软件了。Linus虽然创建了Linux,但Linux的壮大是靠全世界热心的志愿者参与的,这么多人在世界各地为Linux编写代码,那Linux的代码是如何管理的呢？事实是,在2002年以前,世界各地的志愿者把源代码文件通过diff的方式发给Linus,然后由Linus本人通过手工方式合并代码！你也许会想,为什么Linus不把Linux代码放到版本控制系统里呢？不是有CVS、SVN这些免费的版本控制系统吗？因为Linus坚定地反对CVS和SVN,这些集中式的版本控制系统不但速度慢,而且必须联网才能使用。有一些商用的版本控制系统,虽然比CVS、SVN好用，但那是付费的,和Linux的开源精神不符。不过到了2002年,Linux系统已经发展了十年了,代码库之大让Linus很难继续通过手工方式管理了,社区的弟兄们也对这种方式表达了强烈不满,于是Linus选择了一个商业的版本控制系统BitKeeper,BitKeeper的东家BitMover公司出于人道主义精神，授权Linux社区免费使用这个版本控制系统。安定团结的大好局面在2005年就被打破了,原因是Linux社区牛人聚集,不免沾染了一些梁山好汉的江湖习气。开发Samba的Andrew试图破解BitKeeper的协议(这么干的其实也不只他一个),被BitMover公司发现了（监控工作做得不错！）,于是BitMover公司怒了,要收回Linux社区的免费使用权。Linus可以向BitMover公司道个歉，保证以后严格管教弟兄们，嗯，这是不可能的。实际情况是这样的：Linus花了两周时间自己用C写了一个分布式版本控制系统，这就是Git！一个月之内，Linux系统的源码已经由Git管理了！牛是怎么定义的呢？大家可以体会一下。Git迅速成为最流行的分布式版本控制系统，尤其是2008年，GitHub网站上线了，它为开源项目免费提供Git存储,无数开源项目开始迁移至GitHub,包括jQuery, PHP,Ruby等等。历史就是这么偶然，如果不是当年BitMover公司威胁Linux社区，可能现在我们就没有免费而超级好用的Git了。



***<u>集中式与分布式</u>***

&emsp;&emsp;集中式版本控制系统，版本库是集中存放在中央服务器的，而干活的时候，用的都是自己的电脑，所以要先从中央服务器取得最新的版本，然后开始干活，干完活了，再把自己的活推送给中央服务器。中央服务器就好比是一个图书馆，你要改一本书，必须先从图书馆借出来，然后回到家自己改，改完了，再放回图书馆.

&emsp;&emsp;分布式版本控制系统根本没有“中央服务器”，每个人的电脑上都是一个完整的版本库，这样，你工作的时候,就不需要联网了，因为版本库就在你自己的电脑上。既然每个人电脑上都有一个完整的版本库，那多个人如何协作呢?比方说你在自己电脑上改了文件A，你的同事也在他的电脑上改了文件A，这时，你们俩之间只需把各自的修改推送给对方，就可以互相看到对方的修改了。和集中式版本控制系统相比，分布式版本控制系统的安全性要高很多，因为每个人电脑里都有完整的版本库，某一个人的电脑坏掉了不要紧，随便从其他人那里复制一个就可以了。而集中式版本控制系统的中央服务器要是出了问题，所有人都没法干活了。在实际使用分布式版本控制系统的时候，其实很少在两人之间的电脑上推送版本库的修改，因为可能你们俩不在一个局域网内，两台电脑互相访问不了，也可能今天你的同事病了，他的电脑压根没有开机。因此，分布式版本控制系统通常也有一台充当“中央服务器”的电脑，但这个服务器的作用仅仅是用来方便“交换”大家的修改，没有它大家也一样干活，只是交换修改不方便而已。



***<u>git安装与操作流程</u>***

```shell
$ sudo yum -y install git
```

&emsp;&emsp;因为Git是分布式版本控制系统，所以，每个机器都必须自报家门：你的名字和Email地址。你也许会担心，如果有人故意冒充别人怎么办？这个不必担心，首先我们相信大家都是善良无知的群众，其次，真的有冒充的也是有办法可查的。

```shell
$ git config --global user.name "Your Name"
$ git config --global user.email "email@example.com"
```

创建一个空目录，在其中创建一个readme.txt文件和一个代码文件

```shell
$ mkdir learngit
$ cd learngit
$ git init
$ touch readme.txt code.py
```

在readme.txt文件中添加内容，并编写code.py中的代码

```shell
$ vim readme.txt
this is first version.
Date:2018/06/02.
Gitlearn.

$ vim code.py
#!/usr/bin/env python
# -.- coding: utf-8 -.-
print('Hello World.')


$ git add code.py readme.txt
$ git commit -m "Add two files, Date:2018/06/02"
[master (root-commit) 9789c4b] Add two files, Date:2018/06/02
 2 files changed, 7 insertions(+)
 create mode 100644 learngit/code.py
 create mode 100644 learngit/readme.txt
```

要随时掌握工作区的状态，使用`git status`命令,  如果`git status`告诉你有文件被修改过，用`git diff`可以查看修改内容

```shell
$ vim readme.txt
this is first version.
Date:2018/06/02.
Gitlearn.
git-test.

# 查看当前状态
$ git status
位于分支 master
尚未暂存以备提交的变更：
   （使用 "git add <file>..." 更新要提交的内容）
   （使用 "git checkout -- <file>..." 丢弃工作区的改动）

	修改：      readme.txt

修改尚未加入提交（使用 "git add" 和/或 "git commit -a"）

# 查看哪里被修改
$ git diff readme.txt 
diff --git a/readme.txt b/readme.txt
index 325152e..baf2d90 100644
--- a/readme.txt
+++ b/readme.txt
@@ -1,3 +1,4 @@
 this is first version.
 Date:2018/06/02.
 Gitlearn.
+git-test.

# 提交readme.txt文件
$ git add readme.txt
位于分支 master
要提交的变更：
 （使用 "git reset HEAD <file>..." 撤出暂存区）
      修改：      readme.txt

# 确定提交并描述
$ git commit -m "Add git-test. word"
[master 27e6043] Add git-test. word
 1 file changed, 1 insertion(+)

# 再次查看状态
$ git status
位于分支 master
无文件要提交，干净的工作区

# 若是远程仓库则需push
```



***<u>版本回退</u>***

&emsp;&emsp;你不断对文件进行修改，然后不断提交修改到版本库里，就好比玩RPG游戏时，每通过一关就会自动把游戏状态存盘，如果某一关没过去，你还可以选择读取前一关的状态。有些时候，在打Boss之前，你会手动存盘，以便万一打Boss失败了，可以从最近的地方重新开始。Git也是一样，每当你觉得文件修改到一定程度的时候，就可以“保存一个快照”，这个快照在Git中被称为`commit`。一旦你把文件改乱了，或者误删了文件，还可以从最近的一个`commit`恢复，然后继续工作，而不是把几个月的工作成果全部丢失.

```shell
# 继续上面代码修改
$ vim code.py
#!/usr/bin/env python
# -.- coding:utf-8 -.-
print('Hello Chao.')
print('Hello World.')

# 提交代码
$ git add code.py
$ git commit -m "Add code L1"
[master dcced98] Add code L1
 1 file changed, 1 insertion(+), 1 deletion(-)

# 查看历史提交版本
$ git log
commit dcced98431a90e0556bb4aacf97341ad062dd00a
Author: liuchao <bavduer@163.com>
Date:   Mon Jun 4 10:22:25 2018 +0800

    Add code L1

commit 928d0901026d0ec2b1ca7ae77f8767546e5ecba0
Author: liuchao <bavduer@163.com>
Date:   Mon Jun 4 10:15:19 2018 +0800

    Add git-test-2 word

commit 27e6043f5f57ce4911ec8ed141a6ece48138b3f6
Author: liuchao <bavduer@163.com>
Date:   Mon Jun 4 10:08:00 2018 +0800

    Add git-test. word

commit f87b2bc4073bbdedf31e11788529d70b83b8dd4f
Author: liuchao <bavduer@163.com>
Date:   Mon Jun 4 09:59:24 2018 +0800

    Add two files, Date:2018/06/02
```

使用`git reset --hard HEAD^`回退到上一个版本, 上一个版本就是`HEAD^`, 上上一个版本就是`HEAD^^`, 当然往上100个版本写100个`^`比较容易数不过来，所以写成`HEAD~100`

```shell
$ git reset --hard HEAD^
HEAD 现在位于 928d090 Add git-test-2 word
```

使用`git reset --hard dcced98431`回退到原来最新的版本, 若版本号忘记了可用`git reflog`查看全部历史

```shell
# 查看现在的log信息
$ git log
commit 928d0901026d0ec2b1ca7ae77f8767546e5ecba0
Author: liuchao <bavduer@163.com>
Date:   Mon Jun 4 10:15:19 2018 +0800

    Add git-test-2 word

commit 27e6043f5f57ce4911ec8ed141a6ece48138b3f6
Author: liuchao <bavduer@163.com>
Date:   Mon Jun 4 10:08:00 2018 +0800

    Add git-test. word

commit f87b2bc4073bbdedf31e11788529d70b83b8dd4f
Author: liuchao <bavduer@163.com>
Date:   Mon Jun 4 09:59:24 2018 +0800

    Add two files, Date:2018/06/02

$ git reflog
dcced98 HEAD@{0}: reset: moving to dcced9
928d090 HEAD@{1}: reset: moving to HEAD^
dcced98 HEAD@{2}: commit: Add code L1
928d090 HEAD@{3}: commit: Add git-test-2 word
27e6043 HEAD@{4}: commit: Add git-test. word
f87b2bc HEAD@{5}: commit (initial): Add two files, Date:2018/06/02

$ git reset --hard dcced98
HEAD 现在位于 dcced98 Add code L1
```



***<u>工作区与暂存区</u>***

Git和其他版本控制系统如SVN的一个不同之处就是有暂存区的概念

***版本库：****<u>在工作区中的.git不属于工作区, 而他呗成为版本库</u>.  Git的版本库里存了很多东西，其中最重要的就是称为stage的暂存区, 还有Git为我们自动创建的第一个分支`master`,以及指向`master`的一个指针叫`HEAD`*



***工作区：***<u>我们创建的learngit就是一个工作区, 也就是我们的文件夹</u>

***暂存区：***<u>`git add`提交的所有文件都提交到了stage暂存区中</u>

***分支区：***<u>`git commit`是把暂存区中的文件全部提交到默认创建的master分支中</u>

