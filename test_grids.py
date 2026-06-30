
from vision.detector import generate_grids_and_strides

grids, strides = generate_grids_and_strides()

print(grids.shape)
print(strides.shape)

print(grids[:5])
print(strides[:5])

print("Laatste grid:")
print(grids[-1])
