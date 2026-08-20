#  test_server.py
#
#  Copyright (c) 2025-2026 Junpei Kawamoto
#
#  This software is released under the MIT License.
#
#  http://opensource.org/licenses/mit-license.php
import json
import os
import socketserver
import threading
from collections.abc import AsyncGenerator, Generator
from functools import partial
from http import server
from pathlib import Path
from typing import cast

import pytest
from mcp import ClientSession, StdioServerParameters, stdio_client
from mcp.types import TextContent

TEST_DIR = Path(__file__).resolve().parent
SAMPLE_IMAGE_FILEPATH = str(TEST_DIR / "sample.jpg")
SAMPLE_PDF_FILEPATH = str(TEST_DIR / "sample.pdf")

SERVER_PARAMS = StdioServerParameters(
    command="uv",
    args=["run", "fusion-vision-mcp", "--cache-model", "--model", "florence-community/Florence-2-base"],
)


@pytest.fixture(scope="module")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="module")
async def mcp_client_session() -> AsyncGenerator[ClientSession, None]:
    async with stdio_client(SERVER_PARAMS) as streams, ClientSession(streams[0], streams[1]) as session:
        await session.initialize()
        yield session


@pytest.fixture(scope="module")
def static_file_server() -> Generator[str, None, None]:
    with socketserver.TCPServer(
        ("", 0),
        partial(server.SimpleHTTPRequestHandler, directory=os.path.dirname(__file__)),
    ) as httpd:
        port = httpd.server_address[1]
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.start()

        try:
            yield f"http://localhost:{port}"
        finally:
            httpd.shutdown()
            httpd.server_close()
            server_thread.join()


@pytest.mark.anyio
async def test_list_tools(mcp_client_session: ClientSession) -> None:
    res = await mcp_client_session.list_tools()
    tools = {tool.name for tool in res.tools}

    assert "caption" in tools
    assert "ocr" in tools
    assert "detect_objects" in tools
    assert "point_objects" in tools
    assert "dense_region_caption" in tools
    assert "query_image" in tools
    assert "analyze_image" in tools
    assert "batch_analyze_images" in tools
    assert "process" in tools


@pytest.mark.anyio
async def test_caption(mcp_client_session: ClientSession) -> None:
    res = await mcp_client_session.call_tool(
        "caption",
        arguments={"src": SAMPLE_IMAGE_FILEPATH},
    )
    text = "\n".join(cast(TextContent, c).text for c in res.content)

    assert len(text) > 0
    assert not res.is_error


@pytest.mark.anyio
async def test_caption_url(mcp_client_session: ClientSession, static_file_server: str) -> None:
    res = await mcp_client_session.call_tool(
        "caption",
        arguments={"src": static_file_server + "/sample.jpg"},
    )
    text = "\n".join(cast(TextContent, c).text for c in res.content)

    assert len(text) > 0
    assert not res.is_error


@pytest.mark.anyio
async def test_caption_pdf(mcp_client_session: ClientSession) -> None:
    res = await mcp_client_session.call_tool(
        "caption",
        arguments={"src": SAMPLE_PDF_FILEPATH},
    )
    text = "\n".join(cast(TextContent, c).text for c in res.content)

    assert len(text) > 0
    assert not res.is_error


@pytest.mark.anyio
async def test_caption_pdf_from_web(mcp_client_session: ClientSession, static_file_server: str) -> None:
    res = await mcp_client_session.call_tool(
        "caption",
        arguments={"src": static_file_server + "/sample.pdf"},
    )
    text = "\n".join(cast(TextContent, c).text for c in res.content)

    assert len(text) > 0
    assert not res.is_error


@pytest.mark.anyio
async def test_ocr(mcp_client_session: ClientSession) -> None:
    res = await mcp_client_session.call_tool(
        "ocr",
        arguments={"src": SAMPLE_IMAGE_FILEPATH},
    )
    text = "\n".join(cast(TextContent, c).text for c in res.content)

    assert len(text) > 0
    assert not res.is_error


@pytest.mark.anyio
async def test_ocr_url(mcp_client_session: ClientSession, static_file_server: str) -> None:
    res = await mcp_client_session.call_tool(
        "ocr",
        arguments={"src": static_file_server + "/sample.jpg"},
    )
    text = "\n".join(cast(TextContent, c).text for c in res.content)

    assert len(text) > 0
    assert not res.is_error


@pytest.mark.anyio
async def test_ocr_pdf(mcp_client_session: ClientSession) -> None:
    res = await mcp_client_session.call_tool(
        "ocr",
        arguments={"src": SAMPLE_PDF_FILEPATH},
    )
    text = "\n".join(cast(TextContent, c).text for c in res.content)

    assert len(text) > 0
    assert not res.is_error


@pytest.mark.anyio
async def test_ocr_pdf_from_web(mcp_client_session: ClientSession, static_file_server: str) -> None:
    res = await mcp_client_session.call_tool(
        "ocr",
        arguments={"src": static_file_server + "/sample.pdf"},
    )
    text = "\n".join(cast(TextContent, c).text for c in res.content)

    assert len(text) > 0
    assert not res.is_error


@pytest.mark.anyio
async def test_detect_objects(mcp_client_session: ClientSession) -> None:
    res = await mcp_client_session.call_tool(
        "detect_objects",
        arguments={"src": SAMPLE_IMAGE_FILEPATH, "object_name": "person"},
    )
    regions = json.loads("\n".join(cast(TextContent, c).text for c in res.content))

    assert not res.is_error
    assert "bboxes" in regions
    assert "labels" in regions


@pytest.mark.anyio
async def test_point_objects(mcp_client_session: ClientSession) -> None:
    res = await mcp_client_session.call_tool(
        "point_objects",
        arguments={"src": SAMPLE_IMAGE_FILEPATH, "object_name": "person"},
    )
    regions = json.loads("\n".join(cast(TextContent, c).text for c in res.content))

    assert not res.is_error
    assert "points" in regions
    assert "labels" in regions
    # Points are centres, so each one carries an x and a y.
    assert all(len(point) == 2 for point in regions["points"])


@pytest.mark.anyio
async def test_dense_region_caption(mcp_client_session: ClientSession) -> None:
    res = await mcp_client_session.call_tool(
        "dense_region_caption",
        arguments={"src": SAMPLE_IMAGE_FILEPATH},
    )
    regions = json.loads("\n".join(cast(TextContent, c).text for c in res.content))

    assert not res.is_error
    assert "bboxes" in regions
    assert "labels" in regions


@pytest.mark.anyio
async def test_analyze_image_dispatches_to_ocr(mcp_client_session: ClientSession) -> None:
    res = await mcp_client_session.call_tool(
        "analyze_image",
        arguments={"src": SAMPLE_IMAGE_FILEPATH, "operation": "ocr"},
    )
    text = "\n".join(cast(TextContent, c).text for c in res.content)

    assert not res.is_error
    assert len(text) > 0


@pytest.mark.anyio
async def test_analyze_image_rejects_unknown_operation(mcp_client_session: ClientSession) -> None:
    res = await mcp_client_session.call_tool(
        "analyze_image",
        arguments={"src": SAMPLE_IMAGE_FILEPATH, "operation": "translate"},
    )

    assert res.is_error


@pytest.mark.anyio
async def test_analyze_image_requires_object_name_for_detect(mcp_client_session: ClientSession) -> None:
    res = await mcp_client_session.call_tool(
        "analyze_image",
        arguments={"src": SAMPLE_IMAGE_FILEPATH, "operation": "detect"},
    )

    assert res.is_error


@pytest.mark.anyio
async def test_batch_analyze_images(mcp_client_session: ClientSession) -> None:
    res = await mcp_client_session.call_tool(
        "batch_analyze_images",
        arguments={"srcs": [SAMPLE_IMAGE_FILEPATH, SAMPLE_IMAGE_FILEPATH], "operation": "ocr"},
    )
    results = [json.loads(cast(TextContent, c).text) for c in res.content]

    assert not res.is_error
    assert len(results) == 2
    assert all(item["success"] for item in results)


@pytest.mark.anyio
async def test_batch_analyze_images_reports_failures_per_image(mcp_client_session: ClientSession) -> None:
    missing = str(TEST_DIR / "does-not-exist.jpg")
    res = await mcp_client_session.call_tool(
        "batch_analyze_images",
        arguments={"srcs": [SAMPLE_IMAGE_FILEPATH, missing], "operation": "ocr"},
    )
    results = [json.loads(cast(TextContent, c).text) for c in res.content]

    # A bad image must not abort the batch: the good one still reports a result.
    assert not res.is_error
    assert results[0]["success"]
    assert not results[1]["success"]
    assert results[1]["error"]


@pytest.mark.anyio
async def test_process(mcp_client_session: ClientSession) -> None:
    res = await mcp_client_session.call_tool(
        "process",
        arguments={"src": SAMPLE_IMAGE_FILEPATH, "prompt": "<CAPTION>"},
    )
    text = "\n".join(cast(TextContent, c).text for c in res.content)

    assert len(text) > 0
    assert not res.is_error


@pytest.mark.anyio
async def test_process_url(mcp_client_session: ClientSession, static_file_server: str) -> None:
    res = await mcp_client_session.call_tool(
        "process",
        arguments={"src": static_file_server + "/sample.jpg", "prompt": "<CAPTION>"},
    )
    text = "\n".join(cast(TextContent, c).text for c in res.content)

    assert len(text) > 0
    assert not res.is_error


@pytest.mark.anyio
async def test_process_pdf(mcp_client_session: ClientSession) -> None:
    res = await mcp_client_session.call_tool(
        "process",
        arguments={"src": SAMPLE_PDF_FILEPATH, "prompt": "<CAPTION>"},
    )
    text = "\n".join(cast(TextContent, c).text for c in res.content)

    assert len(text) > 0
    assert not res.is_error


@pytest.mark.anyio
async def test_process_pdf_from_web(mcp_client_session: ClientSession, static_file_server: str) -> None:
    res = await mcp_client_session.call_tool(
        "process",
        arguments={"src": static_file_server + "/sample.pdf", "prompt": "<CAPTION>"},
    )
    text = "\n".join(cast(TextContent, c).text for c in res.content)

    assert len(text) > 0
    assert not res.is_error
