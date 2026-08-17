
import subprocess
import time
from pathlib import Path

from logger import logger


class StaticCamera:

    def __init__(
        self,
        url: str,
        output_dir: Path,
        interval: float = 10.0,
        camera_key: str = "ranger"
    ):
        self.url = url
        self.output_dir = Path(output_dir)
        self.interval = interval
        self.camera_key = camera_key

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.running = False

    def start(self, callback):

        logger.info(
            f"Starting static camera: {self.url}"
        )

        self.running = True

        while self.running:

            frame_path = None

            try:

                timestamp = int(
                    time.time() * 1000
                )

                frame_path = (
                    self.output_dir
                    / f"static_{timestamp}.jpg"
                )

                command = [
                    "ffmpeg",
                    "-rtsp_transport",
                    "tcp",
                    "-i",
                    self.url,
                    "-frames:v",
                    "1",
                    "-q:v",
                    "2",
                    "-y",
                    str(frame_path),
                ]

                logger.info(
                    "Capturing static camera frame with FFmpeg"
                )

                result = subprocess.run(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=20,
                )

                if result.returncode != 0:

                    logger.error(
                        "FFmpeg failed to capture camera frame: "
                        f"{result.stderr[-1000:]}"
                    )

                    if frame_path.exists():
                        frame_path.unlink()

                    time.sleep(5)
                    continue

                if not frame_path.exists():

                    logger.error(
                        "FFmpeg completed but no frame was created"
                    )

                    time.sleep(5)
                    continue

                logger.info(
                    f"Static camera frame captured: "
                    f"{frame_path}"
                )

                callback(
                    str(frame_path),
                    self.camera_key
                )

            except subprocess.TimeoutExpired:

                logger.warning(
                    "FFmpeg camera capture timed out"
                )

                if frame_path and frame_path.exists():
                    frame_path.unlink()

            except Exception:

                logger.exception(
                    "Static camera error"
                )

                if frame_path and frame_path.exists():
                    frame_path.unlink()

            if self.running:

                time.sleep(
                    self.interval
                )

    def stop(self):

        logger.info(
            "Stopping static camera"
        )

        self.running = False

