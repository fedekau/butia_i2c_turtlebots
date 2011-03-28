/*
 * butiá arduino firmware
 * version:     0.2
 * date:        19-6-2010
 * language:    Arduino 0018
 * Authors:	Andrés Aguirre, Pablo Gindel, Jorge Visca, Gonzalo Tejera, Santiago Margni, Federico Andrade
 *
 * (c) MINA Group, Facultad de Ingeniería, Universidad de la República, Uruguay. 
*/

#ifndef PNP__HH
#define PNP__HH

void init_conectores ();

void init_handlers ();

byte get_config (byte globaltype, char* nombre, byte (** funcion) (byte*, byte, byte));

void add_module (byte num_conector);

// defines de sensores y actuadores
#define SENSOR_DISTANCIA   10
#define SENSOR_TEMPERATURA 11
#define SENSOR_LUZ         12
#define SENSOR_GRISES      13
#define SENSOR_BOTON       30
#define SENSOR_CONTACTO    31
#define SENSOR_TILT        32
#define SENSOR_VIBRACION   33
#define SENSOR_MAGNETICO   34
#define ACTUADOR_LED       53
#define SENSOR_POTE        21




#endif
