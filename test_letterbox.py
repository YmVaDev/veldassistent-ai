
import cv2

from vision.detector import preprocess

img = cv2.imread("/opt/oostakkerbos/test.jpg")

tensor, ratio, pad = preprocess(img)

print("Tensor:", tensor.shape)
print("Type:", tensor.dtype)
print("Ratio:", ratio)
print("Pad:", pad)
