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
    help="Model type",
)
@click.option("--cache-model", is_flag=True, help="If set, the model will be kept in VRAM")
def main(model: str, cache_model: bool) -> None:
    """
    An MCP server for processing images using Florence-2.
    """
    logger = logging.getLogger(__name__)

    model_id = f"microsoft/Florence-2-{model}"
    s = Server(SERVER_NAME, model_id, not cache_model)

    logger.info(f"Starting server with {model_id} (Press CTRL+D to quit)")
    s.run()
    logger.info("Server stopped")


__all__: Final = ["main", "SERVER_NAME"]
