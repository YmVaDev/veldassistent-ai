
from fastapi import APIRouter, HTTPException
from storage.database import Database
from api.serializers import observation_to_public
from api.serializers import serialize_species_observation

router = APIRouter(
    prefix="/api",
    tags=["public"]
)

db = Database()


@router.get("/species/{species_id}")
def get_species(species_id: int):

    species = db.get_species_by_id(species_id)

    if species is None:
        raise HTTPException(
            status_code=404,
            detail="Species not found"
        )

    return dict(species)


@router.get("/observations/latest")
def latest_observations(limit: int = 20):

    return db.get_latest_observations(limit)


@router.get("/observations/{observation_id}")
def get_observation(observation_id: int):

    observation = db.get_observation(
        observation_id
    )

    if observation is None:
        raise HTTPException(
            status_code=404,
            detail="Observation not found"
        )

    species = db.get_species_for_observation(
        observation_id
    )

    return observation_to_public(
        observation,
        species
    )

@router.get("/species/{species_id}/observations")
def species_observations(species_id: int):

    rows = db.get_observations_by_species(species_id)

    for row in rows:
        print(dict(row))

    return [
        serialize_species_observation(row)
        for row in rows
    ]

