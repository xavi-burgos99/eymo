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
    MotorControlModule(int motor1Pin1, int motor1Pin2, int motor2Pin1, int motor2Pin2, int motorENB, int motorENA);
    bool move(float direction);
    bool move(int speed, float direction);
    
  private:
    
    bool _turn(float direction); // direction: -1 = left, 0 = straigth on, 1 = right 
    bool _turn_stop(float direction);
    
    int _motor1Pin1;
    int _motor1Pin2;
    int _motor2Pin1;
    int _motor2Pin2;
    int _motorENB;
    int _motorENA;

    int _speed;
};

MotorControlModule::MotorControlModule(int motor1Pin1, int motor1Pin2, int motor2Pin1, int motor2Pin2, int motorENB, int motorENA){
    _motor1Pin1 = motor1Pin1;
    _motor1Pin2 = motor1Pin2;
    _motor2Pin1 = motor2Pin1;
    _motor2Pin2 = motor2Pin2;
    _motorENB = motorENB;
    _motorENA = motorENA;
    _speed = 0;
    pinMode(_motor1Pin1, OUTPUT);
    pinMode(_motor1Pin2, OUTPUT);
    pinMode(_motor2Pin1, OUTPUT);
    pinMode(_motor2Pin2, OUTPUT);
    pinMode(_motorENB, OUTPUT);
    pinMode(_motorENA, OUTPUT);

}

bool MotorControlModule::move(float direction, int speed) {
    _speed = speed;
    if(direction != 0){
        digitalWrite(_motor1Pin1, HIGH);
        digitalWrite(_motor1Pin2, LOW);
        digitalWrite(_motor2Pin1, HIGH);
        digitalWrite(_motor2Pin2, LOW);
        analogWrite(_motorENB, _speed);
        analogWrite(_motorENA, _speed);
    }else{
        if(speed == 0)
            _turn_stop(direction);
        else
            _turn(direction);
            
    }

}
bool MotorControlModule::move(float direction) {

    if(direction != 0){
        digitalWrite(_motor1Pin1, HIGH);
        digitalWrite(_motor1Pin2, LOW);
        digitalWrite(_motor2Pin1, HIGH);
        digitalWrite(_motor2Pin2, LOW);
        analogWrite(_motorENB, _speed);
        analogWrite(_motorENA, _speed);
    }else{
        if(speed == 0)
            _turn_stop(direction);
        else
            _turn(direction);
            
    }

}

bool MotorControlModule::_turn(float direction) {
    
    if(direction < 0){
        digitalWrite(_motor1Pin1, HIGH);
        digitalWrite(_motor1Pin2, LOW);
        digitalWrite(_motor2Pin1, LOW);
        digitalWrite(_motor2Pin2, HIGH);
        analogWrite(_motorENA, turn_speed(direction, _speed));
        analogWrite(_motorENB, turn_speed(direction, _speed));
    }else{
        digitalWrite(_motor1Pin1, LOW);
        digitalWrite(_motor1Pin2, HIGH);
        digitalWrite(_motor2Pin1, HIGH);
        digitalWrite(_motor2Pin2, LOW);
        analogWrite(_motorENA, turn_speed(direction, _speed));
        analogWrite(_motorENB, turn_speed(direction, _speed));
    }
}

bool MotorControlModule::_turn_stop(float direction) {
    if(direction < 0){
        digitalWrite(_motor1Pin1, HIGH);
        digitalWrite(_motor1Pin2, LOW);
        digitalWrite(_motor2Pin1, LOW);
        digitalWrite(_motor2Pin2, HIGH);
        analogWrite(_motorENA, turn_speed(direction));
        analogWrite(_motorENB, turn_speed(direction));
    }else{
        digitalWrite(_motor1Pin1, LOW);
        digitalWrite(_motor1Pin2, HIGH);
        digitalWrite(_motor2Pin1, HIGH);
        digitalWrite(_motor2Pin2, LOW);
        analogWrite(_motorENA, turn_speed(direction));
        analogWrite(_motorENB, turn_speed(direction));
    }
}