#full_client.py
import tritonclient.http as httpclient
import cudf
import cupy as cp
import joblib
import time
import json
import os
import paho.mqtt.client as mqtt
import schedule
import pandas as pd
from datetime import datetime, timedelta
from collections import deque
from sklearn.exceptions import InconsistentVersionWarning
import warnings

from config import (
    MQTT_HOST, MQTT_PORT, ANOMALY_TOPIC, RUL_TOPIC,
    TRITON_URL, ANOMALY_MODEL, RUL_MODEL,
    AD_FREQ_SECONDS, LSTM_FREQ_SECONDS, SEQ_LEN,
    FAILURE_THRESHOLD, FORECAST_STEPS, STEP_INTERVAL_DAYS,
    GEN_PATH_DIR, PRED_PATH_DIR, UNIT_ID,
    INPUT_SCALER_PATH, OUTPUT_SCALER_PATH
)

warnings.simplefilter("ignore", InconsistentVersionWarning)

print(f"[INFO] AI Client connecting to MQTT Broker at {MQTT_HOST}...")
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
try:
    mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
    mqtt_client.loop_start()
except Exception as e:
    print(f"[CRITICAL] AI failed to connect to MQTT: {e}")

anomaly_inputs = ['rpm', 'unit1_motor_voltage_float', 'unit1_motor_current_float', 'unit1_motor_power', 'unit1_flow', 'unit1_motor_temperature']
lstm_input = anomaly_inputs + [ 'anomaly_score' ]
anomaly_score_window = deque(maxlen=SEQ_LEN)

client = httpclient.InferenceServerClient(url=TRITON_URL)
input_scaler = joblib.load(INPUT_SCALER_PATH)
output_scaler = joblib.load(OUTPUT_SCALER_PATH)


os.makedirs(PRED_PATH_DIR, exist_ok=True)

def get_dynamic_paths(date=None):
    if date is None: date = datetime.now()
    date_str = date.strftime("%Y-%m-%d")
    return f"{GEN_PATH_DIR}/{date_str}_{UNIT_ID}.parquet", f"{PRED_PATH_DIR}/{date_str}_Predicted.parquet"

# def predict_anomalies(df: cudf.DataFrame) -> cudf.DataFrame:
#     df_input = df[anomaly_inputs].to_pandas().values.astype(cp.float32)
#     triton_input = httpclient.InferInput("input", df_input.shape, datatype="FP32")
#     triton_input.set_data_from_numpy(df_input)
#     try:
#         response = client.infer(model_name=ANOMALY_MODEL, inputs=[triton_input])
#         return cudf.DataFrame({
#             "anomaly_score": response.as_numpy("scores").flatten(),
#             "anomaly": response.as_numpy("label").flatten()
#         })
#     except Exception as e:
#         print(f"[ERROR] Triton Inference Failed: {e}")
#         return cudf.DataFrame({"anomaly_score": [cp.nan] * len(df), "anomaly": [cp.nan] * len(df)})

import random

def predict_anomalies(df: cudf.DataFrame) -> cudf.DataFrame:

    print("[INFO] Generating simulated anomaly score (Triton Bypass)")


    simulated_score = random.uniform(0.1, 0.4)


    df_pred = cudf.DataFrame(columns=["anomaly_score","anomaly"])
    df_pred["anomaly_score"] = cudf.Series([simulated_score] * len(df))
    df_pred["anomaly"] = cudf.Series([0] * len(df))

    return df_pred

def run_prediction_once():
    GEN_PATH, PRED_PATH = get_dynamic_paths()
    try:
        if not os.path.exists(GEN_PATH):
            print(f"[WARN] Waiting for generator to create {GEN_PATH}...")
            return
        df_all = cudf.read_parquet(GEN_PATH)
    except Exception as e:
        print(f"[ERROR] Could not read Generated Data: {e}")
        return

    now = datetime.now()
    df_all["timestamp"] = cudf.to_datetime(df_all["timestamp"], format="%d-%m-%Y %H:%M:%S", dayfirst=True)


    lookback = now - timedelta(seconds=AD_FREQ_SECONDS + 2)
    recent_rows = df_all[(df_all["timestamp"] >= lookback) & (df_all["timestamp"] <= now)].sort_values("timestamp").tail(SEQ_LEN)

    if len(recent_rows) == 0:
        print(f"[WARN] No recent rows found in {AD_FREQ_SECONDS}s window. Max timestamp in file: {df_all['timestamp'].max()}")
        return


    pandas_recent = recent_rows[anomaly_inputs].to_pandas()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        scaled_pandas = input_scaler.transform(pandas_recent)

    normed = cudf.DataFrame(scaled_pandas, columns=anomaly_inputs)
    mean_norm_df = cudf.DataFrame([normed.mean()])
    mean_norm_df.columns = anomaly_inputs

    predicted = predict_anomalies(mean_norm_df)


    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        scaled_score_pandas = output_scaler.transform(predicted[["anomaly_score"]].to_pandas())

    predicted[['anomaly_score']] = scaled_score_pandas

    if predicted['anomaly_score'].isnull().any():
        print("[WARN] Triton returned NaN. Check if Model is loaded.")
        return

    df_to_pub = cudf.concat([mean_norm_df.reset_index(drop=True), predicted.reset_index(drop=True)], axis=1)
    df_to_pub["timestamp"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")


    try:
        if os.path.exists(PRED_PATH) and os.path.getsize(PRED_PATH) > 0:
            df_existing = cudf.read_parquet(PRED_PATH)
            df_final = cudf.concat([df_existing, df_to_pub], ignore_index=True)
            df_final.to_parquet(PRED_PATH)
        else:
            df_to_pub.to_parquet(PRED_PATH)


        pub_dict = df_to_pub.to_pandas().iloc[0].to_dict()
        mqtt_client.publish(ANOMALY_TOPIC, json.dumps(pub_dict))
        print(f"[{pub_dict['timestamp']}] Anomaly Checked! Score: {pub_dict['anomaly_score']:.4f} | Saved to Parquet")

    except Exception as e:
        print(f"[ERROR] Failed to save/publish prediction: {e}")

def run_lstm_once():
    _, PRED_PATH = get_dynamic_paths()
    if not os.path.exists(PRED_PATH):
        print("[INFO] LSTM: Waiting for Anomaly Check to create the first prediction file...")
        return

    try:
        df_pred = cudf.read_parquet(PRED_PATH)
        required_rows = FORECAST_STEPS * SEQ_LEN
        if len(df_pred) < required_rows:
            print(f"[WARN] LSTM: Accumulating data... ({len(df_pred)}/{required_rows} rows)")
            return

        input_data = df_pred[lstm_input].to_cupy().astype(cp.float32)[-required_rows:]
        batch_sequences = cp.stack([input_data[i : i + SEQ_LEN] for i in range(0, required_rows, SEQ_LEN)])

        triton_input = httpclient.InferInput("input", batch_sequences.shape, datatype="FP32")
        triton_input.set_data_from_numpy(batch_sequences.get())

        raw_output = client.infer(model_name=RUL_MODEL, inputs=[triton_input]).as_numpy("dense_9")
        predictions = cp.asarray(raw_output.flatten())

        failure_index = cp.where(predictions < FAILURE_THRESHOLD)[0]
        rul_message = round(float(failure_index[0]) * STEP_INTERVAL_DAYS, 2) if len(failure_index) > 0 else 7.0

        timestamp_str = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        mqtt_client.publish(RUL_TOPIC, json.dumps({"rul": rul_message, "timestamp": timestamp_str}))

        print(f"[{timestamp_str}] RUL Predicted: {rul_message} days.")

    except Exception as e:
        print(f"[ERROR] LSTM Process Failed: {e}")

def main():
    print(f"[INFO] Anomaly check scheduled every {AD_FREQ_SECONDS}s.")
    print(f"[INFO] LSTM RUL check scheduled every {LSTM_FREQ_SECONDS}s.")

    schedule.every(AD_FREQ_SECONDS).seconds.do(run_prediction_once)

    # Wait longer before first LSTM attempt to allow Anomaly to create the file
    time.sleep(10)
    schedule.every(LSTM_FREQ_SECONDS).seconds.do(run_lstm_once)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping AI Client...")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

if __name__ == "__main__":
    main()

