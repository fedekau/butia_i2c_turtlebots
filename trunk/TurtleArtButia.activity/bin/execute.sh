#!/bin/bash

while [ -n "$2" ] ; do
    case "$1" in
        -b | --bundle-id)     export SUGAR_BUNDLE_ID="$2" ;;
        -a | --activity-id)   export SUGAR_ACTIVITY_ID="$2" ;;
        -o | --object-id)     export SUGAR_OBJECT_ID="$2" ;;
        -u | --uri)           export SUGAR_URI="$2" ;;
        *) echo unknown argument $1 $2 ;;
    esac
    shift;shift
done


if [ "$SUGAR_BUNDLE_PATH" != "" ] ; then

export PYTHONPATH=$SUGAR_BUNDLE_PATH/site-packages:$PYTHONPATH
export LD_LIBRARY_PATH=$SUGAR_BUNDLE_PATH/bin/lib:$LD_LIBRARY_PATH
export PATH=$SUGAR_BUNDLE_PATH/bin:$PATH
cd $SUGAR_BUNDLE_PATH

fi

cd bin

./lua bobot-server.lua &

./waitforbobot.py

cd ..

if [ "$SUGAR_BUNDLE_PATH" != "" ] ; then
    sugar-activity -a $SUGAR_ACTIVITY_ID TurtleArtActivity.TurtleArtActivity
else
    ./turtleart.py
fi

kill `ps ax | grep bobot-server | grep -v grep | awk '{print $1}'`
