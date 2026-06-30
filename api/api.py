
from pathlib import Path
from fastapi import FastAPI

import router

app = FastAPI()


@app.get("/")
def root():
    return {
        "project": "Oostakkerbos",
        "status": "running"
    }


@app.get("/analyze")
def analyze():

    upload_dir = Path("/home/oostakkerbos/uploads")

    photos = list(upload_dir.glob("*.jpg"))

    if not photos:
        return {
            "error": "Geen foto's gevonden"
        }

    return router.analyze("hibird", photos[0])
