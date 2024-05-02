#include <Arduino.h>
#include "../../utilities.hpp"

float UltraSonicMetrics(int trigger, int echo){
  long duration = 0;
  float distance = 0.0f;

  // Emit the pulse
  digitalWrite(trigger, LOW);
  delayMicroseconds(2);
  digitalWrite(trigger, HIGH);

  // Read the pulse data
  delayMicroseconds(10);
  digitalWrite(trigger, LOW);
  duration = pulseIn(echo, HIGH);

  // transform the pulse data to distance in cm
  distance = detection_mesurements(true, duration, 0.0f);
  
  return distance;

}