#!/bin/bash

CURRDIR=`pwd`

rm -rf staging/*
rm -rf *.xo

cd ../bobot/lib
make

cd $CURRDIR
cp -Lr Butialo.activity staging/

cd staging/Butialo.activity/bobot/drivers/
rm ax.lua boot.lua buzzer.lua debug.lua ledA.lua ledR.lua ledV.lua \
	leds.lua motorin.lua motorTm.lua move.lua puerta.lua sec.lua motor.lua \
	stmtr.lua temp_lubot.lua

cd $CURRDIR
cd staging/Butialo.activity
python setup.py fix_manifest
python setup.py dist_xo

cd $CURRDIR
mv staging/Butialo.activity/dist/*.xo .

