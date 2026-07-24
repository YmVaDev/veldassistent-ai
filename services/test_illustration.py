
from storage.database import Database
from services.illustration_service import IllustrationService

db = Database()

species = db.get_species(28)

service = IllustrationService(db)

service.generate_if_missing(species)