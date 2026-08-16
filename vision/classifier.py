
import numpy as np
import onnxruntime as ort
from PIL import Image
from config import MODEL_DIR
from vision.model_config import load_model_config
from domain.prediction import Prediction

class Classifier:

    def __init__(self, model_name):

        self.config = load_model_config(model_name)

        model = MODEL_DIR / model_name / self.config["classifier"]["model"]
        labels = MODEL_DIR / model_name / self.config["classifier"]["labels"]

        self.session = ort.InferenceSession(model)

        with open(labels, "r", encoding="utf-8") as f:
            self.labels = [line.strip() for line in f]


    def classify(self, image):

        # OpenCV (BGR) -> RGB
        image = image[:, :, ::-1]

        img = Image.fromarray(image)

        input_size = self.config["classifier"]["size"]

        img = img.resize(
            (input_size, input_size),
            Image.Resampling.BICUBIC
        )

        x = np.asarray(img).astype(np.float32)

        x = (x / 255.0 - 0.5) / 0.5

        x = np.transpose(x, (2, 0, 1))

        x = np.expand_dims(x, axis=0)

        outputs = self.session.run(
            None,
            {
                "input": x
            }
        )

        logits = outputs[0][0]

        exp = np.exp(
            logits - np.max(logits)
        )

        probs = exp / np.sum(exp)

        indices = np.argsort(probs)[::-1][:5]

        predictions = []

        for rank, idx in enumerate(indices, start=1):

            predictions.append(
                Prediction(
                    species=self.labels[idx],
                    score=round(
                        float(probs[idx]) * 100,
                        1
                    ),
                    rank=rank
                )
            )

        return predictions



