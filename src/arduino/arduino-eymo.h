// Important Libraries
#include <SoftwareSerial.h>

// Master-Slave Communication Pins
#define PIN_RX 2  // Pin de recepción de datos (conectado al pin TX de la Raspberry Pi)
#define PIN_TX 3  // Pin de transmisión de datos (conectado al pin RX de la Raspberry Pi)

// UltraSonic Pins
#define USEcho 8
#define USTrig 9

// Servos Pin
#define ServoPin 11

// IR Pins
#define IREcho A7

// Motor pins
#define MotorE1 3
#define MotorM1 2
#define MotorE2 5
#define MotorM2 4

// Obstacule Detection Module
#include "ObstacleDetectionModule/ObstacleDetectionModule.hpp"

// Motor Control Module
#include "MotorControlModule/MotorControlModule.hpp"

// Servo Movement Module
#include "ServoMovementModule/ServoMovementModule.hpp"


MotorControlModule MCM(MotorM1,MotorM2,MotorE1,MotorE2);
ObstacleDetectionModule ODM(IREcho, USEcho, USTrig);
ServoMovementModule SMM(ServoPin);
SoftwareSerial serial(PIN_RX, PIN_TX);
String* split_string(String msg, int &index);