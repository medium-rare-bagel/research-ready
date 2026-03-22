from pathlib import Path


def validate_name(name: str) -> None:
    if " " in name:
        raise ValueError(f"Name '{name}' must not contain spaces")
    if "/" in name or "\\" in name:
        raise ValueError(f"Name '{name}' must not contain a path separator")


def validate_description(description: str) -> None:
    if len(description) > 280:
        raise ValueError(f"Description must be 280 characters or fewer (got {len(description)})")


def validate_dest_dir(dest_dir: Path, project_root: Path) -> None:
    resolved = dest_dir.resolve()
    root = project_root.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"Destination '{dest_dir}' resolves outside the project root")


def check_overwrite(dest_dir: Path, filename: str) -> None:
    dest = dest_dir / filename
    if dest.exists():
        raise FileExistsError(f"'{dest}' already exists")
