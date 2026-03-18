import shutil
from pathlib import Path

from rr.index import add_entry, generate_index_md, load_index, save_index


def file_asset(
    src: Path,
    new_name: str,
    dest_dir: Path,
    index_path: Path | None = None,
    index_md_path: Path | None = None,
    description: str = "",
) -> Path:
    dest = dest_dir / new_name
    shutil.move(str(src), str(dest))
    if index_path is not None:
        index = load_index(index_path)
        add_entry(index, filename=new_name, directory=dest_dir.name, description=description)
        save_index(index_path, index)
        if index_md_path is not None:
            generate_index_md(index_md_path, index)
    return dest
