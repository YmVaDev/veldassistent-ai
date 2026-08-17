
import threading
import time

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Query,
)

from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from api.errors import (
    general_error_handler,
    http_error_handler,
    validation_error_handler,
)

from api.models import ReviewRequest
from api.public import router as public_router
from api.security import verify_api_key
from api.serializers import (
    serialize_observation,
    serialize_species,
)

from cameras.static_camera import StaticCamera
from config import (
    API_VERSION,
    BASE_URL,
    DATABASE_PATH,
    GENERATED_SPECIES_DIR,
    INCOMING_DIR,
    MODEL_DIR,
    RTSP_ENABLED,
    RTSP_INTERVAL,
    RTSP_OUTPUT_DIR,
    RTSP_URL,
    PTZ_ENABLED,
    PTZ_RTSP_URL,
    PTZ_ONVIF_HOST,
    PTZ_ONVIF_PORT,
    PTZ_ONVIF_USERNAME,
    PTZ_ONVIF_PASSWORD,
    PTZ_OUTPUT_DIR,
    PTZ_INTERVAL,
    PTZ_SETTLE_TIME,
)

from engine.engine import Engine
from engine.loader import load_models
from logger import logger
from services.illustration_service import IllustrationService
from storage.database import Database
from cameras.ptz_camera import PTZCamera


# =========================================================
# Applicatie-initialisatie
# =========================================================

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
    version=API_VERSION,
)


# =========================================================
# Middleware
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[BASE_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# Exception handlers
# =========================================================

app.add_exception_handler(
    HTTPException,
    http_error_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_error_handler,
)

app.add_exception_handler(
    Exception,
    general_error_handler,
)


# =========================================================
# Routers
# =========================================================

app.include_router(public_router)


# =========================================================
# Engine
# =========================================================

engine = Engine()

for model in load_models():
    engine.add_model(model)


# =========================================================
# Analyse
# =========================================================

def process_incoming(
    src_path: str,
    camera_key: str
):
    """
    Analyseer een binnengekomen afbeelding.
    """

    logger.info(
        f"New photo received from "
        f"{camera_key}: {src_path}"
    )

    result = engine.process(
        src_path,
        camera_key
    )

    logger.info(
        f"Analysis completed: {result}"
    )

    return result


def process_rtsp_frame(
    src_path: str,
    camera_key: str
):
    """
    Analyseer een frame afkomstig van een camera.
    """

    try:
        process_incoming(
            src_path,
            camera_key
        )

    except Exception:
        logger.exception(
            f"Exception while analyzing RTSP frame: {src_path}"
        )


# =========================================================
# Camera state
# =========================================================

camera_source = None
camera_thread = None
ptz_camera = None


# =========================================================
# Watchdog
# =========================================================

class FotoHandler(FileSystemEventHandler):
    """
    Verwerkt nieuwe afbeeldingen in de incoming-map.
    """

    def on_created(self, event):

        if event.is_directory:
            return

        if not event.src_path.lower().endswith(
            (".jpg", ".jpeg", ".png")
        ):
            return

        time.sleep(1)

        try:
            process_incoming(
                event.src_path,
                "ranger"
            )

        except Exception:
            logger.exception(
                f"Exception while analyzing: {event.src_path}"
            )


INCOMING_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

observer = Observer()


# =========================================================
# Startup
# =========================================================

@app.on_event("startup")
def startup():

    global camera_source
    global camera_thread
    global ptz_camera

    logger.info(
        "Starting Veldassistent 24/7"
    )

    # -----------------------------------------------------
    # Controleer bestanden en mappen
    # -----------------------------------------------------

    if not DATABASE_PATH.exists():
        logger.error(
            f"Database not found: {DATABASE_PATH}"
        )

    if not MODEL_DIR.exists():
        logger.error(
            f"Model directory missing: {MODEL_DIR}"
        )

    if not GENERATED_SPECIES_DIR.exists():

        GENERATED_SPECIES_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        logger.info(
            "Created species image directory"
        )

    logger.info(
        f"Models loaded: {len(engine.models)}"
    )

    # -----------------------------------------------------
    # Incoming monitoring
    # -----------------------------------------------------

    observer.schedule(
        FotoHandler(),
        str(INCOMING_DIR),
        recursive=False,
    )

    observer.start()

    logger.info(
        "Incoming monitoring started"
    )

    # -----------------------------------------------------
    # Static camera monitoring
    # -----------------------------------------------------

    if not RTSP_ENABLED:

        logger.info(
            "Static camera monitoring disabled"
        )

        return

    camera_source = StaticCamera(
        url=RTSP_URL,
        output_dir=RTSP_OUTPUT_DIR,
        interval=RTSP_INTERVAL,
        camera_key="lumus",
    )

    threading.Thread(
        target=camera_source.start,
        args=(process_rtsp_frame,),
        daemon=True,
    ).start()

    logger.info(
        "Static camera monitoring started"
    )

    # -----------------------------------------------------
    # PTZ camera monitoring
    # -----------------------------------------------------

    if not PTZ_ENABLED:

        logger.info(
            "PTZ camera monitoring disabled"
        )

    else:

        ptz_camera = PTZCamera(
            rtsp_url=PTZ_RTSP_URL,
            onvif_host=PTZ_ONVIF_HOST,
            onvif_port=PTZ_ONVIF_PORT,
            username=PTZ_ONVIF_USERNAME,
            password=PTZ_ONVIF_PASSWORD,
            output_dir=PTZ_OUTPUT_DIR,
            camera_key="wz520",
            interval=PTZ_INTERVAL,
            settle_time=PTZ_SETTLE_TIME,
        )

        logger.info(
            "PTZ camera configured"
        )


# =========================================================
# Shutdown
# =========================================================

@app.on_event("shutdown")
def shutdown():

    global camera_source

    logger.info(
        "Stopping Veldassistent 24/7"
    )

    # -----------------------------------------------------
    # Stop static camera
    # -----------------------------------------------------

    if camera_source:

        camera_source.stop()

        logger.info(
            "Static camera monitoring stopped"
        )

    # -----------------------------------------------------
    # Stop incoming monitoring
    # -----------------------------------------------------

    observer.stop()
    observer.join()

    logger.info(
        "Incoming monitoring stopped"
    )


# =========================================================
# Basic endpoints
# =========================================================

@app.get("/")
def root():

    return {
        "status": "running"
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
        "models": len(engine.models),
    }


# =========================================================
# Review endpoints
# =========================================================

@app.get("/review/pending")
def review_pending():

    return db.get_pending_review()


@app.get("/review/{observation_id}")
def get_review(observation_id: int):

    return db.get_review(observation_id)


@app.post(
    "/review/{observation_id}",
    dependencies=[Depends(verify_api_key)],
)
def submit_review(
    observation_id: int,
    body: ReviewRequest,
):

    if db.has_review(observation_id):

        raise HTTPException(
            status_code=409,
            detail="Observation has already been reviewed.",
        )

    logger.info(
        f"Review confirmed: {body.confirmed_species_id}"
    )

    review_id = db.save_review(
        observation_id=observation_id,
        confirmed=body.confirmed,
        confirmed_species_id=body.confirmed_species_id,
        comment=body.comment,
        reviewed_by=body.reviewed_by,
    )

    db.update_observation_status(
        observation_id,
        "reviewed",
    )

    species = db.get_species_by_id(
        body.confirmed_species_id
    )

    if species:

        illustration_service.generate_if_missing(
            species
        )

    else:

        logger.warning(
            f"Species not found: "
            f"{body.confirmed_species_id}"
        )

    return {
        "success": True,
        "review_id": review_id,
    }


# =========================================================
# Public observation endpoints
# =========================================================

@app.get("/api/observations")
def observations(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):

    offset = (page - 1) * limit

    rows = db.get_public_observations(
        limit,
        offset,
    )

    total = db.count_public_observations()

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "items": [
            serialize_observation(row, db)
            for row in rows
        ],
    }


@app.get("/api/observations/{observation_id}")
def observation_detail(observation_id: int):

    row = db.get_observation(
        observation_id
    )

    if not row:

        raise HTTPException(
            status_code=404,
            detail="Observation not found",
        )

    return serialize_observation(
        row,
        db,
    )


# =========================================================
# Species endpoints
# =========================================================

@app.get("/api/species")
def species():

    rows = db.get_species()

    return [
        serialize_species(row)
        for row in rows
    ]


@app.get("/api/species/{species_id}")
def species_detail(species_id: int):

    row = db.get_species_by_id(
        species_id
    )

    if not row:

        raise HTTPException(
            status_code=404,
            detail="Species not found",
        )

    return serialize_species(
        row
    )