
bool ledStatus = false; 


void setInternalLed(bool status) {
  
  // 1. Comprobación de cambio de estado (para evitar redundancia)
  if ( ledStatus == status ) // Si el estado ya es el solicitado, no hacemos nada
    return;
    
  // 2. Actualización física del hardware
  ledStatus = status;
  if ( status ) {
    infoln("Led Interno: ON");
    digitalWrite(LED_BUILTIN, HIGH);
  } else {
    infoln("Led Interno: OFF");
    digitalWrite(LED_BUILTIN, LOW);
  }

  
  // Usamos la variable 'deviceID' que se define en el .ino principal.
  String statusTopic = String("giirob/pr2/devices/") + deviceID + String("/status");
  
  // Preparamos el mensaje de texto plano
  String statusMessage = status ? "ON" : "OFF";
  
  // Publicamos el estado usando la función auxiliar de g_comunicaciones.ino
  traceln(String("~~>> Publicando auto-estado del LED en: ") + statusTopic);
  enviarMensajePorTopic(statusTopic.c_str(), statusMessage);

}