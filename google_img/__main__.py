# type: ignore[attr-defined]
from typing import Optional

from enum import Enum
from pathlib import Path
from random import choice

import typer
from rich.console import Console

from google_img import version
from google_img.collectors.registry import collector
from google_img.downloader_async import download_async

app = typer.Typer(
    name="google_img",
    help="Awesome `google_img` is a Python cli/package created with https://github.com/TezRomacH/python-package-template",
    add_completion=False,
)
console = Console()


def version_callback(print_version: bool) -> None:
    """Print the version of the package."""
    if print_version:
        console.print(f"[yellow]google_img[/] version: [bold blue]{version}[/]")
        raise typer.Exit()


CollectorsEnum = Enum("CollectorsEnum", {k: k for k in collector.registry})


@app.command(name="")
def main(
    collector_name: CollectorsEnum,
    keywords: str = typer.Argument(..., help="Comma separated kewords for image search"),
    output_folder: Path = typer.Argument(
        ..., help="Output images folder", resolve_path=True, dir_okay=True
    ),
    hidden: bool = typer.Option(True, help="Does not show browser window"),
    print_version: bool = typer.Option(
        None,
        "-v",
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Prints the version of the google_img package.",
    ),
) -> None:
    download_async(
        keywords=keywords,
        collector_name=collector_name.value,
        output_folder=output_folder,
        hidden=hidden,
    )


if __name__ == "__main__":
    app()
