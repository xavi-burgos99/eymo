#include <ArduinoJson.h>

void setup() {
  Serial.begin(9600);
  Serial.println("Arduino is ready.");
}

void loop() {
  StaticJsonDocument<200> doc;
  if (getSerial(doc)) {
    if (doc.isNull()) {
      return;
    }

    // Process the received JSON
    int mode = doc["mode"];
  
    // Send a response
    StaticJsonDocument<200> response;
    response["status"] = "ok";
    response["received_mode"] = mode;
  
    String responseString;
    serializeJson(response, responseString);
    Serial.println(responseString);
  }
}

bool getSerial(StaticJsonDocument<200> &doc) {
  static String input = "";
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      DeserializationError error = deserializeJson(doc, input);
      input = ""; // Clear the buffer
      if (error) {
        Serial.print("Deserialization failed: ");
        Serial.println(error.c_str());
        Serial.println("{\"error\":\"Invalid JSON\"}");
        return false;
      }
      Serial.print("Received: ");
      Serial.println(input);
      return true;
    } else {
      input += c;
    }
  }
  return false;
}