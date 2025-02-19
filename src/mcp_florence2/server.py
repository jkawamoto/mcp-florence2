#  server.py
#
#  Copyright (c) 2025 Junpei Kawamoto
#
#  This software is released under the MIT License.
#
#  http://opensource.org/licenses/mit-license.php

from os import PathLike
from typing import Protocol

from PIL import Image
from mcp.server import FastMCP
from pydantic import Field

from mcp_florence2.florence2 import Florence2, Florence2SP, CaptionLevel


def open_images(file_paths: list[PathLike]) -> list[Image]:
    """Opens a list of image files and converts them to RGB mode."""
    return [Image.open(p).convert("RGB") for p in file_paths]


class Processor(Protocol):
    def ocr(self, images: list[Image]) -> list[str]: ...

    def caption(
        self, images: list[Image], level: CaptionLevel = CaptionLevel.NORMAL
    ) -> list[str]: ...


class Server:
    processor: Processor
    mcp: FastMCP

    def __init__(self, name: str, model_id: str, subprocess: bool = True):
        if subprocess:
            self.processor = Florence2SP(model_id)
        else:
            self.processor = Florence2(model_id)

        self.mcp = FastMCP(name)
        self.mcp.tool()(self.ocr)
        self.mcp.tool()(self.caption)

    def ocr(
        self,
        file_paths: list[PathLike] = Field(
            "A list of file paths to the image files that need to be processed."
        ),
    ) -> list[str]:
        """Processes image file paths with OCR, converting to RGB and returning recognized text."""
        return self.processor.ocr(open_images(file_paths))

    def caption(
        self,
        file_paths: list[PathLike] = Field(
            "A list of file paths to the image files that need to be processed."
        ),
    ) -> list[str]:
        """Generates detailed captions for a list of image file paths."""
        return self.processor.caption(
            open_images(file_paths), CaptionLevel.MORE_DETAILED
        )

    def run(self) -> None:
        """Run the server."""
        self.mcp.run()
