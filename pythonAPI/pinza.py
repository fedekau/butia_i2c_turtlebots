import butiaAPI
import time
#la pinza izq se mueve entre 1023(abierto) y 74(cerrado)
#la pinza der se mueve entre 0(abierto) y 879(cerrado)



PINZA_IZQ = "21"
PINZA_DER = "20"
butiabot = butiaAPI.robot()
butiabot.joint_mode(PINZA_IZQ, "0", "1023") #1023 is 300 degrees
butiabot.joint_mode(PINZA_DER, "0", "1023") #1023 is 300 degrees

"""butiabot.nueva()

butiabot.set_speed(PINZA_IZQ, "0")
butiabot.set_speed(PINZA_DER, "0.2")"""

print "start..."

vel = raw_input("tiempo espera formato 0.05 > ")
inc = int(raw_input("pase el incremento 10 > "))

openDer = 0
closeDer = 879

openIzq = 980
closeIzq = 74
cerrado = False

posDer = openDer
posIzq = openIzq

#inicio abierto
butiabot.set_position(PINZA_DER, str(posDer))
butiabot.set_position(PINZA_IZQ, str(posIzq))
time.sleep(1)

while butiabot.get_position(PINZA_IZQ) > closeDer or butiabot.get_position(PINZA_DER) < closeDer:
	posDer += inc
	posIzq += -inc
	butiabot.set_position(PINZA_DER, str(posDer))
	butiabot.set_position(PINZA_IZQ, str(posIzq))
	time.sleep(float(vel))
		






	

"""	#open and close motion
	butiabot.set_position(PINZA_DER, str(openDer))
	butiabot.set_position(PINZA_IZQ, str(openIzq))
	butiabot.set_position(PINZA_DER, str(openDer))
	butiabot.set_position(PINZA_IZQ, str(openIzq))
	time.sleep(0.3)
	print "izq= ",butiabot.get_position(PINZA_IZQ)
	print "der= ", butiabot.get_position(PINZA_DER)
	#time.sleep(1)
	
	if openDer<= 0:
		inc = 100
	elif openDer> 850:
		inc = -100
		time.sleep(0.5)
	openDer+=inc
	openIzq-=inc
	time.sleep(0.3)"""
	  
butiabot.close()
