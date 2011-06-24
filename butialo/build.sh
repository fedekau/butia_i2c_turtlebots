#!/bin/bash

CURRDIR=`pwd`

rm -rf staging/*
rm -rf *.xo

cd ../bobot/lib
make

cd $CURRDIR
cp -Lr Butialo.activity staging/

cd staging/Butialo.activity
python setup.py fix_manifest
python setup.py dist_xo

cd $CURRDIR
mv staging/Butialo.activity/dist/*.xo .


