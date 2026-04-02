#full_client.py
import time
from datetime import datetime
import numpy as np
import pandas as pd
import schedule

# Import the InfluxDB v3 Client
from influxdb_client_3 import InfluxDBClient3, Point

# ----------------- Configuration -----------------
INFLUX_HOST = "http://10.0.0.17:8181"
INFLUX_TOKEN = "apiv3_BEmIrhG-7CalJC1yN-tD6l6DecxQ68rxqtspX4bW44CJgmaIVwYFdMzZ-MvJS2a5QgjJUkPbAW-iKO0enW2JEQ"
INFLUX_DB = "predictive_maintenance"
AD_FREQ_SECONDS = 30


anomaly_inputs = [
    'rpm', 'voltage', 'current', 'power',
    'flow', 'motor_temperature'
]

def run_prediction_once():

    try:
        client = InfluxDBClient3(host=INFLUX_HOST, token=INFLUX_TOKEN, database=INFLUX_DB)
    except Exception as e:
        print(f"[ERROR] Could not connect to InfluxDB: {e}")
        return

    query = "SELECT * FROM raw_sensors WHERE time >= now() - INTERVAL '1 minute' ORDER BY time"

    try:
        table = client.query(query=query, language="sql")
        df = table.to_pandas()
    except Exception as e:
        print(f"[ERROR] Query failed: {e}")
        return

    if df.empty:
        print("[WARN] No recent data found in the database. Is data_generator.py running?")
        return

    df = df.dropna(subset=anomaly_inputs)

    if len(df) < 2:
        print("[WARN] Not enough data points in the last minute to calculate anomaly. Waiting...")
        return

    recent_rows = df.tail(6).copy()

    eps = 1e-6
    mu = recent_rows[anomaly_inputs].mean()
    sigma = recent_rows[anomaly_inputs].std(ddof=0).replace(0.0, eps)

    z_window = (recent_rows[anomaly_inputs] - mu) / sigma
    z_latest = z_window.iloc[-1]

    mean_abs_z = float(z_latest.abs().mean())


    Z_ANOM_THRESHOLD = 2.0
    anomaly_score = max(0.0, min(1.0, mean_abs_z / Z_ANOM_THRESHOLD))


    ANOMALY_CUTOFF = 0.5
    anomaly_flag = int(anomaly_score >= ANOMALY_CUTOFF)

    point = (
        Point("predicted_anomalies")
        .field("anomaly_score", float(anomaly_score))
        .field("anomaly", int(anomaly_flag))
    )

    try:
        client.write(record=point)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Anomaly Score: {anomaly_score:.3f} | Flag: {anomaly_flag} | Saved to InfluxDB")
    except Exception as e:
        print(f"[ERROR] Failed to write prediction to InfluxDB: {e}")


def main():
    print(f"[INFO] Anomaly Detection Client Started. Running every {AD_FREQ_SECONDS} seconds...")

    schedule.every(AD_FREQ_SECONDS).seconds.do(run_prediction_once)

    run_prediction_once()

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Client stopped by user.")

if __name__ == "__main__":
    main()