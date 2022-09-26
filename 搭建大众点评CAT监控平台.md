#### **搭建大众点评CAT监控平台**

##### **环境清单：**

 * CentOS  7.3
 * jdk-8u121-linux-x64.rpm
 * apache-tomcat-8.5.45.tar.gz
* apache-maven-3.3.9-bin.tar.gz
 * mysql-5.7.23-1.el7.x86_64.rpm-bundle.tar
 * cat-2.0.0.tar.gz
 * git  1.8.3.1



| IP            | hostname | 软件                              | 内存要求 |
| ------------- | -------- | --------------------------------- | -------- |
| 192.168.122.6 | cat-6    | Mysql,Tomcat,Maven,git,cat.tar.gz | 3G及以上 |

###### 		注意事项：

​			1.网络要稳定，必要时开手机热点；



###### JDK，git安装	

```
curl -o /etc/yum.repos.d/163.repo http://mirrors.163.com/.help/CentOS7-Base-163.repo 
curl  -o /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo 
rpm -ivh jdk-8u121-linux-x64.rpm
yum -y install git
```



###### Tomcat安装并启动

```
tar xf apache-tomcat-8.5.45.tar.gz -C /usr/local/
cd  /usr/local/
mv apache-tomcat-8.5.45/ tomcat
echo "export CATAINA_HOME=/usr/local/tomcat" >> /etc/profile
source /etc/profile
java  -version
/usr/local/tomcat/bin/startup.sh
ss -antp | grep 8080
```



###### Mvnen安装

```
tar xf /root/apache-maven-3.3.9-bin.tar.gz -C /usr/local/
cd /usr/local/
mv apache-maven-3.3.9/ maven
cat >> /etc/bashrc <<EOF
export M2_HOME=/usr/local/maven
export M2=\$M2_HOME/bin
export PATH=\$M2:\$PATH:\$HOME/bin:/usr/bin/git
EOF
source  /etc/bashrc
mvn -version
```



###### Mysql安装

```
yum -y install net-tools
rpm -e mariadb-libs --nodeps
tar xvf /root/mysql-5.7.23-1.el7.x86_64.rpm-bundle.tar -C /usr/local/
cd /usr/local/
rpm -ivh mysql-community-server-5.7.23-1.el7.x86_64.rpm  mysql-community-client-5.7.23-1.el7.x86_64.rpm mysql-community-common-5.7.23-1.el7.x86_64.rpm mysql-community-libs-5.7.23-1.el7.x86_64.rpm 
systemctl start mysqld
sed -i '/\[mysqld]/ a skip-grant-tables' /etc/my.cnf
systemctl restart mysqld
mysql <<EOF
        update mysql.user set authentication_string='' where user='root' and Host='localhost';
        flush privileges;
EOF
sed -i '/skip-grant/d' /etc/my.cnf
yum -y install expect
systemctl restart mysqld
expect <<-EOF
spawn  mysqladmin -uroot -p password "XUANji.19"
        expect {
                "password" { send "\r"  }
}
        expect eof
EOF
rm -rf /usr/local/mysql-community-*
```



###### Cat源码包下载

```
yum -y install wget
wget -O /root/cat-2.0.0.tar.gz https://codeload.github.com/dianping/cat/tar.gz/v2.0.0
	OR
git clone https://github.com/dianping/cat.git	推荐使用上面，快；

tar xvf /root/cat-2.0.0.tar.gz  -C /opt/
cd /opt/cat-2.0.0/
mkdir -p /data/appdatas/cat && mkdir -p /data/applogs/cat
mvn install -Dmaven.test.skip=true		# 我开热点差不多下载了十分钟，很多小jar包文件

mvn cat:install							# 不到十秒钟，会出现三串提示，输入MysqlIP：Port
		格式：			jdbc:mysql://127.0.0.1:3306
		Mysql用户名：	root
		Mysql密码：	XUANji.19
	
cd /opt/cat-2.0.0/cat-home/
mvn jetty:run							# 稍等一分钟，启动要下载一点jar包；
ss -antp | grep 2281		# 出来端口就可以浏览器访问了
```

