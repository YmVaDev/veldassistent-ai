
from api.public import router as public_router
from pathlib import Path
import os
import time
from fastapi import FastAPI

from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException

from api.errors import (
    http_error_handler,
    validation_error_handler
)

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
from api.errors import general_error_handler

from fastapi import Depends
from api.security import verify_api_key
from fastapi.middleware.cors import CORSMiddleware
from config import BASE_URL
from config import API_VERSION

from logger import logger

from config import (
    DATABASE_PATH,
    MODEL_DIR,
    GENERATED_SPECIES_DIR
)

db = Database()
illustration_service = IllustrationService(db)

app = FastAPI(
    title="Veldassistent 24/7 API",
    description="""
    API voor automatische soortherkenning,
    waarnemingen en natuurmonitoring.

    Gebruikt door WordPress voor publieke
    waarnemingen en beheer.
    """,
    version=API_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        BASE_URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(
    HTTPException,
    http_error_handler
)

app.add_exception_handler(
    RequestValidationError,
    validation_error_handler
)

app.add_exception_handler(
    Exception,
    general_error_handler
)

app.include_router(public_router)

app.include_router(
    public_router,
    prefix="/api/v1"
)

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
    logger.info(f"New photo recieved: {src_path}")

    result = engine.process(src_path)

    logger.info(
        f"Analysis completed: {result}"
    )

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
            logger.exception(f"Exception while analyzing: {e}")


# -------------------------
# Observer
# -------------------------
incoming_map = Path("incoming")
incoming_map.mkdir(exist_ok=True)

observer = Observer()

@app.on_event("startup")
def startup():

    logger.info("Starting Veldassistent 24/7")

    if not DATABASE_PATH.exists():
        logger.error("Database not found")

    if not MODEL_DIR.exists():
        logger.error("Model directory missing")

    if not GENERATED_SPECIES_DIR.exists():
        GENERATED_SPECIES_DIR.mkdir(
            parents=True,
            exist_ok=True
        )
        logger.info(
            "Created species image directory"
        )

    logger.info(
        f"Models loaded: {len(engine.models)}"
    )

    observer.schedule(
        FotoHandler(),
        str(incoming_map),
        recursive=False
    )

    observer.start()

    logger.info(
        "Monitoring started"
    )


@app.on_event("shutdown")
def shutdown():
    logger.info("Stop monitoring...")

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


@app.post(
    "/review/{observation_id}",
    dependencies=[Depends(verify_api_key)]
)
def review(
    observation_id: int,
    body: ReviewRequest
):

    if db.has_review(observation_id):
        raise HTTPException(
            status_code=409,
            detail="Observation has already been reviewed."
        )

    logger.info(
        f"Review confirmed: {body.confirmed_species_id}"
    )

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

    try:
        db_status = "ok"

        db.get_latest_observations(1)

    except Exception:
        db_status = "error"


    return {
        "status": "ok",
        "version": API_VERSION,
        "database": db_status,
        "models": len(engine.models)
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