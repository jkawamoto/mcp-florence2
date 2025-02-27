#  test_server.py
#
#  Copyright (c) 2025 Junpei Kawamoto
#
#  This software is released under the MIT License.
#
#  http://opensource.org/licenses/mit-license.php
import os
import socketserver
import threading
from functools import partial
from http import server
from typing import AsyncGenerator, Generator, cast

import pytest
from mcp import StdioServerParameters, ClientSession, stdio_client
from mcp.types import TextContent

SAMPLE_IMAGE_FILEPATH = os.path.join(os.path.dirname(__file__), "sample.jpg")
SAMPLE_PDF_FILEPATH = os.path.join(os.path.dirname(__file__), "sample.pdf")

SERVER_PARAMS = StdioServerParameters(command="uv", args=["run", "mcp-florence2", "--cache-model", "--model", "base"])


@pytest.fixture(scope="module")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="module")
async def mcp_client_session() -> AsyncGenerator[ClientSession, None]:
    async with stdio_client(SERVER_PARAMS) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
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
    tools = set(tool.name for tool in res.tools)

    assert "caption" in tools
    assert "ocr" in tools


@pytest.mark.anyio
async def test_caption(mcp_client_session: ClientSession) -> None:
    res = await mcp_client_session.call_tool(
        "caption",
        arguments={"src": SAMPLE_IMAGE_FILEPATH},
    )
    text = "\n".join(cast(TextContent, c).text for c in res.content)

    assert len(text) > 0
    assert not res.isError


@pytest.mark.anyio
async def test_caption_url(mcp_client_session: ClientSession, static_file_server: str) -> None:
    res = await mcp_client_session.call_tool(
        "caption",
        arguments={"src": static_file_server + "/sample.jpg"},
    )
    text = "\n".join(cast(TextContent, c).text for c in res.content)

    assert len(text) > 0
    assert not res.isError


@pytest.mark.anyio
async def test_caption_pdf(mcp_client_session: ClientSession) -> None:
    res = await mcp_client_session.call_tool(
        "caption",
        arguments={"src": SAMPLE_PDF_FILEPATH},
    )
    text = "\n".join(cast(TextContent, c).text for c in res.content)

    assert len(text) > 0
    assert not res.isError


@pytest.mark.anyio
async def test_caption_pdf_from_web(mcp_client_session: ClientSession, static_file_server: str) -> None:
    res = await mcp_client_session.call_tool(
        "caption",
        arguments={"src": static_file_server + "/sample.pdf"},
    )
    text = "\n".join(cast(TextContent, c).text for c in res.content)

    assert len(text) > 0
    assert not res.isError


@pytest.mark.anyio
async def test_ocr(mcp_client_session: ClientSession) -> None:
    res = await mcp_client_session.call_tool(
        "ocr",
        arguments={"src": SAMPLE_IMAGE_FILEPATH},
    )
    text = "\n".join(cast(TextContent, c).text for c in res.content)

    assert len(text) > 0
    assert not res.isError


@pytest.mark.anyio
async def test_ocr_url(mcp_client_session: ClientSession, static_file_server: str) -> None:
    res = await mcp_client_session.call_tool(
        "ocr",
        arguments={"src": static_file_server + "/sample.jpg"},
    )
    text = "\n".join(cast(TextContent, c).text for c in res.content)

    assert len(text) > 0
    assert not res.isError


@pytest.mark.anyio
async def test_ocr_pdf(mcp_client_session: ClientSession) -> None:
    res = await mcp_client_session.call_tool(
        "ocr",
        arguments={"src": SAMPLE_PDF_FILEPATH},
    )
    text = "\n".join(cast(TextContent, c).text for c in res.content)

    assert len(text) > 0
    assert not res.isError


@pytest.mark.anyio
async def test_ocr_pdf_from_web(mcp_client_session: ClientSession, static_file_server: str) -> None:
    res = await mcp_client_session.call_tool(
        "ocr",
        arguments={"src": static_file_server + "/sample.pdf"},
    )
    text = "\n".join(cast(TextContent, c).text for c in res.content)

    assert len(text) > 0
    assert not res.isError
