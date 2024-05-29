#include "arduino-eymo.h"

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
  * * * CUERPO,ADELANTE,speed
  * * * CUERPO,STOP
  * * * CUERPO,ATRAS,speed
  * * * CUERPO,STOP,(- % giro)          // Giro en estatico hacia la izquierda 
  * * * CUERPO,STOP,(% giro)            // Giro en estatico hacia la derecha
  * * * CUERPO,ADELANTE,speed,(% giro)   // Giro hacia delante a la derecha
  * * * CUERPO,ADELANTE,speed,(- % giro) // Giro hacia delante a la izquierda
  * * * CUERPO,ATRAS,speed,(% giro)      // Giro hacia detras a la izquierda
  * * * CUERPO,ATRAS,speed,(- % giro)     // Giro hacia detras a la derecha
*/

void loop(){
  int cap = 0;
  bool error_M, error_S;

  if (serial.available()) {
    String mensaje = serial.readStringUntil('\n');  // Lee un mensaje hasta el caracter de nueva línea
    String *ordenes = split_string(mensaje, cap);
    if (ordenes[0] == "APAGAR")
      error_S = SMM.Shutdown();
    else if(ordenes[0] == "CABEZA"){
      if(ordenes[1] == "DERECHA")
        error_S = SMM.head_movement(-0.06);
      else
        error_S = SMM.head_movement(0.06);
    } 
    else if(ordenes[0] == "CUERPO"){

      if (ordenes[1] == "ADELANTE"){
        float speed = atof(ordenes[2].c_str());
        if(cap == 3)
          error_M = MCM.move(speed,0, ODM.get_distances());
        else {
          float giro = atof(ordenes[2].c_str())/100;
          error_M = MCM.move(speed,giro, ODM.get_distances());
        }
      } 
      else if (ordenes[1] == "STOP"){
        if(cap == 2)
          error_M = MCM.move(0,0, ODM.get_distances());
        else{
          float giro = atof(ordenes[3].c_str())/100;
          error_M = MCM.move(0,giro, ODM.get_distances());
        }
      } 
      else if (ordenes[1] == "ATRAS"){
        float speed = -(atof(ordenes[2].c_str()));
        if(cap == 3)
          error_M = MCM.move(speed,0, ODM.get_distances());
        else {
          float giro = atof(ordenes[3].c_str())/100;
          error_M = MCM.move(speed,giro, ODM.get_distances());
        }
      }
    }
  }
}

String* split_string(String msg, int &index) {
  static String partes[4]; // Arreglo de String
  int inicio = 0;
  int coma = 0;
  int i = 0;
  while (coma != -1 && i < 4) { // Verifica límite del arreglo
    coma = msg.indexOf(',', inicio); 
    if (coma != -1) {
      partes[i] = msg.substring(inicio, coma);
      inicio = coma + 1;
    } else {
      partes[i] = msg.substring(inicio);
    }
    i++;
  }
  index = i; // Actualiza el índice
  return partes; // Devuelve un puntero al arreglo
}
