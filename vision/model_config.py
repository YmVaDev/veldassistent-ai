
import json

from config import MODEL_DIR

def load_model_config(model_name):

    config_path = MODEL_DIR / model_name / "config.json"

    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)

    return config