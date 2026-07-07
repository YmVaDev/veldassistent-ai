
from pathlib import Path
import os

API_VERSION = "1.0.0"
APP_NAME = "Veldassistent 24/7"

BASE_URL = "https://oostakkerbos.be"
BASE_DIR = Path(__file__).resolve().parent

MODEL_DIR = BASE_DIR / "models"
INCOMING_DIR = BASE_DIR / "incoming"
ARCHIVE_DIR = BASE_DIR / "archive"
CROP_DIR = BASE_DIR / "crops"
DATABASE_PATH = BASE_DIR / "veldassistent.db"
LOG_DIR = BASE_DIR / "logs"

REFERENCE_IMAGE = BASE_DIR / "references" / "illustration_style.png"
