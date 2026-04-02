import pandas as pd
import numpy as np
import time
from datetime import datetime
import json
import paho.mqtt.client as mqtt
import threading
import os

from config import (
    MQTT_HOST, MQTT_PORT, TELEMETRY_TOPIC,
    DATA_DELAY, MAX_ROWS, UNIT_ID, GEN_PATH_DIR
)

unit1_columns = [
    'timestamp', 'rpm', 'unit1_motor_voltage_float', 'unit1_motor_current_float',
    'unit1_motor_power', 'unit1_motor_vibration', 'unit1_inlet_pressure',
    'unit1_outlet_pressure', 'unit1_tank_level', 'unit1_flow',
    'unit1_motor_temperature', 'unit1_pump_temperature', 'unit1_motor_status'
]

stop_event = threading.Event()

print(f"[INFO] Data Generator connecting to MQTT Broker at {MQTT_HOST}...")

# FIX: Removed the MQTT Deprecation Warning
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

try:
    mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
    mqtt_client.loop_start()
except Exception as e:
    print(f"[CRITICAL] Generator failed to connect to MQTT: {e}")

def oscillate(base, amplitude, freq, noise_level=0.05, step=0):
    return np.around(base + amplitude * np.sin(2 * np.pi * freq * step) + np.random.normal(0, noise_level), 2)

def generate_synthetic_data(stop_event=None):
    df_synthetic = pd.DataFrame(columns=unit1_columns)
    step = 0
    os.makedirs(GEN_PATH_DIR, exist_ok=True)

    try:
        while not stop_event.is_set():
            timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            rpm = oscillate(1400, 200, 0.2, 0.5, step)
            u1_voltage = oscillate(230, 5, 0.005, 0.5, step)
            u1_current = oscillate(2.5, 0.8, 0.007, 0.2, step)
            u1_power = np.around(u1_voltage * u1_current + np.random.normal(0, 1), 2)
            u1_inlet_pressure = oscillate(2.0, 0.5, 0.01, 0.1, step)
            u1_outlet_pressure = np.around(u1_inlet_pressure + oscillate(0.5, 0.2, 0.01, 0.05, step), 2)
            u1_flow = np.around(u1_outlet_pressure * 10 + np.random.normal(0, 1), 2)
            u1_tank = np.around(500 + 50 * np.sin(2 * np.pi * step / 300), 2)
            u1_motor_vib = np.around(2.0 + 0.5 * u1_current + np.random.normal(0, 0.1), 2)
            u1_pump_vib = np.around(u1_motor_vib + np.random.normal(0, 0.05), 2)
            u1_motor_temp = np.around(40 + 10 * u1_current + np.random.normal(0, 1), 2)
            u1_pump_temp = np.around(u1_motor_temp + 5 + np.random.normal(0, 1), 2)
            motor1_status = True

            row = [
                timestamp, int(rpm), float(u1_voltage), float(u1_current),
                float(u1_power), float(u1_pump_vib), float(u1_inlet_pressure),
                float(u1_outlet_pressure), float(u1_tank), float(u1_flow),
                float(u1_motor_temp), float(u1_pump_temp), motor1_status
            ]

            new_row_df = pd.DataFrame([row], columns=unit1_columns)

            # FIX: Removed the Pandas concat FutureWarning
            if df_synthetic.empty:
                df_synthetic = new_row_df
            else:
                df_synthetic = pd.concat([df_synthetic, new_row_df], ignore_index=True)

            if len(df_synthetic) > MAX_ROWS:
                df_synthetic = df_synthetic.tail(MAX_ROWS)

            date_str = datetime.now().strftime("%Y-%m-%d")
            df_synthetic.to_parquet(f"{GEN_PATH_DIR}/{date_str}_{UNIT_ID}.parquet", index=False)

            payload = json.dumps(dict(zip(unit1_columns, row)))
            mqtt_client.publish(TELEMETRY_TOPIC, payload)

            print(f"[{timestamp}]  PUBLISHED: RPM={int(rpm)} | Current={u1_current}A | Temp={u1_motor_temp}°C | Vib={u1_motor_vib}mm/s")

            step += 1
            time.sleep(DATA_DELAY)

    except Exception as e:
        print(f"[ERROR] Generator thread crashed: {e}")

def main():
    generator_thread = threading.Thread(target=generate_synthetic_data, kwargs={"stop_event": stop_event})
    generator_thread.start()
    try:
        while generator_thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping Data Generator...")
        stop_event.set()
        generator_thread.join()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

if __name__ == "__main__":
    main()