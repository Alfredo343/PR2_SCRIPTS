import paho.mqtt.client as mqtt
import psycopg2
import time

# --- CONFIGURACIÓN MQTT (Según Memoria) ---
BROKER = "broker.emqx.io"
TOPIC_NIVEL = "emqx/ESP32_S3/cont_zumo"

# --- CONFIGURACIÓN BD (Según proyectoSQL.sql) ---
DB_CONFIG = {
    "host": "localhost",
    "database": "proyectos2", # Asegúrate de que este sea el nombre real de tu BD
    "user": "usuario_gdi",
    "password": "tu_password",
    "options": "-c search_path=proyecto" # Para usar el esquema 'proyecto' automáticamente
}

def f_verificar_y_actualizar_gdi(id_tanque, cantidad_necesaria):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 1. Consultar volumen actual (Tabla: TanqueDeZumo según SQL)
        cur.execute("SELECT volumen FROM TanqueDeZumo WHERE idZumo = %s", (id_tanque,))
        row = cur.fetchone()
        
        if row:
            volumen_actual = row[0]
            # 2. Verificar si hay suficiente para la operación
            if volumen_actual >= cantidad_necesaria:
                nuevo_volumen = volumen_actual - cantidad_necesaria
                cur.execute("UPDATE TanqueDeZumo SET volumen = %s WHERE idZumo = %s", (nuevo_volumen, id_tanque))
                conn.commit()
                
                # 3. Lógica de Alarma según PDF:
                # "Baja cantidad de zumo" -> mensaje "1" (encendido LED) si es poco.
                # Definimos un umbral crítico (ej. 50 unidades)
                umbral_critico = 50.0
                estado_alarma = "1" if nuevo_volumen < umbral_critico else "0"
                
                # Publicar estado a la ESP32-S3
                client.publish(TOPIC_NIVEL, estado_alarma)
                print(f"Tanque {id_tanque}: Volumen restante {nuevo_volumen}. Alarma: {estado_alarma}")
                
                resultado = True
            else:
                # Si no hay suficiente zumo para rellenar, avisamos (Alarma "1")
                client.publish(TOPIC_NIVEL, "1")
                print(f"Tanque {id_tanque}: Zumo insuficiente para rellenar.")
                resultado = False
        else:
            print(f"Error: Tanque {id_tanque} no encontrado.")
            resultado = False
            
        cur.close()
        conn.close()
        return resultado

    except Exception as e:
        print(f"Error de base de datos: {e}")
        return False

# --- CLIENTE MQTT ---
client = mqtt.Client()
client.connect(BROKER, 1883, 60)
client.loop_start()
