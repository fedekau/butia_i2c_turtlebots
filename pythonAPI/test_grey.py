import butiaAPI
import time


butiabot = butiaAPI.robot()
modules = butiabot.get_modules_list()

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
        val = butiabot.getGrayScale(number)
        if val == -1:
            error = True
        else:
            print val
        #time.sleep(1)
else:
    print 'No grey sensor was found'

butiabot.closeService()
