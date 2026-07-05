
from storage.database import Database
from domain.photo import Photo
from domain.bounding_box import BoundingBox
from domain.observation import Observation
from domain.prediction import Prediction

db = Database()

camera_id = db.get_or_create_camera(
    "Ranger",
    "Oostakkerbos"
)

photo = Photo(
    camera_id=camera_id,
    relative_path="incoming/test.jpg"
)

db.save_photo(photo)

box = BoundingBox(
    100,
    200,
    300,
    400
)

observation = Observation(
    photo=photo,
    model_id=1,
    box=box,
    crop_path="crops/test.jpg"
)

db.save_observation(observation)

prediction = Prediction(
    species="Hawfinch",
    score=96.4,
    rank=1
)

db.save_prediction(
    observation.id,
    prediction
)

print("Photo ID:", photo.id)
print("Observation ID:", observation.id)