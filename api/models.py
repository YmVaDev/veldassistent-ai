
from pydantic import BaseModel

class ReviewRequest(BaseModel):

    confirmed: bool

    confirmed_species: str | None = None

    comment: str | None = None

    reviewed_by: str | None = None