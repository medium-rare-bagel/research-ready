import click
import logging
import pytest
from click.testing import CliRunner
from pathlib import Path

from rr.cli import cli, ProjectContext


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
