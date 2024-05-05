#include <Arduino.h>
#include "../utilities.hpp"
#include <Wire.h>

class ServoMovementModule {
public:
	ServoMovementModule();
	bool head_movement(int angle); // angle: -1 = left, 0 = straigth on, 1 = right
private:
	int;
	int;
};