#include <Arduino.h>
#include "../utilities.hpp"

/**
 * @brief 
 * Angulos de 30º hacia un lado y hacia el otro
 * 
 */

class ServoMovementModule {
public:
	ServoMovementModule();
	bool head_movement(int direction); // direction: -1 = left == -30º, 0 = straigth on, 1 = right == 30º
private:
	int _angle=0;
};