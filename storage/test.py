
from storage.database import Database

db = Database()

db.update_species_image_path(
    1,
    "generated/species/test.webp"
)

db.update_habitat_image_path(
    1,
    "generated/habitats/test.webp"
)

species = db.get_species(1)

print(dict(species))

print(species["species_image_path"])

print(dict(species))

