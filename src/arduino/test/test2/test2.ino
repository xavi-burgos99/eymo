#include "arduino-eymo.h"


// the setup function runs once when you press reset or power the board

// Modules
MotorControlModule MCM(MotorM1, MotorM2, MotorE1, MotorE2);
ObstacleDetectionModule ODB(IREcho, US2Echo, US2Trig);

// Variables for this test
int speed = 0;
int direction = 0;
int time = 2000;
float sensorDist[2] = {15,15};
SensorState ODB_state = Initiating;

void setup() {
    Serial.begin(9600);
    Serial.println("Setup done.\nBeginning test...");
}

// the loop function runs over and over again forever
void loop() {
    // Serial.println("\n\n\nLoop...");

    // Testing Dangerous
    speed = 255;
    // Serial.print("Initial speed: ");
    Serial.println(speed);
    Serial.print("Worst state: ");
    Serial.println(ODB.WorstState);
    Serial.print("IR state: ");
    Serial.println(ODB.IRState);
    Serial.println(ODB.IRDistance);
    Serial.print("Back state: ");
    Serial.println(ODB.BackState);
    Serial.println(ODB.BackDistance);


    ODB.update();
    MCM.checkObstacles(speed, ODB.WorstState);
    MCM.move(speed, direction);
    Serial.print("[Transformed] speed: ");
    Serial.println(speed);
    delay(time);

/*
    // Move straight backwards
    speed = -250;
    direction = 0;
    MCM.move(speed, direction);
    delay(time);
    MCM.move(speed, direction);
    delay(time);
    MCM.move(speed, direction);
    delay(time);

    // Move left forward
    speed = 200;
    direction = -1;
    MCM.move(speed, direction);
    delay(time);
    MCM.move(speed, direction);
    delay(time);
    MCM.move(speed, direction);
    delay(time);

    // Move left backwards
    speed = -200;
    direction = -1;
    MCM.move(speed, direction);
    delay(time);
    MCM.move(speed, direction);
    delay(time);
    MCM.move(speed, direction);
    delay(time);

     // Move right forward
    speed = 200;
    direction = 1;
    MCM.move(speed, direction);
    delay(time);
    MCM.move(speed, direction);
    delay(time);
    MCM.move(speed, direction);
    delay(time);

    // Move right backwards
    speed = -200;
    direction = 1;
    MCM.move(speed, direction);
    delay(time);
    MCM.move(speed, direction);
    delay(time);
    MCM.move(speed, direction);
    delay(time);*/
}
