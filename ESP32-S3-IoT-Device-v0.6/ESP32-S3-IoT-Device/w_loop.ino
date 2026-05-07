void on_loop() {

  // --- LÓGICA DE LECTURA DE SENSORES Y PUBLICACIÓN MQTT ---

  // Asumimos que el sensor es normlamemte abierto y cierra a masa
  if (digitalRead(PIN_BARRERA_ENTRADA) == LOW) { 
    // La barrera detecta que la caja está entrando
    traceln("Barrera activada: Detectada caja entrando.");
    
    // Publicamos el evento por MQTT
    enviarMensajePorTopic(TOPIC_SENSORES_GENERAL, "caja_en_zona");
  }


  // 2. Gestión del FINAL DE CARRERA (Parada de precisión)
  // Según tu código original, se activa a HIGH.
  if (digitalRead(PIN_FINAL_CARRERA) == HIGH) {
    // Toca el final de carrera
    traceln("Final de carrera activado: Caja en posición.");

    digitalWrite(PIN_MOTOR, LOW); 
    
    // Informamos al sistema central vía MQTT
    enviarMensajePorTopic(TOPIC_FINAL_CARRERA_A, "ACTIVADO");
    
    // Imprimimos info por serial (como en tu código original)
    Serial.println("Caja en posición final. Motor parado localmente. Esperando robot...");
.
    
    // Pequeño delay para evitar re-detecciones constantes mientras la caja está ahí
    delay(500); 
  }

}