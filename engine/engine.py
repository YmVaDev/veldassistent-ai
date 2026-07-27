
import cv2
from storage.database import Database
from domain.photo import Photo
from utils.photo_utils import get_photo_timestamp
from storage.archive import archive_photo

API_VERSION = "1.0"

class Engine:

    def __init__(self):
        self.db = Database()
        self.models = []

    def add_model(self, model):
        model.database_id = self.db.sync_model(model)
        self.models.append(model)

    def process(self, src_path):
        objects = []
        detections = []
        observation = None

        for model in self.models:

            result = model.process(src_path)

            if observation is None:
                observation = result["observation"]

            detections.extend(result["detections"])
            objects.extend(result["objects"])

        camera_id = self.db.get_or_create_camera(
            "Ranger",
            "Oostakkerbos"
        )

        image = cv2.imread(src_path)
        height, width = image.shape[:2]

        photo = Photo(
            camera_id=camera_id,
            relative_path=src_path.replace("\\", "/"),
            width=width,
            height=height,
            taken_at=get_photo_timestamp(src_path)
        )

        self.db.save_photo(photo)         

        for observation in objects:

            observation.photo = photo

            self.db.save_observation(observation)

            for prediction in observation.predictions:
                self.db.save_prediction(
                    observation.id,
                    prediction
                )

        new_path = archive_photo(src_path)

        photo.relative_path = new_path

        self.db.update_photo(photo)

        return {
            "success": True,
            "api_version": API_VERSION,
            "observation": observation,
            "summary": {
                "count": len(detections)
            },
            "detections": detections,
            "objects": objects
        }