#define MotorE1 3
#define MotorM1 2
#define MotorE2 5
#define MotorM2 4

#define MAX_SPEED 135
#define MAX_REVERSE 160

// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(MotorE1, OUTPUT);
  pinMode(MotorE2, OUTPUT);
  pinMode(MotorM1, OUTPUT);
  pinMode(MotorM2, OUTPUT);
}

// the loop function runs over and over again forever
void loop() {
  digitalWrite(MotorM1, LOW);
  digitalWrite(MotorM2, LOW);
  analogWrite(MotorE1, MAX_SPEED);
  analogWrite(MotorE2, MAX_SPEED);
  delay(5000);
  analogWrite(MotorE1, 0);
  analogWrite(MotorE2, 0);
  delay(1500);
  digitalWrite(MotorM1, LOW);
  digitalWrite(MotorM2, HIGH);
  analogWrite(MotorE1, MAX_SPEED);
  analogWrite(MotorE2, MAX_REVERSE);
  delay(2500);
  analogWrite(MotorE1, 0);
  analogWrite(MotorE2, 0);
  delay(1500);
  digitalWrite(MotorM1, HIGH);
  digitalWrite(MotorM2, LOW);
  analogWrite(MotorE1, MAX_REVERSE);
  analogWrite(MotorE2, MAX_SPEED);
  delay(2500);
  analogWrite(MotorE1, 0);
  analogWrite(MotorE2, 0);
  delay(1500);
  digitalWrite(MotorM1, HIGH);
  digitalWrite(MotorM2, HIGH);
  analogWrite(MotorE1, MAX_REVERSE);
  analogWrite(MotorE2, MAX_REVERSE);
  delay(5000);
  analogWrite(MotorE1, 0);
  analogWrite(MotorE2, 0);
  delay(1500);
}
