# Florence-2 MCP Server

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Python Application](https://github.com/jkawamoto/mcp-florence2/actions/workflows/python-app.yaml/badge.svg)](https://github.com/jkawamoto/mcp-florence2/actions/workflows/python-app.yaml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![GitHub License](https://img.shields.io/github/license/jkawamoto/mcp-florence2)](https://github.com/jkawamoto/mcp-florence2/blob/main/LICENSE)

[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/jkawamoto-mcp-florence2-badge.png)](https://mseep.ai/app/jkawamoto-mcp-florence2)

An MCP server for processing images using [Florence-2](https://huggingface.co/microsoft/Florence-2-large).

You can process images or PDF files stored on a local or web server to extract text using OCR (Optical Character
Recognition) or generate descriptive captions summarizing the content of the images.

## Installation

### [Claude](https://claude.com/download)
Download the latest MCP bundle `mcp-florence2.mcpb` from
the [Releases](https://github.com/jkawamoto/mcp-florence2/releases) page,
then open the downloaded `.mcpb `file or drag it into the Claude Desktop's Settings window.

<details>
<summary>Manually configuration</summary>

You can also manually configure this server for Claude Desktop.
Edit the `claude_desktop_config.json` file by adding the following entry under `mcpServers`:

```json
{
  "mcpServers": {
    "florence-2": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/jkawamoto/mcp-florence2",
        "mcp-florence2"
      ]
    }
  }
}
```

After editing, restart the application.

</details>

For more information,
see: [Connect to local MCP servers - Model Context Protocol](https://modelcontextprotocol.io/docs/develop/connect-local-servers).

### [goose](https://block.github.io/goose/)
Open this link
```
goose://extension?cmd=uvx&arg=--from&arg=git%2Bhttps%3A%2F%2Fgithub.com%2Fjkawamoto%2Fmcp-florence2&arg=mcp-florence2&id=florence2&name=Florence-2&description=An%20MCP%20server%20for%20processing%20images%20using%20Florence-2
```
to launch the installer, then click "Yes" to confirm the installation.

<details>
<summary>Manually configuration</summary>

You can also directly edit the config file (`~/.config/goose/config.yaml`) to include the following entry:

```yaml
extensions:
  florence2:
    name: Florence-2
    cmd: uvx
    args: [ --from, git+https://github.com/jkawamoto/mcp-florence2, mcp-florence2 ]
    enabled: true
    type: stdio
```
</details>

For more details on configuring MCP servers in Goose, refer to the documentation:
[Using Extensions | goose](https://block.github.io/goose/docs/getting-started/using-extensions#mcp-servers).

### [LM Studio](https://lmstudio.ai/)
To configure this server for LM Studio, click the button below.

[![Add MCP Server florence-2 to LM Studio](https://files.lmstudio.ai/deeplink/mcp-install-light.svg)](https://lmstudio.ai/install-mcp?name=florence-2&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyItLWZyb20iLCJnaXQraHR0cHM6Ly9naXRodWIuY29tL2prYXdhbW90by9tY3AtZmxvcmVuY2UyIiwibWNwLWZsb3JlbmNlMiJdfQ%3D%3D)

## Tools

### ocr

Process an image file or URL using OCR to extract text.

#### Arguments:

- **src**: A file path or URL to the image file that needs to be processed.

### caption

Processes an image file and generates captions for the image.

#### Arguments:

- **src**: A file path or URL to the image file that needs to be processed.

## License

This application is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
