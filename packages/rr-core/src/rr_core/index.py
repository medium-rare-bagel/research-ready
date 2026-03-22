import json
from datetime import date
from pathlib import Path


def add_entry(index: dict, filename: str, directory: str, description: str) -> None:
    path = f"{directory}/{filename}"
    entry = {
        "filename": filename,
        "directory": directory,
        "path": path,
        "description": description,
        "added": date.today().isoformat(),
        "tags": [],
    }
    for i, existing in enumerate(index["files"]):
        if existing["path"] == path:
            index["files"][i] = entry
            return
    index["files"].append(entry)


def generate_index_md(path: Path, index: dict) -> None:
    lines = [
        "# Project Index",
        "",
        f"Last rebuilt: {index['last_rebuilt']}",
        "",
        "| File | Directory | Added | Description |",
        "|------|-----------|-------|-------------|",
    ]
    for entry in index["files"]:
        lines.append(
            f"| [{entry['filename']}]({entry['path']}) "
            f"| {entry['directory']} "
            f"| {entry['added']} "
            f"| {entry['description']} |"
        )
    path.write_text("\n".join(lines) + "\n")


def save_index(path: Path, index: dict) -> None:
    path.write_text(json.dumps(index, indent=2))


def load_index(path: Path) -> dict:
    if not path.exists():
        return {"last_rebuilt": date.today().isoformat(), "files": []}
    return json.loads(path.read_text())


def resolve_filename(index: dict, file_path: str) -> str:
    """Resolve a bare filename to its full path via index lookup.

    If file_path already contains a slash or matches an existing path entry,
    returns it unchanged. If it's a bare filename matching exactly one entry,
    returns that entry's path. Raises ValueError on ambiguous matches.
    """
    if "/" in file_path or any(e["path"] == file_path for e in index["files"]):
        return file_path
    matches = [e["path"] for e in index["files"] if e["filename"] == file_path]
    if len(matches) > 1:
        paths = ", ".join(matches)
        raise ValueError(f"multiple files match '{file_path}': {paths} — specify the full path")
    if len(matches) == 1:
        return matches[0]
    return file_path
