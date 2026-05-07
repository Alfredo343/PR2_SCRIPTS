#define BAUDS 115200

#define LOGGER_ENABLED            // Comentar para deshabilitar el logger por consola serie

#define LOG_LEVEL TRACE           // niveles en c_logger: TRACE, DEBUG, INFO, WARN, ERROR, FATAL, NONE

#define DEVICE_GIIROB_PR2_ID      "09" 

// WIFI
#define NET_SSID                  "UPV-PSK"
#define NET_PASSWD                "giirob-pr2-2023"

// MQTT Broker UPV
#define MQTT_SERVER_IP            "mqtt.dsic.upv.es"
#define MQTT_SERVER_PORT          1883
#define MQTT_USERNAME             "giirob"    // Usuario para el broker de la UPV
#define MQTT_PASSWORD             "UPV2024"   // Contraseña para el broker de la UPV

const int PIN_BARRERA_ENTRADA = 14; 
const int PIN_FINAL_CARRERA    = 27;
const int PIN_MOTOR            = 26; // El motor de ESTA cinta

// --- NUEVO: Pin para el Dispensador (Electroválvula o Bomba) ---
// He elegido el Pin 15, cámbialo por el que uses tú físicamente.
const int PIN_DISPENSADOR      = 15; 

// 2. Definición de Topics MQTT (Estructura de tu código original)
#define TOPIC_SENSORES_GENERAL  "emqx/Grupo_09/sensores"       // Para publicar "caja_en_zona"
#define TOPIC_FINAL_CARRERA_A   "emqx/Grupo_09/final_carrera_A" // Para publicar "ACTIVADO"
#define TOPIC_MOTOR_A           "emqx/Grupo_09/motor_A"         // Para suscribirse y recibir "ON"/"OFF"
#define TOPIC_DISPENSADOR_CMD   "emqx/Grupo_09/dispensador/llenar" 
#define TOPIC_DISPENSADOR_ESTADO "emqx/Grupo_09/dispensador/estado"

// IO Predefinidos (no tocar si no es necesario)
#define LED_BUILTIN               2