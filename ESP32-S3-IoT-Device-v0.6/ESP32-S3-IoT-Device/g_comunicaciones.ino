// --- g_comunicaciones.ino ---
// (CORREGIDO: Se ha añadido la lógica completa para el Dispensador de Líquido)

void suscribirseATopics() {
  // Nos suscribimos al topic que controla NUESTRO motor de cinta
  mqtt_subscribe(TOPIC_MOTOR_A); 

  // --- NUEVA SUSCRIPCIÓN: Comando del Dispensador ---
  mqtt_subscribe(TOPIC_DISPENSADOR_CMD); 
}

void alRecibirMensajePorTopic(char* topic, String incomingMessage) {

  traceln("<<~~ Procesando mensaje en topic de control...");

  // --- LÓGICA 1: CONTROL DEL MOTOR VIA MQTT ---

  // Comprobamos si el mensaje es para nuestro motor de cinta
  if (strcmp(topic, TOPIC_MOTOR_A) == 0) {
    info("Orden recibida para MOTOR_A: ");
    infoln(incomingMessage);

    if (incomingMessage == "ON") {
      // Orden de encender el motor
      infoln("--> Encendiendo Motor Físicamente");
      digitalWrite(PIN_MOTOR, HIGH); 
    }
    else if (incomingMessage == "OFF") {
      // Orden de apagar el motor
      infoln("--> Apagando Motor Físicamente");
      digitalWrite(PIN_MOTOR, LOW); 
    }
    else {
      warnln("!! Orden para motor no reconocida (se esperaba ON u OFF)");
    }
  }
  // --- FIN LÓGICA MOTOR ---

  // Comprobamos si el mensaje es para el dispensador
  if (strcmp(topic, TOPIC_DISPENSADOR_CMD) == 0) {
    info("Orden recibida para DISPENSADOR: ");
    infoln(incomingMessage);

    if (incomingMessage == "INICIAR" || incomingMessage == "START" || incomingMessage == "ON") {
      
      infoln("--> INICIANDO PROCESO DE LLENADO");

      // 1. Informamos que estamos llenando
      enviarMensajePorTopic(TOPIC_DISPENSADOR_ESTADO, "LLENANDO");

      // 2. Activamos físicamente el dispensador (electrovalvula/bomba)
      digitalWrite(PIN_DISPENSADOR, HIGH); 
      setInternalLed(true); // Encendemos LED interno como indicador visual extra
      
      // 3. TIEMPO DE LLENADO: Esperamos 2 segundos
      infoln("... Llenando durante 2 segundos ...");
      delay(2000); 
      
      // 4. Apagamos físicamente el dispensador
      digitalWrite(PIN_DISPENSADOR, LOW); 
      setInternalLed(false); // Apagamos LED interno

      // 5. Informamos que hemos terminado el llenado
      enviarMensajePorTopic(TOPIC_DISPENSADOR_ESTADO, "LISTO");
      infoln("--> Proceso de llenado finalizado.");

    }
    else {
      warnln("!! Orden para dispensador no reconocida (se esperaba INICIAR o similar)");
    }
  }
  // --- FIN LÓGICA DISPENSADOR ---
}

void enviarMensajePorTopic(const char* topic, String outgoingMessage) {
  mqtt_publish(topic, outgoingMessage.c_str());
}