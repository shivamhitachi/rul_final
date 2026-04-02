#data_generator.py
import threading
import time
from datetime import datetime

import numpy as np
import pandas as pd


from influxdb_client_3 import InfluxDBClient3, Point

unit1 = [
    'timestamp', 'rpm',
    'unit1_motor_voltage_float', 'unit1_motor_current_float',
    'unit1_motor_power', 'unit1_motor_vibration',
    'unit1_inlet_pressure', 'unit1_outlet_pressure',
    'unit1_tank_level', 'unit1_flow',
    'unit1_motor_temperature', 'unit1_pump_temperature',
    'unit1_motor_status'
]

# --------- Oscillator Function ----------
def oscillate(base, amplitude, freq, noise_level=0.05, step=0):
    return np.around(base + amplitude * np.sin(2 * np.pi * freq * step) + np.random.normal(0, noise_level), 2)

# --------- Data Generator Function ----------
def generate_synthetic_data(
        influx_host="http://10.0.0.17:8181",
        token="apiv3_BEmIrhG-7CalJC1yN-tD6l6DecxQ68rxqtspX4bW44CJgmaIVwYFdMzZ-MvJS2a5QgjJUkPbAW-iKO0enW2JEQ",
        database="predictive_maintenance",
        delay=5,
        loop_forever=True,
        max_steps=None,
        stop_event=None
):
    step = 0


    try:
        client = InfluxDBClient3(host=influx_host, token=token, database=database)
        print("[INFO] Connected to InfluxDB v3 successfully!")
    except Exception as e:
        print(f"[ERROR] Could not connect to InfluxDB: {e}")
        return

    try:
        while not (stop_event and stop_event.is_set()):
            start_time = time.perf_counter()


            rpm = oscillate(1400, 200, 0.2, 0.5, step)
            u1_voltage = oscillate(230, 5, 0.005, 0.5, step)
            u1_current = oscillate(2.5, 0.8, 0.007, 0.2, step)
            u1_power = np.around(u1_voltage * u1_current + np.random.normal(0, 1), 2)
            u1_inlet_pressure = oscillate(2.0, 0.5, 0.01, 0.1, step)
            u1_outlet_pressure = np.around(u1_inlet_pressure + oscillate(0.5, 0.2, 0.01, 0.05, step), 2)
            u1_flow = np.around(u1_outlet_pressure * 10 + np.random.normal(0, 1), 2)
            u1_tank = np.around(500 + 50 * np.sin(2 * np.pi * step / 300), 2)
            u1_motor_vib = np.around(2.0 + 0.5 * u1_current + np.random.normal(0, 0.1), 2)
            u1_pump_temp = np.around(40 + 10 * u1_current + np.random.normal(0, 1), 2)
            u1_motor_temp = np.around(u1_pump_temp - 5, 2)


            point = (
                Point("raw_sensors")
                .field("rpm", float(rpm))
                .field("voltage", float(u1_voltage))
                .field("current", float(u1_current))
                .field("power", float(u1_power))
                .field("motor_vibration", float(u1_motor_vib))
                .field("inlet_pressure", float(u1_inlet_pressure))
                .field("outlet_pressure", float(u1_outlet_pressure))
                .field("tank_level", float(u1_tank))
                .field("flow", float(u1_flow))
                .field("motor_temperature", float(u1_motor_temp))
                .field("pump_temperature", float(u1_pump_temp))
                .field("motor_status", int(1))
            )


            try:
                client.write(record=point)
                saved_to = "InfluxDB v3"
            except Exception as e:
                saved_to = f"Failed: {e}"

            loop_time = time.perf_counter() - start_time
            print(f"Saved to: {saved_to} | Loop time: {loop_time:.3f}s")

            step += 1
            time.sleep(delay)

    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user.")


if __name__ == "__main__":
    print("[INFO] Starting Data Generator...")
    generate_synthetic_data()