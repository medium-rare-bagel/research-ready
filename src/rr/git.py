import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def git_init(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
    logger.debug("Initialized git repo at %s", path)


def git_commit_all(path: Path, message: str) -> None:
    subprocess.run(["git", "add", "-A"], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=path,
        check=True,
        capture_output=True,
    )
    logger.debug("Git commit: %s", message)
