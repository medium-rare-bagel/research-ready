import shutil
from pathlib import Path


def file_asset(src: Path, new_name: str, dest_dir: Path) -> Path:
    dest = dest_dir / new_name
    shutil.move(str(src), str(dest))
    return dest
