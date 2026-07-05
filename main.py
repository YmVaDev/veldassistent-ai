
from pathlib import Path
import os
import time
from fastapi import FastAPI
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from engine.engine import Engine
from engine.loader import load_models
from storage.database import Database
from api.models import ReviewRequest

db = Database()
app = FastAPI()

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
    print(f"Nieuwe foto: {src_path}")

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
            print(f"Fout tijdens analyseren: {e}")


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

    review_id = db.save_review(
        observation_id=observation_id,
        confirmed=body.confirmed,
        confirmed_species=body.confirmed_species,
        comment=body.comment,
        reviewed_by=body.reviewed_by
    )

    db.update_observation_status(
        observation_id,
        "reviewed"
    )

    return {
        "success": True,
        "review_id": review_id
    }
