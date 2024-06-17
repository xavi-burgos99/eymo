#include <ArduinoJson.h>
#include "Ultrasonic.h"

#define MotorE1 3
#define MotorM1 2
#define MotorE2 5
#define MotorM2 4

#define UltrasonicEcho 9
#define UltrasonicTrig 8

#define InfraredSignal A7

#define MAX_SPEED 160

#define MAX_BACK_DISTANCE 10
#define MIN_BACK_DISTANCE 6

#define MAX_FRONT_DISTANCE 10
#define MIN_FRONT_DISTANCE 6
#define DROP_DISTANCE 18

int it = 0;

int motorBaseSpeed = 0;
int motorLSpeed = 0;
int motorRSpeed = 0;
int motorLPinSpeed = 0;
int motorRPinSpeed = 0;
int motorLTargetSpeed = 0;
int motorRTargetSpeed = 0;
int motorLDirection = 0;
int motorRDirection = 0;
int motorLPinDirection = 0;
int motorRPinDirection = 0;

Ultrasonic ultrasonic(UltrasonicTrig, UltrasonicEcho);
int usDistance = 0;

int irDistance = 0;

int fakeIt = 0;

void setup() {
  Serial.begin(9600);

  pinMode(UltrasonicEcho, INPUT);
  pinMode(UltrasonicTrig, OUTPUT);
  digitalWrite(UltrasonicTrig, LOW);

  pinMode(InfraredSignal, INPUT);

  pinMode(MotorE1, OUTPUT);
  pinMode(MotorE2, OUTPUT);
  pinMode(MotorM1, OUTPUT);
  pinMode(MotorM2, OUTPUT);
  analogWrite(MotorE1, 0);
  analogWrite(MotorE2, 0);
  digitalWrite(MotorM1, LOW);
  digitalWrite(MotorM2, LOW);
}

void getSerial(StaticJsonDocument<200> &doc) {
  if (Serial.available() == 0)
    return;
  String input = Serial.readStringUntil('\n');
  DeserializationError error = deserializeJson(doc, input);
  if (error) {
    return;
  }
}

void getFake(StaticJsonDocument<200> &doc) {
  String input;
  if (fakeIt == 0)
    input = "{\"joystick\":{\"x\":0, \"y\":1}}"; // Adelante
  else if (fakeIt == 75)
    input = "{\"joystick\":{\"x\":0, \"y\":0}}";
  else if (fakeIt == 100)
    input = "{\"joystick\":{\"x\":1, \"y\":0}}"; // Girar derecha
  else if (fakeIt == 175)
    input = "{\"joystick\":{\"x\":0, \"y\":0}}";
  else if (fakeIt == 200)
    input = "{\"joystick\":{\"x\":-1, \"y\":0}}"; // Girar izquierda
  else if (fakeIt == 275)
    input = "{\"joystick\":{\"x\":0, \"y\":0}}";
  else if (fakeIt == 300)
    input = "{\"joystick\":{\"x\":0, \"y\":-1}}"; // Atrás
  else if (fakeIt == 375)
    input = "{\"joystick\":{\"x\":0, \"y\":0}}";
  if (fakeIt >= 400)
    fakeIt = 0;
  else
    fakeIt++;
  deserializeJson(doc, input);
}

void calcUsDistance() {
  usDistance = ultrasonic.read();
}

void calcIrDistance() {
  uint16_t irValue = analogRead(InfraredSignal);
  if (irValue <= 0) {
    irDistance = 0;
    return;
  }
  float voltage = irValue * (5.0f / 1023.0f);
  if (voltage <= 0.20f) {
    irDistance = 0;
    return;
  }
  irDistance = (int)(12.08f / (voltage - 0.20f));
}

void processJson(StaticJsonDocument<200> doc) {
  if (doc.containsKey("joystick")) {
    float x = doc["joystick"]["x"];
    float y = doc["joystick"]["y"];
    calcMotorSpeed(x, y);
  }
}

void calcMotorSpeed(float x, float y) {
  motorBaseSpeed = (int)(y * MAX_SPEED);
  int baseSpeed = abs(motorBaseSpeed);
  int adjust = (int)(abs(x) * MAX_SPEED);
  if (x > 0) {
    motorLTargetSpeed = baseSpeed + adjust;
    motorRTargetSpeed = baseSpeed - adjust;
  } else {
    motorLTargetSpeed = baseSpeed - adjust;
    motorRTargetSpeed = baseSpeed + adjust;
  }
  motorLTargetSpeed = min(motorLTargetSpeed, MAX_SPEED);
  motorRTargetSpeed = min(motorRTargetSpeed, MAX_SPEED);
  if (y >= 0) {
    motorLDirection = motorLTargetSpeed >= 0 ? 0 : 1;
    motorRDirection = motorRTargetSpeed >= 0 ? 0 : 1;
  } else {
    motorLDirection = motorLTargetSpeed >= 0 ? 1 : 0;
    motorRDirection = motorRTargetSpeed >= 0 ? 1 : 0;
  }
  motorLTargetSpeed = abs(motorLTargetSpeed);
  motorLSpeed = motorLTargetSpeed;
  motorRTargetSpeed = abs(motorRTargetSpeed);
  motorRSpeed = motorRTargetSpeed;
}

void fixSpeed() {
  if (motorBaseSpeed < 0) {
    if (usDistance <= MIN_BACK_DISTANCE) {
      motorLSpeed = 0;
      motorRSpeed = 0;
    } else if (usDistance >= MAX_BACK_DISTANCE) {
      motorLSpeed = motorLTargetSpeed;
      motorRSpeed = motorRTargetSpeed;
      return;
    } else {
      float d = (float)(usDistance - MIN_BACK_DISTANCE) / (MAX_BACK_DISTANCE - MIN_BACK_DISTANCE);
      motorLSpeed = d * float(motorLTargetSpeed);
      motorRSpeed = d * float(motorRTargetSpeed);
    }
  } else if (motorBaseSpeed > 0) {
    if (irDistance <= MIN_FRONT_DISTANCE || irDistance >= DROP_DISTANCE) {
      motorLSpeed = 0;
      motorRSpeed = 0;
    } else if (irDistance >= MAX_FRONT_DISTANCE) {
      motorLSpeed = motorLTargetSpeed;
      motorRSpeed = motorRTargetSpeed;
      return;
    } else {
      float d = (float)(irDistance - MIN_FRONT_DISTANCE) / (MAX_FRONT_DISTANCE - MIN_FRONT_DISTANCE);
      motorLSpeed = d * float(motorLTargetSpeed);
      motorRSpeed = d * float(motorRTargetSpeed);
    }
  }
}

void setMotorSpeed() {
  if (motorLPinSpeed != motorLSpeed) {
    motorLPinSpeed = motorLSpeed;
    analogWrite(MotorE1, motorLPinSpeed);
  }
  if (motorRPinSpeed != motorRSpeed) {
    motorRPinSpeed = motorRSpeed;
    analogWrite(MotorE2, motorRPinSpeed);
  }
  if (motorLPinDirection != motorLDirection) {
    motorLPinDirection = motorLDirection;
    digitalWrite(MotorM1, motorLPinDirection == 0 ? LOW : HIGH);
  }
  if (motorRPinDirection != motorRDirection) {
    motorRPinDirection = motorRDirection;
    digitalWrite(MotorM2, motorRPinDirection == 0 ? LOW : HIGH);
  }
}

void printSerial() {
  Serial.print("Iteration: " + String(it) + "  ///  ");
  Serial.print("Speed -> " + String(motorBaseSpeed) + "  ///  ");
  Serial.print("Motors -> L: " + String(motorLDirection == 0 ? "" : "-") + String(motorLSpeed) + " | R: " + String(motorRDirection == 0 ? "" : "-") + String(motorRSpeed) + "  ///  ");
  Serial.print("Ult. Sensor -> " + String(usDistance) + "cm  ///  ");
  Serial.print("Inf. Sensor -> " + String(irDistance) + "cm  ///  ");
  Serial.println("");
}

void loop() {
  StaticJsonDocument<200> doc;
  getSerial(doc);
  //getFake(doc);
  processJson(doc);
  calcUsDistance();
  calcIrDistance();
  fixSpeed();
  setMotorSpeed();
  //printSerial();
  it++;
  delay(25);
}
