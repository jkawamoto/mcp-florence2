# Florence-2 MCP Server

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Python Application](https://github.com/jkawamoto/mcp-florence2/actions/workflows/python-app.yaml/badge.svg)](https://github.com/jkawamoto/mcp-florence2/actions/workflows/python-app.yaml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![GitHub License](https://img.shields.io/github/license/jkawamoto/mcp-florence2)](https://github.com/jkawamoto/mcp-florence2/blob/main/LICENSE)

[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/jkawamoto-mcp-florence2-badge.png)](https://mseep.ai/app/jkawamoto-mcp-florence2)

An MCP server for processing images using [Florence-2](https://huggingface.co/microsoft/Florence-2-large)
and [Moondream2](https://huggingface.co/vikhyatk/moondream2).

You can process images or PDF files stored on a local or web server to extract text using OCR (Optical Character
Recognition), generate descriptive captions summarizing the content of the images, locate named objects and
return their bounding boxes or centre points, caption every salient region, and ask free-form questions about an
image.

Florence-2 handles captioning, OCR, detection and grounding. Moondream2 backs the `query_image` tool, because
Florence-2 has no open-ended visual question answering task.

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

### detect_objects

Detect instances of a named object in an image, returning bounding boxes and labels.

#### Arguments:

- **src**: A file path or URL to the image file that needs to be processed.
- **object_name**: Name of the object to locate, e.g. `person`, `car`, `face`.

### point_objects

Locate instances of a named object in an image, returning the centre coordinates of each match.

#### Arguments:

- **src**: A file path or URL to the image file that needs to be processed.
- **object_name**: Name of the object to locate, e.g. `person`, `car`, `face`.

### dense_region_caption

Generate a caption for every salient region of an image, with bounding boxes.

#### Arguments:

- **src**: A file path or URL to the image file that needs to be processed.

### query_image

Ask a free-form question about an image (visual question answering). Backed by Moondream2.

#### Arguments:

- **src**: A file path or URL to the image file that needs to be processed.
- **question**: A free-form question to ask about the image.

### analyze_image

Multi-purpose tool that dispatches to any of the operations above. Useful for agents that would rather choose an
operation by name than pick between tools.

#### Arguments:

- **src**: A file path or URL to the image file that needs to be processed.
- **operation**: One of `caption`, `ocr`, `detect`, `point`, `dense_caption`, `query`.
- **question**: Required when the operation is `query`.
- **object_name**: Required when the operation is `detect` or `point`.

### batch_analyze_images

Runs `analyze_image`'s operation over several images. Each image reports its own success or failure, so one bad
file does not abort the batch.

#### Arguments:

- **srcs**: File paths or URLs of the images to process.
- **operation**: One of `caption`, `ocr`, `detect`, `point`, `dense_caption`, `query`.
- **question**: Required when the operation is `query`.
- **object_name**: Required when the operation is `detect` or `point`.

### process

Processes an image file with a custom prompt using the Florence-2 model. Useful for Florence-2
task tokens this server does not expose as their own tool.

#### Arguments:

- **src**: A file path or URL to the image file that needs to be processed.
- **prompt**: A custom prompt for the Florence-2 model.

## Options

- **--model**: The Florence-2 model used for captioning, OCR, detection and grounding.
- **--cache-model**: Keep the Florence-2 model loaded between requests instead of running each one in a fresh
  subprocess.
- **--moondream-model** / **--moondream-revision**: The Moondream2 model and revision backing `query_image`.
- **--idle-timeout**: Minutes of inactivity after which both models are unloaded and their memory released; they
  reload automatically on the next request. `0`, the default, keeps them loaded for the lifetime of the server.

The models are large, so a server left running holds several gigabytes of memory. Setting `--idle-timeout 10`
keeps repeat calls fast during a burst of work while handing the memory back once the work stops.


## License

This application is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
