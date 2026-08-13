
from datetime import datetime

class Photo:

    def __init__(
        self,
        camera_id,
        relative_path,
        taken_at=None,
        width=None,
        height=None,
        world=None,
        id=None,
        created_at=None
    ):

        self.id = id

        self.camera_id = camera_id

        self.relative_path = relative_path

        self.taken_at = taken_at

        self.width = width

        self.height = height

        self.world = world

        self.created_at = created_at or datetime.utcnow()