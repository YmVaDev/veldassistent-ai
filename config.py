
from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

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
GENERATED_SPECIES_DIR = BASE_DIR / "generated" / "species"
GENERATED_SPECIESHABITAT_DIR = BASE_DIR / "generated" / "habitats"
MEDIA_URL = "https://oostakkerbos.be/media/"

ENVIRONMENT = os.getenv(
    "ENVIRONMENT",
    "development"
)

API_PREFIX = "/api/v1"
API_KEY = os.getenv("API_KEY")

SPECIES_MEDIA_URL = MEDIA_URL + "species/"
HABITAT_MEDIA_URL = MEDIA_URL + "habitats/"

# -------------------------
# RTSP configuratie
# -------------------------

RTSP_ENABLED = os.getenv(
    "RTSP_ENABLED",
    "true"
).lower() == "true"

RTSP_URL = os.getenv("RTSP_URL")

RTSP_INTERVAL = 30

RTSP_OUTPUT_DIR = BASE_DIR / "rtsp_frames"


CAMERAS = {
    "ranger": {
        "name": "Ranger",
        "location": "Oostakkerbos",
        "world": "bos",
    },

    "lumus": {
        "name": "Lumus",
        "location": "Tuin",
        "world": "tuin",
    },

}