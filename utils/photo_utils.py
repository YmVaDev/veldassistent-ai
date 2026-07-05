
from pathlib import Path
from datetime import datetime

def get_photo_timestamp(path):

    try:
        timestamp = Path(path).stat().st_mtime
        return datetime.fromtimestamp(timestamp)
    except Exception:
        return datetime.now()