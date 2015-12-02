## 一个加强版的docker registry

### 特性：

1、基于 docker-registry v1

2、新增：支持 https 协议，支持自颁发证书

3、新增：支持 basic auth，基于 nginx

4、修改：默认接入 mysql，新增 tag、layer 、cnt（layer 的依赖数）表 

5、新增：支持通过原删除 tag 的 api 同时删除该tag相关Layer （不删除有其他 tag 依赖的 layer） 节省存储资源

6、新增：查询接口，allnamespaces 、alltags by namespace


### 部署过程：

1、下拉镜像

```
docker pull index.alauda.cn/alauda/mysql
docker tag index.alauda.cn/alauda/mysql mysql

docker pull index.alauda.cn/zhengxiaochuan/nginx-auth-proxy
docker tag index.alauda.cn/zhengxiaochuan/nginx-auth-proxy nginx-auth-proxy

docker pull index.alauda.cn/zhengxiaochuan/docker-image-pier
docker tag index.alauda.cn/zhengxiaochuan/docker-image-pier docker-image-pier
```

2、启动 mysql 服务 并创建名称为 registry 的 database

    docker run -d  --name=mysql -e MYSQL_ROOT_PASSWORD=zxc -p 3366:3306 mysql 

    ＃ 创建数据库
    docker run -it --link mysql:mysql --rm mysql sh -c 'exec mysql -h"$MYSQL_PORT_3306_TCP_ADDR" -P"$MYSQL_PORT_3306_TCP_PORT" -uroot -p"$MYSQL_ENV_MYSQL_ROOT_PASSWORD"'
    mysql > create database registry;
    mysql > exit

3、启动 registry 服务

```
mkdir -p /docker-registry/localconfig/
mkdir -p /docker-registry/localdata/
git clone https://github.com/zhengxiaochuan-3/docker-image-pier.git
cd docker-image-pier
cp config/config.yml /docker-registry/localconfig/

docker run -d --name=registry -v /docker-registry/localconfig/:/docker-registry/localconfig/ -v /docker-registry/localdata/:/docker-registry/localdata/ --link mysql:mysql -p 5555:5000 docker-image-pier
```

4、启动nginx auth proxy 服务


    docker run -d --name nginx --link registry:registry -p 443:443 nginx-auth-proxy

这里面默认有如下配置：用户名:密码 zxc:zxc 、 CA证书 ( 对应域名为 reg.jd.com )

增加自己的用户名、密码：
```
   # 使用htpasswd生成用户名密码 （可以借用官方的 registry:2.2 镜像里面的 htpasswd 来生成）
   docker run -d --name=htpasswdtool registry:2.2 
   docker run -it htpasswdtool /bin/bash
      htpasswd -c htpasswdfile username
      cat htpasswdfile
      将该用户名密码，追加到容器 registry 的  /usr/local/nginx/conf/docker-registry.htpasswd 文件中

  # 为自己域名的自颁发证书 (如果你有购买的官方CA证书更好)
        以 "reg.jd.com" 为例子
    mkdir certs && cd certs
    openssl req -x509 -days 3650 -subj '/CN=reg.jd.com/' -nodes -newkey rsa:2048 -keyout server.key -out server.crt

       将该证书 server.key -out server.crt ，上传到容器 registry 的 /etc/ssl/certs/docker-registry 目录，使用 docker cp 命令
       注意保留这个两个文件，尤其是证书文件 server.crt
```

### 状态：

![alt tag](http://note.youdao.com/yws/public/resource/6b820b6afed5c9a1c5e2807129f6a6ed/E2384F91BA8348D999D1DC686218084B)


![alt tag](http://note.youdao.com/yws/public/resource/6b820b6afed5c9a1c5e2807129f6a6ed/2C6AF81600DC47EB8B700DB7EB8A7571)

### 测试：

本机docker ：

    echo "127.0.0.1  reg.jd.com" >> /etc/hosts
    mkdir -p /etc/docker/certs.d/reg.jd.com
    cp server.crt /etc/docker/certs.d/reg.jd.com
    重启dockerd 
    docker login reg.jd.com

![alt tag](http://note.youdao.com/yws/public/resource/6b820b6afed5c9a1c5e2807129f6a6ed/358DD05A6BDC4FE698A41575F7592164)

![alt tag](http://note.youdao.com/yws/public/resource/6b820b6afed5c9a1c5e2807129f6a6ed/DCD994DBE09D4CD49FC1145B5B98C960)

### 远程docker：

    echo "[your nginx auth server ip]   reg.jd.com" >> /etc/hosts
    mkdir -p /etc/docker/certs.d/reg.jd.com
    cp server.crt /etc/docker/certs.d/reg.jd.com
        重启dockerd 
    docker login reg.jd.com


### 源码：

https://github.com/zhengxiaochuan-3/docker-image-pier.git

https://github.com/zhengxiaochuan-3/nginx-auth-proxy.git   forked from https://github.com/larrycai/nginx-auth-proxy.git

### 参考资料：

http://dockone.io/article/845

http://cloud.51cto.com/art/201412/458680_all.htm

http://www.csdn.net/article/2015-11-24/2826315and1=1
