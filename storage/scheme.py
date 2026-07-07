
from storage.database import Database

def create_cameras(cursor):

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cameras (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL UNIQUE,

            location TEXT,

            active INTEGER DEFAULT 1

        )
    """)

def create_models(cursor):

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS models (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL UNIQUE,

            category TEXT NOT NULL,

            version TEXT,

            active INTEGER DEFAULT 1

        )
    """)

def create_species(cursor):

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS species (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            model_id INTEGER NOT NULL,

            english TEXT NOT NULL,

            scientific TEXT,

            external_id INTEGER,

            habitat TEXT,

            diet TEXT,

            species_image_path TEXT,
            
            habitat_image_path TEXT,

            FOREIGN KEY(model_id)
            REFERENCES models(id)

        )
    """)

def create_observations(cursor):

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS observations (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            photo_id INTEGER NOT NULL,

            model_id INTEGER NOT NULL,

            crop_path TEXT,

            box_left INTEGER NOT NULL,
            box_top INTEGER NOT NULL,
            box_right INTEGER NOT NULL,
            box_bottom INTEGER NOT NULL,

            status TEXT NOT NULL DEFAULT 'pending',

            created_at TEXT NOT NULL,

            FOREIGN KEY(photo_id)
                REFERENCES photos(id),

            FOREIGN KEY(model_id)
                REFERENCES models(id)

        )
    """)


def create_photos(cursor):

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS photos (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            camera_id INTEGER NOT NULL,

            relative_path TEXT NOT NULL,

            taken_at TEXT,

            width INTEGER,

            height INTEGER,

            created_at TEXT NOT NULL,

            FOREIGN KEY(camera_id)
                REFERENCES cameras(id)

        )
    """)

def create_predictions(cursor):

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            observation_id INTEGER NOT NULL,

            species TEXT NOT NULL,

            score REAL NOT NULL,

            rank INTEGER NOT NULL,

            FOREIGN KEY(observation_id)
                REFERENCES observations(id)

        )
    """)


def create_reviews(cursor):

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            observation_id INTEGER NOT NULL,

            confirmed INTEGER NOT NULL,

            confirmed_species TEXT,

            comment TEXT,

            reviewed_by TEXT,

            reviewed_at TEXT NOT NULL,

            FOREIGN KEY(observation_id)
                REFERENCES observations(id)

        )
    """)

def create_scheme():

    db = Database()

    cursor = db.cursor()

    create_cameras(cursor)
    create_models(cursor)
    create_species(cursor)
    create_photos(cursor)
    create_observations(cursor)
    create_predictions(cursor)
    create_reviews(cursor)

    db.commit()

    db.close()

    print("Database scheme ready")




