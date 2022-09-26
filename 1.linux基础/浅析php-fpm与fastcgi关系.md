## 浅析php-fpm与fastcgi关系

-Author: bavdu

-Mail: bavduer@163.com

-Github: https://github.com/bavdu

---



在整个网站架构中, Web Server只是内容分发者. 举个例子：

- 客户端请求的是index.html, 那么Web Server会去文件系统中找到这个文件, 发给浏览器, 这里分发的是静态数据

![未命名文件](/Users/chaoliu/Downloads/未命名文件.png)

如果请求的是 index.php, 根据配置文件, Web Server知道这个不是静态文件, 需要去找 PHP 解析器来处理, 那么他会把这个请求简单处理, 然后交给PHP解析器

![未命名文件 (1)](/Users/chaoliu/Downloads/未命名文件 (1).png)

当Web Server收到 index.php 这个请求后, 会启动对应的 CGI 程序, 这里就是PHP的解析器. 

接下来PHP解析器会解析php.ini文件, 初始化执行环境, 然后处理请求, 再以规定CGI规定的格式返回处理后的结果, 退出进程

Web server再把结果返回给浏览器. 

这就是一个完整的动态PHP Web访问流程, 接下来再引出这些概念, 就好理解多了

- **CGI：**是 Web Server 与 Web Application 之间数据交换的一种协议
- **FastCGI：**同 CGI，是一种通信协议，但比 CGI 在效率上做了一些优化。同样，SCGI 协议与 FastCGI 类似
- **PHP-CGI：**是 PHP （Web Application）对 Web Server 提供的 CGI 协议的接口程序
- **PHP-FPM：**是 PHP（Web Application）对 Web Server 提供的 FastCGI 协议的接口程序, 额外还提供了相对智能一些任务管理