
from storage.repository import Repository

repo = Repository()

model_id = repo.get_or_create_model(
    "birds",
    "bird",
    "1.0"
)

species = repo.get_species(
    model_id,
    "Hawfinch"
)

print(dict(species))