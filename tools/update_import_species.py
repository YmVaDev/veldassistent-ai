
from storage.database import Database

db = Database()

# Pas dit alleen aan als jouw modelnaam anders is
model_name = "birds"

# Haal het model-ID op
cursor = db.cursor()

cursor.execute("""
    SELECT id
    FROM models
    WHERE name = ?
""", (model_name,))

row = cursor.fetchone()

if row is None:
    raise RuntimeError(f"Model niet gevonden: {model_name}")

model_id = row[0]

print(f"Model: {model_name}")
print(f"Model ID: {model_id}")

# Import uitvoeren
db.import_species(model_id, model_name)

print(">>> NIEUWE import_species() WORDT UITGEVOERD <<<")

# Controleren
cursor.execute("""
    SELECT
        english,
        priority,
        clip_duration
    FROM species
    WHERE model_id = ?
    AND english IN (
        'hawfinch',
        'middle spotted woodpecker',
        'kingfisher'
    )
    ORDER BY english
""", (model_id,))

print()
print("Resultaat:")

for row in cursor.fetchall():
    print(row)

db.close()
db.close()

