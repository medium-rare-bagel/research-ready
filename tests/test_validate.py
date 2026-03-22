import pytest

from pathlib import Path

from rr_core.validate import check_overwrite, validate_description, validate_dest_dir, validate_name


def test_validate_name_rejects_spaces():
    with pytest.raises(ValueError, match="spaces"):
        validate_name("my report.pdf")


def test_validate_name_accepts_valid_name():
    validate_name("my-report-2026-03-22.pdf")


def test_validate_name_rejects_forward_slash():
    with pytest.raises(ValueError, match="path separator"):
        validate_name("dir/file.pdf")


def test_validate_name_rejects_backslash():
    with pytest.raises(ValueError, match="path separator"):
        validate_name("dir\\file.pdf")


def test_validate_description_rejects_over_280():
    with pytest.raises(ValueError, match="280"):
        validate_description("x" * 281)


def test_validate_description_accepts_280():
    validate_description("x" * 280)


def test_validate_description_accepts_empty():
    validate_description("")


def test_validate_dest_rejects_path_traversal(tmp_path):
    project_root = tmp_path / "my-project"
    project_root.mkdir()
    dest_dir = project_root / ".." / "escape"
    with pytest.raises(ValueError, match="outside.*project"):
        validate_dest_dir(dest_dir, project_root)


def test_validate_dest_accepts_valid_subdir(tmp_path):
    project_root = tmp_path / "my-project"
    project_root.mkdir()
    dest_dir = project_root / "sources"
    dest_dir.mkdir()
    validate_dest_dir(dest_dir, project_root)


def test_check_overwrite_raises_when_exists(tmp_path):
    dest_dir = tmp_path / "sources"
    dest_dir.mkdir()
    (dest_dir / "report.pdf").write_bytes(b"%PDF")
    with pytest.raises(FileExistsError, match="already exists"):
        check_overwrite(dest_dir, "report.pdf")


def test_check_overwrite_passes_when_no_conflict(tmp_path):
    dest_dir = tmp_path / "sources"
    dest_dir.mkdir()
    check_overwrite(dest_dir, "report.pdf")
