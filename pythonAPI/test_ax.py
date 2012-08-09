import butiaAPI
import time


butiabot = butiaAPI.robot()
butiabot.joint_mode("11")
butiabot.joint_mode("16")

error = False
while not error:
    butiabot.set_position("11","0")
    butiabot.set_position("16","0")
    time.sleep(1)
    butiabot.set_position("11","512")
    butiabot.set_position("16","512")
    time.sleep(1)
    butiabot.set_position("11","1023")
    butiabot.set_position("16","1023")
    time.sleep(1)
butiabot.close()
