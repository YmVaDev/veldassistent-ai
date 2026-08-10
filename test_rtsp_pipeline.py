
from pathlib import Path

from services.rtsp_source import RTSPSource
from engine.engine import Engine
from engine.loader import load_models


PASSWORD = "YmkeV6581**!"

RTSP_URL = (
    f"rtsp://admin:{PASSWORD}"
    "@192.168.129.66:554/Preview_01_main"
)


# -------------------------
# Engine initialiseren
# -------------------------

engine = Engine()

for model in load_models():
    engine.add_model(model)

print(
    f"Models loaded: {len(engine.models)}"
)


# -------------------------
# RTSP frame verwerken
# -------------------------

def process_rtsp_frame(path: str):

    print(
        f"\nRTSP FRAME: {path}"
    )

    try:

        result = engine.process(
            path
        )

        print(
            "ANALYSIS RESULT:"
        )

        print(
            result
        )

    except Exception as e:

        print(
            "ERROR DURING ANALYSIS:"
        )

        print(
            e
        )


# -------------------------
# RTSP starten
# -------------------------

source = RTSPSource(
    url=RTSP_URL,
    output_dir=Path("rtsp_frames"),
    interval=10
)


try:

    source.start(
        process_rtsp_frame
    )

except KeyboardInterrupt:

    print(
        "\nStopping..."
    )

    source.stop()