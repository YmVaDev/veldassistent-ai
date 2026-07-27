
from pydantic import BaseModel

class ReviewRequest(BaseModel):
    confirmed: bool
    confirmed_species_id: int | None = None
    comment: str | None = None
    reviewed_by: str | None = None