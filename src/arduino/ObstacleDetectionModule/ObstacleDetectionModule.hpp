#include <Arduino.h>
#include "../utilities.hpp"

enum SensorState {
    Initiating = 0,
    Safe = 1,
    Close = 2,
    Warning = 3,
    Dangerous = 4,

};

class ObstacleDetectionModule{
    public:
        SensorState IRState, BackState;
    private:
        // Sensor pins
        int _pinIR, _BackEcho, _BackTrig;
        // Front sensors
        float IRDistance;

        // Back sensors
        float _BackDistance;

        ObstacleDetectionModule(int pinIR, int BackEcho, int BackTrig);
        void update();
		float readInfrared(int pin);
		float UltraSonicMetrics(int trigger, int echo);

};

ObstacleDetectionModule::ObstacleDetectionModule(int pinIR, int BackEcho, int BackTrig) {

    _pinIR = pinIR;
    _BackEcho = BackEcho;
    _BackTrig = BackTrig;

    IRDistance = 0.0f;

    _BackDistance = 0.0f;
    IRState = Initiating;
    BackState = Initiating;
}

void ObstacleDetectionModule::update() {
    IRDistance = readInfrared(_pinIR);
    _BackDistance = UltraSonicMetrics(_BackTrig, _BackEcho);

    if (IRDistance < 10) {
        IRState = Dangerous;
    }
    else if (IRDistance < 20) {
        IRState = Warning;
    }
    else if (IRDistance < 30) {
        IRState = Close;
    }
    else {
        IRState = Safe;
    }

    if (_BackDistance < 10) {
        BackState = Dangerous;
    }
    else if (_BackDistance < 20) {
        BackState = Warning;
    }
    else if (_BackDistance < 30) {
        BackState = Close;
    }
    else {
        BackState = Safe;
    }
}

float ObstacleDetectionModule::readInfrared(int pin) {
    //? Read sensor value
    uint16_t sensorValue_raw = 0;
    float sensorValue = 0.0f;
    sensorValue_raw = analogRead(pin);

    //* print the results to the Serial Monitor:
    Serial.print("Infrared sensor value: ", sensorValue_raw);

    //*  filter unstable values
    if (sensorValue_raw < 0) {
        return -1;
    }

    // transform the sensor value to distance in cm
    sensorValue = detection_mesurements(false, 0, (float)sensorValue_raw);

    return sensorValue;
}

float ObstacleDetectionModule::UltraSonicMetrics(int trigger, int echo) {
    long duration = 0;
    float distance = 0.0f;

    // Emit the pulse
    digitalWrite(trigger, LOW);
    delayMicroseconds(2);
    digitalWrite(trigger, HIGH);

    // Read the pulse data
    delayMicroseconds(10);
    digitalWrite(trigger, LOW);
    duration = pulseIn(echo, HIGH);

    // transform the pulse data to distance in cm
    distance = detection_mesurements(true, duration, 0.0f);

    return distance;

}