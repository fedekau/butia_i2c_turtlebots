/*
 * butiá arduino firmware
 * version:     0.2
 * date:        19-6-2010
 * language:    Arduino 0018
 * Authors:	Andrés Aguirre, Pablo Gindel, Jorge Visca, Gonzalo Tejera, Santiago Margni, Federico Andrade
 *
 * (c) MINA Group, Facultad de Ingeniería, Universidad de la República, Uruguay. 
*/

#ifndef PERIFERICOS__HH
#define PERIFERICOS__HH


void sample () ; 

void motor_init () ;

void display_init () ;

void movimiento (byte direccion, int velocidad);

#endif


