
from storage.database import Database

db = Database()

species = db.get_species(1)

print(dict(species))