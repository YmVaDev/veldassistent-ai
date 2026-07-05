
from storage.database import Database
import json
from pathlib import Path
from config import BASE_DIR

class Repository:

    def __init__(self):
        self.db = Database()

    def add_model(self, name, category, version=None):

        cursor = self.db.cursor()

        cursor.execute("""
            INSERT INTO models
            (name, category, version)
            VALUES (?, ?, ?)
        """, (name, category, version))

        self.db.commit()

        return cursor.lastrowid

    def get_model(self, name):

        cursor = self.db.cursor()

        cursor.execute("""
            SELECT *
            FROM models
            WHERE name = ?
        """, (name,))

        return cursor.fetchone()

    def get_or_create_model(self, name, category, version=None):

        cursor = self.db.cursor()

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
            (name, category, version)
            VALUES (?, ?, ?)
        """, (name, category, version))

        self.db.commit()

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

        cursor = self.db.cursor()

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

        self.db.commit()

        print(f"{imported} species imported")

    def get_species(self, model_id, english):

        cursor = self.db.cursor()

        cursor.execute("""
            SELECT *
            FROM species
            WHERE model_id = ?
            AND english = ?
        """, (
            model_id,
            english
        ))

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)