#include "arduino-eymo.h"


// the setup function runs once when you press reset or power the board


MotorControlModule MCM(MotorM1, MotorM2, MotorE1, MotorE2);
int speed = 0;
int direction = 0;
int time = 2000;

void setup() {
    Serial.begin(9600);
    Serial.println("Setup done.\nBeginning test...");
}

// the loop function runs over and over again forever
void loop() {
    // Move straight forward
    speed = 250;
    direction = 0;
    MCM.move(speed, direction);
    delay(time);
    MCM.move(speed, direction);
    delay(time);
    MCM.move(speed, direction);
    delay(time);

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
    delay(time);
}
