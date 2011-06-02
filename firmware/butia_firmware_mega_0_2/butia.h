#ifndef BUTIA__HH
#define BUTIA__HH

#include "ax12.h"
#include "conector.h"

#define NUM_MOTORS      2                             // número de motores AX12
#define VEL_CONST       0.07692                       // coeficiente de velocidad (depende del período y del voltaje)

// defines
#define SAMPLE_CONST    20                            // período de muestreo (o polling) de sensores
#define MAX_MODULES     28                            // número máximo de módulos
#define FW_VERSION    20                            // versión del firmware 
#define NUM_CONNECTORS  8                             // número de conectores butiá PnP


extern AX12 motor[NUM_MOTORS];
extern volatile int presentP [];
extern volatile int presentS [];
extern volatile int presentL [];
extern volatile float pasos[];

extern Conector conector [NUM_CONNECTORS];
extern byte num_modules;

// la estructura 'H' consta de un nombre, un puntero a función (el handler) y un número de conector
struct H {
  char nombre [8];
  byte (* funcion) (byte*, byte, byte);
  byte num_conector;
};

extern struct H handler [MAX_MODULES];



#endif

