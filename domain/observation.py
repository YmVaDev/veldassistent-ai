
from datetime import datetime
from domain.bounding_box import BoundingBox

class Observation:

    def __init__(
        self,
        photo,
        model_id,
        box: BoundingBox,
        crop_path=None,
        id=None,
        status="pending",
        created_at=None
    ):

        self.id = id

        self.photo = photo

        self.model_id = model_id

        self.box = box

        self.crop_path = crop_path

        self.status = status

        self.created_at = created_at or datetime.utcnow()

        # Hier komen later de Top-5 voorspellingen
        self.predictions = []

        # Hier komt later de menselijke validatie
        self.validation = None