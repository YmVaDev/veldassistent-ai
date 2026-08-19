
import uuid
import os
import cv2
import json
from config import MODEL_DIR
from datetime import datetime

from vision.detector import (
    Detector,
    decode_outputs,
    calculate_scores,
    nms_boxes,
    scale_boxes,
    crop_detections,
)

from vision.classifier import Classifier
from vision.model_config import load_model_config

from domain.bounding_box import BoundingBox
from domain.observation import Observation


class AIModel:

    def __init__(self, model_name: str):

        self.model_name = model_name
        self.database_id = None

        self.config = load_model_config(
            model_name
        )

        self.detector = Detector(
            model_name
        )

        self.classifier = Classifier(
            model_name
        )

        # -------------------------------------------------
        # Species data
        # -------------------------------------------------

        with open(
            MODEL_DIR
            / self.model_name
            / self.config["classifier"]["species"],
            encoding="utf-8"
        ) as f:

            self.species_map = json.load(f)

        # -------------------------------------------------
        # Species settings
        # -------------------------------------------------

        settings_path = (
            MODEL_DIR
            / self.model_name
            / "classifier"
            / "species_settings.json"
        )

        with open(
            settings_path,
            encoding="utf-8"
        ) as f:

            self.species_settings = json.load(f)


    def process(self, src_path):

        observations = []

        image = cv2.imread(
            src_path
        )

        output, ratio, pad = (
            self.detector.inference(image)
        )

        decoded = decode_outputs(
            output,
            self.detector.input_size
        )

        scores, classes = calculate_scores(
            decoded
        )

        detections = nms_boxes(
            decoded,
            scores
        )

        detections = scale_boxes(
            detections,
            ratio,
            pad
        )

        crops = crop_detections(
            image,
            detections
        )

        results = []

        os.makedirs(
            "crops",
            exist_ok=True
        )

        COUNT_THRESHOLD = 85.0

        changed = False
        counted_species = set()

        web_path_original = (
            src_path.replace(
                "/opt/oostakkerbos",
                ""
            )
        )

        # =================================================
        # Verwerk iedere detectie
        # =================================================

        for det, crop in zip(
            detections,
            crops
        ):

            # -------------------------------------------------
            # Top-5 classificatie
            # -------------------------------------------------

            predictions = (
                self.classifier.classify(
                    crop
                )
            )

            # Top-1
            prediction = predictions[0]

            # Alleen echte herkenningen worden observations
            OBSERVATION_THRESHOLD = 50.0

            if prediction.score < OBSERVATION_THRESHOLD:
                continue

            english = prediction.species

            if english.strip().lower() == "unknown":
                continue

            # -------------------------------------------------
            # Crop alleen bewaren bij geldige observation
            # -------------------------------------------------

            filename = (
                f"crops/{uuid.uuid4().hex}.jpg"
            )

            cv2.imwrite(
                filename,
                crop
            )

            # -------------------------------------------------
            # Species uit database
            # -------------------------------------------------

            db_species = (
                self.database.get_species_by_english(
                    english,
                    self.database_id
                )
            )

            if db_species:

                priority = db_species["priority"]
                clip_duration = db_species["clip_duration"]

            else:

                priority = "interesting"
                clip_duration = 30

            # -------------------------------------------------
            # Bounding box
            # -------------------------------------------------

            box = BoundingBox(
                *det["box"]
            )

            # -------------------------------------------------
            # Observation
            # -------------------------------------------------

            observation = Observation(
                photo=None,
                model_id=self.database_id,
                box=box,
                crop_path=filename
            )

            # Alle Top-5 voorspellingen opslaan
            observation.predictions.extend(
                predictions
            )

            observations.append(
                observation
            )

            # -------------------------------------------------
            # Species informatie
            # -------------------------------------------------

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

            # -------------------------------------------------
            # Soort tellen
            # -------------------------------------------------

            if (
                english in self.species_map
                and prediction.score >= COUNT_THRESHOLD
                and english not in counted_species
            ):

                now = datetime.now().isoformat(
                    timespec="seconds"
                )

                species = self.species_map[
                    english
                ]

                # Eén keer tellen per soort per foto
                species["count"] = (
                    species.get("count") or 0
                ) + 1

                # Eerste waarneming
                if not species.get(
                    "first_seen"
                ):

                    species["first_seen"] = now

                # Laatste waarneming
                species["last_seen"] = now

                # Hoogste AI-score ooit
                if prediction.score > (
                    species.get("best_score") or 0
                ):

                    species["best_score"] = (
                        prediction.score
                    )

                counted_species.add(
                    english
                )

                changed = True

            # -------------------------------------------------
            # Resultaat voor API
            # -------------------------------------------------

            results.append({

                "species": {
                    "en": english,
                    "birdbaseId": species[
                        "birdbaseId"
                    ],
                    "scientificName": species[
                        "scientificName"
                    ],
                    "habitat": species[
                        "habitat"
                    ],
                    "diet": species[
                        "diet"
                    ],
                    "count": species.get(
                        "count",
                        0
                    ),
                    "best_score": species.get(
                        "best_score",
                        0
                    ),
                    "first_seen": species.get(
                        "first_seen"
                    ),
                    "last_seen": species.get(
                        "last_seen"
                    ),
                },

                # Top-1 score
                "score": prediction.score,

                # Volledige Top-5
                "predictions": [
                    {
                        "species": p.species,
                        "score": p.score,
                        "rank": p.rank
                    }
                    for p in predictions
                ],

                "priority": priority,

                "clip_duration": clip_duration,

                "box": det["box"],

                "crop_path": filename,

                "crop_url": (
                    f"https://oostakkerbos.be/"
                    f"{filename}"
                ),
            })

        # =================================================
        # Species JSON opslaan indien gewijzigd
        # =================================================

        if changed:

            with open(
                MODEL_DIR
                / self.model_name
                / self.config[
                    "classifier"
                ]["species"],
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    self.species_map,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

        # =================================================
        # Resultaat
        # =================================================

        return {

            "observation": {

                "camera": "Ranger",

                "image": {

                    "original_url": (
                        "https://oostakkerbos.be"
                        f"{web_path_original}"
                    ),
                },
            },

            "detections": results,

            "objects": observations
        }