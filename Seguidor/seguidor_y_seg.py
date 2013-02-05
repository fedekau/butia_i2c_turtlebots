import butiaAPI
import multiPatternDetectionAPI

butiabot = butiaAPI.robot()
negro = 39000
blanco = 22000
idIzq = "1"
idDer = "3"
distMinMark = 200
def main():
    det = multiPatternDetectionAPI.detection()
    salida = det.arMultiGetIdsMarker()
    print salida


    modulos = butiabot.get_modules_list()
    print modulos



    while True:
        butiabot.set2MotorSpeed("0","600", "0", "600")
        print "pase"
        print str(idIzq) + " "  + str(butiabot.getGrayScale(idIzq))
        print str(idDer) + " "  + str(butiabot.getGrayScale(idDer))
        # chequeo a la izquierda
        if butiabot.getGrayScale(idIzq) < negro and butiabot.getGrayScale(idDer) >negro:
            busco_camino_izquierda()
            print "corrijo izq"

        #chequeo a la derecha
        if butiabot.getGrayScale(idIzq)>negro and butiabot.getGrayScale(idDer)< negro:
            corregir_derecha()
            print "corrijo derecha"

        #si los dos estan en blanco miro a ver si hay senial
        if butiabot.getGrayScale(idIzq) < negro and butiabot.getGrayScale(idDer) < negro:
            if det.getMarkerTrigDist("Right") > -1 and det.getMarkerTrigDist("Right") < distMinMark:
                print "encontre la signal Right"
                # busco el camino a la derecha
                busco_camino_derecha()
            else:
                if  det.getMarkerTrigDist("Left") > -1 and det.getMarkerTrigDist("Left") < distMinMark:
                    print "encontre la signal Left"
                    busco_camino_izquierda()
                else:
                    butiabot.set2MotorSpeed("0","0", "0", "0")
                    print "no vio signal"
                    break


def corregir_izquierda():
    # busco linea a la derecha
    butiabot.set2MotorSpeed("0","0", "0", "0")
    while butiabot.getGrayScale(idIzq) == blanco:
          butiabot.set2MotorSpeed("1", "100", "0", "100") #giro hacia la derecha


def corregir_derecha():
    # busco linea a la izquierda
    butiabot.set2MotorSpeed("0","0", "0", "0")
    while butiabot.getGrayScale(idDer) == blanco:
          butiabot.set2MotorSpeed("0", "100", "1", "100") #giro hacia la izquierda

def busco_camino_izquierda():
    # giro a la izquierda hasta que el sensor derecho este en negro
    while butiabot.getGrayScale(idDer) != negro:
          butiabot.set2MotorSpeed("0", "100", "1", "100") #giro hacia la izquierda

def busco_camino_derecha():
        while butiabot.getGrayScale(idIzq) != negro:
          butiabot.set2MotorSpeed("1", "100", "0", "100") #giro hacia la derecha

if __name__ == "__main__":
    main()