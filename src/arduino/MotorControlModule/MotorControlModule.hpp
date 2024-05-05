#include <Arduino.h>
#include "../utilities.hpp"

/**
 * max speed = 255
 * limited max speed to 225
 * Min speed = 0
 * 
 */

class MotorControlModule {
  public:
    MotorControlModule(int motorP1, int motorP2, int motorE1, int motorE2);
    bool move(float direction);
    bool move(int speed, float direction);
    
  private:
    
    bool _turn(float direction); // direction: -1 = left, 0 = straigth on, 1 = right 
    bool _turn_stop(float direction);
    
    int _motorP1;
    int _motorP2;
    int _motorE1;
    int _motorE2;

    int _speed;
};

MotorControlModule::MotorControlModule(int motorP1, int motorP2, int motorE1, int motorE2) {
    _motorP1 = motorP1;
    _motorP2 = motorP2;

    _motorE1 = motorE1;
    _motorE2 = motorE2;
    _speed = 0;

    pinMode(_motorP1, OUTPUT);
    pinMode(_motorP2, OUTPUT);
    pinMode(_motorE1, OUTPUT);
    pinMode(_motorE2, OUTPUT);

}

bool MotorControlModule::move(float direction, int speed) {
    _speed = speed;
    if(direction != 0){
        digitalWrite(_motorP1, HIGH);
        digitalWrite(_motorP2, HIGH);

        analogWrite(_motorE1, _speed);
        analogWrite(_motorE2, _speed);
    }else{
        if(speed == 0)
            _turn_stop(direction);
        else
            _turn(direction);
            
    }

}
bool MotorControlModule::move(float direction) {

    if(direction != 0){
        digitalWrite(_motorP1, HIGH);
        digitalWrite(_motorP2, HIGH);

        analogWrite(_motorE1, _speed);
        analogWrite(_motorE2, _speed);
    }else{
        if(speed == 0)
            _turn_stop(direction);
        else
            _turn(direction);
            
    }

}

bool MotorControlModule::_turn(float direction) {
    
    if(direction < 0){
        digitalWrite(_motorP1, HIGH);
        digitalWrite(_motorP2, LOW);
        
        analogWrite(_motorE1, turn_speed(direction, _speed));
        analogWrite(_motorE2, turn_speed(direction, _speed));
    }else{
        digitalWrite(_motorP1, LOW);
        digitalWrite(_motorP2, HIGH);
        
        analogWrite(_motorE1, turn_speed(direction, _speed));
        analogWrite(_motorE2, turn_speed(direction, _speed));
    }
}

bool MotorControlModule::_turn_stop(float direction) {
    if(direction < 0){
        digitalWrite(_motorP1, HIGH);
        digitalWrite(_motorP2, LOW);

        analogWrite(_motorE1, turn_speed(direction));
        analogWrite(_motorE2, turn_speed(direction));
    }else{
        digitalWrite(_motorP1, LOW);
        digitalWrite(_motorP2, HIGH);

        analogWrite(_motorE1, turn_speed(direction));
        analogWrite(_motorE2, turn_speed(direction));
    }
}