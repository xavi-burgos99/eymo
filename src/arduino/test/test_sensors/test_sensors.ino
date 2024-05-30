#include "arduino-eymo.h"


// the setup function runs once when you press reset or power the board
ObstacleDetectionModule ODB(IREcho, US2Trig, US2Echo);
int speed = 0;
int direction = 0;
int delay_time = 50;
float ultrasonic_dist = 0.0;
void setup() {
    Serial.println("Beginning setup...");
    Serial.begin(9600);
    Serial.println("Setup done.\nBeginning loop...");
}

// the loop function runs over and over again forever
void loop() {
    ultrasonic_dist = ODB.UltraSonicMetrics(US2Trig, US2Echo);
    Serial.println(ultrasonic_dist);
    delay(delay_time);
}
