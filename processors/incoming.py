
from pathlib import Path

from engine.model import AIModel

model = AIModel("birds")

def process_incoming():

    incoming = Path("incoming")

    for image_path in incoming.glob("*.jpg"):

        result = model.process(str(image_path))

        print(result)

process_incoming()