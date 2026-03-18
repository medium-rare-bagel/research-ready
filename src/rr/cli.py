from dataclasses import dataclass
from pathlib import Path
import logging

import click

from rr.config import find_project_root, load_config


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


def main() -> None:
    cli()
