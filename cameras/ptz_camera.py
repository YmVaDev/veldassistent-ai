
import time
import cv2

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

        if self.capture is None:

            self.capture = cv2.VideoCapture(
                self.rtsp_url,
                cv2.CAP_FFMPEG,
                [
                    cv2.CAP_PROP_OPEN_TIMEOUT_MSEC,
                    5000,
                    cv2.CAP_PROP_READ_TIMEOUT_MSEC,
                    5000,
                ]
            )

        if not self.capture.isOpened():

            raise RuntimeError(
                "Could not open PTZ camera RTSP stream"
            )

        success, frame = self.capture.read()

        if not success:

            raise RuntimeError(
                "Could not read PTZ camera frame"
            )

        timestamp = int(
            time.time() * 1000
        )

        frame_path = (
            self.output_dir
            / f"ptz_{timestamp}.jpg"
        )

        if not cv2.imwrite(
            str(frame_path),
            frame
        ):
            raise RuntimeError(
                f"Could not save frame: {frame_path}"
            )

        logger.info(
            f"PTZ frame captured: {frame_path}"
        )

        return frame_path

    def stop(self):

        logger.info(
            "Stopping PTZ camera"
        )

        self.running = False

        if self.capture:

            self.capture.release()
            self.capture = None