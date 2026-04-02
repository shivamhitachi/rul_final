import os
from dotenv import load_dotenv

# Load variables from the local .env file
load_dotenv()

def get_required_env(key_name):
    """Fetches an environment variable and crashes intentionally if missing."""
    value = os.getenv(key_name)
    if not value or value.strip() == "":
        raise ValueError(f"[CRITICAL ERROR] Missing required configuration: '{key_name}' in .env file.")
    return value

# Enforce strict requirements with NO defaults
INFLUX_URL = get_required_env("E2CC_INFLUX_URL")
INFLUX_TOKEN = get_required_env("E2CC_INFLUX_TOKEN")
INFLUX_ORG = get_required_env("E2CC_INFLUX_ORG")
INFLUX_DB = get_required_env("E2CC_INFLUX_DB")