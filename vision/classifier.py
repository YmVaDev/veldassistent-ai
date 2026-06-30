
import numpy as np
import onnxruntime as ort
from PIL import Image

from config import MODEL_DIR
from config import CLASSIFIER_SIZE

MODEL = MODEL_DIR / "birds" / "onnx" / "convnext_v1_tiny_eu_common.onnx"
LABELS = MODEL_DIR / "birds" / "onnx" / "convnext_v1_tiny_eu_common_labels.txt"

session = ort.InferenceSession(MODEL)

with open(LABELS, "r", encoding="utf-8") as f:
    labels = [line.strip() for line in f]


def classify(image):

    # OpenCV (BGR) -> RGB
    image = image[:, :, ::-1]

    img = Image.fromarray(image)

    img = img.resize((CLASSIFIER_SIZE, CLASSIFIER_SIZE), Image.Resampling.BICUBIC)

    x = np.asarray(img).astype(np.float32)

    x = (x / 255.0 - 0.5) / 0.5

    x = np.transpose(x, (2, 0, 1))

    x = np.expand_dims(x, axis=0)

    print("Input:", session.get_inputs()[0].shape)

    print("Classifier verwacht:", session.get_inputs()[0].shape)
    print("Classifier tensor:", x.shape)

    outputs = session.run(
        None,
        {
            "input": x
        }
    )

    print("Aantal outputs:", len(outputs))
    print("Classifier tensor:", x.shape)
    print("Expected:", session.get_inputs()[0].shape)

    for i, out in enumerate(outputs):
        print(i, out.shape, out.dtype)

    logits = outputs[0]

    idx = int(np.argmax(logits[0]))

    score = float(logits[0][idx])

    english = labels[idx]

    return {
        "species": english,
        "score": score
    }
