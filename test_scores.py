
import cv2
import numpy as np

from vision.detector import inference
from vision.detector import decode_outputs
from vision.detector import calculate_scores

img = cv2.imread("/opt/oostakkerbos/test.jpg")

output, ratio, pad = inference(img)

decoded = decode_outputs(output)

scores, classes = calculate_scores(decoded)

order = np.argsort(scores)[::-1]

print("Top 20 detecties:\n")

for i in order[:20]:

    print(
        f"{i:4}",
        f"score={scores[i]:.4f}",
        f"class={classes[i]}"
    )
