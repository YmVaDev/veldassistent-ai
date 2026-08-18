
from pathlib import Path
import sqlite3
import json
from datetime import datetime
from config import BASE_DIR
from config import DATABASE_PATH

import os
print("DATABASE FILE:", os.path.abspath("veldassistent.db"))

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

    def get_or_create_camera(
        self,
        name,
        location=None,
        world=None
    ):

        cursor = self.cursor()

        cursor.execute("""
            SELECT id
            FROM cameras
            WHERE name = ?
        """, (name,))

        row = cursor.fetchone()

        if row:

            if world is not None:

                cursor.execute("""
                    UPDATE cameras
                    SET world = ?
                    WHERE id = ?
                """, (
                    world,
                    row["id"]
                ))

                self.commit()

            return row["id"]

        cursor.execute("""
            INSERT INTO cameras
            (
                name,
                location,
                world
            )
            VALUES (?, ?, ?)
        """, (
            name,
            location,
            world
        ))

        self.commit()

        return cursor.lastrowid

    def update_camera_world(self, camera_id, world):

        cursor = self.cursor()

        cursor.execute("""
            UPDATE cameras
            SET world = ?
            WHERE id = ?
        """, (
            world,
            camera_id
        ))

        self.commit()

    def get_cameras(self):

        cursor = self.cursor()

        cursor.execute("""
            SELECT *
            FROM cameras
            ORDER BY id
        """)

        return cursor.fetchall()

    def get_camera(self, camera_id):

        cursor = self.cursor()

        cursor.execute("""
            SELECT *
            FROM cameras
            WHERE id = ?
        """, (camera_id,))

        return cursor.fetchone()

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
                world,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            photo.camera_id,
            photo.relative_path,
            photo.taken_at,
            photo.width,
            photo.height,
            photo.world,
            photo.created_at.isoformat()
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

        species_dir = (
            BASE_DIR
            / "models"
            / model_name
            / "classifier"
        )

        species_file = species_dir / "species.json"
        settings_file = species_dir / "species_settings.json"

        if not species_file.exists():
            raise FileNotFoundError(species_file)

        if not settings_file.exists():
            raise FileNotFoundError(settings_file)

        # -------------------------------------------------------------
        # species.json laden
        # -------------------------------------------------------------

        with open(species_file, encoding="utf-8") as f:
            species_map = json.load(f)

        # -------------------------------------------------------------
        # species_settings.json laden
        # -------------------------------------------------------------

        with open(settings_file, encoding="utf-8") as f:
            settings_map = json.load(f)

        cursor = self.cursor()

        imported = 0
        updated = 0

        # -------------------------------------------------------------
        # Soorten verwerken
        # -------------------------------------------------------------

        for english, data in species_map.items():

            # ---------------------------------------------------------
            # Instellingen ophalen
            # ---------------------------------------------------------

            settings = settings_map.get(english, {})

            priority = settings.get("priority", "interesting")
            clip_duration = settings.get("clip_duration", 30)

            # ---------------------------------------------------------
            # Bestaat de soort al?
            # ---------------------------------------------------------

            cursor.execute("""
                SELECT id
                FROM species
                WHERE model_id = ?
                AND english = ?
            """, (model_id, english))

            row = cursor.fetchone()

            # ---------------------------------------------------------
            # Nieuwe soort
            # ---------------------------------------------------------

            if row is None:

                cursor.execute("""
                    INSERT INTO species
                    (
                        model_id,
                        english,
                        scientific,
                        external_id,
                        habitat,
                        diet,
                        priority,
                        clip_duration
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    model_id,
                    english,
                    data.get("scientificName"),
                    data.get("birdbaseId"),
                    data.get("habitat"),
                    data.get("diet"),
                    priority,
                    clip_duration
                ))

                imported += 1

            # ---------------------------------------------------------
            # Bestaande soort
            # ---------------------------------------------------------

            else:

                species_id = row[0]

                cursor.execute("""
                    UPDATE species
                    SET
                        scientific = ?,
                        external_id = ?,
                        habitat = ?,
                        diet = ?,
                        priority = ?,
                        clip_duration = ?
                    WHERE id = ?
                """, (
                    data.get("scientificName"),
                    data.get("birdbaseId"),
                    data.get("habitat"),
                    data.get("diet"),
                    priority,
                    clip_duration,
                    species_id
                ))

                updated += 1

        self.commit()

        print(f"Species imported: {imported}")
        print(f"Species updated: {updated}")

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

    def get_pending_review(self):

        cursor = self.cursor()

        cursor.execute("""
            SELECT
                o.id,
                o.crop_path,
                o.status,

                p.species,
                p.score,
                p.rank,

                s.id AS species_id,
                s.scientific,
                s.priority

            FROM observations o

            JOIN predictions p
                ON p.observation_id = o.id

            LEFT JOIN species s
                ON s.english = p.species
                AND s.model_id = o.model_id

            WHERE
                o.status = 'pending'
                AND p.rank <= 5

            ORDER BY
                o.id DESC,
                p.rank
        """)

        rows = [
            dict(row)
            for row in cursor.fetchall()
        ]

        reviews = {}

        for row in rows:

            observation_id = row["id"]

            if observation_id not in reviews:

                reviews[observation_id] = {
                    "id": observation_id,
                    "crop_path": row["crop_path"],
                    "status": row["status"],
                    "crop_url": (
                        f"https://oostakkerbos.be/"
                        f"{row['crop_path']}"
                    ),
                    "predictions": []
                }

            reviews[observation_id]["predictions"].append({
                "species": row["species"],
                "score": row["score"],
                "rank": row["rank"],
                "species_id": row["species_id"],
                "scientific": row["scientific"],
                "priority": row["priority"],
            })

        return list(reviews.values())

    def get_review(self, observation_id):

        cursor = self.cursor()

        cursor.execute("""
            SELECT
                o.id,
                o.crop_path,
                o.status,

                p.species,
                p.score,
                p.rank,

                s.id AS species_id,
                s.scientific,
                s.priority

            FROM observations o

            JOIN predictions p
                ON p.observation_id = o.id

            LEFT JOIN species s
                ON s.english = p.species
                AND s.model_id = o.model_id

            WHERE
                o.id = ?
                AND p.rank <= 5

            ORDER BY
                p.rank
        """, (observation_id,))

        rows = [
            dict(row)
            for row in cursor.fetchall()
        ]

        for row in rows:

            row["crop_url"] = (
                f"https://oostakkerbos.be/"
                f"{row['crop_path']}"
            )

        return rows

    def save_review(
        self,
        observation_id,
        confirmed,
        confirmed_species_id=None,
        comment=None,
        reviewed_by=None
    ):

        cursor = self.cursor()

        cursor.execute("""
            INSERT INTO reviews
            (
                observation_id,
                confirmed,
                confirmed_species_id,
                comment,
                reviewed_by,
                reviewed_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            observation_id,
            confirmed,
            confirmed_species_id,
            comment,
            reviewed_by,
            datetime.now().isoformat()
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

    def get_species_by_english(self, english, model_id):

        cursor = self.cursor()

        cursor.execute("""
            SELECT *
            FROM species
            WHERE english = ?
            AND model_id = ?
        """, (english, model_id))

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


    def update_habitat_image_path(
        self,
        species_id,
        habitat_image_path
    ):

        cursor = self.cursor()

        cursor.execute("""
            UPDATE species
            SET habitat_image_path = ?
            WHERE id = ?
        """, (
            habitat_image_path,
            species_id
        ))

        self.commit()

    def get_observation(self, observation_id):

        cursor = self.cursor()

        cursor.execute("""
            SELECT
                o.*,
                p.world
            FROM observations o

            JOIN photos p
                ON p.id = o.photo_id

            WHERE o.id = ?
        """, (observation_id,))

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def get_latest_observations(self, limit=20):

        cursor = self.cursor()

        cursor.execute("""
            SELECT *
            FROM observations
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))

        return [
            dict(row)
            for row in cursor.fetchall()
        ]


    def get_species_for_observation(self, observation_id):

        cursor = self.cursor()

        cursor.execute("""
            SELECT species.*
            FROM reviews
            JOIN species
                ON reviews.confirmed_species_id = species.id
            WHERE reviews.observation_id = ?
        """, (observation_id,))

        return cursor.fetchone()

    def get_public_observations(self, limit=20, offset=0):

        cursor = self.cursor()

        cursor.execute("""
            SELECT
                o.*,
                p.world
            FROM observations o

            JOIN photos p
                ON p.id = o.photo_id

            ORDER BY o.id DESC

            LIMIT ? OFFSET ?
        """, (limit, offset))

        return cursor.fetchall()

    def count_public_observations(self):

        cursor = self.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM observations
        """)

        return cursor.fetchone()[0]

    def get_today_observations(self):

        cursor = self.cursor()

        cursor.execute("""
            SELECT
                o.id AS observation_id,
                o.created_at,
                o.crop_path,

                p.world,

                r.confirmed_species_id,

                s.english AS species,
                s.scientific,
                s.species_image_path,
                s.habitat_image_path

            FROM observations o

            JOIN photos p
                ON p.id = o.photo_id

            JOIN reviews r
                ON r.observation_id = o.id

            JOIN species s
                ON s.id = r.confirmed_species_id

            WHERE
                o.status = 'reviewed'
                AND r.confirmed = 1
                AND date(o.created_at) =
                    date('now', 'localtime')

            ORDER BY
                o.created_at DESC
        """)

        return cursor.fetchall()

    def get_species(self):

        cursor = self.cursor()

        cursor.execute("""
            SELECT *
            FROM species
            ORDER BY english
        """)

        return cursor.fetchall()

    def get_species_by_id(self, species_id):

        cursor = self.cursor()

        cursor.execute("""
            SELECT *
            FROM species
            WHERE id = ?
        """, (species_id,))

        return cursor.fetchone()

    def get_observations_by_species(self, species_id):

        cursor = self.cursor()

        cursor.execute("""
            SELECT
                o.id AS observation_id,
                p.relative_path AS photo_path,
                p.world,
                o.created_at,
                r.confirmed_species_id,
                s.english,
                s.species_image_path,
                s.habitat_image_path

            FROM observations o

            JOIN photos p
                ON p.id = o.photo_id

            JOIN reviews r
                ON r.observation_id = o.id

            JOIN species s
                ON s.id = r.confirmed_species_id

            WHERE r.confirmed_species_id = ?

            ORDER BY o.created_at DESC
        """, (species_id,))

        return cursor.fetchall()
            