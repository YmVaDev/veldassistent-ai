
from pathlib import Path

UPLOAD_DIR = Path("/home/oostakkerbos/uploads")

print("🌳 Oostakkerbos AI Core\n")

if not UPLOAD_DIR.exists():
    print("❌ Uploadmap bestaat niet.")
    exit()

print("📂 Uploadmap gevonden.\n")

photos = list(UPLOAD_DIR.glob("*.jpg"))

print(f"📸 {len(photos)} JPG-bestanden gevonden.\n")

