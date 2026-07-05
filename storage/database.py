
from pathlib import Path
import sqlite3
import json
from datetime import datetime
from config import BASE_DIR

class Database:

    def __init__(self, db_name="veldassistent.db"):

        self.db_path = Path(db_name)

        self.connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False
        )
        print(self.db_path.resolve())

        self.connection.row_factory = sqlite3.Row

    def cursor(self):
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()

    def get_or_create_model(self, name, category, version=None):

        cursor = self.cursor()

        cursor.execute("""
            SELECT id
            FROM models
            WHERE name = ?
        """, (name,))

        row = cursor.fetchone()

        if row:
            return row["id"]

        cursor.execute("""
            INSERT INTO models
            (
                name,
                category,
                version
            )
            VALUES (?, ?, ?)
        """, (
            name,
            category,
            version
        ))

        self.commit()

        return cursor.lastrowid

    def get_models(self):

        cursor = self.cursor()

        cursor.execute("""
            SELECT *
            FROM models
            ORDER BY id
        """)

        return cursor.fetchall()

    def sync_model(self, model):

        model_id = self.get_or_create_model(
            model.config["id"],
            model.config["category"],
            model.config["version"]
        )

        self.import_species(
            model_id,
            model.config["id"]
        )

        return model_id

    def get_or_create_camera(self, name, location=None):

        cursor = self.cursor()

        cursor.execute("""
            SELECT id
            FROM cameras
            WHERE name = ?
        """, (name,))

        row = cursor.fetchone()

        if row:
            return row["id"]

        cursor.execute("""
            INSERT INTO cameras
            (
                name,
                location
            )
            VALUES (?, ?)
        """, (
            name,
            location
        ))

        self.commit()

        return cursor.lastrowid

    def get_cameras(self):

        cursor = self.cursor()

        cursor.execute("""
            SELECT *
            FROM cameras
            ORDER BY id
        """)

        return cursor.fetchall()

    def add_photo(
        self,
        camera_id,
        relative_path,
        taken_at=None,
        width=None,
        height=None
    ):

        cursor = self.cursor()

        cursor.execute("""
            INSERT INTO photos
            (
                camera_id,
                relative_path,
                taken_at,
                width,
                height,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            camera_id,
            relative_path,
            taken_at,
            width,
            height,
            datetime.utcnow().isoformat()
        ))

        self.commit()

        return cursor.lastrowid

    def save_photo(self, photo):

        cursor = self.cursor()

        cursor.execute("""
            INSERT INTO photos
            (
                camera_id,
                relative_path,
                taken_at,
                width,
                height,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            photo.camera_id,
            photo.relative_path,
            photo.taken_at,
            photo.width,
            photo.height,
            datetime.utcnow().isoformat()
        ))

        self.commit()

        photo.id = cursor.lastrowid

        return photo

    def save_observation(self, observation):

        cursor = self.cursor()

        cursor.execute("""
            INSERT INTO observations
            (
                photo_id,
                model_id,
                crop_path,
                box_left,
                box_top,
                box_right,
                box_bottom,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            observation.photo.id,
            observation.model_id,
            observation.crop_path,
            observation.box.left,
            observation.box.top,
            observation.box.right,
            observation.box.bottom,
            observation.status,
            observation.created_at.isoformat()
        ))

        self.commit()

        observation.id = cursor.lastrowid

        return observation

    def save_prediction(self, observation_id, prediction):

        cursor = self.cursor()

        cursor.execute("""
            INSERT INTO predictions
            (
                observation_id,
                species,
                score,
                rank
            )
            VALUES (?, ?, ?, ?)
        """, (
            observation_id,
            prediction.species,
            prediction.score,
            prediction.rank
        ))

        self.commit()

        return cursor.lastrowid

    def import_species(self, model_id, model_name):

        species_file = (
            BASE_DIR
            / "models"
            / model_name
            / "classifier"
            / "species.json"
        )

        print("BASE_DIR:", BASE_DIR)
        print("Model:", model_name)
        print("Zoekt:", species_file)
        print("Bestaat:", species_file.exists())

        if not species_file.exists():
            raise FileNotFoundError(species_file)

        with open(species_file, encoding="utf-8") as f:
            species_map = json.load(f)

        cursor = self.cursor()

        imported = 0

        for english, data in species_map.items():

            cursor.execute("""
                SELECT id
                FROM species
                WHERE model_id = ?
                AND english = ?
            """, (model_id, english))

            if cursor.fetchone():
                continue

            cursor.execute("""
                INSERT INTO species
                (
                    model_id,
                    english,
                    scientific,
                    external_id,
                    habitat,
                    diet
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                model_id,
                english,
                data.get("scientificName"),
                data.get("birdbaseId"),
                data.get("habitat"),
                data.get("diet")
            ))

            imported += 1

        self.commit()

        print(f"{imported} species imported")
