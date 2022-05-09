
#include "Arduino.h"
#include "coms.h"

 void setup() {
  Serial.begin(9600);
}

void loop() {
  if(!run_reader()){
    getM()->show();
  }
}
