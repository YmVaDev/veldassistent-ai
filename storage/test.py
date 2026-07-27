
from storage.database import Database
from config import MEDIA_URL

db = Database()

image = db.get_observation_image(1)

print(MEDIA_URL + image["crop_path"])

