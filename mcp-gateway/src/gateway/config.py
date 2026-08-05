import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parents[3] / "config.json"


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())
