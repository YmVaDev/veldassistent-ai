
from pathlib import Path
import sqlite3
import json
from datetime import datetime
from config import BASE_DIR
from config import DATABASE_PATH

class Database:

    def __init__(self, db_name="veldassistent.db"):

        self.db_path = DATABASE_PATH

        self.connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False
        )

        self.connection.row_factory = sqlite3.Row

        self.connection.execute(
            "PRAGMA foreign_keys = ON"
        )

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

    def update_photo(self, photo):

        cursor = self.cursor()

        cursor.execute("""
            UPDATE photos
            SET relative_path = ?
            WHERE id = ?
        """, (
            photo.relative_path,
            photo.id
        ))

        self.commit()


    def get_pending_observations(self):

        cursor = self.cursor()

        cursor.execute("""
            SELECT *
            FROM observations
            WHERE status = 'pending'
            ORDER BY id DESC
        """)

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def get_pending_review(self):

        cursor = self.cursor()

        cursor.execute("""
            SELECT

                o.id,
                o.crop_path,
                o.status,

                p.species,
                p.score

            FROM observations o

            JOIN predictions p
                ON p.observation_id = o.id

            WHERE
                o.status = 'pending'
                AND p.rank = 1

            ORDER BY o.id DESC
        """)

        rows = [
            dict(row)
            for row in cursor.fetchall()
        ]

        for row in rows:
            row["crop_url"] = f"https://oostakkerbos.be/{row['crop_path']}"

        return rows

    def get_review(self, observation_id):

        cursor = self.cursor()
        cursor.execute("""
            SELECT

                o.id,
                o.crop_path,
                o.status,

                p.species,
                p.score,
                p.rank

            FROM observations o

            JOIN predictions p
                ON p.observation_id = o.id

            WHERE
                o.id = ?

            ORDER BY
                p.rank
        """, (observation_id,))

        rows = [
            dict(row)
            for row in cursor.fetchall()
        ]

        for row in rows:
            row["crop_url"] = f"https://oostakkerbos.be/{row['crop_path']}"

        return rows


    def save_review(
        self,
        observation_id,
        confirmed,
        confirmed_species=None,
        comment=None,
        reviewed_by=None
    ):

        cursor = self.cursor()

        cursor.execute("""
            INSERT INTO reviews
            (
                observation_id,
                confirmed,
                confirmed_species,
                comment,
                reviewed_by,
                reviewed_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            observation_id,
            int(confirmed),
            confirmed_species,
            comment,
            reviewed_by,
            datetime.utcnow().isoformat()
        ))

        self.commit()

        return cursor.lastrowid


    def update_observation_status(
        self,
        observation_id,
        status
    ):

        cursor = self.cursor()

        cursor.execute("""
            UPDATE observations
            SET status = ?
            WHERE id = ?
        """, (
            status,
            observation_id
        ))

        self.commit()

    def has_review(self, observation_id):

        cursor = self.cursor()

        cursor.execute("""
            SELECT 1
            FROM reviews
            WHERE observation_id = ?
        """, (observation_id,))

        return cursor.fetchone() is not None

    def get_species_image(self, species):

        cursor = self.cursor()

        cursor.execute("""
            SELECT image_path
            FROM species
            WHERE english = ?
        """, (species,))

        row = cursor.fetchone()

        if row is None:
            return None

        return row["image_path"]

        print(species)
        print(species["id"])
        print(species["english"])
        print(image_path)

    def update_species_images(
        self,
        species_id,
        species_image_path,
        habitat_image_path
    ):
        cursor = self.cursor()

        cursor.execute("""
            UPDATE species
            SET image_path = ?
            WHERE id = ?
        """, (
            image_path,
            species_id
        ))

        print("Updated rows:", cursor.rowcount)
        self.commit()


    def get_species(self, species_id):

        cursor = self.cursor()

        cursor.execute("""
            SELECT *
            FROM species
            WHERE id = ?
        """, (species_id,))

        return cursor.fetchone()


    def update_species_image_path(
        self,
        species_id,
        species_image_path
    ):

        cursor = self.cursor()

        cursor.execute("""
            UPDATE species
            SET species_image_path = ?
            WHERE id = ?
        """, (
            species_image_path,
            species_id
        ))

        self.commit()





        