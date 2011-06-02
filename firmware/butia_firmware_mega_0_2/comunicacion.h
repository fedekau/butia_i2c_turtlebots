/*
 * butiá arduino firmware
 * version:     0.2
 * date:        19-6-2010
 * language:    Arduino 0018
 * Authors:	Andrés Aguirre, Pablo Gindel, Jorge Visca, Gonzalo Tejera, Santiago Margni, Federico Andrade
 *
 * (c) MINA Group, Facultad de Ingeniería, Universidad de la República, Uruguay. 
*/

#ifndef COMUNICACION__HH
#define COMUNICACION__HH

void leer_serial ();

void sendMsg (byte handler, byte *msg, byte largo);

byte unescape (byte* buffer, byte largo);

byte dispatch (byte *buffer, byte largo);

#endif


