import commands
import butiaAPI
import time

from taconstants import BOX_COLORS

#definicion de constantes
ERROR_SENSOR_READ=-1 # valor de retorno en caso de error al leer el sensor

WAIT_TIME = 2 # espera luego de una accion antes de detener los motores
MAX_SPEED = 1024 # velocidad maxima para los AX-12 10 bits



class TAButia(object):
#atributos de la clase
    actualSpeed = 600 # velocidad con la que realiza los movimientos forward, backward, left y right

#metodos 
    def __init__(self):
        object.__init__(self)
        self.butia = None
        self.dynamicLoadBlockColors()

    def _check_init(self):
        if self.butia is None:
            self.butia = butiaAPI.robot()
        print "Inicializando butia ..."
        self.butia.abrirSensor()
        self.butia.abrirMotores()
        # TODO: si es necesario abrir otros modulos

    def dynamicLoadBlockColors(self):
        self._check_init()
        lista = self.butia.listarModulos()
        COLOR_NOTPRESENT = ["#A0A0A0","#808080"]
        if self.butia.isPresent('butia') == False:
            BOX_COLORS['forwardButia'] = COLOR_NOTPRESENT
            BOX_COLORS['backwardButia'] = COLOR_NOTPRESENT
            BOX_COLORS['leftButia'] = COLOR_NOTPRESENT
            BOX_COLORS['rightButia'] = COLOR_NOTPRESENT
            BOX_COLORS['stopButia'] = COLOR_NOTPRESENT
            BOX_COLORS['speedButia'] = COLOR_NOTPRESENT
        if self.butia.isPresent('led') == False:
            BOX_COLORS['ledButia'] = COLOR_NOTPRESENT
        if self.butia.isPresent('boton') == False:
            BOX_COLORS['pushbuttonButia'] = COLOR_NOTPRESENT
        if self.butia.isPresent('grises') == False:
            BOX_COLORS['grayscaleButia'] = COLOR_NOTPRESENT
        if self.butia.isPresent('temp') == False:
            BOX_COLORS['temperatureButia'] = COLOR_NOTPRESENT
        if self.butia.isPresent('vibra') == False:
            BOX_COLORS['vibrationButia'] = COLOR_NOTPRESENT
        if self.butia.isPresent('tilt') == False:
            BOX_COLORS['tiltButia'] = COLOR_NOTPRESENT
        if self.butia.isPresent('magnet') == False:
            BOX_COLORS['magneticinductionButia'] = COLOR_NOTPRESENT
        if self.butia.isPresent('luz') == False:
            BOX_COLORS['ambientlightButia'] = COLOR_NOTPRESENT
        if self.butia.isPresent('ctouch') == False:
            BOX_COLORS['capacitivetouchButia'] = COLOR_NOTPRESENT
        if self.butia.isPresent('dist') == False:
            BOX_COLORS['distButia'] = COLOR_NOTPRESENT
        # falta el modulo "lcd", y capas otros.


    def set_vels(self, left, right):
        self._check_init()
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
        return sensor

    def delay(self, waitTime):
	time.sleep(waitTime)

    def forward(self):
        self._check_init()
        self.set_vels(self.actualSpeed, self.actualSpeed)

    def backward(self):
        self._check_init()
        self.set_vels(-self.actualSpeed, -self.actualSpeed)

    def left(self):
        self._check_init()
        self.set_vels(-self.actualSpeed, self.actualSpeed)

    def right(self):
        self._check_init()
        self.set_vels(self.actualSpeed, -self.actualSpeed)

    def stop(self):
        self._check_init()
        self.set_vels(0, 0)

    def pushbutton(self):
        self._check_init()
        sensor = self.butia.getBoton()
        if sensor == "nil value\n" or sensor == '' or sensor == " " or sensor == None:
					sensor = ERROR_SENSOR_READ
        return sensor

    def ambientlight(self):
        self._check_init()
        sensor = self.butia.getLuzAmbiente()
        if sensor == "nil value\n" or sensor == '' or sensor == " " or sensor == None:
					sensor = ERROR_SENSOR_READ
        return sensor

    def distance(self):
        self._check_init()
        sensor = self.butia.getDistancia()
        if sensor == "nil value\n" or sensor == '' or sensor == " " or sensor == None:
					sensor = ERROR_SENSOR_READ
        return sensor

    def grayscale(self):
        self._check_init()
        sensor = self.butia.getEscalaGris()
        if sensor == "nil value\n" or sensor == '' or sensor == " " or sensor == None:
					sensor = ERROR_SENSOR_READ
        return sensor

    def temperature(self):
        self._check_init()
        sensor = self.butia.getTemperature()
        if sensor == "nil value\n" or sensor == '' or sensor == " " or sensor == None:
					sensor = ERROR_SENSOR_READ
        return sensor

    def vibration(self):
        self._check_init()
        sensor = self.butia.getVibration()
        if sensor == "nil value\n" or sensor == '' or sensor == " " or sensor == None:
					sensor = ERROR_SENSOR_READ
        return sensor

    def tilt(self):
        self._check_init()
        sensor = self.butia.getTilt()
        if sensor == "nil value\n" or sensor == '' or sensor == " " or sensor == None:
					sensor = ERROR_SENSOR_READ
        return sensor

    def capacitivetouch(self):
        self._check_init()
        sensor = self.butia.getContactoCapacitivo()
        if sensor == "nil value\n" or sensor == '' or sensor == " " or sensor == None:
					sensor = ERROR_SENSOR_READ
        return sensor

    def magneticinduction(self):
        self._check_init()
        sensor = self.butia.getInduccionMagnetica()
        if sensor == "nil value\n" or sensor == '' or sensor == " " or sensor == None:
					sensor = ERROR_SENSOR_READ
        return sensor

    def led(self, level):
        self._check_init()
        self.butia.setLed(level)
	
    def speed(self, speed):
	print "Setear velocidad actual: " + str(speed)
	if speed > MAX_SPEED:
		speed = MAX_SPEED
	self.actualSpeed = speed

