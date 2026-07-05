
from storage.database import Database
from storage.scheme import create_scheme

db = Database()

create_scheme()

db.commit()

print("Schema aangemaakt.")

db.close()