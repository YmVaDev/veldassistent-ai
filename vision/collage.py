
import cv2
import math
import numpy as np


def make_collage(original_image, image_paths, size=300):

    images = []

    for path in image_paths:

        img = cv2.imread(path)

        if img is None:
            continue

        img = cv2.resize(img, (size, size))
        images.append(img)

    if not images:
        return None

    filename = "crops/collage.jpg"

    # ==========================================
    # 1 vogel
    # ==========================================

    if len(images) == 1:

        original = cv2.resize(original_image, (size * 2, size))
        crop = cv2.resize(images[0], (size * 2, size))

        final = np.vstack([original, crop])

        cv2.imwrite(filename, final)

        return filename

    # ==========================================
    # 2 of meer vogels
    # ==========================================

    cols = 2
    rows = math.ceil(len(images) / cols)

    original = cv2.resize(original_image, (size * cols, size))

    while len(images) < rows * cols:
        images.append(np.zeros((size, size, 3), dtype=np.uint8))

    rows_img = []

    for r in range(rows):

        row = np.hstack(images[r * cols:(r + 1) * cols])

        rows_img.append(row)

    collage = np.vstack(rows_img)

    final = np.vstack([original, collage])

    cv2.imwrite(filename, final)

    return filename
