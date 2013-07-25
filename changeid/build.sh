#!/bin/bash

CURRDIR=`pwd`

rm -rf /tmp/staging
rm -rf *.xo
mkdir /tmp/staging

cp -Lr BAX12ID.activity -t /tmp/staging

cd /tmp/staging/BAX12ID.activity
rm -rf locale
git init
git add *
git commit -m 'all files'
python setup.py build
python setup.py dist_xo

cd $CURRDIR
mv /tmp/staging/BAX12ID.activity/dist/*.xo .


