
import uuid
import os
import cv2
import json
from config import BASE_DIR
from datetime import datetime

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

        COUNT_THRESHOLD = 85.0

        changed = False
        counted_species = set()

        web_path_original = src_path.replace("/opt/oostakkerbos", "")

        for det, crop in zip(detections, crops):

            filename = f"crops/{uuid.uuid4().hex}.jpg"

            cv2.imwrite(filename, crop)

            prediction = self.classifier.classify(crop)

            english = prediction["species"]
            prediction["score"] = round(float(prediction["score"]), 1)

            species = self.species_map.get(
                english,
                {
                    "birdbaseId": None,
                    "scientificName": None,
                    "habitat": None,
                    "diet": None,
                    "count": 0,
                    "best_score": 0,
                    "first_seen": None,
                    "last_seen": None,
                }
            )

            # Alleen bestaande soorten bijwerken
            if (
                english in self.species_map
                and prediction["score"] >= COUNT_THRESHOLD
                and english not in counted_species
            ):

                now = datetime.now().isoformat(timespec="seconds")

                species = self.species_map[english]

                # Eén keer tellen per soort per foto
                species["count"] = species.get("count", 0) + 1

                # Eerste waarneming
                if not species.get("first_seen"):
                    species["first_seen"] = now

                # Laatste waarneming
                species["last_seen"] = now

                # Hoogste AI-score ooit
                if prediction["score"] > species.get("best_score", 0):
                    species["best_score"] = prediction["score"]

                counted_species.add(english)
                changed = True

                print("Soort:", english)
                print("Bestaat:", english in self.species_map)
                print("Score:", prediction["score"])
                print("Threshold:", COUNT_THRESHOLD)

            results.append({
                "species": {
                    "en": english,
                    "birdbaseId": species["birdbaseId"],
                    "scientificName": species["scientificName"],
                    "habitat": species["habitat"],
                    "diet": species["diet"],
                    "count": species.get("count", 0),
                    "best_score": species.get("best_score", 0),
                    "first_seen": species.get("first_seen"),
                    "last_seen": species.get("last_seen"),
                },
                "score": prediction["score"],
                "box": det["box"],
                "crop_path": filename,
                "crop_url": f"https://oostakkerbos.be/{filename}",
            })

        # Alleen opslaan als er iets gewijzigd is
        if changed:
            with open(
                BASE_DIR / "models" / self.model_id / "classifier" / "species.json",
                "w",
                encoding="utf-8"
            ) as f:
                json.dump(self.species_map, f, indent=4, ensure_ascii=False)

        return {
            "observation": {
                "camera": "Ranger",
                "image": {
                    "original_url": f"https://oostakkerbos.be{web_path_original}",
                }
            },
            "detections": results
        }