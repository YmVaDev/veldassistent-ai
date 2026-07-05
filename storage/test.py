
from storage.database import Database

db = Database()

for row in db.get_pending_review():
    print(row)