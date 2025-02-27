#  server.py
#
#  Copyright (c) 2025 Junpei Kawamoto
#
#  This software is released under the MIT License.
#
#  http://opensource.org/licenses/mit-license.php
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass
from io import BytesIO
from os import PathLike
from typing import Protocol, AsyncIterator, Iterator

import requests
from PIL.Image import Image, open as open_image
from mcp.server import FastMCP
from mcp.server.fastmcp import Context
from pydantic import Field

from mcp_florence2.florence2 import Florence2, Florence2SP, CaptionLevel


@contextmanager
def get_images(src: PathLike | str) -> Iterator[list[Image]]:
    """Opens and returns a list of images from a file path or URL."""
    if not isinstance(src, PathLike) and (src.startswith("http://") or src.startswith("https://")):
        res = requests.get(src)
        res.raise_for_status()
        with open_image(BytesIO(res.content)) as image:
            yield [image]
    else:
        with open_image(src) as image:
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


def new_server(name: str, model_id: str, subprocess: bool = True) -> FastMCP:
    @asynccontextmanager
    async def app_lifespan(_server: FastMCP) -> AsyncIterator[AppContext]:
        processor: Processor
        if subprocess:
            processor = Florence2SP(model_id)
        else:
            processor = Florence2(model_id)
        yield AppContext(processor)

    mcp = FastMCP(name, lifespan=app_lifespan)

    @mcp.tool()
    def ocr(
        ctx: Context,
        src: PathLike | str = Field(description="A file path or URL to the image file that needs to be processed."),
    ) -> list[str]:
        """Process an image file or URL using OCR to extract text."""
        with get_images(src) as images:
            processor: Processor = ctx.request_context.lifespan_context.processor
            return processor.ocr(images)

    @mcp.tool()
    def caption(
        ctx: Context,
        src: PathLike | str = Field(description="A file path or URL to the image file that needs to be processed."),
    ) -> list[str]:
        """Processes an image file and generates captions for the image."""
        with get_images(src) as images:
            processor: Processor = ctx.request_context.lifespan_context.processor
            return processor.caption(images, CaptionLevel.MORE_DETAILED)

    return mcp
