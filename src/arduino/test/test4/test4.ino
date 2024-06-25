#include <ArduinoJson.h>

// Definiciones
#define MotorE1 3
#define MotorM1 2
#define MotorE2 5
#define MotorM2 4

#define MAX_FRONT_SPEED 160
#define MAX_BACK_SPEED 180

#define SMOOTH_STEPS 10

int currentSpeed1 = 0;
int currentSpeed2 = 0;
int targetSpeed1 = 0;
int targetSpeed2 = 0;
int iteration = 0;
int smoothStep1 = 0;
int smoothStep2 = 0;
int smoothCounter = 0;
bool currentDirection1 = true;
bool currentDirection2 = true;

void setup() {
  Serial.begin(9600);
  pinMode(MotorM1, OUTPUT);
  pinMode(MotorE1, OUTPUT);
  pinMode(MotorM2, OUTPUT);
  pinMode(MotorE2, OUTPUT);
  digitalWrite(MotorM1, LOW);
  digitalWrite(MotorM2, LOW);
}

void loop() {
  // Emulate Serial input
  StaticJsonDocument<200> doc;
  emulateSerial(doc);

  /*
  // Comentar esta sección para pruebas sin Serial
  if (Serial.available() > 0) {
    // Leer la entrada del serial
    String input = Serial.readString();
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, input);
    
    if (error) {
      Serial.println("Error de deserialización");
      return;
    }
    
    processJson(doc);
  }
  */

  // Procesar el JSON
  processJson(doc);

  // Aplicar suavizado de velocidad
  applySmooth();

  // Change direction
  changeDirection();

  delay(100);  // Bucle que se ejecuta cada 100ms
}

void emulateSerial(StaticJsonDocument<200> &doc) {
  String input;

  if (iteration == 0) {
    input = "{\"joystick\":{\"x\":0, \"y\":1}}"; // Adelante
  } else if (iteration == 75) {
    input = "{\"joystick\":{\"x\":0, \"y\":0}}";
  } else if (iteration == 100) {
    input = "{\"joystick\":{\"x\":1, \"y\":0}}"; // Girar derecha
  } else if (iteration == 175) {
    input = "{\"joystick\":{\"x\":0, \"y\":0}}";
  } else if (iteration == 200) {
    input = "{\"joystick\":{\"x\":-1, \"y\":0}}"; // Girar izquierda
  } else if (iteration == 275) {
    input = "{\"joystick\":{\"x\":0, \"y\":0}}";
  } else if (iteration == 300) {
    input = "{\"joystick\":{\"x\":0, \"y\":-1}}"; // Atrás
  } else if (iteration == 375) {
    input = "{\"joystick\":{\"x\":0, \"y\":0}}";
  }
  if (iteration >= 400) {
    iteration = 0;
  } else {
    iteration++;
  }

  deserializeJson(doc, input);
}

void processJson(StaticJsonDocument<200> &doc) {
  if (doc.containsKey("joystick")) {
    float x = doc["joystick"]["x"];
    float y = doc["joystick"]["y"];
    
    int speedY;
    if (y > 0) {
      speedY = y * MAX_FRONT_SPEED;
    } else if (y < 0) {
      speedY = y * MAX_BACK_SPEED;
    } else {
      speedY = 0;
    }

    int speedX = x * MAX_FRONT_SPEED; // Ajuste de velocidad para girar

    // Calcula las velocidades objetivo para cada motor
    targetSpeed1 = constrain(speedY + speedX, -MAX_BACK_SPEED, MAX_FRONT_SPEED);
    targetSpeed2 = constrain(speedY - speedX, -MAX_BACK_SPEED, MAX_FRONT_SPEED);

    // Inicializar el suavizado
    initSmooth();
  }
}

void initSmooth() {
  smoothStep1 = (targetSpeed1 - currentSpeed1) / SMOOTH_STEPS;
  smoothStep2 = (targetSpeed2 - currentSpeed2) / SMOOTH_STEPS;
  smoothCounter = SMOOTH_STEPS;
}

void applySmooth() {
  if (smoothCounter > 0) {
    currentSpeed1 += smoothStep1;
    currentSpeed2 += smoothStep2;
    analogWrite(MotorE1, abs(currentSpeed1));
    analogWrite(MotorE2, abs(currentSpeed2));
    smoothCounter--;
    return;
  }
  if (currentSpeed1 != targetSpeed1) {
    currentSpeed1 = targetSpeed1;
    analogWrite(MotorE1, abs(targetSpeed1));
  }
  if (currentSpeed2 != targetSpeed2) {
    analogWrite(MotorE2, abs(targetSpeed2));
    currentSpeed2 = targetSpeed2;
  }
}

void changeDirection() {
  bool newDirection1 = currentSpeed1 >= 0;
  bool newDirection2 = currentSpeed2 >= 0;
  if (currentDirection1 != newDirection1) {
    currentDirection1 = newDirection1;
    digitalWrite(MotorM1, newDirection1 ? LOW : HIGH);
  }
  if (currentDirection2 != newDirection2) {
    currentDirection2 = newDirection2;
    digitalWrite(MotorM2, newDirection2 ? LOW : HIGH);
  }
}