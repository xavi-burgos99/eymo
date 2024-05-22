#define MotorE1 9
#define MotorM1 10
#define MotorE2 11
#define MotorM2 12 
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
  digitalWrite(MotorM1, HIGH);
  digitalWrite(MotorM2, HIGH);
  analogWrite(MotorE1, 110);
  analogWrite(MotorE2, 110);
  delay(3000);
  digitalWrite(MotorM1, LOW);
  digitalWrite(MotorM2, LOW);
  analogWrite(MotorE1, 0);
  analogWrite(MotorE2, 110);
  delay(1000);
  digitalWrite(MotorM1, LOW);
  digitalWrite(MotorM2, LOW);
  analogWrite(MotorE1, 110);
  analogWrite(MotorE2, 0);
  delay(1000);
}
