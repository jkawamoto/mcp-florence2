#  cli.py
#
#  Copyright (c) 2025-2026 Junpei Kawamoto
#
#  This software is released under the MIT License.
#
#  http://opensource.org/licenses/mit-license.php
import logging

import rich_click as click

from . import DEFAULT_MOONDREAM_MODEL, DEFAULT_MOONDREAM_REVISION, DEFAULT_SAM2_MODEL, SERVER_NAME, server


@click.command()
@click.option(
    "--model",
    default="florence-community/Florence-2-large",
    show_default=True,
    help="Specifies the Florence-2 model to be used for caption/OCR/detection/grounding.",
)
@click.option("--cache-model", is_flag=True, help="Keeps the model in VRAM for faster subsequent operations if set.")
@click.option(
    "--moondream-model",
    default=DEFAULT_MOONDREAM_MODEL,
    show_default=True,
    help="Specifies the Moondream2 model used for the query_image (VQA) tool.",
)
@click.option(
    "--moondream-revision",
    default=DEFAULT_MOONDREAM_REVISION,
    show_default=True,
    help="Specifies the Moondream2 model revision used for the query_image (VQA) tool.",
)
@click.option(
    "--sam2-model",
    default=DEFAULT_SAM2_MODEL,
    show_default=True,
    help="Specifies the SAM2 model used for the spatial_relations tool.",
)
@click.option(
    "--idle-timeout",
    type=float,
    default=0,
    show_default=True,
    help=(
        "Minutes of inactivity after which the models are unloaded and their memory released. "
        "They reload automatically on the next request. Set to 0 to keep them loaded for the "
        "lifetime of the server. Implies --cache-model, since repeat calls reuse the loaded model."
    ),
)
@click.version_option()
def main(
    model: str,
    cache_model: bool,
    moondream_model: str,
    moondream_revision: str,
    sam2_model: str,
    idle_timeout: float,
) -> None:
    """
    An MCP server for processing images using Florence-2, Moondream2 and SAM2.
    """
    logger = logging.getLogger(__name__)

    idle_seconds = idle_timeout * 60
    s = server(
        SERVER_NAME,
        model,
        subprocess=not cache_model,
        moondream_model_id=moondream_model,
        moondream_revision=moondream_revision,
        sam2_model_id=sam2_model,
        idle_timeout=idle_seconds,
    )

    logger.info(f"Starting server with {model} + {moondream_model}@{moondream_revision} (Press CTRL+D to quit)")
    if idle_seconds > 0:
        logger.info(f"Models will be released after {idle_timeout:g} minutes of inactivity")
    s.run()
    logger.info("Server stopped")
