// Important Libraries
#include <Arduino.h>
#include <SoftwareSerial.h>

// Master-Slave Communication Pins
#define PIN_RX 2  // Pin de recepción de datos (conectado al pin TX de la Raspberry Pi)
#define PIN_TX 3  // Pin de transmisión de datos (conectado al pin RX de la Raspberry Pi)

// UltraSonic Pins
#define USEcho 2
#define USTrig 3

// IR Pins
#define IREcho A0

// Motor pins
#define MotorE1 9
#define MotorM1 10
#define MotorE2 11
#define MotorM2 12

// Obstacule Detection Module
#include "ObstacleDetectionModule/ObstacleDetectionModule.hpp"

// Motor Control Module
#include "MotorControlModule/MotorControlModule.hpp"

// Servo Movement Module
#include "ServoMovementModule/ServoMovementModule.hpp"