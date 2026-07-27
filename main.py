
from api.public import router as public_router
from pathlib import Path
import os
import time
from fastapi import FastAPI
from fastapi import HTTPException
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from engine.engine import Engine
from engine.loader import load_models
from storage.database import Database
from api.models import ReviewRequest
from services.illustration_service import IllustrationService
from api.serializers import serialize_observation
from fastapi import Query
from api.serializers import serialize_species

db = Database()
app = FastAPI()
app.include_router(public_router)

illustration_service = IllustrationService(db)

# -------------------------
# Engine initialiseren
# -------------------------
engine = Engine()

for model in load_models():
    engine.add_model(model)


# -------------------------
# Analysefunctie
# -------------------------
def process_incoming(src_path: str):
    print(f"New photo: {src_path}")

    result = engine.process(src_path)

    print(result)
    return result


# -------------------------
# Watchdog handler
# -------------------------
class FotoHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        if not event.src_path.lower().endswith((".jpg", ".jpeg", ".png")):
            return

        # Wacht even zodat het bestand volledig is gekopieerd
        time.sleep(1)

        try:
            process_incoming(event.src_path)
        except Exception as e:
            print(f"Exception while analyzing: {e}")


# -------------------------
# Observer
# -------------------------
incoming_map = Path("incoming")
incoming_map.mkdir(exist_ok=True)

observer = Observer()


@app.on_event("startup")
def startup():
    print("Start monitoring...")

    observer.schedule(
        FotoHandler(),
        str(incoming_map),
        recursive=False
    )
    observer.start()


@app.on_event("shutdown")
def shutdown():
    print("Stop monitoring...")

    observer.stop()
    observer.join()


# -------------------------
# API-endpoints
# -------------------------
@app.get("/")
def root():
    return {"status": "running"}


@app.get("/observations/pending")
def get_pending_observations():
    return db.get_pending_observations()


@app.get("/review/pending")
def review_pending():
    return db.get_pending_review()


@app.get("/review/{observation_id}")
def review(observation_id: int):
    return db.get_review(observation_id)


@app.post("/review/{observation_id}")
def review(
    observation_id: int,
    body: ReviewRequest
):

    if db.has_review(observation_id):
        raise HTTPException(
            status_code=409,
            detail="Observation has already been reviewed."
        )

    print("CONFIRMED:", body.confirmed_species_id)

    review_id = db.save_review(
        observation_id=observation_id,
        confirmed=body.confirmed,
        confirmed_species_id=body.confirmed_species_id,
        comment=body.comment,
        reviewed_by=body.reviewed_by
    )

    db.update_observation_status(
        observation_id,
        "reviewed"
    )

    species = db.get_species(
        body.confirmed_species_id
    )

    if species:
        print(dict(species))
    else:
        print("Species not found:", body.confirmed_species_id)

    print("CONFIRMED ID:", body.confirmed_species_id)

    print("FOUND SPECIES:", species)

    illustration_service.generate_if_missing(
        species
    )
    return {
        "success": True,
        "review_id": review_id
    }

@app.get("/health")
def health():

    return {
        "status": "ok",
        "version": API_VERSION
    }

@app.get("/api/observations")
def observations(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):

    offset = (page - 1) * limit

    rows = db.get_public_observations(
        limit,
        offset
    )

    total = db.count_public_observations()

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "items": [
            serialize_observation(row, db)
            for row in rows
        ]
    }

@app.get("/api/observations/{observation_id}")
def observation_detail(observation_id: int):

    row = db.get_observation(observation_id)

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Observation not found"
        )

    return serialize_observation(row, db)

@app.get("/api/species")
def species():

    rows = db.get_species()

    return [
        serialize_species(row)
        for row in rows
    ]

@app.get("/api/species/{species_id}")
def species_detail(species_id: int):

    row = db.get_species_by_id(species_id)

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Species not found"
        )

    return serialize_species(row)