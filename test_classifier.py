
import cv2

from vision.classifier import classify

img = cv2.imread("/opt/oostakkerbos/crop_0.jpg")

result = classify(img)

print(result)
