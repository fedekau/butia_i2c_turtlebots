/*
 * butiá arduino firmware
 * version:     0.2
 * date:        19-6-2010
 * language:    Arduino 0018
 * Authors:	Andrés Aguirre, Pablo Gindel, Jorge Visca, Gonzalo Tejera, Santiago Margni, Federico Andrade
 *
 * (c) MINA Group, Facultad de Ingeniería, Universidad de la República, Uruguay. 
*/

#include <string.h>
#include "butia.h"


#define MAX_CALLBACKS      10

void (* callbacks[MAX_CALLBACKS]) () ;                   //   array de callbacks
static byte next_callback = 0 ;


int agendar_polling (void (* callback) () ) {
    if (next_callback == MAX_CALLBACKS) {return -1;}
    callbacks[next_callback] = callback;
    next_callback ++;
    return next_callback-1;
}


boolean desagendar_polling (byte num_callback) {
    
    if (num_callback >= next_callback) {return false;}
    
    //// borrar
    
    next_callback --;

    return false; //guille: agregado porque daba warning
                  //        no tengo idea de pa que es esta funcion
}


void init_polling(void){
  next_callback = 0;
};

