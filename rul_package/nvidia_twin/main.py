# main.py
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib

# ---- Columns (must match your pipeline) ----
anomaly_inputs = [
    'rpm', 'unit1_motor_voltage_float',
    'unit1_motor_current_float', 'unit1_motor_power',
    'unit1_flow', 'unit1_motor_temperature'
]

# ---- Placeholder min/max ranges (tune as needed) ----
RANGES = {
    'rpm': (1000, 1800),
    'unit1_motor_voltage_float': (220.0, 240.0),
    'unit1_motor_current_float': (1.5, 3.5),
    'unit1_motor_power': (400.0, 900.0),
    'unit1_flow': (10.0, 45.0),
    'unit1_motor_temperature': (40.0, 80.0),
}

# Build a tiny DataFrame with the declared mins and maxes so MinMaxScaler
# learns exact bounds (min->0, max->1) for each feature.
mins = {k: RANGES[k][0] for k in anomaly_inputs}
maxs = {k: RANGES[k][1] for k in anomaly_inputs}
df_bounds = pd.DataFrame([mins, maxs])  # shape (2, n_features)

# 1) Input scaler
input_scaler = MinMaxScaler(feature_range=(0.0, 1.0))
input_scaler.fit(df_bounds[anomaly_inputs])
joblib.dump(input_scaler, "minmax_scaler.pkl")
print("[INFO] Saved input scaler -> minmax_scaler.pkl")

# 2) Output scaler (for anomaly_score in [0,1])
# We use two points [0.0], [1.0] so the scaler becomes identity over 0..1
df_out_bounds = pd.DataFrame({"anomaly_score": [0.0, 1.0]})
output_scaler = MinMaxScaler(feature_range=(0.0, 1.0))
output_scaler.fit(df_out_bounds[["anomaly_score"]])
joblib.dump(output_scaler, "minmax_scaler_output.pkl")
print("[INFO] Saved output scaler -> minmax_scaler_output.pkl")