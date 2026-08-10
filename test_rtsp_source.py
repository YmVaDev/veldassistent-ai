
from pathlib import Path

from services.rtsp_source import RTSPSource


PASSWORD = "YmkeV6581**!"

RTSP_URL = (
    f"rtsp://admin:{PASSWORD}"
    "@192.168.129.66:554/Preview_01_main"
)


def frame_received(path: str):

    print(
        f"FRAME ONTVANGEN: {path}"
    )


source = RTSPSource(
    url=RTSP_URL,
    output_dir=Path("rtsp_frames"),
    interval=10
)


try:

    source.start(
        frame_received
    )

except KeyboardInterrupt:

    print(
        "\nStoppen..."
    )

    source.stop()