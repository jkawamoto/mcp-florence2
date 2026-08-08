#  __init__.py
#
#  Copyright (c) 2025-2026 Junpei Kawamoto
#
#  This software is released under the MIT License.
#
#  http://opensource.org/licenses/mit-license.php
import os
from collections.abc import AsyncIterator, Iterator
from contextlib import ExitStack, asynccontextmanager, closing, contextmanager
from dataclasses import dataclass
from functools import partial
from io import BytesIO
from pathlib import Path
from typing import Annotated, Final, Protocol

import requests
from mcp.server.mcpserver import Context, MCPServer
from PIL.Image import Image
from PIL.Image import open as open_image
from pydantic import Field
from pypdfium2 import PdfDocument

from mcp_florence2.florence2 import CaptionLevel, Florence2, Florence2SP

SERVER_NAME: Final[str] = "Florence2"


@contextmanager
def get_images(src: os.PathLike[str] | str) -> Iterator[list[Image]]:
    """Opens and returns a list of images from a file path or URL."""
    if isinstance(src, str) and src.startswith(("http://", "https://")):
        res = requests.get(src)
        res.raise_for_status()

        if res.headers["Content-Type"] == "application/pdf":
            with ExitStack() as stack:
                images = []
                with closing(PdfDocument(res.content)) as doc:
                    for page in doc:
                        images.append(stack.enter_context(page.render().to_pil()))
                yield images

        else:
            with open_image(BytesIO(res.content)) as image:
                yield [image]

    else:
        path = Path(src)
        ext = os.path.splitext(path)[1].lower()
        if ext == ".pdf":
            with ExitStack() as stack:
                images = []
                with closing(PdfDocument(path)) as doc:
                    for page in doc:
                        images.append(stack.enter_context(page.render().to_pil()))
                yield images
        else:
            with open_image(path) as image:
                yield [image]


class Processor(Protocol):
    """Represents a protocol for processing image data.

    This class provides an interface for implementing image processing
    operations, including optical character recognition (OCR) and generating
    captions based on the content of the images. It is meant to be used as a
    guideline for defining specific processors that conform to this protocol.
    """

    def ocr(self, images: list[Image]) -> list[str]:
        """Performs optical character recognition (OCR) on a list of images.

        This function takes a list of images and processes each image using OCR
        to retrieve the text content present within the images. The function
        returns a list of strings, where each string corresponds to the text
        extracted from the respective image in the input list.
        """
        ...

    def caption(self, images: list[Image], level: CaptionLevel = CaptionLevel.NORMAL) -> list[str]:
        """Generates a list of captions for the given images based on the specified captioning level.

        It processes an input list of images and returns the corresponding captions
        in a text format. The caption level influences the verbosity or granularity
        of the generated captions.
        """
        ...


@dataclass
class AppContext:
    """Context for the FastMCP app."""

    processor: Processor


@asynccontextmanager
async def app_lifespan(_server: MCPServer, model_id: str, subprocess: bool) -> AsyncIterator[AppContext]:
    """Context manager for the FastMCP app lifespan."""
    processor: Processor
    if subprocess:
        processor = Florence2SP(model_id)
    else:
        processor = Florence2(model_id)
    yield AppContext(processor)


def server(name: str, model_id: str, subprocess: bool = True) -> MCPServer:
    """Creates a new FastMCP server instance with the specified name and model ID."""
    mcp = MCPServer(name, lifespan=partial(app_lifespan, model_id=model_id, subprocess=subprocess))

    @mcp.tool()
    def ocr(
        ctx: Context[AppContext],
        src: Annotated[
            os.PathLike[str] | str,
            Field(description="A file path or URL to the image file that needs to be processed."),
        ],
    ) -> list[str]:
        """Process an image file or URL using OCR to extract text."""
        with get_images(src) as images:
            return ctx.request_context.lifespan_context.processor.ocr(images)

    @mcp.tool()
    def caption(
        ctx: Context[AppContext],
        src: Annotated[
            os.PathLike[str] | str,
            Field(description="A file path or URL to the image file that needs to be processed."),
        ],
    ) -> list[str]:
        """Processes an image file and generates captions for the image."""
        with get_images(src) as images:
            return ctx.request_context.lifespan_context.processor.caption(images, CaptionLevel.MORE_DETAILED)

    return mcp


__all__: Final = ["SERVER_NAME", "server"]
