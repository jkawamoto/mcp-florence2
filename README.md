# Florence-2 MCP Server

[![Python Application](https://github.com/jkawamoto/mcp-florence2/actions/workflows/python-app.yaml/badge.svg)](https://github.com/jkawamoto/mcp-florence2/actions/workflows/python-app.yaml)
[![GitHub License](https://img.shields.io/github/license/jkawamoto/mcp-florence2)](https://github.com/jkawamoto/mcp-florence2/blob/main/LICENSE)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![smithery badge](https://smithery.ai/badge/@jkawamoto/mcp-florence2)](https://smithery.ai/server/@jkawamoto/mcp-florence2)

An MCP server for processing images using [Florence-2](https://huggingface.co/microsoft/Florence-2-large).

You can process images or PDF files stored on a local or web server to extract text using OCR (Optical Character
Recognition) or generate descriptive captions summarizing the content of the images.

## Installation

### For Claude Desktop

To configure this server for Claude Desktop, edit the `claude_desktop_config.json` file with the following entry under
`mcpServers`:

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
For more information,
see: [For Claude Desktop Users - Model Context Protocol](https://modelcontextprotocol.io/quickstart/user).

### For Goose CLI

To enable the Bear extension in Goose CLI,
edit the configuration file `~/.config/goose/config.yaml` to include the following entry:

```yaml
extensions:
  bear:
    name: Florence-2
    cmd: uvx
    args: [ --from, git+https://github.com/jkawamoto/mcp-florence2, mcp-florence2 ]
    enabled: true
    type: stdio
```

### For Goose Desktop

Add a new extension with the following settings:

- **Type**: Standard IO
- **ID**: florence-2
- **Name**: Florence-2
- **Description**: An MCP server for processing images using Florence-2
- **Command**: `uvx --from git+https://github.com/jkawamoto/mcp-florence2 mcp-florence2`

For more details on configuring MCP servers in Goose Desktop,
refer to the documentation:
[Using Extensions - MCP Servers](https://block.github.io/goose/docs/getting-started/using-extensions#mcp-servers).

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
