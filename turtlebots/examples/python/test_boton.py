#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Test button

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
    if s.startswith('button:'):
        number = s.strip('button:')

number = int(number)
if number > 0:
    error = False
    while not error:
        val = butia.getButton(number)
        if val == -1:
            error = True
        else:
            print val
        #time.sleep(1)
else:
    print 'No button sensor was found'

butia.close()
