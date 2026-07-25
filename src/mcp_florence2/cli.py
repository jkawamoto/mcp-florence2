#  cli.py
#
#  Copyright (c) 2025-2026 Junpei Kawamoto
#
#  This software is released under the MIT License.
#
#  http://opensource.org/licenses/mit-license.php
import logging

import rich_click as click

from . import SERVER_NAME, server


@click.command()
@click.option(
    "--model",
    default="florence-community/Florence-2-large",
    show_default=True,
    help="Specifies the model to be used for processing.",
)
@click.option("--cache-model", is_flag=True, help="Keeps the model in VRAM for faster subsequent operations if set.")
@click.version_option()
def main(model: str, cache_model: bool) -> None:
    """
    An MCP server for processing images using Florence-2.
    """
    logger = logging.getLogger(__name__)

    s = server(SERVER_NAME, model, not cache_model)

    logger.info(f"Starting server with {model} (Press CTRL+D to quit)")
    s.run()
    logger.info("Server stopped")
