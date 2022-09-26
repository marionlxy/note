## 企业级https配置方法



```nginx
#配置共享会话缓存大小，视站点访问情况设定
ssl_session_cache   shared:SSL:10m;
#配置会话超时时间
ssl_session_timeout 10m;
server {
    listen       80;
    listen 443 default ssl;
    server_name  www.xiaoxiaohei.com.cn;

    error_page 497  https://$host$uri?$args; #http重定向到https

    #设置长连接
    keepalive_timeout   70; 

    #HSTS策略
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    ssl on;
    ssl_certificate /etc/nginx/conf.d/1_www.xiaoxiaohei.com.cn_bundle.crt;
    ssl_certificate_key /etc/nginx/conf.d/2_www.xiaoxiaohei.com.cn.key;
    ssl_session_timeout 5m;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:HIGH:!aNULL:!MD5:!RC4:!DHE;
    ssl_prefer_server_ciphers on;

    #使用DH文件
    ssl_dhparam /etc/ssl/certs/dhparam.pem;

    #减少点击劫持
    add_header X-Frame-Options DENY;
    #禁止服务器自动解析资源类型
    add_header X-Content-Type-Options nosniff;
    #防XSS攻击
    add_header X-Xss-Protection 1;


    #charset koi8-r;
    #access_log  /var/log/nginx/log/host.access.log  main;

    location / {
        #root   /usr/share/nginx/html;
        root   /data/web/webapp/public;
        index  index.html index.htm index.php;

        if (!-e $request_filename) {
            rewrite  ^(.*)$  /index.php?s=/$1  last;
            break;
        }

    }

    #error_page  404              /404.html;

    # redirect server error pages to the static page /50x.html
    #
    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        #root   /usr/share/nginx/html;
        root   /data/web/webapp/public;
    }

    # proxy the PHP scripts to Apache listening on 127.0.0.1:80
    #
    #location ~ \.php$ {
    #    proxy_pass   http://127.0.0.1;
    #}

    # pass the PHP scripts to FastCGI server listening on 127.0.0.1:9000
    #
    location ~ \.php$ {
        #root           /usr/share/nginx/html;
        root   /data/web/webapp/public;
        fastcgi_pass   127.0.0.1:9000;
        fastcgi_index  index.php;
        fastcgi_param  SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include        fastcgi_params;
    }


    # deny access to .htaccess files, if Apache's document root
    # concurs with nginx's one
    #
    #location ~ /\.ht {
    #    deny  all;
    #}
}
```

把80端口的服务，转接到443端口，虚拟主机配置 例：

```nginx
server {
        listen 80;
        server_name www.example.com;
        rewrite ^(.*) https://$server_name$1 permanent;
}
```

```nginx
server {
        listen 443 ssl;
        server_name www.example.com;
        ssl on;
        ssl_certificate /usr/local/nginx/key/server.crt;
        ssl_certificate_key /usr/local/nginx/key/server.key;
        ssl_session_timeout  5m;
        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;     #指定SSL服务器端支持的协议版本
        ssl_ciphers  HIGH:!aNULL:!MD5;
        #ssl_ciphers  ALL：!ADH：!EXPORT56：RC4+RSA：+HIGH：+MEDIUM：+LOW：+SSLv2：+EXP;    #指定加密算法
        ssl_prefer_server_ciphers   on;    #在使用SSLv3和TLS协议时指定服务器的加密算法要优先于客户端的加密算法
        location / {
            # proxy_pass http://localhost:8080; 指定代理服务器
        	root /var/www/www.example.com;
        	index index.html index.htm;
        } 
}
```



