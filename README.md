# Florence-2 MCP Server
[![GitHub License](https://img.shields.io/github/license/jkawamoto/mcp-florence2)](https://github.com/jkawamoto/mcp-florence2/blob/main/LICENSE)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![smithery badge](https://smithery.ai/badge/@jkawamoto/mcp-florence2)](https://smithery.ai/server/@jkawamoto/mcp-florence2)

An MCP server for processing images using [Florence-2](https://huggingface.co/microsoft/Florence-2-large).

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
    args: [--from, git+https://github.com/jkawamoto/mcp-florence2, mcp-florence2]
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
Performs Optical Character Recognition (OCR) on the provided image file paths.

#### Arguments:
- **file_paths**: A list of file paths to the image files to be processed.

### ocr_urls
Processes image urls with OCR and returning recognized text.

#### Arguments:
- **urls**: A list of urls to the image files that need to be processed.

### caption
Generates detailed and descriptive captions for the provided image file paths.

#### Arguments:
- **file_paths**: A list of file paths to the image files to be processed.

### caption_urls
Generates detailed captions for a list of image urls.

#### Arguments:
- **urls**: A list of urls to the image files that need to be processed.

## License
This application is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
