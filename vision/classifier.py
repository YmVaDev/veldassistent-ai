
import numpy as np
import onnxruntime as ort
from PIL import Image

MODEL = "/opt/oostakkerbos/models/birds/onnx/convnext_v1_tiny_eu_common.onnx"
LABELS = "/opt/oostakkerbos/models/birds/onnx/convnext_v1_tiny_eu_common_labels.txt"

session = ort.InferenceSession(MODEL)

with open(LABELS, "r", encoding="utf-8") as f:
    labels = [line.strip() for line in f]


def classify(image):

    # OpenCV (BGR) -> RGB
    image = image[:, :, ::-1]

    img = Image.fromarray(image)

    img = img.resize((384, 384), Image.Resampling.BICUBIC)

    x = np.asarray(img).astype(np.float32)

    x = (x / 255.0 - 0.5) / 0.5

    x = np.transpose(x, (2, 0, 1))

    x = np.expand_dims(x, axis=0)

    outputs = session.run(
        None,
        {
            "input": x
        }
    )

    logits = outputs[0]

    idx = int(np.argmax(logits))

    score = float(logits[0][idx])

    return {
        "species": labels[idx],
        "score": score,
    }
