#config.py
import yaml
import os
import sys

def load_config(filepath="config.yaml"):
    if not os.path.exists(filepath):
        print(f"[CRITICAL] Configuration file '{filepath}' not found!")
        sys.exit(1)

    with open(filepath, "r") as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(f"[CRITICAL] Error parsing YAML file: {exc}")
            sys.exit(1)

app_config = load_config("secret.yaml")


MQTT_HOST = app_config['mqtt']['host']
MQTT_PORT = app_config['mqtt']['port']
TELEMETRY_TOPIC = app_config['topics']['telemetry']
ANOMALY_TOPIC = app_config['topics']['anomaly']
RUL_TOPIC = app_config['topics']['rul']


TRITON_URL = app_config['triton']['url']
ANOMALY_MODEL = app_config['triton']['anomaly_model']
RUL_MODEL = app_config['triton']['rul_model']


AD_FREQ_SECONDS = app_config['ai_settings']['ad_freq_seconds']
LSTM_FREQ_SECONDS = app_config['ai_settings']['lstm_freq_seconds']
SEQ_LEN = app_config['ai_settings']['seq_len']
FAILURE_THRESHOLD = app_config['ai_settings']['failure_threshold']
FORECAST_STEPS = app_config['ai_settings']['forecast_steps']
STEP_INTERVAL_DAYS = app_config['ai_settings']['step_interval_days']


UNIT_ID = app_config['system']['unit_id']
DATA_DELAY = app_config['system']['data_generation_delay']
MAX_ROWS = app_config['system']['max_parquet_rows']
GEN_PATH_DIR = app_config['paths']['generated_dataset']
PRED_PATH_DIR = app_config['paths']['predicted_dataset']
INPUT_SCALER_PATH = app_config['paths']['input_scaler']
OUTPUT_SCALER_PATH = app_config['paths']['output_scaler']