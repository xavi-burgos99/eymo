#include "arduino-eymo.h"

MotorControlModule MCM(MotorM1,MotorM2,MotorE1,MotorE2);
ObstacleDetectionModule ODM(IREcho, USEcho, USTrig);
ServoMovementModule SMM;
SoftwareSerial serial(PIN_RX, PIN_TX);

void setup(){
  serial.begin(9600);
  pinMode(MotorE1, OUTPUT);
  pinMode(MotorE2, OUTPUT);
  pinMode(MotorM1, OUTPUT);
  pinMode(MotorM2, OUTPUT);
  pinMode(USEcho, INPUT);
  pinMode(USTrig, INPUT);

}
/**
  * Ordenes a recibir:
  * * Orientación cabeza: 
  * * * CABEZA,DERECHA
  * * * CABEZA,IZQUIERDA
  * * Dirección cuerpo: 
  * * * CUERPO,ADELANTE
  * * * CUERPO,STOP
  * * * CUERPO,ATRAS
  * * * CUERPO,STOP,(- % giro)          // Giro en estatico hacia la izquierda 
  * * * CUERPO,STOP,(% giro)            // Giro en estatico hacia la derecha
  * * * CUERPO,ADELANTE (- % giro) // Giro hacia delante a la izquierda
  * * * CUERPO,ATRAS(- % giro)     // Giro hacia detras a la derecha
  * * * CUERPO,ADELANTE (% giro)   // Giro hacia delante a la derecha
  * * * CUERPO,ATRAS (% giro)      // Giro hacia detras a la izquierda
*/

void loop(){
  if (serial.available()) {
    String mensaje = serial.readStringUntil('\n');  // Lee un mensaje hasta el caracter de nueva línea
    String ordenes[] = mensaje.split(',');
    if(ordenes[0] == "CABEZA"){
      if(ordenes[1] == "DERECHA"){

      }else{

      }
    } else if(ordenes[0] == "CUERPO"){
      switch(ordenes[1]){
        case "ADELANTE":
          if(ordenes.size() == 2){

          }else{
            float giro = float(ordenes[2])/100;
          }
          break;
        case "STOP":
          if(ordenes.size() == 2){

          }else{
            float giro = float(ordenes[2])/100;
          }
          break;
        case "ATRAS":
          if(ordenes.size() == 2){

          }else{
            float giro = float(ordenes[2])/100;
          }
          break;
        default:
          break;
      }
    }else{
      continue;
    }


  }

}