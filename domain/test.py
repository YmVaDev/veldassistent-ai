
from domain.photo import Photo
from domain.bounding_box import BoundingBox
from domain.observation import Observation

photo = Photo(
    camera_id=1,
    relative_path="incoming/test.jpg"
)

box = BoundingBox(
    100,
    200,
    300,
    500
)

observation = Observation(
    photo=photo,
    model_id=1,
    box=box,
    crop_path="crops/test.jpg"
)

print(observation.box.width)
print(observation.box.height)
print(observation.status)