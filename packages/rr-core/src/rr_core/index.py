import json
from datetime import date
from pathlib import Path


def add_entry(index: dict, filename: str, directory: str, description: str) -> None:
    index["files"].append({
        "filename": filename,
        "directory": directory,
        "path": f"{directory}/{filename}",
        "description": description,
        "added": date.today().isoformat(),
        "tags": [],
    })


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
