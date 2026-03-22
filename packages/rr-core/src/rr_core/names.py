import datetime
from pathlib import Path


def suggest_filename(original: str, date: datetime.date) -> str:
    """Return original filename with a date suffix inserted before the extension."""
    p = Path(original)
    stem = p.stem.replace(" ", "-")
    return f"{stem}-{date.isoformat()}{p.suffix}"
