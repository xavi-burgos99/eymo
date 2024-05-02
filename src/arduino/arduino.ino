#include <Wire.h>
#include "arduino-eymo.h"
void setup(){
  ObstacleDetectionModule(IREcho, US1Echo, US1Trig, US2Echo, US2Trig);
  MotorControlModule(MotorIN1,MotorIN2,MotorIN3,MotorIN4,MotorENA,MotorENB);
}

void loop(){

}