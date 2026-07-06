
from engine.loader import load_models
from storage.database import Database

db = Database()

for model in load_models():

    print(f"Synchronizing: {model.config['id']}")

    db.sync_model(model)

print("Ready!")