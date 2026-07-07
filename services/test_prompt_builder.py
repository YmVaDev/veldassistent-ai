
from storage.database import Database
from services.prompt_builder import PromptBuilder

db = Database()

species = db.get_species(1)

builder = PromptBuilder()

print(builder.build_species_illustration(species))
print(builder.build_habitat_illustration(species))