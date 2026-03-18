import click
import json
import logging
import subprocess
import pytest
from click.testing import CliRunner
from datetime import date
from pathlib import Path

from rr.cli import cli, ProjectContext, require_project
from rr.init import init_project
from rr.names import suggest_filename


@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_group_resolves_project_root(tmp_path, monkeypatch, runner):
    (tmp_path / "project.yaml").write_text("name: test\ndirectories:\n  - data\n")
    monkeypatch.chdir(tmp_path)

    captured = []

    @cli.command("_dummy_root")
    @click.pass_context
    def dummy(ctx):
        captured.append(ctx.obj)

    try:
        result = runner.invoke(cli, ["_dummy_root"])
        assert result.exit_code == 0
        assert isinstance(captured[0], ProjectContext)
        assert captured[0].root == tmp_path
    finally:
        cli.commands.pop("_dummy_root", None)


def test_cli_group_sets_none_outside_project(tmp_path, monkeypatch, runner):
    monkeypatch.chdir(tmp_path)

    captured = []

    @cli.command("_dummy_none")
    @click.pass_context
    def dummy(ctx):
        captured.append(ctx.obj)

    try:
        result = runner.invoke(cli, ["_dummy_none"])
        assert result.exit_code == 0
        assert captured[0] is None
    finally:
        cli.commands.pop("_dummy_none", None)


def test_verbose_flag_sets_debug_logging(tmp_path, monkeypatch, runner):
    (tmp_path / "project.yaml").write_text("name: test\ndirectories:\n  - data\n")
    monkeypatch.chdir(tmp_path)

    captured = []
    original_level = logging.getLogger().level

    @cli.command("_dummy_verbose")
    @click.pass_context
    def dummy(ctx):
        captured.append(logging.getLogger().level)

    try:
        result = runner.invoke(cli, ["-v", "_dummy_verbose"])
        assert result.exit_code == 0
        assert captured[0] == logging.DEBUG
    finally:
        cli.commands.pop("_dummy_verbose", None)
        logging.getLogger().setLevel(original_level)


def test_require_project_exits_outside_project(tmp_path, monkeypatch, runner):
    monkeypatch.chdir(tmp_path)

    @cli.command("_dummy_req_none")
    @click.pass_context
    def dummy(ctx):
        require_project(ctx)

    try:
        result = runner.invoke(cli, ["_dummy_req_none"])
        assert result.exit_code == 1
        assert "not inside an rr project" in result.output
    finally:
        cli.commands.pop("_dummy_req_none", None)


def test_require_project_returns_context_inside_project(tmp_path, monkeypatch, runner):
    (tmp_path / "project.yaml").write_text("name: test\ndirectories:\n  - data\n")
    monkeypatch.chdir(tmp_path)

    captured = []

    @cli.command("_dummy_req_ok")
    @click.pass_context
    def dummy(ctx):
        captured.append(require_project(ctx))

    try:
        result = runner.invoke(cli, ["_dummy_req_ok"])
        assert result.exit_code == 0
        assert isinstance(captured[0], ProjectContext)
        assert captured[0].root == tmp_path
    finally:
        cli.commands.pop("_dummy_req_ok", None)


def test_reindex_outside_project_shows_error(tmp_path, monkeypatch, runner):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(cli, ["reindex"])
    assert result.exit_code != 0
    assert "not inside an rr project" in result.output


def test_reindex_prints_summary(tmp_path, monkeypatch, runner):
    init_project("test-proj", tmp_path)
    project_root = tmp_path / "test-proj"
    (project_root / "sources" / "paper.pdf").write_bytes(b"%PDF")
    monkeypatch.chdir(project_root)
    result = runner.invoke(cli, ["reindex"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "paper.pdf" in result.output


def test_reindex_nothing_changed_prints_clean(tmp_path, monkeypatch, runner):
    init_project("test-proj", tmp_path)
    project_root = tmp_path / "test-proj"
    monkeypatch.chdir(project_root)
    result = runner.invoke(cli, ["reindex"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "Nothing changed" in result.output


def test_file_command_moves_and_indexes(tmp_path, monkeypatch):
    init_project("test-proj", tmp_path)
    project_root = tmp_path / "test-proj"
    src = project_root / "inbox" / "test.png"
    src.write_bytes(b"\x89PNG")
    monkeypatch.chdir(project_root)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["file", "inbox/test.png"],
        input="test-2026-03-18.png\nsources\nA test image\n",
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert (project_root / "sources" / "test-2026-03-18.png").exists()
    assert not src.exists()

    index = json.loads((project_root / "index.json").read_text())
    assert len(index["files"]) == 1
    entry = index["files"][0]
    assert entry["filename"] == "test-2026-03-18.png"
    assert entry["directory"] == "sources"
    assert entry["description"] == "A test image"

    log = subprocess.check_output(
        ["git", "log", "-1", "--format=%s"], cwd=project_root, text=True
    ).strip()
    assert "test-2026-03-18.png" in log


def test_file_command_preserves_extension_when_user_omits_it(tmp_path, monkeypatch):
    init_project("test-proj", tmp_path)
    project_root = tmp_path / "test-proj"
    src = project_root / "inbox" / "report.pdf"
    src.write_bytes(b"%PDF")
    monkeypatch.chdir(project_root)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["file", "inbox/report.pdf"],
        input="report\nsources\n\n",
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert (project_root / "sources" / "report.pdf").exists()


def test_init_no_argument_shows_error(tmp_path, monkeypatch, runner):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(cli, ["init"])
    assert result.exit_code != 0


def test_init_creates_project_directory(tmp_path, monkeypatch, runner):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(cli, ["init", "my-project"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (tmp_path / "my-project").is_dir()


def test_init_prints_confirmation(tmp_path, monkeypatch, runner):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(cli, ["init", "my-project"], catch_exceptions=False)
    assert "my-project" in result.output


def test_init_fails_if_directory_exists(tmp_path, monkeypatch, runner):
    (tmp_path / "my-project").mkdir()
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(cli, ["init", "my-project"])
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_init_creates_scaffolding(tmp_path, monkeypatch, runner):
    monkeypatch.chdir(tmp_path)
    runner.invoke(cli, ["init", "my-project"], catch_exceptions=False)
    project = tmp_path / "my-project"
    assert (project / "project.yaml").exists()
    assert (project / "index.json").exists()
    assert (project / "sources").is_dir()


def test_init_works_outside_project(tmp_path, monkeypatch, runner):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(cli, ["init", "new-project"], catch_exceptions=False)
    assert result.exit_code == 0


def test_cli_remove_with_yes_flag(tmp_path, monkeypatch):
    init_project("test-proj", tmp_path)
    project_root = tmp_path / "test-proj"
    src = project_root / "sources" / "report.pdf"
    src.write_bytes(b"%PDF")
    # Add to index via reindex
    import json
    index_path = project_root / "index.json"
    index = json.loads(index_path.read_text())
    index["files"].append({
        "filename": "report.pdf",
        "directory": "sources",
        "path": "sources/report.pdf",
        "description": "A test file",
        "added": "2026-03-18",
        "tags": [],
    })
    index_path.write_text(json.dumps(index))
    monkeypatch.chdir(project_root)

    runner = CliRunner()
    result = runner.invoke(cli, ["remove", "sources/report.pdf", "--yes"], catch_exceptions=False)

    assert result.exit_code == 0
    assert not src.exists()
    assert "Removed" in result.output


def test_cli_remove_prompts_for_confirmation(tmp_path, monkeypatch):
    init_project("test-proj", tmp_path)
    project_root = tmp_path / "test-proj"
    src = project_root / "sources" / "report.pdf"
    src.write_bytes(b"%PDF")
    import json
    index_path = project_root / "index.json"
    index = json.loads(index_path.read_text())
    index["files"].append({
        "filename": "report.pdf",
        "directory": "sources",
        "path": "sources/report.pdf",
        "description": "Quarterly report",
        "added": "2026-03-18",
        "tags": [],
    })
    index_path.write_text(json.dumps(index))
    monkeypatch.chdir(project_root)

    runner = CliRunner()
    result = runner.invoke(cli, ["remove", "sources/report.pdf"], input="y\n", catch_exceptions=False)

    assert result.exit_code == 0
    assert not src.exists()
    assert "report.pdf" in result.output


def test_cli_remove_confirmation_declined(tmp_path, monkeypatch):
    init_project("test-proj", tmp_path)
    project_root = tmp_path / "test-proj"
    src = project_root / "sources" / "report.pdf"
    src.write_bytes(b"%PDF")
    import json
    index_path = project_root / "index.json"
    index = json.loads(index_path.read_text())
    index["files"].append({
        "filename": "report.pdf",
        "directory": "sources",
        "path": "sources/report.pdf",
        "description": "Quarterly report",
        "added": "2026-03-18",
        "tags": [],
    })
    index_path.write_text(json.dumps(index))
    monkeypatch.chdir(project_root)

    runner = CliRunner()
    result = runner.invoke(cli, ["remove", "sources/report.pdf"], input="n\n", catch_exceptions=False)

    assert result.exit_code == 0
    assert src.exists()  # file not deleted
    assert "Aborted" in result.output


def test_cli_remove_outside_project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["remove", "sources/report.pdf"])
    assert result.exit_code != 0
    assert "not inside an rr project" in result.output


def test_cli_remove_shows_warning_for_untracked(tmp_path, monkeypatch):
    init_project("test-proj", tmp_path)
    project_root = tmp_path / "test-proj"
    src = project_root / "sources" / "orphan.pdf"
    src.write_bytes(b"%PDF")
    monkeypatch.chdir(project_root)

    runner = CliRunner()
    result = runner.invoke(cli, ["remove", "sources/orphan.pdf", "--yes"], catch_exceptions=False)

    assert result.exit_code == 0
    assert not src.exists()
    assert "Warning" in result.output


def test_cli_remove_confirmation_shows_description_for_bare_filename(tmp_path, monkeypatch):
    init_project("test-proj", tmp_path)
    project_root = tmp_path / "test-proj"
    src = project_root / "sources" / "report.pdf"
    src.write_bytes(b"%PDF")
    import json
    index_path = project_root / "index.json"
    index = json.loads(index_path.read_text())
    index["files"].append({
        "filename": "report.pdf",
        "directory": "sources",
        "path": "sources/report.pdf",
        "description": "Quarterly report",
        "added": "2026-03-18",
        "tags": [],
    })
    index_path.write_text(json.dumps(index))
    monkeypatch.chdir(project_root)

    runner = CliRunner()
    result = runner.invoke(cli, ["remove", "report.pdf"], input="y\n", catch_exceptions=False)

    assert result.exit_code == 0
    assert not src.exists()
    assert "not in index" not in result.output
    assert "Quarterly report" in result.output


def test_cli_remove_confirmation_ambiguous_bare_filename(tmp_path, monkeypatch):
    init_project("test-proj", tmp_path)
    project_root = tmp_path / "test-proj"
    (project_root / "sources" / "report.pdf").write_bytes(b"%PDF")
    (project_root / "analysis" / "report.pdf").write_bytes(b"%PDF")
    import json
    index_path = project_root / "index.json"
    index = json.loads(index_path.read_text())
    index["files"].extend([
        {"filename": "report.pdf", "directory": "sources", "path": "sources/report.pdf",
         "description": "A", "added": "2026-03-18", "tags": []},
        {"filename": "report.pdf", "directory": "analysis", "path": "analysis/report.pdf",
         "description": "B", "added": "2026-03-18", "tags": []},
    ])
    index_path.write_text(json.dumps(index))
    monkeypatch.chdir(project_root)

    runner = CliRunner()
    result = runner.invoke(cli, ["remove", "report.pdf", "--yes"])

    assert result.exit_code != 0
    assert "multiple files match" in result.output


def test_file_command_uses_default_name_when_accepted(tmp_path, monkeypatch):
    init_project("test-proj", tmp_path)
    project_root = tmp_path / "test-proj"
    src = project_root / "inbox" / "report.pdf"
    src.write_bytes(b"%PDF")
    monkeypatch.chdir(project_root)

    expected_name = suggest_filename("report.pdf", date.today())

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["file", "inbox/report.pdf"],
        input="\nsources\nQuarterly report\n",
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert (project_root / "sources" / expected_name).exists()
