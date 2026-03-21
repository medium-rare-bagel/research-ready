from dataclasses import dataclass
from datetime import date
from pathlib import Path
import logging

import click

from rr_core.config import find_project_root, load_config
from rr_core.file import file_asset
from rr_core.index import load_index
from rr_core.init import init_project
from rr_core.names import suggest_filename
from rr_core.reindex import reindex
from rr_core.remove import remove_asset


@dataclass
class ProjectContext:
    root: Path
    config: dict


@click.group()
@click.option("--verbose", "-v", is_flag=True, default=False)
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    try:
        root = find_project_root(Path.cwd())
        ctx.obj = ProjectContext(root=root, config=load_config(root))
    except FileNotFoundError:
        ctx.obj = None


def require_project(ctx: click.Context) -> ProjectContext:
    if ctx.obj is None:
        click.echo("Error: not inside an rr project (no project.yaml found)")
        ctx.exit(1)
    return ctx.obj


@cli.command("init")
@click.argument("project_name")
@click.pass_context
def init_cmd(ctx: click.Context, project_name: str) -> None:
    try:
        init_project(project_name, Path.cwd())
    except FileExistsError:
        click.echo(f"Error: '{project_name}' already exists")
        ctx.exit(1)
        return
    click.echo(f"Initialized project: {project_name}")


@cli.command("reindex")
@click.pass_context
def reindex_cmd(ctx: click.Context) -> None:
    project = require_project(ctx)
    result = reindex(project.root, project.config)
    if not result["added"] and not result["removed"]:
        click.echo("Nothing changed.")
        return
    if result["added"]:
        click.echo(f"Added: {', '.join(result['added'])}")
    if result["removed"]:
        click.echo(f"Removed: {', '.join(result['removed'])}")
    click.echo(
        f"+{len(result['added'])} added, -{len(result['removed'])} removed, "
        f"{result['unchanged']} unchanged"
    )


@cli.command("file")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.pass_context
def file_cmd(ctx: click.Context, src: Path) -> None:
    project = require_project(ctx)
    allowed_dirs = project.config["structure"]["directories"]
    default_name = suggest_filename(src.name, date.today())

    new_name = click.prompt("New name", default=default_name)
    if not Path(new_name).suffix and src.suffix:
        new_name = new_name + src.suffix
    dest_dir_name = click.prompt("Destination directory", default="sources")
    description = click.prompt("Description", default="")

    dest_dir = project.root / dest_dir_name
    result_path = file_asset(
        src=src,
        new_name=new_name,
        dest_dir=dest_dir,
        index_path=project.root / "index.json",
        index_md_path=project.root / "index.md",
        description=description,
        project_root=project.root,
        allowed_dirs=allowed_dirs,
    )
    click.echo(f"Filed: {result_path.relative_to(project.root)}")


@cli.command("remove")
@click.argument("path")
@click.option("--yes", "-y", is_flag=True, default=False)
@click.pass_context
def remove_cmd(ctx: click.Context, path: str, yes: bool) -> None:
    project = require_project(ctx)

    if not yes:
        index = load_index(project.root / "index.json")
        entry = next((e for e in index["files"] if e["path"] == path), None)
        if entry is None and "/" not in path:
            matches = [e for e in index["files"] if e["filename"] == path]
            if len(matches) > 1:
                paths = ", ".join(e["path"] for e in matches)
                click.echo(f"Error: multiple files match '{path}': {paths} — specify the full path")
                ctx.exit(1)
                return
            if len(matches) == 1:
                entry = matches[0]
        if entry:
            desc = entry.get("description", "")
            display = entry["path"]
            click.echo(f"{display}: {desc}" if desc else display)
        else:
            click.echo(f"{path} (not in index)")
        confirmed = click.confirm("Remove this file?", default=False)
        if not confirmed:
            click.echo("Aborted.")
            return

    try:
        result = remove_asset(path, project.root)
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"Error: {e}")
        ctx.exit(1)
        return

    if result["warning"]:
        click.echo(f"Warning: {result['warning']}")
    click.echo(f"Removed: {path}")


def main() -> None:
    cli()
