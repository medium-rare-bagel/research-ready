"""Smoke test: rr is installable as a uv tool and its CLI entry point works."""

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_rr_cli_entry_point_responds():
    """rr CLI entry point should respond to --help with usage info."""
    result = subprocess.run(
        ["uv", "run", "rr", "--help"],
        capture_output=True, text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, f"rr --help failed:\n{result.stderr}"
    assert "Usage" in result.stdout
    assert "init" in result.stdout
