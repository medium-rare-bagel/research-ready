import json
from pathlib import Path


def load_index(path: Path) -> dict:
    return json.loads(path.read_text())
