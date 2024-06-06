#include <Arduino.h>
#include "utilities.hpp"

/**
 * max speed = 255
 * limited max speed to 225
 * Min speed = 0
 * strucr delante atras y parado, y uno distinto de derecha izquierda
 */

class MotorControlModule
{
public:
    MotorControlModule(int motorM1, int motorM2, int motorE1, int motorE2);
    bool move(int speed, int direction);
    bool checkObstacles(int &speed, SensorState IRState, SensorState BackState, SensorState WorstState);

private:
    bool _soft_speed_update(int speed, float alpha);
    bool _move_motor(int motorM, int motorE, int speed, int direction); // direction: 0 = forward, 1 = backward
    bool _coerce_speed_boundaries();
    bool _stop();
    bool _compute_speed_and_direction(int speed, int direction,
                                      int &speed1, int &speed2,
                                      int &motor_direction1, int &motor_direction2);

    int _motorM1;
    int _motorM2;
    int _motorE1;
    int _motorE2;

    int _speed;
    float _epsilon;
};

MotorControlModule::MotorControlModule(int motorM1, int motorM2, int motorE1, int motorE2)
{
    _motorM1 = motorM1;
    _motorM2 = motorM2;

    _motorE1 = motorE1;
    _motorE2 = motorE2;

    _speed = 0;
    _epsilon = 3;

    pinMode(_motorM1, OUTPUT);
    pinMode(_motorM2, OUTPUT);
    pinMode(_motorE1, OUTPUT);
    pinMode(_motorE2, OUTPUT);
}

bool MotorControlModule::_compute_speed_and_direction(int speed, int direction,
                                                      int &speed1, int &speed2,
                                                      int &motor_direction1, int &motor_direction2)
{
    speed1 = abs(speed);
    speed2 = speed1;
    switch (direction)
    {
    case -1: // turn left
        speed1 = 0;
        break;
    case -2: // rotate left
        motor_direction1 = 1;
        break;
    case 1: // turn right
        speed2 = 0;
        break;
    case 2: // rotate right
        motor_direction2 = 1;
        break;
    default:
        break;
    }

    if (speed < 0)
    {
        motor_direction1 = 1;
        motor_direction2 = 1;
    }
}

bool MotorControlModule::checkObstacles(int &speed, SensorState IRState, SensorState BackState, SensorState WorstState) 
{
    // Si intenta avanzar y está en el borde parada de emergencia
    if (IRState == Dangerous && speed > 0)
    {
        _stop();
        speed = 0;
    }
    // Si intenta retroceder y está cerca de un objeto parada de emergencia
    if (BackState == Dangerous && speed < 0)
    {
        _stop();
        speed = 0;
    }
    if (WorstState == Warning)
    {
        speed = (int) (0.25 * speed);
    }
    if (WorstState == Close)
    {
        speed = (int) (0.75 * speed);
    }
}

bool MotorControlModule::move(int speed, int direction)
{
    _soft_speed_update(-speed, 0.8);

    // Inicializacion de velocidades y direcciones
    int speed1 = 0;
    int speed2 = 0;
    int motor_direction1 = 0;
    int motor_direction2 = 0;

    // Cálculo de velocidades y direcciones
    _compute_speed_and_direction(_speed, direction, speed1, speed2, motor_direction1, motor_direction2);

    // Mover motores
    _move_motor(_motorM1, _motorE1, speed1, motor_direction1);
    _move_motor(_motorM2, _motorE2, speed2, motor_direction2);
}

bool MotorControlModule::_move_motor(int motorM, int motorE, int speed, int motor_direction)
{
    // Hacia delante
    if (motor_direction == 0)
    {
        digitalWrite(motorM, HIGH);
    }
    // Hacia atrás
    else
    {
        digitalWrite(motorM, LOW);
    }
    analogWrite(motorE, speed);
}

bool MotorControlModule::_stop()
{
    // Parar bruscamente los motores
    _speed = 0;
    _move_motor(_motorM1, _motorE1, 0, 0);
    _move_motor(_motorM2, _motorE2, 0, 0);
}

bool MotorControlModule::_coerce_speed_boundaries()
{
    // Controlar overflow de la velocidad
    if (_speed > 255)
    {
        _speed = 255;
    }
    if (_speed < -255)
    {
        _speed = -255;
    }
}

bool MotorControlModule::_soft_speed_update(int target_speed, float alpha)
{
    // Si la velocidad objetivo no se ha alcanzado se añade un porcentaje de la diferencia
    if (abs(_speed - target_speed) >= _epsilon)
    {
        _speed = (int) _speed + (target_speed - _speed) * alpha;
    }
    else
    {
        _speed = target_speed;
    }
    // Controlar overflow
    _coerce_speed_boundaries();
}
