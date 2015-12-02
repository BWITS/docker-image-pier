## An enhanced version of docker registry v1

### Hightlights:

1, Based on docker-registry v1

4. manage layers by mysql database

5, Support to delete associated Layer (do not delete any other tag-dependent layer) to save storage resources

6, Added: query interface, allnamespaces, alltags by namespace


### Deployment process:

1, Pull and build images

```
docker pull mysql

git clone https://github.com/zhengxiaochuan-3/docker-image-pier.git
cd docker-image-pier
docker build -t docker-image-pier . 
```

2, Start mysql service and create database `registry`

    docker run -d --name=mysql -e MYSQL_ROOT_PASSWORD=zxc mysql

    # Create database
    docker run -it --link mysql: mysql --rm mysql sh -c 'exec mysql -h "$ MYSQL_PORT_3306_TCP_ADDR" -P "$ MYSQL_PORT_3306_TCP_PORT" -uroot -p "$ MYSQL_ENV_MYSQL_ROOT_PASSWORD"'
    mysql> create database registry;
    mysql> exit

3, Start docker-registry service

```
mkdir -p /docker-registry/localconfig/
mkdir -p /docker-registry/localdata/
cp config/config.yml /docker-registry/localconfig/

docker run -d --name=registry -v /docker-registry/localconfig/:/docker-registry/localconfig/ -v /docker-registry/localdata/:/docker-registry/localdata/ --link mysql:mysql -p 5555:5000 docker-image-pier
```

4, Start nginx auth proxy service (option)

refer: https://www.digitalocean.com/community/tutorials/how-to-set-up-a-private-docker-registry-on-ubuntu-14-04

! [Alt tag] (http://note.youdao.com/yws/public/resource/6b820b6afed5c9a1c5e2807129f6a6ed/E2384F91BA8348D999D1DC686218084B)

### push images to private registry server:
```
docker tag mysql localhost:5555/mysql
docker push localhost:5555/mysql

docker run -it --link mysql:mysql --rm mysql sh -c 'exec mysql -h"$MYSQL_PORT_3306_TCP_ADDR" -P"$MYSQL_PORT_3306_TCP_PORT" -uroot -p"$MYSQL_ENV_MYSQL_ROOT_PASSWORD"'
mysql > create database registry;
mysql > use register;
mysql > select * from tables;
mysql > select * from layer;
mysql > select * from tag;
mysql > exit
```
! [Alt tag] (http://note.youdao.com/yws/public/resource/6b820b6afed5c9a1c5e2807129f6a6ed/2C6AF81600DC47EB8B700DB7EB8A7571)

### delete image via API
```
curl -X "DELETE" http://localhost:5555/v1/repositories/mysql/
```

### Source:

https://github.com/zhengxiaochuan-3/docker-image-pier.git

https://github.com/zhengxiaochuan-3/nginx-auth-proxy.git forked from https://github.com/larrycai/nginx-auth-proxy.git

### References:

http://dockone.io/article/845

http://cloud.51cto.com/art/201412/458680_all.htm

http://www.csdn.net/article/2015-11-24/2826315and1=1
