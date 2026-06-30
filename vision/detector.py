
import cv2
import numpy as np


def letterbox(image, new_shape=(384, 384), color=(114, 114, 114)):
    h, w = image.shape[:2]

    r = min(new_shape[0] / h, new_shape[1] / w)

    new_unpad = (int(round(w * r)), int(round(h * r)))

    dw = new_shape[1] - new_unpad[0]
    dh = new_shape[0] - new_unpad[1]

    dw /= 2
    dh /= 2

    resized = cv2.resize(
        image,
        new_unpad,
        interpolation=cv2.INTER_LINEAR
    )

    top = int(round(dh - 0.1))
    bottom = int(round(dh + 0.1))
    left = int(round(dw - 0.1))
    right = int(round(dw + 0.1))

    resized = cv2.copyMakeBorder(
        resized,
        top,
        bottom,
        left,
        right,
        cv2.BORDER_CONSTANT,
        value=color
    )

    return resized, r, (dw, dh)


def preprocess(image):
    img, ratio, pad = letterbox(image)

    img = img.astype(np.float32)

    # HWC -> CHW
    img = np.transpose(img, (2, 0, 1))

    # Batch toevoegen
    img = np.expand_dims(img, axis=0)

    return img, ratio, pad


import onnxruntime as ort


from config import MODEL_DIR
MODEL = MODEL_DIR / "birds" / "detector" / "bird_crop_detector_accurate_yolox_tiny.onnx"

session = ort.InferenceSession(MODEL)


def inference(image):

    tensor, ratio, pad = preprocess(image)

    input_name = session.get_inputs()[0].name

    output = session.run(
        None,
        {
            input_name: tensor
        }
    )[0]

    return output, ratio, pad

def objectness(output):

    scores = output[0, :, 4]

    order = np.argsort(scores)[::-1]

    result = []

    for i in order[:20]:

        result.append(
            {
                "index": int(i),
                "score": float(scores[i]),
                "raw": output[0, i]
            }
        )

    return result

def debug_boxes(output):

    scores = output[0, :, 4]

    order = np.argsort(scores)[::-1]

    for i in order[:10]:

        row = output[0, i]

        print(
            f"{i:4}",
            f"score={scores[i]:.3f}",
            f"cx={row[0]:.3f}",
            f"cy={row[1]:.3f}",
            f"w={row[2]:.3f}",
            f"h={row[3]:.3f}",
        )

def generate_grids_and_strides(
    input_size=384,
    strides=(8, 16, 32),
):
    grids = []
    expanded_strides = []

    for stride in strides:

        hsize = input_size // stride
        wsize = input_size // stride

        xv, yv = np.meshgrid(
            np.arange(wsize),
            np.arange(hsize)
        )

        grid = np.stack((xv, yv), axis=2).reshape(-1, 2)

        grids.append(grid)

        expanded_strides.append(
            np.full((grid.shape[0], 1), stride)
        )

    grids = np.concatenate(grids, axis=0)
    expanded_strides = np.concatenate(
        expanded_strides,
        axis=0,
    )

    return grids, expanded_strides

def decode_outputs(output):

    grids, expanded_strides = generate_grids_and_strides()

    predictions = output[0].copy()

    predictions[:, 0:2] = (
        predictions[:, 0:2] + grids
    ) * expanded_strides

    predictions[:, 2:4] = (
        np.exp(predictions[:, 2:4])
        * expanded_strides
    )

    return predictions

def calculate_scores(predictions):

    objectness = predictions[:, 4]

    class_scores = predictions[:, 5:]

    best_class = np.argmax(class_scores, axis=1)

    best_score = np.max(class_scores, axis=1)

    scores = objectness * best_score

    return scores, best_class

def nms_boxes(predictions, scores, score_threshold=0.30, nms_threshold=0.45):

    boxes = []

    valid_scores = []

    valid_indices = []

    for i in range(len(scores)):

        if scores[i] < score_threshold:
            continue

        cx, cy, w, h = predictions[i, :4]

        x = cx - w / 2
        y = cy - h / 2

        boxes.append([
            float(x),
            float(y),
            float(w),
            float(h),
        ])

        valid_scores.append(float(scores[i]))
        valid_indices.append(i)

    indices = cv2.dnn.NMSBoxes(
        boxes,
        valid_scores,
        score_threshold,
        nms_threshold,
    )

    result = []

    if len(indices) == 0:
        return result

    indices = np.array(indices).flatten()

    for idx in indices:

        i = valid_indices[idx]

        result.append(
            {
                "box": boxes[idx],
                "score": valid_scores[idx],
                "prediction_index": i,
            }
        )

    return result

def scale_boxes(detections, ratio, pad):

    dw, dh = pad

    scaled = []

    for det in detections:

        x, y, w, h = det["box"]

        x1 = (x - dw) / ratio
        y1 = (y - dh) / ratio

        x2 = (x + w - dw) / ratio
        y2 = (y + h - dh) / ratio

        det = det.copy()

        det["box"] = [
            int(round(x1)),
            int(round(y1)),
            int(round(x2)),
            int(round(y2)),
        ]

        scaled.append(det)

    return scaled

def crop_detections(image, detections):

    crops = []

    h, w = image.shape[:2]

    for det in detections:

        x1, y1, x2, y2 = det["box"]

        x1 = max(0, x1)
        y1 = max(0, y1)

        x2 = min(w, x2)
        y2 = min(h, y2)

        crop = image[y1:y2, x1:x2]

        crops.append(crop)

    return crops
