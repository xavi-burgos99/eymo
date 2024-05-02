#include <Arduino.h>
#include "../../utilities.hpp"

float readInfrared(int pin) {
    //? Read sensor value
    uint16_t sensorValue_raw = 0;
    float sensorValue = 0.0f;
    sensorValue_raw = analogRead(pin);

    //* print the results to the Serial Monitor:
    Serial.print("Infrared sensor value: ", sensorValue_raw);

    //*  filter unstable values
    if(sensorValue_raw < 0 ){
        return -1;
    }

    // transform the sensor value to distance in cm
    sensorValue = detection_mesurements(false, 0, (float)sensorValue_raw);

    return sensorValue;
}
