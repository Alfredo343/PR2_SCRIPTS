void on_setup() {

    // 1. Configurar LED interno (de la plantilla)
    pinMode(LED_BUILTIN, OUTPUT);
    setInternalLed(0); // Asegurar que empieza apagado

    // 2. Configurar Pines de Usuario (Cinta A y Sensores)
    
    pinMode(PIN_BARRERA_ENTRADA, INPUT_PULLUP); 
    
    pinMode(PIN_FINAL_CARRERA, INPUT);

    // Motor: Salida digital
    pinMode(PIN_MOTOR, OUTPUT);
    digitalWrite(PIN_MOTOR, LOW); // Motor APAGADO inicialmente
    

    pinMode(PIN_DISPENSADOR, OUTPUT);
    digitalWrite(PIN_DISPENSADOR, LOW); // Dispensador APAGADO (Cerrado) inicialmente
    

    infoln("--- Hardware Inicializado (Motores, Sensores y Dispensador) ---");
}


}

