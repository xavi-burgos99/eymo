#include <Servo.h>
#include <ArduinoJson.h>
#include "Ultrasonic.h"

#define MotorM1 2
#define MotorE1 3
#define MotorM2 4
#define MotorE2 5

#define UltrasonicEcho 9
#define UltrasonicTrig 8

#define InfraredSignal A7

#define ServoPWM 11

#define SERVO_CENTER_ANGLE 90
#define SERVO_MAX_ANGLE 30
#define SERVO_MIN_X 0.1
#define SERVO_MAX_X 0.75

#define REVERSE_DIRECTION 1
#define MAX_SPEED 90
#define FRONT_SPEED_MULTIPLIER 1

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

Servo servo;
int servoAngle = SERVO_CENTER_ANGLE;
int servoTargetAngle = SERVO_CENTER_ANGLE;

Ultrasonic ultrasonic(UltrasonicTrig, UltrasonicEcho);
int usDistance = 0;

int irDistance = 0;

int fakeIt = 0;

void setup() {
  Serial.begin(9600);

  servo.attach(ServoPWM);
  servo.write(SERVO_CENTER_ANGLE);

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

bool getSerial(StaticJsonDocument<200> &doc) {
  static String input = "";
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      DeserializationError error = deserializeJson(doc, input);
      input = "";
      if (error)
        return false;
      return true;
    } else {
      input += c;
    }
  }
  return false;
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
  if (doc.containsKey("displacement")) {
    float x = doc["displacement"]["x"];
    float y = doc["displacement"]["y"];
    calcMotorSpeed(x, y);
    calcServoAngle(x, y);
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
  motorLTargetSpeed = constrain(motorLTargetSpeed, -MAX_SPEED, MAX_SPEED);
  motorRTargetSpeed = constrain(motorRTargetSpeed, -MAX_SPEED, MAX_SPEED);
  if (y == 0) {
    motorLDirection = motorLTargetSpeed >= 0 ? !REVERSE_DIRECTION : REVERSE_DIRECTION;
    motorRDirection = motorRTargetSpeed >= 0 ? !REVERSE_DIRECTION : REVERSE_DIRECTION;
  } else if (y > 0) {
    motorLDirection = motorLTargetSpeed >= 0 ? REVERSE_DIRECTION : !REVERSE_DIRECTION;
    motorRDirection = motorRTargetSpeed >= 0 ? REVERSE_DIRECTION : !REVERSE_DIRECTION;
  } else {
    motorLDirection = motorLTargetSpeed >= 0 ? !REVERSE_DIRECTION : REVERSE_DIRECTION;
    motorRDirection = motorRTargetSpeed >= 0 ? !REVERSE_DIRECTION : REVERSE_DIRECTION;
  }
  if (motorLTargetSpeed > 0)
    motorLTargetSpeed = int(float(motorLTargetSpeed) * FRONT_SPEED_MULTIPLIER);
  if (motorRTargetSpeed > 0)
    motorRTargetSpeed = int(float(motorRTargetSpeed) * FRONT_SPEED_MULTIPLIER);
  motorLTargetSpeed = abs(motorLTargetSpeed);
  motorLSpeed = motorLTargetSpeed;
  motorRTargetSpeed = abs(motorRTargetSpeed);
  motorRSpeed = motorRTargetSpeed;
}

void calcServoAngle(float x, float y) {
  float abs_x = abs(x);
  if (abs_x < SERVO_MIN_X || y < 0) {
    servoTargetAngle = SERVO_CENTER_ANGLE;
    return;
  }
  if (abs_x > SERVO_MAX_X) {
    servoTargetAngle = x > 0 ? SERVO_CENTER_ANGLE - SERVO_MAX_ANGLE : SERVO_CENTER_ANGLE + SERVO_MAX_ANGLE;
    return;
  }
  servoTargetAngle = x > 0 ?
    SERVO_CENTER_ANGLE - int(SERVO_MAX_ANGLE * abs_x / SERVO_MAX_X) :
    SERVO_CENTER_ANGLE + int(SERVO_MAX_ANGLE * abs_x / SERVO_MAX_X);
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

void setServoAngle() {
  if (servoAngle != servoTargetAngle) {
    servoAngle = servoTargetAngle;
    servo.write(servoAngle);
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
  if (getSerial(doc))
    processJson(doc);
  calcUsDistance();
  calcIrDistance();
  fixSpeed();
  //setMotorSpeed();
  //setServoAngle();
  it++;
  delay(25);
}
