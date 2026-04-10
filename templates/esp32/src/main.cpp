#include <Arduino.h>

#include "config.h"

void setup() {
  Serial.begin(SERIAL_BAUD_RATE);
  delay(500);
  Serial.printf("[MAIN] {{PROJECT_NAME}} booting...\n");

  // TODO: inicializar periféricos (WiFi, MQTT, sensores, tasks)
}

void loop() {
  // Loop principal deve ser mínimo — toda lógica vive em tasks.
  // Mantenha vivo pra TWDT.
  vTaskDelay(pdMS_TO_TICKS(1000));
}
