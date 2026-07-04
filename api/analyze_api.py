
import sys
sys.path.append("/opt/oostakkerbos")
import models.birds.model as model
import json
from pathlib import Path
from PIL import Image

def analyze(photo_path):

    img = Image.open(photo_path)

    result = model.predict(photo_path)

    return result


if __name__ == "__main__":

    UPLOAD_DIR = Path("/home/oostakkerbos/incoming")

    photos = list(UPLOAD_DIR.glob("*.jpg"))

    if not photos:
        print("Geen foto's gevonden.")
        exit()

    result = analyze(photos[0])

    print(json.dumps(result, indent=4))
