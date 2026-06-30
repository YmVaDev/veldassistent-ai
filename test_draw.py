
import cv2

from vision.detector import (
    inference,
    decode_outputs,
    calculate_scores,
    nms_boxes,
    scale_boxes,
)

img = cv2.imread("/opt/oostakkerbos/test.jpg")

output, ratio, pad = inference(img)

decoded = decode_outputs(output)

scores, classes = calculate_scores(decoded)

birds = nms_boxes(decoded, scores)

birds = scale_boxes(birds, ratio, pad)

print(birds)

for bird in birds:

    x1, y1, x2, y2 = bird["box"]

    cv2.rectangle(
        img,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        8,
    )

cv2.imwrite(
    "/opt/oostakkerbos/test_detected.jpg",
    img,
)

print("\n✅ test_detected.jpg opgeslagen!")
