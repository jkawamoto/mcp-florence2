#  server.py
#
#  Copyright (c) 2025 Junpei Kawamoto
#
#  This software is released under the MIT License.
#
#  http://opensource.org/licenses/mit-license.php
from contextlib import asynccontextmanager
from dataclasses import dataclass
from io import BytesIO
from os import PathLike
from typing import Protocol, AsyncIterator

import requests
from PIL import Image
from mcp.server import FastMCP
from mcp.server.fastmcp import Context
from pydantic import Field

from mcp_florence2.florence2 import Florence2, Florence2SP, CaptionLevel


def open_images(file_paths: list[PathLike]) -> list[Image]:
    """Opens a list of image files and converts them to RGB mode."""
    return [Image.open(p).convert("RGB") for p in file_paths]


def download_images(urls: list[str]) -> list[Image]:
    """Downloads a list of image files and converts them to RGB mode."""
    images = []
    for url in urls:
        response = requests.get(url)
        response.raise_for_status()

        images.append(Image.open(BytesIO(response.content)).convert("RGB"))
    return images


class Processor(Protocol):
    """Represents a protocol for processing image data.

    This class provides an interface for implementing image processing
    operations, including optical character recognition (OCR) and generating
    captions based on the content of the images. It is meant to be used as a
    guideline for defining specific processors that conform to this protocol.
    """

    def ocr(self, images: list[Image]) -> list[str]: ...

    def caption(self, images: list[Image], level: CaptionLevel = CaptionLevel.NORMAL) -> list[str]: ...


@dataclass
class AppContext:
    """Context for the FastMCP app."""

    processor: Processor


def new_server(name: str, model_id: str, subprocess: bool = True, remote: bool = False) -> FastMCP:
    @asynccontextmanager
    async def app_lifespan(_server: FastMCP) -> AsyncIterator[AppContext]:
        if subprocess:
            processor = Florence2SP(model_id)
        else:
            processor = Florence2(model_id)
        yield AppContext(processor)

    mcp = FastMCP(name, lifespan=app_lifespan)

    if not remote:
        @mcp.tool()
        def ocr(
                ctx: Context,
                file_paths: list[PathLike] = Field(
                    "A list of file paths to the image files that need to be processed."),
        ) -> list[str]:
            """Processes image file paths with OCR and returning recognized text."""
            return ctx.request_context.lifespan_context.processor.ocr(open_images(file_paths))

        @mcp.tool()
        def caption(
                ctx: Context,
                file_paths: list[PathLike] = Field(
                    "A list of file paths to the image files that need to be processed."),
        ) -> list[str]:
            """Generates detailed captions for a list of image file paths."""
            return ctx.request_context.lifespan_context.processor.caption(
                open_images(file_paths), CaptionLevel.MORE_DETAILED
            )

    @mcp.tool()
    def ocr_urls(
            ctx: Context,
            urls: list[str] = Field("A list of urls to the image files that need to be processed."),
    ) -> list[str]:
        """Processes image urls with OCR and returning recognized text."""
        return ctx.request_context.lifespan_context.processor.ocr(download_images(urls))

    @mcp.tool()
    def caption_urls(
            ctx: Context,
            urls: list[str] = Field("A list of urls to the image files that need to be processed."),
    ) -> list[str]:
        """Generates detailed captions for a list of image urls."""
        return ctx.request_context.lifespan_context.processor.caption(download_images(urls), CaptionLevel.MORE_DETAILED)

    return mcp
