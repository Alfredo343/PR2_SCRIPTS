import paho.mqtt.client as mqtt
import time
import sys

# --- CONFIGURACIÓN MQTT BROKER UPV (Igual que en ESP32 Config.h) ---
MQTT_BROKER     = "mqtt.dsic.upv.es"
MQTT_PORT       = 1883
MQTT_USER       = "giirob"    # Usuario del broker UPV
MQTT_PASS       = "UPV2024"   # Contraseña del broker UPV
MQTT_GROUP_ID   = "Grupo_01"  # Tu ID de grupo

# --- DEFINICIÓN DE TOPICS MQTT (Adaptado a ESP32 Config.h) ---
# Asumimos que la ESP32 controla la Cinta A y su Dispensador A.
TOPIC_BASE = f"emqx/{MQTT_GROUP_ID}"

# 1. Topics para Escuchar a la ESP32 (Suscripciones)
TOPIC_BARRERA_ENTRADA_A_RAW   = f"{TOPIC_BASE}/sensores"       # Recibe "caja_en_zona"
TOPIC_FINAL_CARRERA_A_RAW     = f"{TOPIC_BASE}/final_carrera_A" # Recibe "ACTIVADO"
TOPIC_DISPENSADOR_A_ESTADO    = f"{TOPIC_BASE}/dispensador/estado" # Recibe "LLENANDO", "LISTO"

# 2. Topics para Ordenar a la ESP32 (Publicaciones)
TOPIC_MOTOR_A_CMD             = f"{TOPIC_BASE}/motor_A"         # Publicar "ON"/"OFF"
TOPIC_DISPENSADOR_A_CMD       = f"{TOPIC_BASE}/dispensador/llenar" # Publicar "INICIAR"

# 3. Topics para otra ESP32 (Cinta B - Opcional, para lógica de exclusividad)
# TOPIC_MOTOR_B_CMD           = f"{TOPIC_BASE}/motor_B"         # Publicar "ON"/"OFF"
# TOPIC_FINAL_CARRERA_B       = f"{TOPIC_BASE}/final_carrera_B" # Para lógica completa de exclusividad

# 4. Topics de RoboDK/Robot (Para simular la parte de trabajo del robot)
TOPIC_ROBOT_A_TRABAJANDO_CMD   = f"{TOPIC_BASE}/robot/trabajando_a" # Recibir "SOLICITAR_LLENADO", "TRABAJO_FINALIZADO"
TOPIC_ROBOT_ESTADO             = f"{TOPIC_BASE}/robot/estado"      # Publicar "ESPERANDO", "TRABAJANDO"

# --- LÓGICA DE CONTROL Y EXCLUSIVIDAD (Cerebro del Sistema) ---
contador_bricks = 0
robot_ocupado_con_cinta = None # Indica si el robot está ocupado con la Cinta A (o B, si la hubiese)
caja_en_barrera_a = False
caja_en_final_carrera_a = False
dispensador_llenando_a = False

# Función simulada de RoboDK para mover el robot (Remplázala por tu código de simulación real)
def mover_robot_a_brick(brick_num, cinta):
    print(f"[RoboDK Sim] Movimiento Robot: Cogiendo y colocando Brick {brick_num} en caja de {cinta}")
    time.sleep(1) # Simular tiempo de movimiento

# Función simulada para verificar GDI (De tu código original, ajustada)
def f_verificar_y_actualizar_gdi(zona, cantidad_requerida):
    print(f"[GDI] Verificando stock de GDI para {zona}. Requiere {cantidad_requerida} unidades.")
    # Simulación simple, siempre hay stock.
    return True 

# --- CALLBACKS MQTT ---

def on_connect(client, userdata, flags, rc):
    """Callback llamado al conectarse con éxito al broker."""
    if rc == 0:
        print(f"[MQTT] Conectado exitosamente al broker UPV en {MQTT_BROKER}:{MQTT_PORT}")
        # Publicar estado inicial
        client.publish(TOPIC_ROBOT_ESTADO, "ESPERANDO")
        
        # Suscribirse a todos los topics necesarios
        topics_to_subscribe = [
            (TOPIC_BARRERA_ENTRADA_A_RAW, 0),
            (TOPIC_FINAL_CARRERA_A_RAW, 0),
            (TOPIC_DISPENSADOR_A_ESTADO, 0),
            (TOPIC_ROBOT_A_TRABAJANDO_CMD, 0)
            # (TOPIC_FINAL_CARRERA_B, 0) # Si hay cinta B
        ]
        client.subscribe(topics_to_subscribe)
        print("[MQTT] Suscripciones realizadas.")
    else:
        print(f"[MQTT Error] Error de conexión, código de retorno: {rc}")
        sys.exit(1)

def on_message(client, userdata, msg):
    """Callback llamado al recibir un mensaje MQTT."""
    global contador_bricks, robot_ocupado_con_cinta, caja_en_barrera_a, caja_en_final_carrera_a, dispensador_llenando_a
    payload = msg.payload.decode()
    topic = msg.topic

    # --- ESCENARIO 1: GESTIÓN DE SENSORES DE LA ESP32 (Escuchar a ESP32) ---

    # Barrera de entrada detecta caja (Cinta A)
    if topic == TOPIC_BARRERA_ENTRADA_A_RAW and payload == "caja_en_zona":
        if not caja_en_barrera_a: # Solo la primera vez
            print("[INFO] Caja detectada entrando en Cinta A. Avanzando cinta.")
            caja_en_barrera_a = True
            # Nos aseguramos de que el motor de la cinta A esté encendido
            client.publish(TOPIC_MOTOR_A_CMD, "ON") 

    # Final de carrera activado (Cinta A). La ESP32 ya ha parado el motor localmente.
    elif topic == TOPIC_FINAL_CARRERA_A_RAW and payload == "ACTIVADO":
        if not caja_en_final_carrera_a: # Solo la primera vez
            print("[INFO] Caja ha llegado al final de carrera de Cinta A (PARADA).")
            caja_en_final_carrera_a = True
            
            # --- NUEVA LÓGICA DE EXCLUSIVIDAD: El robot coge la prioridad ---
            if robot_ocupado_con_cinta is None:
                robot_ocupado_con_cinta = "CINTA_A"
                print(">> [EXCLUSIVIDAD] Robot bloqueado con Cinta A.")
                # Opcional: Si hubiese Cinta B, ordenar pararla.
                # client.publish(TOPIC_MOTOR_B_CMD, "OFF")
                
                # Publicar estado de RoboDK
                client.publish(TOPIC_ROBOT_ESTADO, "TRABAJANDO_A")
                
                # Resetear contador para nueva caja
                contador_bricks = 0 
                
                print(">> Iniciando proceso de bricks en Cinta A.")
            else:
                print(f"!! [EXCLUSIVIDAD Warning] Caja llegó a final A, pero robot ya ocupado con {robot_ocupado_con_cinta}. ESTO NO DEBERÍA PASAR.")

    # Estado del Dispensador de la ESP32 (Lllenando o Listo)
    elif topic == TOPIC_DISPENSADOR_A_ESTADO:
        if payload == "LLENANDO":
            print("[DISP] Dispensador de Cinta A está LLENANDO.")
            dispensador_llenando_a = True
        elif payload == "LISTO":
            print("[DISP] Dispensador de Cinta A ha finalizado y está LISTO.")
            dispensador_llenando_a = False
            # Lógica para reanudar la cinta después del llenado (si es necesario)
            # En tu código original lo hacías al recibir botellas: 3.
            # Aquí lo gestionaremos en la parte de TRABAJO DEL ROBOT.


    # --- ESCENARIO 2: TRABAJO DEL ROBOT (Simulado en RoboDK o vía topic) ---
    
    # Topic simulado para avanzar el trabajo del robot en la simulación
    elif topic == TOPIC_ROBOT_A_TRABAJANDO_CMD:
        
        # 1. Lógica para bricks
        if "BRICK" in payload and robot_ocupado_con_cinta == "CINTA_A":
            contador_bricks += 1
            print(f"[ROBOT] Trabajando en {robot_ocupado_con_cinta}: Brick {contador_bricks}/2 colocado.")
            mover_robot_a_brick(contador_bricks, "CINTA_A") # Simulación

            # ¿Caja llena de bricks?
            if contador_bricks >= 2:
                print(f"[ROBOT] Caja de {robot_ocupado_con_cinta} llena con {contador_bricks} bricks. Finalizando bricks.")
                
                # --- NUEVO: Simular orden de SOLICITAR_LLENADO ---
                # Una vez puestos los bricks, ordenamos el llenado.
                # Publicamos mensaje para nosotros mismos para procesarlo en el siguiente bloque.
                client.publish(TOPIC_ROBOT_A_TRABAJANDO_CMD, "SOLICITAR_LLENADO")
                

        # 2. Lógica para solicitar LLENADO (vía dispensador)
        elif payload == "SOLICITAR_LLENADO" and robot_ocupado_con_cinta == "CINTA_A":
            print("[ROBOT] Caja lista para llenado en Cinta A. Verificando stock...")
            # Simulamos verificación de stock
            if f_verificar_y_actualizar_gdi("Z1", 1.0):
                print("[ROBOT] Stock verificado. Ordenando llenado de líquido a la ESP32.")
                
                # --- ORDENAR A LA ESP32 LLENAR ---
                # Publicamos la orden a la ESP32 para que active el dispensador.
                client.publish(TOPIC_DISPENSADOR_A_CMD, "INICIAR") 
                
                # Pequeña espera para asegurar que la ESP32 reciba y confirme LLENANDO
                time.sleep(0.5) 
                
                if dispensador_llenando_a:
                    # Esperamos bloqueando a que la ESP32 termine (delay() de 2seg en ESP32 + delays de red)
                    print("... Esperando a que la ESP32 confirme fin de llenado ...")
                    while dispensador_llenando_a:
                        time.sleep(0.5)
                        
                    print("[ROBOT] ESP32 confirma fin de llenado.")
                    
                    # --- NUEVO: Simular orden de FINALIZAR_TRABAJO ---
                    client.publish(TOPIC_ROBOT_A_TRABAJANDO_CMD, "TRABAJO_FINALIZADO")
                else:
                    print("!! [ROBOT Error] Orden de llenado enviada pero ESP32 no confirma 'LLENANDO'. Posible desconexión o fallo.")


        # 3. Lógica para FINALIZAR TRABAJO y REANUDAR CINTA
        elif payload == "TRABAJO_FINALIZADO" and robot_ocupado_con_cinta == "CINTA_A":
            print(f"[ROBOT] Caja de {robot_ocupado_con_cinta} totalmente procesada. Liberando robot.")
            
            # --- ORDENAR A LA ESP32 REANUDAR LA CINTA ---
            # Mandamos avanzar a la cinta que acaba de terminar
            client.publish(TOPIC_MOTOR_A_CMD, "ON") 
            
            # Si hubiese Cinta B, opcionalmente reanudarla
            # client.publish(TOPIC_MOTOR_B_CMD, "ON") 
            
            # --- NUEVA LÓGICA DE EXCLUSIVIDAD: Liberar bloqueo ---
            robot_ocupado_con_cinta = None
            print(">> [EXCLUSIVIDAD] Robot Liberado.")
            
            # Publicar estado de RoboDK
            client.publish(TOPIC_ROBOT_ESTADO, "ESPERANDO")
            
            # Resetear variables de sensores locales para la siguiente caja
            caja_en_final_carrera_a = False
            caja_en_barrera_a = False
            contador_bricks = 0 
            
            print(">> Sistema listo para nueva caja.")


# --- MQTT SETUP (Igual que en ESP32, no tocar si no es necesario) ---
print("--- Iniciando Script de Control Central RoboDK ---")

# Crear cliente MQTT
client = mqtt.Client()

# Configurar autenticación (obligatorio para el broker UPV)
client.username_pw_set(MQTT_USER, MQTT_PASS)

# Asignar callbacks
client.on_connect = on_connect
client.on_message = on_message

# Conectar al broker
try:
    print(f"[MQTT] Intentando conectar a: 'mqtt://{MQTT_BROKER}:{MQTT_PORT}' con usuario: '{MQTT_USER}' ...")
    client.connect(MQTT_BROKER, MQTT_PORT)
except Exception as e:
    print(f"[MQTT Error] Error al conectar: {e}")
    sys.exit(1)

# --- BUCLE PRINCIPAL DE SIMULACIÓN ---
print("[Main] Sistema activo y loop MQTT iniciado.")

# --- BUCLE BLOQUEANTE DE MQTT (obligatorio, loop_forever() bloquea el script) ---
client.loop_forever() 
