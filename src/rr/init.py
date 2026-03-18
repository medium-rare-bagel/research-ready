from pathlib import Path


def init_project(name: str, parent: Path) -> None:
    (parent / name).mkdir()
