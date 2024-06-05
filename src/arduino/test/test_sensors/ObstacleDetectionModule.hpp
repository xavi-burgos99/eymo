#include <Arduino.h>

enum SensorState {
    Initiating = 0,
    Safe = 1,
    Close = 2,
    Warning = 3,
    Dangerous = 4,
};

class ObstacleDetectionModule{
    public:
        // States for each sensor
        SensorState IRState, BackState;
        // Front sensor value
        float IRDistance;
        // Back sensor value
        float BackDistance;

        ObstacleDetectionModule(int pinIR, int BackEcho, int BackTrig);
        void update();

    private:
        // Sensor pins
        int _pinIR, _BackEcho, _BackTrig;

		float readInfrared(int pin);
		float UltraSonicMetrics(int trigger, int echo);
};

ObstacleDetectionModule::ObstacleDetectionModule(int pinIR, int BackEcho, int BackTrig) {

    _pinIR = pinIR;
    _BackEcho = BackEcho;
    _BackTrig = BackTrig;

    IRDistance = 0.0f;

    BackDistance = 0.0f;
    IRState = Initiating;
    BackState = Initiating;

    // Inicializa el pin Trigger como salida
    pinMode(BackTrig, OUTPUT);
    // Inicializa el pin Echo como entrada
    pinMode(BackEcho, INPUT);
    pinMode(pinIR, INPUT);
}

void ObstacleDetectionModule::update() {
    IRDistance = readInfrared(_pinIR);
    BackDistance = UltraSonicMetrics(_BackTrig, _BackEcho);

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

    if (BackDistance < 10) {
        BackState = Dangerous;
    }
    else if (BackDistance < 20) {
        BackState = Warning;
    }
    else if (BackDistance < 30) {
        BackState = Close;
    }
    else {
        BackState = Safe;
    }
}

float ObstacleDetectionModule::readInfrared(int pin) {
    // Read sensor value
    uint16_t sensorValue_raw = 0;
    float sensorValue = 0.0f;
    sensorValue_raw = analogRead(pin);

    //  filter unstable values
    if (sensorValue_raw < 0) {
        return -1;
    }

    // transform the sensor value to distance in cm
    sensorValue = (6787.0f /sensorValue_raw - 3.0f) - 4.0f;
    return sensorValue;
}

float ObstacleDetectionModule::UltraSonicMetrics(int trigger, int echo) {
    long duration = 0;
    float distance = 0.0f;

    // Emit the pulse
    digitalWrite(trigger, LOW);
    delayMicroseconds(2);

    // Read the pulse data
    digitalWrite(trigger, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigger, LOW);

    duration = pulseIn(echo, HIGH);
    distance = duration * 0.034 / 2;
    return distance;
}
