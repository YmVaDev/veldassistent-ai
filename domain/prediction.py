
from dataclasses import dataclass


@dataclass(slots=True)
class Prediction:

    species: str

    score: float

    rank: int = 1

    species_id: int | None = None