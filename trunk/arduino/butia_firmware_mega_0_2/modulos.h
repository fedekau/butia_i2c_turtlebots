#ifndef MODULOS__HH
#define MODULOS__HH



byte sistema (byte* buffer, byte largo, byte handler_id);

byte butia (byte* buffer, byte largo, byte handler_id);
  
byte tortuga (byte* buffer, byte largo, byte handler_id);

byte motores (byte* buffer, byte largo, byte handler_id);

byte sensores (byte* buffer, byte largo, byte handler_id);

byte lback (byte* buffer, byte largo, byte handler_id);


byte ax12 (byte* buffer, byte largo, byte handler_id);


byte lcd_display (byte* buffer, byte largo, byte handler_id);

byte genericSensorPnP (byte* buffer, byte largo, byte handler_id);
byte genericActuatorPnP (byte* buffer, byte largo, byte handler_id);
byte boton (byte* buffer, byte largo, byte handler_id);
byte led (byte* buffer, byte largo, byte handler_id);


#endif


