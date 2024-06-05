#include "arduino-eymo.h"


// the setup function runs once when you press reset or power the board
ObstacleDetectionModule ODB(IREcho, US2Echo, US2Trig);
int speed = 0;
int direction = 0;
int delay_time = 500;
float ultrasonic_dist = 0.0;
float infrarred_dist = 0.0;
void setup() {
    Serial.begin(9600);
    Serial.println("Beginning setup...");
    Serial.println("Setup done.\nBeginning loop...");
}

// the loop function runs over and over again forever
void loop() {
    ODB.update();
    Serial.print("Ultrasonic: ");
    Serial.println(ODB.BackDistance);

    Serial.print("infrarred: ");
    Serial.println(ODB.IRDistance);

    delay(delay_time);
}
