
from pathlib import Path
import subprocess
import tempfile
import time


BUFFER_DIR = Path("buffer")
OUTPUT_DIR = Path("clips_test")

SEGMENT_TIME = 5

BEFORE_SECONDS = 15
CLIP_DURATION = 30


def create_clip(duration=30, before=15, filename="test_clip.mp4"):

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    after = duration - before

    print()
    print("================================")
    print("CLIP TEST")
    print("================================")
    print(f"Totale duur  : {duration}s")
    print(f"Voor detectie: {before}s")
    print(f"Na detectie  : {after}s")
    print()

    # ---------------------------------------------------------
    # Simuleer detectie
    # ---------------------------------------------------------

    print(">>> DETECTIE <<<")
    print()

    if after > 0:
        print(
            f"Wachten op {after} seconden post-buffer..."
        )

        time.sleep(after)

        print("Post-buffer beschikbaar.")
        print()

    # ---------------------------------------------------------
    # Complete segmenten ophalen
    # ---------------------------------------------------------

    segments = get_complete_segments()

    if not segments:
        print("Niet genoeg buffersegmenten.")
        return None

    print(f"Complete segmenten: {len(segments)}")

    # ---------------------------------------------------------
    # Concat-bestand
    # ---------------------------------------------------------

    concat_file = create_concat_file(segments)

    temp_file = OUTPUT_DIR / "buffer_temp.mp4"
    output_file = OUTPUT_DIR / filename

    # ---------------------------------------------------------
    # STAP 1
    # Maak één normale videostream van de buffer
    # ---------------------------------------------------------

    print()
    print("Stap 1: volledige buffer samenvoegen...")

    command = [
        "ffmpeg",
        "-y",

        "-fflags", "+genpts",

        "-f", "concat",
        "-safe", "0",

        "-i", str(concat_file),

        "-c:v", "libx264",
        "-preset", "veryfast",

        "-an",

        str(temp_file)
    ]

    result = subprocess.run(command)

    concat_file.unlink(missing_ok=True)

    if result.returncode != 0:

        print("❌ Buffer kon niet worden samengevoegd.")
        return None

    # ---------------------------------------------------------
    # Werkelijke bufferdduur bepalen
    # ---------------------------------------------------------

    probe = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(temp_file)
        ],
        capture_output=True,
        text=True
    )

    try:
        buffer_duration = float(
            probe.stdout.strip()
        )
    except ValueError:

        print("❌ Kon bufferdduur niet bepalen.")

        temp_file.unlink(missing_ok=True)

        return None

    print(
        f"Werkelijke bufferdduur: "
        f"{buffer_duration:.2f}s"
    )

    if buffer_duration < duration:

        print(
            f"❌ Buffer bevat maar "
            f"{buffer_duration:.2f}s."
        )

        temp_file.unlink(missing_ok=True)

        return None

    # ---------------------------------------------------------
    # STAP 2
    # Exact laatste X seconden pakken
    # ---------------------------------------------------------

    print()
    print(
        f"Stap 2: laatste {duration}s exporteren..."
    )

    start = buffer_duration - duration

    command = [
        "ffmpeg",
        "-y",

        "-ss", str(start),

        "-i", str(temp_file),

        "-t", str(duration),

        "-c:v", "libx264",
        "-preset", "veryfast",

        "-an",

        str(output_file)
    ]

    result = subprocess.run(command)

    temp_file.unlink(missing_ok=True)

    if result.returncode != 0:

        print("❌ Clip kon niet worden gemaakt.")

        return None

    # ---------------------------------------------------------
    # Werkelijke clipduur controleren
    # ---------------------------------------------------------

    probe = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(output_file)
        ],
        capture_output=True,
        text=True
    )

    actual_duration = probe.stdout.strip()

    print()
    print("================================")
    print("CLIP GEMAAKT")
    print("================================")
    print(f"Bestand : {output_file}")
    print(f"Duur    : {actual_duration}s")
    print("================================")
    print()

    return output_file

if __name__ == "__main__":
    create_clip()