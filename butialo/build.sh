#!/bin/bash

CURRDIR=`pwd`

rm -rf staging
rm -rf *.xo
mkdir staging

cd ../butiaXO
make

cd $CURRDIR
cp -Lr Butialo.activity -t staging


cd $CURRDIR
cd staging/Butialo.activity
python setup.py build
python setup.py dist_xo

cd $CURRDIR
mv staging/Butialo.activity/dist/*.xo .


