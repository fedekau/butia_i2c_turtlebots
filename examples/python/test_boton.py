import butiaAPI
import time


butiabot = butiaAPI.robot()
modules = butiabot.get_modules_list()

if modules == []:
    print 'No modules detected'

number = 0
for s in modules:
    if s.startswith('button:'):
        number = s.strip('button:')

number = int(number)
if number > 0:
    error = False
    while not error:
        val = butiabot.getButton(number)
        if val == -1:
            error = True
        else:
            print val
        #time.sleep(1)
else:
    print 'No button sensor was found'

butiabot.closeService()
