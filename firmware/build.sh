#!/bin/bash

CURRDIR=`pwd`

rm -rf tmp
rm -rf *.xo
mkdir tmp

cp -Lr ButiaFirmware.activity -t tmp

cd tmp/ButiaFirmware.activity
python setup.py build

cd $CURRDIR
cd tmp

#a la antigua
zip -r ButiaFirmware-3.xo ButiaFirmware.activity

cd $CURRDIR
mv tmp/*.xo .

