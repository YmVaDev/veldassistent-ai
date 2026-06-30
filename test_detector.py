
import cv2

from vision.detector import inference
from vision.detector import debug_boxes

img = cv2.imread("/opt/oostakkerbos/test.jpg")

output, ratio, pad = inference(img)

debug_boxes(output)
