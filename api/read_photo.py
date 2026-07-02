from pathlib import Path
from PIL import Image

UPLOAD_DIR = Path("/home/oostakkerbos/incoming")

photos = list(UPLOAD_DIR.glob("*.jpg"))

if not photos:
    print("Geen foto's gevonden.")
    exit()

photo = photos[0]

print(f"Foto gevonden: {photo.name}")

img = Image.open(photo)

print(f"Breedte : {img.width}")
print(f"Hoogte  : {img.height}")
print(f"Formaat : {img.format}")
