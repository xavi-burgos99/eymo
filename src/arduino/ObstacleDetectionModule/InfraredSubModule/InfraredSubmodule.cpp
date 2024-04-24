include "main.h"

void readInfrared(int pin) {
    // Read sensor value
    int sensorValue = 0;
    sensorValue = analogRead(analogInPin);

    // print the results to the Serial Monitor:
    Serial.print("Infrared sensor value: ", sensorValue);

    // TODO: filter unstable values

    return sensorValue;
}
