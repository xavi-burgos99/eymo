#define MAX_TURN_SPEED 225
#define MAX_SPEED 255
#define MIN_SPEED 0

int turn_speed(float direction, int speed = 0);
float detection_mesurements(bool type, long US_raw = 0, float IR_raw = 0);



int turn_speed(float direction, int speed = MIN_SPEED){
    return speed;
}

float detection_mesurements(bool type, long US_raw, float IR_raw){
    if(type)
        return (US_raw/2) / 29.1;
    else
        return (6787.0f /IR_raw - 3.0f) - 4.0f;
}