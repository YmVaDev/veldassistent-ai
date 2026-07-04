
from pathlib import Path
import os
import time
from fastapi import FastAPI
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from engine.engine import Engine
from engine.loader import load_models

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
# Eventuele API-endpoint
# -------------------------
@app.get("/")
def root():
    return {"status": "running"}