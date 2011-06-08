/*
  check PCB is ok
 */

#include <inttypes.h>

#define NUMBER_DIGITAL_PINS 54
#define NUMBER_ANALOG_PINS 16
#define NUMBER_PINS (NUMBER_DIGITAL_PINS + NUMBER_ANALOG_PINS)

#define NOTCHECK 255

void setup() {                
  // initialize the digital pin as an output.
  // Pin 13 has an LED connected on most Arduino boards:
  uint8_t i= 0;
  for (i=0 ; i < NUMBER_PINS ; ++i) {
    pinMode(i, INPUT);     
    digitalWrite(i, HIGH);   // set pull up
  }
}




void dontcheck(uint8_t pin) {


}


void init(uint8_t * nocheck)


int check(){
  uint8_t i,j;
  for (i=0; i < MAX_DIGITAL_PINS; ++i){
    pinMode(i, INPUT);     
    digitalWrite(i, LOW);


    for (j=i+1; j < MAX_DIGITAL_PINS; ++j){
      // check digital - digital
    
    
    }
    for (j=0; j < MAX_ANALOG_PINS ; ++j) {
    
    }
  }


  digitalWrite(13, HIGH);   // set the LED on
  delay(1000);              // wait for a second
  digitalWrite(13, LOW);    // set the LED off
  delay(1000);              // wait for a second


} 

class Shortcheck {
  private:
  byte pins[NUMBER_PINS];

  public:
  Shortcheck(){
    for (i=0; i < NUMBER_PINS ; ++i) pins[i] = i;
  };
  
  void notcheckpin(uint8_t pin){
    if (pin > NUMBER_PINS) return;
    if pins[pin]=
    pins[pin] = NOTCHECK;
  };
  
  void checkpin(uint8_t pin){
    if (pin > NUMBER_PINS) return;
    pins[pin] = pin;
  };

  void addshort(uint8_t a, uint8_t b){
    uint8_t aux;
    if (b > NUMBER_PINS) return;
    if (a > NUMBER_PINS) return;
    if (a > NUMBER_PINS) return;
    if (a > NUMBER_PINS) return;
    if (a > b) { aux=a ; a=b ; b=aux ; };
    
    if pins[a] = 
    pins[a] = b;
  
  }
  
  uint16_t check(){
  
    return 0;
  };
}







void loop() {


}


