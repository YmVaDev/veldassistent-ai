
import cv2

from vision.detector import inference
from vision.detector import decode_outputs

img = cv2.imread("/opt/oostakkerbos/test.jpg")

output, ratio, pad = inference(img)

decoded = decode_outputs(output)

print(decoded.shape)

print(decoded[0])
print(decoded[1])
print(decoded[2])
