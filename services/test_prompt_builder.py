
from storage.database import Database
from services.prompt_builder import PromptBuilder

db = Database()

species = db.get_species(1)

builder = PromptBuilder()

print(builder.build_stage1(species))
print(builder.build_stage2(species))