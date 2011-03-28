#ifndef SERVICIOS__HH
#define SERVICIOS__HH



int agendar_polling (void (* callback) () );

boolean desagendar_polling (byte num_callback);

void init_polling(void);





#endif

