#!/bin/bash

set -x

SRC_DIR=`pwd`
PROJECT='docker-registry'

# 0 mkdir
mkdir -p ${SRC_DIR}
mkdir -p /export
mkdir -p /export/log
mkdir -p /export/log/${PROJECT}
mkdir -p /export/${PROJECT}

mkdir -p /etc/${PROJECT}
mkdir -p /var/run/${PROJECT}
mkdir -p /var/lock/subsys/${PROJECT}


# 1 yum
yum install -y gcc python-devel xz-devel swig openssl-devel unzip

# 2 setuptools
cd ${SRC_DIR}
tar zxf setuptools-5.8.tar.gz
cd setuptools-5.8
python setup.py install

# 3 pip
cd ${SRC_DIR}
tar zxf pip-1.2.1.tar.gz
cd pip-1.2.1
python setup.py install

# 5 install pybundle
cd ${SRC_DIR}
pip install core.pybundle
pip install registry.pybundle


# 6 install project src
#cd ${SRC_DIR}
#tar zxf docker-registry-core-2.0.3.tar.gz
#cd docker-registry-core-2.0.3
#python setup.py install

# 7 install python-jssclient
cd ${SRC_DIR}
#unzip python-jssclient.zip
cd python-jssclient/
python setup.py clean
python setup.py build
python setup.py install

# 8 install docker-registry-driver-jss
cd ${SRC_DIR}
#unzip docker-registry-driver-jss.zip
cd docker-registry-driver-jss/
python setup.py clean
python setup.py build
python setup.py install

cd ${SRC_DIR}
#tar zxf ${PROJECT}.tar.gz
unzip ${PROJECT}.zip
cd ${PROJECT}
python setup.py install

# 9 config
cd ${SRC_DIR}/
cp config.yml /etc/${PROJECT}/config.yml
cp docker-registry.logrotate /etc/logrotate.d/docker-registry
cp docker-registry.init /etc/init.d/docker-registry
chmod +x /etc/init.d/docker-registry

# set flavor
export SETTINGS_FLAVOR=jssstorage

# restart
chkconfig docker-registry on
/etc/init.d/docker-registry restart
