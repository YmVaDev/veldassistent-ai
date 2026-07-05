
from storage.database import Database

db = Database()

review_id = db.save_review(
    observation_id=4,
    confirmed=False,
    confirmed_species="Greenfinch",
    comment="Snavel is te klein voor Hawfinch"
)

print(review_id)