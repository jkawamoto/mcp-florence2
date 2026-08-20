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
from typing import Annotated, Any, Final, Protocol, cast

import requests
from mcp.server.mcpserver import Context, MCPServer
from PIL.Image import Image
from PIL.Image import open as open_image
from pydantic import Field
from pypdfium2 import PdfDocument

from mcp_florence2.florence2 import CaptionLevel, Florence2, Florence2SP
from mcp_florence2.idle import IdleProxy, IdleReleased
from mcp_florence2.moondream import DEFAULT_MOONDREAM_MODEL, DEFAULT_MOONDREAM_REVISION, Moondream

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

    def detect_objects(self, images: list[Image], object_name: str) -> list[dict[str, Any]]:
        """Locates instances of the named object, returning bounding boxes and labels."""
        ...

    def point_objects(self, images: list[Image], object_name: str) -> list[dict[str, Any]]:
        """Locates instances of the named object, returning center points and labels."""
        ...

    def dense_region_caption(self, images: list[Image]) -> list[dict[str, Any]]:
        """Generates a caption for every salient region in the image, with bounding boxes."""
        ...

    def generate(self, prompt: str, images: list[Image]) -> list[str]:
        """Generates text responses for the given images based on a custom prompt.

        This function processes a list of images using the Florence-2 model with
        a custom prompt string. It allows for flexible image analysis by accepting
        task-specific prompts that define what information to extract or generate
        from the images.

        Args:
            prompt: A task prompt string that specifies the operation to perform
                on the images (e.g., "<OCR>", "<CAPTION>", or custom task prompts
                supported by the Florence-2 model).
            images: A list of PIL Image objects to be processed.

        Returns:
            A list of strings containing the generated text for each image, where
            each string corresponds to the model's response for the respective
            input image.
        """
        ...


class VqaProcessor(Protocol):
    """Represents a protocol for free-form visual question answering (VQA)."""

    def query(self, images: list[Image], question: str) -> list[str]:
        """Answers a free-form question about each image."""
        ...


@dataclass
class AppContext:
    """Context for the FastMCP app."""

    processor: Processor
    vqa: VqaProcessor


@asynccontextmanager
async def app_lifespan(
    _server: MCPServer,
    model_id: str,
    subprocess: bool,
    moondream_model_id: str,
    moondream_revision: str,
    idle_timeout: float = 0,
) -> AsyncIterator[AppContext]:
    """Context manager for the FastMCP app lifespan."""
    processor: Processor
    vqa: VqaProcessor
    if idle_timeout > 0:
        # Keep both models in this process so repeat calls stay fast, and let the
        # idle timer hand their memory back once the work stops.
        processor = cast(
            Processor,
            IdleProxy(IdleReleased(lambda: Florence2(model_id), idle_timeout, "Florence-2")),
        )
        vqa = cast(
            VqaProcessor,
            IdleProxy(
                IdleReleased(
                    lambda: Moondream(moondream_model_id, moondream_revision),
                    idle_timeout,
                    "Moondream",
                )
            ),
        )
    else:
        if subprocess:
            processor = Florence2SP(model_id)
        else:
            processor = Florence2(model_id)
        vqa = Moondream(moondream_model_id, moondream_revision)
    yield AppContext(processor, vqa)


def server(
    name: str,
    model_id: str,
    subprocess: bool = True,
    moondream_model_id: str = DEFAULT_MOONDREAM_MODEL,
    moondream_revision: str = DEFAULT_MOONDREAM_REVISION,
    idle_timeout: float = 0,
) -> MCPServer:
    """Creates a new FastMCP server instance with the specified name and model ID."""
    mcp = MCPServer(
        name,
        lifespan=partial(
            app_lifespan,
            model_id=model_id,
            subprocess=subprocess,
            moondream_model_id=moondream_model_id,
            moondream_revision=moondream_revision,
            idle_timeout=idle_timeout,
        ),
    )

    ImagePath = Annotated[
        os.PathLike[str] | str, Field(description="A file path or URL to the image file that needs to be processed.")
    ]
    ObjectName = Annotated[str, Field(description="Name of the object to locate, e.g. 'person', 'car', 'face'.")]
    CustomPrompt = Annotated[str, Field(description="A custom prompt for the Florence-2 model.")]

    @mcp.tool()
    def ocr(ctx: Context[AppContext], src: ImagePath) -> list[str]:
        """Process an image file or URL using OCR to extract text."""
        with get_images(src) as images:
            return ctx.request_context.lifespan_context.processor.ocr(images)

    @mcp.tool()
    def caption(ctx: Context[AppContext], src: ImagePath) -> list[str]:
        """Processes an image file and generates captions for the image."""
        with get_images(src) as images:
            return ctx.request_context.lifespan_context.processor.caption(images, CaptionLevel.MORE_DETAILED)

    @mcp.tool()
    def detect_objects(ctx: Context[AppContext], src: ImagePath, object_name: ObjectName) -> list[dict[str, Any]]:
        """Detect instances of a named object in an image, returning bounding boxes."""
        with get_images(src) as images:
            return ctx.request_context.lifespan_context.processor.detect_objects(images, object_name)

    @mcp.tool()
    def point_objects(ctx: Context[AppContext], src: ImagePath, object_name: ObjectName) -> list[dict[str, Any]]:
        """Locate instances of a named object in an image, returning center coordinates."""
        with get_images(src) as images:
            return ctx.request_context.lifespan_context.processor.point_objects(images, object_name)

    @mcp.tool()
    def dense_region_caption(ctx: Context[AppContext], src: ImagePath) -> list[dict[str, Any]]:
        """Generate a caption for every salient region of an image, with bounding boxes."""
        with get_images(src) as images:
            return ctx.request_context.lifespan_context.processor.dense_region_caption(images)

    @mcp.tool()
    def query_image(
        ctx: Context[AppContext],
        src: ImagePath,
        question: Annotated[str, Field(description="A free-form question to ask about the image.")],
    ) -> list[str]:
        """Ask a free-form question about an image (visual question answering)."""
        with get_images(src) as images:
            return ctx.request_context.lifespan_context.vqa.query(images, question)

    @mcp.tool()
    def analyze_image(
        ctx: Context[AppContext],
        src: ImagePath,
        operation: Annotated[
            str, Field(description="One of: 'caption', 'ocr', 'detect', 'point', 'dense_caption', 'query'.")
        ],
        question: Annotated[str, Field(description="Required when operation is 'query'.")] = "",
        object_name: Annotated[str, Field(description="Required when operation is 'detect' or 'point'.")] = "",
    ) -> Any:
        """Multi-purpose image analysis tool dispatching to caption/ocr/detect/point/dense_caption/query."""
        with get_images(src) as images:
            return _dispatch(
                ctx.request_context.lifespan_context, operation, images, question=question, object_name=object_name
            )

    @mcp.tool()
    def batch_analyze_images(
        ctx: Context[AppContext],
        srcs: Annotated[
            list[os.PathLike[str] | str], Field(description="File paths or URLs of the images to process.")
        ],
        operation: Annotated[
            str, Field(description="One of: 'caption', 'ocr', 'detect', 'point', 'dense_caption', 'query'.")
        ],
        question: Annotated[str, Field(description="Required when operation is 'query'.")] = "",
        object_name: Annotated[str, Field(description="Required when operation is 'detect' or 'point'.")] = "",
    ) -> list[dict[str, Any]]:
        """Runs analyze_image's operation over multiple images, reporting per-image success/failure."""
        results = []
        for src in srcs:
            try:
                with get_images(src) as images:
                    result = _dispatch(
                        ctx.request_context.lifespan_context,
                        operation,
                        images,
                        question=question,
                        object_name=object_name,
                    )
                results.append({"src": str(src), "success": True, "result": result})
            except Exception as e:  # noqa: BLE001 - reported per-image, batch must continue
                results.append({"src": str(src), "success": False, "error": str(e)})
        return results

    @mcp.tool()
    def process(ctx: Context[AppContext], src: ImagePath, prompt: CustomPrompt) -> list[str]:
        """Processes an image file with a custom prompt using the Florence-2 model."""
        with get_images(src) as images:
            return ctx.request_context.lifespan_context.processor.generate(prompt, images)

    return mcp


def _dispatch(app: AppContext, operation: str, images: list[Image], *, question: str, object_name: str) -> Any:
    """Routes an `analyze_image`/`batch_analyze_images` operation to the right processor call."""
    if operation == "caption":
        return app.processor.caption(images, CaptionLevel.MORE_DETAILED)
    if operation == "ocr":
        return app.processor.ocr(images)
    if operation == "detect":
        if not object_name:
            raise ValueError("object_name is required for the 'detect' operation")
        return app.processor.detect_objects(images, object_name)
    if operation == "point":
        if not object_name:
            raise ValueError("object_name is required for the 'point' operation")
        return app.processor.point_objects(images, object_name)
    if operation == "dense_caption":
        return app.processor.dense_region_caption(images)
    if operation == "query":
        if not question:
            raise ValueError("question is required for the 'query' operation")
        return app.vqa.query(images, question)
    raise ValueError(f"Unknown operation: {operation!r}")


__all__: Final = ["SERVER_NAME", "server"]
