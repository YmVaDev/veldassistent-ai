
import time
import cv2
import subprocess

from pathlib import Path
from logger import logger
from onvif import ONVIFCamera


class PTZCamera:

    def __init__(
        self,
        rtsp_url: str,
        onvif_host: str,
        onvif_port: int,
        username: str,
        password: str,
        output_dir: Path,
        camera_key: str = "wz520",
        interval: float = 30.0,
        settle_time: float = 3.0,
    ):
        self.rtsp_url = rtsp_url
        self.onvif_host = onvif_host
        self.onvif_port = onvif_port
        self.username = username
        self.password = password

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.camera_key = camera_key
        self.interval = interval
        self.settle_time = settle_time

        self.running = False
        self.capture = None

        self.camera = None
        self.ptz = None
        self.profile = None

    def connect(self):

        logger.info(
            f"Connecting to PTZ camera: "
            f"{self.onvif_host}:{self.onvif_port}"
        )

        self.camera = ONVIFCamera(
            self.onvif_host,
            self.onvif_port,
            self.username,
            self.password,
        )

        media = self.camera.create_media_service()
        self.ptz = self.camera.create_ptz_service()

        profiles = media.GetProfiles()

        if not profiles:
            raise RuntimeError(
                "No ONVIF media profiles found"
            )

        self.profile = profiles[0]

        logger.info(
            f"ONVIF connected, profile: "
            f"{self.profile.token}"
        )

    def capture_frame(self):
        timestamp = int(time.time() * 1000)

        frame_path = (
            self.output_dir / f"ptz_{timestamp}.jpg"
        )

        command = [
            "ffmpeg",
            "-rtsp_transport", "tcp",
            "-i", self.rtsp_url,
            "-frames:v", "1",
            "-q:v", "2",
            "-y",
            str(frame_path),
        ]

        try:
            result = subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                timeout=15,
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(
                "FFmpeg timed out while capturing PTZ frame"
            )

        if result.returncode != 0:
            raise RuntimeError(
                f"FFmpeg failed to capture PTZ frame: "
                f"{result.stderr[-2000:]}"
            )

        if not frame_path.exists() or frame_path.stat().st_size == 0:
            raise RuntimeError(
                f"FFmpeg did not create a valid frame: {frame_path}"
            )

        logger.info(f"PTZ frame captured: {frame_path}")

        return frame_path

    def start(self, process_callback):

        logger.info(
            f"Starting PTZ camera monitoring: "
            f"{self.camera_key}"
        )

        self.running = True

        # -------------------------------------------------
        # ONVIF verbinding
        # -------------------------------------------------

        try:

            self.connect()

        except Exception:

            logger.exception(
                "Failed to connect to PTZ camera via ONVIF"
            )

        # -------------------------------------------------
        # Monitoring loop
        # -------------------------------------------------

        while self.running:

            cycle_start = time.time()

            try:

                frame_path = self.capture_frame()

                process_callback(
                    str(frame_path),
                    self.camera_key
                )

            except Exception:

                logger.exception(
                    "Exception while capturing/analyzing "
                    "PTZ camera frame"
                )

            elapsed = time.time() - cycle_start

            sleep_time = max(
                0,
                self.interval - elapsed
            )

            if sleep_time > 0:

                time.sleep(
                    sleep_time
                )

        logger.info(
            "PTZ camera monitoring loop stopped"
        )

    def stop(self):

        logger.info(
            "Stopping PTZ camera"
        )

        self.running = False

        if self.capture:

            self.capture.release()
            self.capture = None