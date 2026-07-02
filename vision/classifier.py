
import numpy as np
import onnxruntime as ort
from PIL import Image
from config import MODEL_DIR
from vision.model_config import load_model_config

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

        self.input_size = self.config["classifier"]["size"]

        img = img.resize((self.input_size, self.input_size), Image.Resampling.BICUBIC)

        x = np.asarray(img).astype(np.float32)

        x = (x / 255.0 - 0.5) / 0.5

        x = np.transpose(x, (2, 0, 1))

        x = np.expand_dims(x, axis=0)

        print("Input:", self.session.get_inputs()[0].shape)

        print("Classifier verwacht:", self.session.get_inputs()[0].shape)
        print("Classifier tensor:", x.shape)

        outputs = self.session.run(
            None,
            {
                "input": x
            }
        )

        print("Aantal outputs:", len(outputs))
        print("Classifier tensor:", x.shape)
        print("Expected:", self.session.get_inputs()[0].shape)

        for i, out in enumerate(outputs):
            print(i, out.shape, out.dtype)

        logits = outputs[0]

        idx = int(np.argmax(logits[0]))

        score = float(logits[0][idx])

        english = self.labels[idx]

        return {
            "species": english,
            "score": score
        }

classifier = Classifier("birds")

def classify(image):
    return classifier.classify(image)