import shutil
from pathlib import Path

from rr_core.git import git_commit_all
from rr_core.index import add_entry, generate_index_md, load_index, save_index


def file_asset(
    src: Path,
    new_name: str,
    dest_dir: Path,
    index_path: Path | None = None,
    index_md_path: Path | None = None,
    description: str = "",
    project_root: Path | None = None,
    allowed_dirs: list[str] | None = None,
) -> Path:
    if allowed_dirs is not None and dest_dir.name not in allowed_dirs:
        raise ValueError(f"'{dest_dir.name}' is not in the project's allowed directories: {allowed_dirs}")
    dest = dest_dir / new_name
    shutil.move(str(src), str(dest))
    if index_path is not None:
        index = load_index(index_path)
        add_entry(index, filename=new_name, directory=dest_dir.name, description=description)
        save_index(index_path, index)
        if index_md_path is not None:
            generate_index_md(index_md_path, index)
    if project_root is not None:
        git_commit_all(project_root, f"File: {new_name} → {dest_dir.name}/")
    return dest
