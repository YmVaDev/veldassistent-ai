
import subprocess
import time
from pathlib import Path

from logger import logger

class RTSPSource:

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

    def start(self, callback):

        logger.info(
            f"Starting RTSP source: {self.url}"
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
                    / f"rtsp_{timestamp}.jpg"
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
                    "Capturing RTSP frame with FFmpeg"
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
                        "FFmpeg failed to capture RTSP frame: "
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
                    f"RTSP frame captured: {frame_path}"
                )

                callback(
                    str(frame_path)
                )

            except subprocess.TimeoutExpired:

                logger.warning(
                    "FFmpeg RTSP capture timed out"
                )

                if frame_path and frame_path.exists():
                    frame_path.unlink()

                time.sleep(5)

            except Exception:

                logger.exception(
                    "RTSP source error"
                )

                if frame_path and frame_path.exists():
                    frame_path.unlink()

                time.sleep(5)

            if self.running:

                time.sleep(
                    self.interval
                )

    def stop(self):

        logger.info(
            "Stopping RTSP source"
        )

        self.running = False

