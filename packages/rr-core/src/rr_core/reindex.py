from datetime import date
from pathlib import Path
import logging

from rr_core.git import git_commit_all, git_has_changes
from rr_core.index import generate_index_md, load_index, save_index

logger = logging.getLogger(__name__)


def reindex(
    project_root: Path,
    config: dict,
    index_path: Path | None = None,
    index_md_path: Path | None = None,
) -> dict:
    if index_path is None:
        index_path = project_root / "index.json"
    if index_md_path is None:
        index_md_path = project_root / "index.md"

    # Ensure all configured directories exist
    for d in config["structure"]["directories"]:
        (project_root / d).mkdir(exist_ok=True)
        logger.debug("Ensured directory exists: %s", d)

    tracked_dirs = config["index"]["tracked_dirs"]

    index = load_index(index_path)

    # Build lookup of existing entries keyed by (directory, filename)
    existing: dict[tuple[str, str], dict] = {
        (e["directory"], e["filename"]): e for e in index["files"]
    }

    # Scan tracked dirs for files currently on disk
    on_disk: dict[tuple[str, str], Path] = {}
    for dir_name in tracked_dirs:
        dir_path = project_root / dir_name
        if not dir_path.is_dir():
            continue
        for f in dir_path.iterdir():
            if f.name.startswith(".") or not f.is_file():
                continue
            on_disk[(dir_name, f.name)] = f
            logger.debug("Found on disk: %s/%s", dir_name, f.name)

    existing_keys = set(existing)
    disk_keys = set(on_disk)
    added_keys = disk_keys - existing_keys
    removed_keys = existing_keys - disk_keys
    unchanged_keys = existing_keys & disk_keys

    added = sorted(k[1] for k in added_keys)
    removed = sorted(k[1] for k in removed_keys)

    if not added_keys and not removed_keys:
        logger.debug("No changes detected, skipping commit")
        return {"added": [], "removed": [], "unchanged": len(unchanged_keys)}

    new_files: list[dict] = []

    for key in unchanged_keys:
        new_files.append(existing[key])

    for dir_name, filename in sorted(added_keys):
        file_path = on_disk[(dir_name, filename)]
        added_date = date.fromtimestamp(file_path.stat().st_mtime).isoformat()
        new_files.append({
            "filename": filename,
            "directory": dir_name,
            "path": f"{dir_name}/{filename}",
            "description": "(no description)",
            "added": added_date,
            "tags": [],
        })
        logger.debug("Adding new entry: %s/%s", dir_name, filename)

    new_files.sort(key=lambda e: (e["directory"], e["filename"]))

    index["files"] = new_files
    index["last_rebuilt"] = date.today().isoformat()

    save_index(index_path, index)
    generate_index_md(index_md_path, index)

    commit_msg = f"Reindex: +{len(added)} added, -{len(removed)} removed"
    if git_has_changes(project_root):
        git_commit_all(project_root, commit_msg)
        logger.debug("Committed: %s", commit_msg)
    else:
        logger.debug("No git changes after reindex, skipping commit")

    return {"added": added, "removed": removed, "unchanged": len(unchanged_keys)}
