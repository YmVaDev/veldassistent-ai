from pathlib import Path
import json
import time
import requests

LABELS = Path("models/birds/onnx/convnext_v1_tiny_eu_common_labels.txt")
OUTPUT = Path("birds/species.json")

species = {}

labels = LABELS.read_text(encoding="utf-8").splitlines()

for i, english in enumerate(labels, start=1):

    english = english.strip()

    if not english:
        continue

    print(f"[{i}/{len(labels)}] {english}")

    try:

        search = requests.get(
            "https://api.gbif.org/v1/species/search",
            params={
                "q": english,
                "limit": 10
            },
            timeout=15
        ).json()

        result = None

        for item in search.get("results", []):

            if item.get("rank") != "SPECIES":
                continue

            if item.get("taxonomicStatus") == "ACCEPTED":
                result = item
                break

            if result is None:
                result = item

        if result is None:

            print("   ❌ Niet gevonden")

            species[english] = {
                "la": None,
                "gbif": None
            }

            continue

        gbif = result["key"]
        latin = result["scientificName"]

        species[english] = {
            "la": latin,
            "gbif": gbif
        }

        print(f"   ✅ {latin}")

    except Exception as e:

        print(f"   ❌ {e}")

        species[english] = {
            "la": None,
            "gbif": None
        }

    time.sleep(0.1)

# Altijd toevoegen
species["Unknown"] = {
    "la": None,
    "gbif": None
}

OUTPUT.parent.mkdir(exist_ok=True)

OUTPUT.write_text(
    json.dumps(
        species,
        indent=4,
        ensure_ascii=False
    ),
    encoding="utf-8"
)

print("")
print("================================")
print(f"Soorten verwerkt : {len(species)}")
print(f"JSON opgeslagen  : {OUTPUT}")
print("================================")