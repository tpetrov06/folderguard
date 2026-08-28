import os
from pathlib import Path
import json
import uuid

DEFAULT_CONFIG = {
    "settings": {
        "relock_timeout_minutes": 5,
        "match_tolerance": 0.5,
        "auth_attempts": 3,
    },
    "protected_folders":{}
}

def app_data_dir():
    base = os.getenv("LOCALAPPDATA")
    folder = Path(base) / "folderguard"
    folder.mkdir(parents=True, exist_ok=True)
    return folder

def config_path():
    return app_data_dir() / "config.json"

def save_config(cfg):
    with open(config_path(), "w") as f:
        json.dump(cfg, f, indent=2)

def load_config():
    if not config_path().exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    with open(config_path(), "r") as f:
        cfg = json.load(f)

    for key, value in DEFAULT_CONFIG["settings"].items():
        cfg["settings"].setdefault(key, value)

    return cfg

def new_id():
    return uuid.uuid4().hex[:12]

def face_data_path():
    return app_data_dir() / "face_data.bin"
