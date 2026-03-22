import logging
from datetime import date
from pathlib import Path

from rr_core.git import git_commit_all, git_has_changes
from rr_core.index import generate_index_md, load_index, resolve_filename, save_index

logger = logging.getLogger(__name__)


def remove_asset(
    file_path: str,
    project_root: Path,
    index_path: Path | None = None,
    index_md_path: Path | None = None,
) -> dict:
    """Remove a file from the project and update the index.

    Returns {"removed_from_index": bool, "removed_from_disk": bool, "warning": str | None}
    """
    if index_path is None:
        index_path = project_root / "index.json"
    if index_md_path is None:
        index_md_path = project_root / "index.md"

    index = load_index(index_path)
    file_path = resolve_filename(index, file_path)

    abs_path = project_root / file_path
    on_disk = abs_path.exists()
    in_index = any(e["path"] == file_path for e in index["files"])

    if not on_disk and not in_index:
        raise FileNotFoundError(f"{file_path} not found on disk or in index")

    removed_from_disk = False
    removed_from_index = False
    warning = None

    if on_disk:
        abs_path.unlink()
        removed_from_disk = True
        logger.debug("Deleted file: %s", abs_path)

    if in_index:
        index["files"] = [e for e in index["files"] if e["path"] != file_path]
        removed_from_index = True
        logger.debug("Removed from index: %s", file_path)
    else:
        warning = f"{file_path} was not in the index"
        logger.info("Warning: %s", warning)

    index["last_rebuilt"] = date.today().isoformat()
    save_index(index_path, index)
    generate_index_md(index_md_path, index)

    filename = Path(file_path).name
    if git_has_changes(project_root):
        git_commit_all(project_root, f"Remove: {filename}")

    return {
        "removed_from_index": removed_from_index,
        "removed_from_disk": removed_from_disk,
        "warning": warning,
    }
