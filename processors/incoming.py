
from pathlib import Path
from engine.model import AIModel
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os

model = AIModel("birds")

# Dit is jouw analysefunctie
def process_incoming():

        result = model.process(str(image_path))

        print(result)


class FotoHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        extensie = os.path.splitext(event.src_path)[1].lower()

        if extensie in [".jpg", ".jpeg", ".png"]:
            # Kleine wachttijd zodat het bestand volledig is weggeschreven
            time.sleep(1)
            process_incoming(event.src_path)


incoming_map = Path("incoming")

observer = Observer()
observer.schedule(FotoHandler(), incoming_map, recursive=False)
observer.start()

print("Map wordt gemonitord...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()

