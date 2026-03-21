import datetime
from pathlib import Path


def suggest_filename(original: str, date: datetime.date) -> str:
    """Return original filename with a date suffix inserted before the extension."""
    p = Path(original)
    return f"{p.stem}-{date.isoformat()}{p.suffix}"
