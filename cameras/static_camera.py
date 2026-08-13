
import cv2
import time
from pathlib import Path

from logger import logger


class StaticCamera:

    def __init__(
        self,
        url: str,
        output_dir: Path,
        interval: float = 10.0
    ):
        self.url = url
        self.output_dir = Path(output_dir)
        self.interval = interval

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.running = False
        self.capture = None

    def start(self, callback):

        logger.info(
            f"Starting static camera: {self.url}"
        )

        self.running = True

        while self.running:

            try:

                self.capture = cv2.VideoCapture(
                    self.url
                )

                if not self.capture.isOpened():

                    logger.error(
                        "Could not open camera stream"
                    )

                    self.capture.release()
                    self.capture = None

                    time.sleep(5)
                    continue

                logger.info(
                    "Static camera connected"
                )

                while self.running:

                    success, frame = (
                        self.capture.read()
                    )

                    if not success:

                        logger.warning(
                            "Failed to read camera frame"
                        )

                        break

                    timestamp = int(
                        time.time() * 1000
                    )

                    frame_path = (
                        self.output_dir
                        / f"static_{timestamp}.jpg"
                    )

                    saved = cv2.imwrite(
                        str(frame_path),
                        frame
                    )

                    if not saved:

                        logger.error(
                            f"Could not save frame: "
                            f"{frame_path}"
                        )

                        continue

                    logger.info(
                        f"Static camera frame captured: "
                        f"{frame_path}"
                    )

                    callback(
                        str(frame_path)
                    )

                    time.sleep(
                        self.interval
                    )

            except Exception:

                logger.exception(
                    "Static camera error"
                )

            finally:

                if self.capture:

                    self.capture.release()
                    self.capture = None

                if self.running:

                    logger.info(
                        "Reconnecting to static camera..."
                    )

                    time.sleep(5)

    def stop(self):

        logger.info(
            "Stopping static camera"
        )

        self.running = False

        if self.capture:

            self.capture.release()
            self.capture = None

