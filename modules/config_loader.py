import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def load_config():
    config_path = PROJECT_ROOT / "config.json"

    with open(config_path, "r", encoding="utf-8") as file:
        config = json.load(file)

    return config