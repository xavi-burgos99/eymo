#include <Arduino.h>
#include <Servo.h> 


/**
 * @brief 
 * 
 *
 * Angulos de 30º hacia un lado y hacia el otro
 * 
 */
class ServoMovementModule {
public:
	ServoMovementModule( int S_pin);
	bool head_movement(float direction); // direction: -1 = left view == -30º, 0 = front view = 0º, 1 = right view == 30º
									   // Función para mover el servomotor
private:
  	Servo servo;
	int _initialAngle = 30; // Posición inicial del servomotor (en grados)
	int _moveRange = 30; // Rango de movimiento del servomotor (en grados)
	int _actualAngle = 0; // Posición actual del servomotor (en grados)

};

ServoMovementModule::ServoMovementModule( int S_pin){
	servo.attach(S_pin); 
    bool error = head_movement(_initialAngle);
}

// Función para mover el servomotor
bool ServoMovementModule::head_movement(float direction) {
	int grados = int(_actualAngle + direction * _moveRange);
    if (grados >= _initialAngle - _moveRange && grados <= _initialAngle + _moveRange) {
      servo.write(grados);
	  _actualAngle = grados;
	  return true;
    } else {
      return false;
    }
}