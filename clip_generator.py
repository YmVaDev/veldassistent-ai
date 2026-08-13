
from pathlib import Path
import subprocess
import tempfile
import time


BUFFER_DIR = Path("buffer")
OUTPUT_DIR = Path("clips_test")

CLIP_DURATION = 30
BEFORE_SECONDS = 15
AFTER_SECONDS = CLIP_DURATION - BEFORE_SECONDS


def get_complete_segments():
    segments = sorted(BUFFER_DIR.glob("segment_*.ts"))

    # Laatste segment wordt nog geschreven.
    if len(segments) < 2:
        return []

    return segments[:-1]


def create_concat_file(segments):

    f = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        delete=False,
        encoding="utf-8"
    )

    concat_file = Path(f.name)

    for segment in segments:
        f.write(
            f"file '{segment.resolve().as_posix()}'\n"
        )

    f.close()

    return concat_file


def create_clip(duration=30, before=15, filename="test_clip.mp4"):

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    after = duration - before

    if before < 0:
        raise ValueError("before mag niet negatief zijn")

    if after < 0:
        raise ValueError("before kan niet groter zijn dan duration")

    print()
    print("================================")
    print("CLIP TEST")
    print("================================")
    print(f"Totale duur  : {duration}s")
    print(f"Voor detectie: {before}s")
    print(f"Na detectie  : {after}s")
    print()

    # ---------------------------------------------------------
    # Simuleer AI-detectie NU
    # ---------------------------------------------------------

    print(">>> DETECTIE <<<")
    print()

    # ---------------------------------------------------------
    # Wachten op post-buffer
    # ---------------------------------------------------------

    if after > 0:

        print(
            f"Wachten op {after} seconden post-buffer..."
        )

        time.sleep(after)

        print("Post-buffer beschikbaar.")
        print()

    # ---------------------------------------------------------
    # Complete segmenten
    # ---------------------------------------------------------

    segments = get_complete_segments()

    if not segments:
        print("Niet genoeg buffersegmenten.")
        return None

    print(
        f"Complete segmenten: {len(segments)}"
    )

    # ---------------------------------------------------------
    # Concat
    # ---------------------------------------------------------

    concat_file = create_concat_file(
        segments
    )

    output_file = OUTPUT_DIR / filename

    # ---------------------------------------------------------
    # FFmpeg
    # ---------------------------------------------------------

    command = [
        "ffmpeg",
        "-y",

        "-fflags", "+genpts",

        "-sseof", f"-{duration}",

        "-f", "concat",
        "-safe", "0",

        "-i", str(concat_file),

        "-t", str(duration),

        "-c:v", "libx264",
        "-preset", "veryfast",

        "-an",

        str(output_file)
    ]

    print("FFmpeg maakt clip...")

    result = subprocess.run(command)

    concat_file.unlink(missing_ok=True)

    if result.returncode != 0:

        print()
        print("❌ FFmpeg fout.")

        return None

    # ---------------------------------------------------------
    # Werkelijke duur controleren
    # ---------------------------------------------------------

    probe = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
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
    print()

    return output_file

if __name__ == "__main__":

    create_clip(
        duration=30,
        before=15,
        filename="test_30s.mp4"
    )