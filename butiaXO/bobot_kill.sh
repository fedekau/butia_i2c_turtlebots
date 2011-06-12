#!/bin/bash

kill `ps ax | grep bobot-server | grep -v grep | awk '{print $1}'`
