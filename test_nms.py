
import cv2

from vision.detector import inference
from vision.detector import decode_outputs
from vision.detector import calculate_scores
from vision.detector import nms_boxes

img = cv2.imread("/opt/oostakkerbos/test.jpg")

output, ratio, pad = inference(img)

decoded = decode_outputs(output)

scores, classes = calculate_scores(decoded)

birds = nms_boxes(decoded, scores)

print(f"\nAantal detecties: {len(birds)}\n")

for bird in birds:

    print(
        bird["prediction_index"],
        round(bird["score"], 3),
        bird["box"],
    )
