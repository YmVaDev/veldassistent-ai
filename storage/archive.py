
from pathlib import Path
import shutil
from datetime import datetime


def archive_photo(src_path):

    src = Path(src_path)

    now = datetime.now()

    archive_dir = (
        Path("archive")
        / str(now.year)
        / f"{now.month:02d}"
    )

    archive_dir.mkdir(parents=True, exist_ok=True)

    destination = archive_dir / src.name

    shutil.move(src, destination)

    return destination.as_posix()