
from pathlib import Path

BASE_URL = "https://oostakkerbos.be"
BASE_DIR = Path(__file__).resolve().parent

MODEL_DIR = BASE_DIR / "models"
INCOMING_DIR = BASE_DIR / "incoming"
ARCHIVE_DIR = BASE_DIR / "archive"
CROP_DIR = BASE_DIR / "crops"

DETECTOR_SIZE = 416
CLASSIFIER_SIZE = 384