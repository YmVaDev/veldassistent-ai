

from fastapi import FastAPI
from pydantic import BaseModel

from vision.pipeline import detect_and_classify

app = FastAPI()


class AnalyzeRequest(BaseModel):
    image_path: str


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Oostakkerbos AI"
    }


@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    return detect_and_classify(request.image_path)
