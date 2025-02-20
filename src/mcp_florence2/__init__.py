#  __init__.py
#
#  Copyright (c) 2025 Junpei Kawamoto
#
#  This software is released under the MIT License.
#
#  http://opensource.org/licenses/mit-license.php

import logging
from typing import Final

import click

from .server import Server

SERVER_NAME: Final[str] = "Florence2"


@click.command()
@click.option(
    "--model",
    type=click.Choice(["base", "base-ft", "large", "large-ft"]),
    default="large",
    show_default=True,
    help="Specifies the model type to be used for processing.",
)
@click.option("--cache-model", is_flag=True, help="Keeps the model in VRAM for faster subsequent operations if set.")
@click.option(
    "--remote", is_flag=True, help="Disables local file access and runs the server in remote-only mode if set."
)
def main(model: str, cache_model: bool, remote: bool) -> None:
    """
    An MCP server for processing images using Florence-2.
    """
    logger = logging.getLogger(__name__)

    model_id = f"microsoft/Florence-2-{model}"
    s = Server(SERVER_NAME, model_id, not cache_model, remote)

    logger.info(f"Starting server with {model_id} (Press CTRL+D to quit)")
    s.run()
    logger.info("Server stopped")


__all__: Final = ["main", "SERVER_NAME"]
