import commands
import butiaAPI
import time

#definicion de constantes
ERROR_SENSOR_READ=-1 # valor de retorno en caso de error al leer el sensor

MAX_VEL = 600 # velocidad con la que realiza los movimientos forward, backward, left y right
WAIT_TIME = 2 # espera luego de una accion antes de detener los motores

class TAButia(object):
    def __init__(self, baud=115200):
        object.__init__(self)
        self._dev='/dev/ttyUSB0'
        self._baud = baud
        self.butia = None

	status,output=commands.getstatusoutput("ls /dev/ | grep ttyUSB")
	output=output.split('\n')
	for i in output:
		status,aux=commands.getstatusoutput("udevinfo -a -p /class/tty/%s | grep ftdi_sio > /dev/null"%i)
		if (not status):
			self._dev='/dev/%s'%i
			break
#inicializar variables aqui
	

    def _check_init(self):
        if self.butia is None:
            self.butia = butiaAPI.robot()
        print "Inicializando butia ..."
        self.butia.abrirSensor()
        self.butia.abrirMotores()

    def set_vels(self, left, right):
        self._check_init()
				# llamar operacion del API Butia
        print "Setear velocidades: " + str(left) + "-" + str(right)
        if left>0:
					sentLeft = "0"
        else:
					sentLeft = "1"
        if right>0:
					sentRight = "0"
        else:
					sentRight = "1"
        self.butia.setVelocidadMotores(sentLeft,str(abs(left)), sentRight, str(abs(right)))

    def get_sensor(self, sensor):
        self._check_init()
        sensor = self.butia.getValSenAnalog(str(sensor))
        if sensor == "nil value\n" or sensor == '' or sensor == " " or sensor == None:
					sensor = ERROR_SENSOR_READ
        #print "Lectura sensor: " + str(sensor)
        return sensor

    def delay(self, orgiagastrica):
	time.sleep(orgiagastrica)

    def forward(self):
        self._check_init()
        self.set_vels(MAX_VEL, MAX_VEL)
	self.delay(WAIT_TIME)
        self.set_vels(0, 0)

    def backward(self):
        self._check_init()
        self.set_vels(-MAX_VEL, -MAX_VEL)
	self.delay(WAIT_TIME)
        self.set_vels(0, 0)

    def left(self):
        self._check_init()
        self.set_vels(-MAX_VEL, MAX_VEL)
	self.delay(WAIT_TIME)
        self.set_vels(0, 0)

    def right(self):
        self._check_init()
        self.set_vels(MAX_VEL, -MAX_VEL)
	self.delay(WAIT_TIME)
        self.set_vels(0, 0)

    def stop(self):
        self._check_init()
        sensor = set_vels(0, 0)

    def pushbuttonButia(self):
        self._check_init()
        sensor = self.butia.getBoton()
        if sensor == "nil value\n" or sensor == '' or sensor == " " or sensor == None:
					sensor = ERROR_SENSOR_READ
        #print "Lectura sensor: " + str(sensor)
        return sensor
