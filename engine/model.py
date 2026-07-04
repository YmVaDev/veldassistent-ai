
import uuid
import os
import cv2
import json
from config import BASE_DIR

from vision.detector import (
    Detector,
    decode_outputs,
    calculate_scores,
    nms_boxes,
    scale_boxes,
    crop_detections,
)

from vision.classifier import (
    Classifier
)

class AIModel:

    def __init__(self, model_name: str):
        self.model_id = model_name
        self.detector = Detector(model_name)
        self.classifier = Classifier(model_name)

        with open(
            BASE_DIR / "models" / self.model_id / "classifier" / "species.json",
            encoding="utf-8"
        ) as f:
            self.species_map = json.load(f)

    def process(self, src_path):

        image = cv2.imread(src_path)

        output, ratio, pad = self.detector.inference(image)

        decoded = decode_outputs(output, self.detector.input_size)

        scores, classes = calculate_scores(decoded)

        print(f"Totaal aantal voorspellingen: {len(scores)}")
        print(f"Hoogste score: {max(scores):.3f}")
        print(f"Aantal scores > 0.20: {(scores > 0.20).sum()}")

        detections = nms_boxes(decoded, scores)

        print(f"Aantal detecties na NMS: {len(detections)}")

        detections = scale_boxes(detections, ratio, pad)

        crops = crop_detections(image, detections)

        print(f"Detecties: {len(detections)}")
        print(f"Crops: {len(crops)}")

        results = []

        os.makedirs("crops", exist_ok=True)

        for det, crop in zip(detections, crops):

            filename = f"crops/{uuid.uuid4().hex}.jpg"

            web_path_original = src_path.replace ("/opt/oostakkerbos","")

            cv2.imwrite(filename, crop)

            prediction = self.classifier.classify(crop)

            english = prediction["species"]

            species = self.species_map.get(
                english,
                {
                    "birdbaseId": None,
                    "scientificName": None,
                    "habitat": None,
                    "diet": None
                }
            )

            prediction["species"] = {
                "birdbaseId": species["birdbaseId"],
                "scientificName": species["scientificName"],
                "habitat": species["habitat"],
                "diet": species["diet"]
            }

            prediction["score"] = round(float(prediction["score"]), 1)

            results.append({
                "species": {
                    "en": english,
                    "birdbaseId": species["birdbaseId"],
                    "scientificName": species["scientificName"],
                    "habitat": species["habitat"],
                    "diet": species["diet"]
                },
                "score": prediction["score"],
                "box": det["box"],
                "crop_path": filename,
                "crop_url": f"https://oostakkerbos.be/{filename}",
            })

        api_response = {
            "success": True,
            "api_version": "1.0",

            "observation": {
                "camera": "Ranger",
                "image": {
                    "original_url": f"https://oostakkerbos.be{web_path_original}",
                }
            },

            "summary": {
                "count": len(results)
            },

            "detections": results
        }

        return {
            "observation": {
                "camera": "Ranger",
                "image": {
                    "original_url": f"https://oostakkerbos.be{web_path_original}",
                }
            },
            "detections": results
        }