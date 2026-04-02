#rul_days.py

import time
from datetime import datetime
import pandas as pd
import schedule

from influxdb_client_3 import InfluxDBClient3, Point

# --- CONFIGURATION ---
INFLUX_HOST = "http://10.0.0.17:8181"
INFLUX_TOKEN = "apiv3_380fh-u2dKAxzrnE-o7ZYwKvA6dURE2tCoLXnUYIjP_osSXH1gIExggakMOGvF74X-UbJA6yRukw6kkmp1Y8kA"
INFLUX_DB = "predictive_maintenance"


MAX_RUL_DAYS = 100.0           # Maximum possible RUL
ANOMALY_THRESHOLD = 0.5        # Threshold where degradation penalty starts accumulating
PENALTY_FACTOR = 0.05          # Days subtracted from RUL per 30-sec tick above threshold
PENALTY_RECOVERY = 0.01        # Days recovered per tick if anomaly score goes back down
TREND_WINDOW_HOURS = 1         # Look at the last 1 hour of data to build the penalty state
MOVING_AVG_POINTS = 5          # Number of points to average (ignores short random spikes)
CALC_FREQ_SECONDS = 60         # Calculate RUL every 60 seconds

def calculate_rul():
    try:
        client = InfluxDBClient3(host=INFLUX_HOST, token=INFLUX_TOKEN, database=INFLUX_DB)
    except Exception as e:
        print(f"[ERROR] Could not connect to InfluxDB: {e}")
        return

    query = f"SELECT * FROM predicted_anomalies WHERE time >= now() - INTERVAL '{TREND_WINDOW_HOURS} hour' ORDER BY time"

    try:
        table = client.query(query=query, language="sql")
        df = table.to_pandas()
    except Exception as e:
        print(f"[ERROR] Query failed: {e}")
        return

    if df.empty or len(df) < MOVING_AVG_POINTS:
        print("[WARN] Not enough anomaly data to calculate RUL yet. Waiting for more data...")
        return

    df = df.dropna(subset=['anomaly_score']).copy()
    df['anomaly_score'] = df['anomaly_score'].clip(0.0, 1.0)

    df['smoothed_score'] = df['anomaly_score'].rolling(window=MOVING_AVG_POINTS, min_periods=1).mean()

    current_penalty = 0.0
    for score in df['smoothed_score']:
        if score > ANOMALY_THRESHOLD:
            current_penalty += PENALTY_FACTOR
        else:
            current_penalty = max(0.0, current_penalty - PENALTY_RECOVERY)

    latest_smoothed_score = df['smoothed_score'].iloc[-1]
    current_health = 1.0 - latest_smoothed_score

    base_rul = current_health * MAX_RUL_DAYS
    final_rul = base_rul - current_penalty

    final_rul = max(0.0, min(final_rul, MAX_RUL_DAYS))

    clean_rul = int(round(final_rul))

    point = (
        Point("rul_predictions")
        .field("rul_days", float(clean_rul))
        .field("current_health", float(current_health))
        .field("accumulated_penalty", float(current_penalty))
    )

    try:
        client.write(record=point)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] RUL Calculated: {clean_rul} days | Health: {current_health:.2f} | Penalty: {current_penalty:.2f} | Saved to InfluxDB")
    except Exception as e:
        print(f"[ERROR] Failed to write RUL to InfluxDB: {e}")


def main():
    print(f"[INFO] RUL Calculator Started. Running every {CALC_FREQ_SECONDS} seconds...")
    schedule.every(CALC_FREQ_SECONDS).seconds.do(calculate_rul)

    calculate_rul()

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] RUL Calculator stopped.")

if __name__ == "__main__":
    main()