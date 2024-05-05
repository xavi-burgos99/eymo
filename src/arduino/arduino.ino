#include "arduino-eymo.h"
void setup(){
  ObstacleDetectionModule(IREcho, US1Echo, US1Trig, US2Echo, US2Trig);
  MotorControlModule(MotorM1,MotorM2,MotorE1,MotorE2);
}

void loop(){

}