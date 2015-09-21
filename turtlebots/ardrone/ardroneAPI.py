
import libardrone

class ardroneAPI(object):
    
    def __init__(self):
        self.instanciaArDrone = libardrone.ARDrone()
        
    def despegar(self):
        self.instanciaArDrone.takeoff()

    def flotar(self):
        self.instanciaArDrone.hover()
    
    def apagar(self):
        self.instanciaArDrone.halt()
        
    def aterrizar(self):
        self.instanciaArDrone.land()
        
    def izquierda(self):
        self.instanciaArDrone.move_left()
        
    def derecha(self):
        self.instanciaArDrone.move_right()
        
    def arriba(self):
        self.instanciaArDrone.move_up()
        
    def abajo(self):
        self.instanciaArDrone.move_down()
        
    def adelante(self):
        self.instanciaArDrone.move_forward()
        
    def atras(self):
        self.instanciaArDrone.move_backward()
        
    def girarIzquierda(self):
        self.instanciaArDrone.turn_left()
        
    def girarDerecha(self):
        self.instanciaArDrone.turn_right()

    def calibrar(self):
        self.instanciaArDrone.trim()
    
    def emergencia(self):
        self.instanciaArDrone.reset()
         
    def bateria(self):
        if 0 in self.instanciaArDrone.navdata:
            if 'battery' in self.instanciaArDrone.navdata[0]:
                return self.instanciaArDrone.navdata[0]['battery']
        return 0

    def anguloTheta(self):
        if 0 in self.instanciaArDrone.navdata:
            if 'theta' in self.instanciaArDrone.navdata[0]:
                return self.instanciaArDrone.navdata[0]['theta']
        return 0
    
    def anguloPhi(self):
        if 0 in self.instanciaArDrone.navdata:
            if 'phi' in self.instanciaArDrone.navdata[0]:
                return self.instanciaArDrone.navdata[0]['phi']
        return 0
    
    def anguloPsi(self):
        if 0 in self.instanciaArDrone.navdata:
            if 'psi' in self.instanciaArDrone.navdata[0]:
                return self.instanciaArDrone.navdata[0]['psi']
        return 0
    
    def altura(self):
        if 0 in self.instanciaArDrone.navdata:
            if 'altitude' in self.instanciaArDrone.navdata[0]:
                return self.instanciaArDrone.navdata[0]['altitude']
        return 0
