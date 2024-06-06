#include "arduino-eymo.h"


// the setup function runs once when you press reset or power the board

// Modules
MotorControlModule MCM(MotorM1, MotorM2, MotorE1, MotorE2);
ObstacleDetectionModule ODB(IREcho, US2Echo, US2Trig);

// Variables for this test
int speed = 0;
int direction = 0;
int time = 10000;
float sensorDist[2] = {15,15};
SensorState ODB_state = Initiating;

void setup() {
    Serial.begin(9600);
    Serial.println("Setup done.\nBeginning test...");
}

// the loop function runs over and over again forever
void loop() {
    Serial.println("\n\n\nLoop...");

    // FORWARD MOVE
    Serial.print("Testing frontal forward move: ");
    speed = 255;
    Serial.print("Initial speed: ");
    Serial.println(speed);
    Serial.println("Reading Sensors...");
    ODB.update();
    printStatesAndDistances(ODB.IRState, ODB.IRDistance, ODB.BackState, ODB.BackDistance, ODB.WorstState);
    MCM.checkObstacles(speed, ODB.IRState, ODB.BackState, ODB.WorstState);
    MCM.move(speed, direction);
    Serial.print("Resulting speed: ");
    Serial.println(speed);
    delay(time);


    // BACKWARD MOVE
    Serial.print("Testing frontal backward move: ");
    speed = -255;
    Serial.print("Initial speed: ");
    Serial.println(speed);
    Serial.println("Reading Sensors...");
    ODB.update();
    printStatesAndDistances(ODB.IRState, ODB.IRDistance, ODB.BackState, ODB.BackDistance, ODB.WorstState);
    MCM.checkObstacles(speed, ODB.IRState, ODB.BackState, ODB.WorstState);
    MCM.move(speed, direction);
    Serial.print("Resulting speed: ");
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
