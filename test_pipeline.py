
from vision.pipeline import detect_and_classify

results = detect_and_classify("/opt/oostakkerbos/test.jpg")

print()

for bird in results:

    print("-------------------------")
    print("🐦", bird["species"])
    print("Score:", round(bird["score"], 2))
    print("Box:", bird["box"])

