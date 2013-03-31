#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Test grey sensor

import sys
sys.path.append('../../pybot')
import pybot_client
import time

butia = pybot_client.robot()
modules = butia.getModulesList()
if modules == []:
    print 'No modules detected'
else:
    print modules

number = 0
for s in modules:
    if s.startswith('grey:'):
        number = s.strip('grey:')

number = int(number)
if number > 0:
    error = False
    while not error:
        val = butia.getGray(number)
        if val == -1:
            error = True
        else:
            print val
        #time.sleep(1)
else:
    print 'No grey sensor was found'

butia.close()

