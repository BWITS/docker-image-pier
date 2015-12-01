# VERSION 0.1
# AUTHOR:         Jim Raynor <zhengxiaochuan-3@163.com>
# DESCRIPTION:    Image with docker-registry project and dependecies
# TO_BUILD:       docker build -rm -t docker-image-pier .
# TO_RUN:         docker run -d --name=registry -v /docker-registry/localconfig/:/docker-registry/localconfig/ -v /docker-registry/localdata/:/docker-registry/localdata/ --link mysql:mysql -p 5555:5000 docker-image-pier

# Latest Ubuntu LTS
from    ubuntu:14.04

# Update
run apt-get update
run apt-get -y upgrade

# Install pip
run apt-get -y install python-pip

# Install deps for backports.lzma (python2 requires it)
run apt-get -y install python-dev liblzma-dev libevent1-dev python-mysqldb 

add . /docker-registry
add ./config/boto.cfg /etc/boto.cfg

# Install core
run pip install /docker-registry/depends/docker-registry-core

# Install registry
run pip install file:///docker-registry#egg=docker-registry[bugsnag,newrelic]

VOLUME ["/docker-registry/localconfig/"]
VOLUME ["/docker-registry/localdata/"]

env DOCKER_REGISTRY_CONFIG /docker-registry/localconfig/config.yml
env SETTINGS_FLAVOR dev

expose 5000

cmd exec docker-registry
