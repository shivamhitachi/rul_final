# main.py
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib


anomaly_inputs = [
    'rpm', 'unit1_motor_voltage_float',
    'unit1_motor_current_float', 'unit1_motor_power',
    'unit1_flow', 'unit1_motor_temperature'
]


RANGES = {
    'rpm': (1000, 1800),
    'unit1_motor_voltage_float': (220.0, 240.0),
    'unit1_motor_current_float': (1.5, 3.5),
    'unit1_motor_power': (400.0, 900.0),
    'unit1_flow': (10.0, 45.0),
    'unit1_motor_temperature': (40.0, 80.0),
}


mins = {k: RANGES[k][0] for k in anomaly_inputs}
maxs = {k: RANGES[k][1] for k in anomaly_inputs}
df_bounds = pd.DataFrame([mins, maxs])  # shape (2, n_features)


input_scaler = MinMaxScaler(feature_range=(0.0, 1.0))
input_scaler.fit(df_bounds[anomaly_inputs])
joblib.dump(input_scaler, "minmax_scaler.pkl")
print("[INFO] Saved input scaler -> minmax_scaler.pkl")


df_out_bounds = pd.DataFrame({"anomaly_score": [0.0, 1.0]})
output_scaler = MinMaxScaler(feature_range=(0.0, 1.0))
output_scaler.fit(df_out_bounds[["anomaly_score"]])
joblib.dump(output_scaler, "minmax_scaler_output.pkl")
print("[INFO] Saved output scaler -> minmax_scaler_output.pkl")