#ifndef UTILITIES_HPP
#define UTILITIES_HPP

#define MAX_TURN_SPEED 225
#define MAX_SPEED 255
#define MIN_SPEED 0

enum SensorState {
    Initiating = 0,
    Safe = 1,
    Close = 2,
    Warning = 3,
    Dangerous = 4,
};

// Function for debbuging purposes
void printStatesAndDistances(SensorState IRState, float IRDistance, SensorState BackState, float BackDistance, SensorState WorstState) {
    // IR
    Serial.print("IR state: ");
    Serial.print(IRState);
    Serial.print(", IR distance: ");
    Serial.println(IRDistance);
    // US
    Serial.print("US state: ");
    Serial.print(BackState);
    Serial.print(", US distance: ");
    Serial.println(BackDistance);
    // Worst state
    Serial.print("Worst state: ");
    Serial.println(WorstState);
}

#endif // UTILITIES_HPP