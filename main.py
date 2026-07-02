
from fastapi import FastAPI
from pydantic import BaseModel
from engine.engine import Engine
from engine.model import AIModel

app = FastAPI()

class AnalyzeRequest(BaseModel):
    image_path: str

from engine.loader import load_models

engine = Engine()

for model in load_models():
    engine.add_model(model)

@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    return engine.process(request.image_path)

