#include "arduino-eymo.h"


// ServoMovementModule SMM(ServoPin);
Servo servo;
void setup() {
    Serial.begin(9600);
    Serial.println("Setup done.\nBeginning test...");
    servo.attach(ServoPin);
}

// the loop function runs over and over again forever
void loop() {

  servo.write(90);
  delay(1000);
  servo.write(75);
  delay(1000);
  servo.write(100);
  delay(1000);
  // Serial.println("Loop...");
  // Serial.println("Servo a posicion -1");
  // SMM.head_movement(-1.0f);
  // delay(1500);

  // Serial.println("Servo a posicion 0.5");
  // SMM.head_movement(-0.5f);
  // delay(1500);
  // Serial.println("Servo a posicion 0.5");
  // SMM.head_movement(0.5f);
  // delay(1500);

  // Serial.println("Servo a posicion 1");
  // SMM.head_movement(1.0f);
  // delay(1500);

  // Serial.println("Servo apagando");
  // SMM.Shutdown();
}
