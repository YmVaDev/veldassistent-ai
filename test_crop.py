
import cv2

from vision.detector import (
    inference,
    decode_outputs,
    calculate_scores,
    nms_boxes,
    scale_boxes,
    crop_detections,
)

img = cv2.imread("/opt/oostakkerbos/test.jpg")

output, ratio, pad = inference(img)

decoded = decode_outputs(output)

scores, classes = calculate_scores(decoded)

birds = nms_boxes(decoded, scores)

birds = scale_boxes(birds, ratio, pad)

crops = crop_detections(img, birds)

for i, crop in enumerate(crops):

    cv2.imwrite(
        f"/opt/oostakkerbos/crop_{i}.jpg",
        crop
    )

print(f"{len(crops)} crop(s) opgeslagen!")
