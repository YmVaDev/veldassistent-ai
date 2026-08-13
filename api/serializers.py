
from config import MEDIA_URL

def observation_to_public(observation, species=None):

    data = {
        "id": observation["id"],
        "status": observation["status"],
        "created_at": observation["created_at"]
    }

    if species:

        data["species"] = {
            "id": species["id"],
            "name": species["english"],
            "scientific": species["scientific"],
            "image_url": (
                MEDIA_URL +
                f"species/{species['id']}.webp"
            ),
            "habitat_image_url": (
                MEDIA_URL +
                f"habitats/{species['id']}.webp"
            )
        }

    return data

def serialize_observation(row, db):

    data = {
        "id": row["id"],
        "status": row["status"],
        "created_at": row["created_at"],
        "world": row["world"]
    }

    # afbeelding
    if row["crop_path"]:
        data["image"] = {
            "crop_url": MEDIA_URL + row["crop_path"]
        }

    # soort ophalen
    species = db.get_species_by_observation(
        row["id"]
    )

    if species:

        data["species"] = {
            "id": species["id"],
            "name": species["english"],
            "scientific": species["scientific"],
            "image_url": (
                MEDIA_URL +
                f"species/{species['id']}.webp"
            ),
            "habitat_image_url": (
                MEDIA_URL +
                f"habitats/{species['id']}.webp"
            )
        }

    return data

def serialize_species(row):

    return {
        "id": row["id"],
        "name": row["english"],
        "scientific_name": row["scientific"],
        "habitat": row["habitat"],
        "diet": row["diet"],
        "image_url": (
            MEDIA_URL +
            f"species/{row['id']}.webp"
        ),
        "habitat_image_url": (
            MEDIA_URL +
            f"habitats/{row['id']}.webp"
        )
    }

def serialize_species_observation(row):
    return {
        "id": row["observation_id"],
        "photo": row["photo_path"],
        "world": row["world"],
        "species_id": row["confirmed_species_id"],
        "species": row["english"],
        "species_image": row["species_image_path"],
        "habitat_image": row["habitat_image_path"],
        "date": row["created_at"]
    }