#!/bin/bash

CURRDIR=`pwd`

rm -rf /tmp/staging
rm -rf *.xo
mkdir /tmp/staging

cd ../butiaXO
make

cd $CURRDIR
cp -Lr Butialo.activity -t /tmp/staging

cd $CURRDIR
cd /tmp/staging/Butialo.activity
git init
git add *
git commit -m 'all files'
python setup.py build
python setup.py dist_xo

cd $CURRDIR
mv /tmp/staging/Butialo.activity/dist/*.xo .


