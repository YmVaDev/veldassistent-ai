
from pathlib import Path
import subprocess
import time


# ============================================================
# CONFIG
# ============================================================

RTSP_URL = "rtsp://admin:YmkeV6581**!@192.168.129.66:554/Preview_01_main"

BUFFER_DIR = Path("buffer")

SEGMENT_TIME = 5
BUFFER_SECONDS = 120


# ============================================================
# BUFFER
# ============================================================

def cleanup_buffer():

    now = time.time()
    max_age = BUFFER_SECONDS + 10

    for file in BUFFER_DIR.glob("segment_*.ts"):

        try:
            age = now - file.stat().st_mtime

            if age > max_age:
                file.unlink()

        except FileNotFoundError:
            pass


def start_buffer():

    BUFFER_DIR.mkdir(parents=True, exist_ok=True)

    print("================================")
    print("Veldassistent RTSP buffer")
    print("================================")
    print(f"Buffer directory : {BUFFER_DIR}")
    print(f"Segment duration : ~{SEGMENT_TIME}s")
    print(f"Buffer duration  : ~{BUFFER_SECONDS}s")
    print()

    # Oude testbuffer verwijderen
    for file in BUFFER_DIR.glob("segment_*.ts"):
        file.unlink()

    output_pattern = BUFFER_DIR / "segment_%Y%m%d_%H%M%S.ts"

    command = [
        "ffmpeg",

        "-rtsp_transport", "tcp",

        "-i", RTSP_URL,

        "-an",

        "-c", "copy",

        "-f", "segment",
        "-segment_time", str(SEGMENT_TIME),
        "-strftime", "1",
        "-reset_timestamps", "1",

        str(output_pattern)
    ]

    print("Start FFmpeg...")
    print()

    process = subprocess.Popen(command)

    try:

        while True:

            time.sleep(2)

            cleanup_buffer()

            segments = sorted(
                BUFFER_DIR.glob("segment_*.ts")
            )

            print(
                f"\rBuffer: {len(segments)} segmenten",
                end=""
            )

    except KeyboardInterrupt:

        print()
        print("Stopping buffer...")

        process.terminate()

        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

        print("Buffer stopped.")


if __name__ == "__main__":
    start_buffer()