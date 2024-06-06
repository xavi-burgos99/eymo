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


#endif // UTILITIES_HPP