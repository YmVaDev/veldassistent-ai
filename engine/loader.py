
from config import MODEL_DIR
from engine.model import AIModel

def load_models():

    models = []

    for folder in MODEL_DIR.iterdir():

        if not folder.is_dir():
            continue

        if not (folder / "config.json").exists():
            continue

        models.append(
            AIModel(folder.name)
        )

    return models