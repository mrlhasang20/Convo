import json
import logging
import os
from pathlib import Path

SETTINGS_FILE = "settings.json"

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler("image_converter.log"),
            logging.StreamHandler()
        ]
    )

def load_config():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        return {}
    except Exception as e:
        logging.getLogger(__name__).error(f"Error loading config: {str(e)}")
        return {}

def save_config(config):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        logging.getLogger(__name__).error(f"Error saving config: {str(e)}")
        raise

def validate_path(path):
    try:
        return Path(path).exists()
    except Exception:
        return False