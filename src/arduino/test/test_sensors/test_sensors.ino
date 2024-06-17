#include "arduino-eymo.h"


// the setup function runs once when you press reset or power the board
ObstacleDetectionModule ODB(IREcho, US2Echo, US2Trig, FLOOR);
int delay_time = 2000;

void setup() {
    Serial.begin(9600);
    Serial.println("Beginning setup...");
    Serial.println("Setup done.\nBeginning loop...");
}

// the loop function runs over and over again forever
void loop() {
    ODB.update();
    printStatesAndDistances(ODB.IRState, ODB.IRDistance,
                            ODB.BackState, ODB.BackDistance,
                            ODB.FloorState, ODB.FloorDetected,
                            ODB.WorstState);
    delay(delay_time);
}
