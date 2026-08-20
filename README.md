# FusionVisionMCP

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Python Application](https://github.com/warrens951/FusionVisionMCP/actions/workflows/python-app.yaml/badge.svg)](https://github.com/warrens951/FusionVisionMCP/actions/workflows/python-app.yaml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![GitHub License](https://img.shields.io/github/license/warrens951/FusionVisionMCP)](https://github.com/warrens951/FusionVisionMCP/blob/main/LICENSE)

An MCP server fusing [Florence-2](https://huggingface.co/microsoft/Florence-2-large)
and [Moondream2](https://huggingface.co/vikhyatk/moondream2) into one computer-vision toolset. Fork of
[jkawamoto/mcp-florence2](https://github.com/jkawamoto/mcp-florence2), adding Moondream2 visual question
answering, object grounding, batch analysis, and idle-timeout memory release on top of the original
Florence-2-only server.

You can process images or PDF files stored on a local or web server to extract text using OCR (Optical Character
Recognition), generate descriptive captions summarizing the content of the images, locate named objects and
return their bounding boxes or centre points, caption every salient region, and ask free-form questions about an
image.

Florence-2 handles captioning, OCR, detection and grounding. Moondream2 backs the `query_image` tool, because
Florence-2 has no open-ended visual question answering task.

> **OCR vs. query_image**: Florence-2's OCR head is built for dense, printed, document-style text and can
> confidently misread stylized, cursive, or low-contrast text (watermarks, logos, signage) rather than failing
> visibly. For that kind of text, prefer `query_image` with a question like *"What does the text/watermark say,
> exactly?"* — see the routing note in each tool's description below.

## Installation

### [Claude](https://claude.com/download)
Download the latest MCP bundle `fusion-vision-mcp.mcpb` from
the [Releases](https://github.com/warrens951/FusionVisionMCP/releases) page,
then open the downloaded `.mcpb `file or drag it into the Claude Desktop's Settings window.

<details>
<summary>Manually configuration</summary>

You can also manually configure this server for Claude Desktop.
Edit the `claude_desktop_config.json` file by adding the following entry under `mcpServers`:

```json
{
  "mcpServers": {
    "fusionvision": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/warrens951/FusionVisionMCP",
        "fusion-vision-mcp"
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

You can directly edit the config file (`~/.config/goose/config.yaml`) to include the following entry:

```yaml
extensions:
  fusionvision:
    name: FusionVisionMCP
    cmd: uvx
    args: [ --from, git+https://github.com/warrens951/FusionVisionMCP, fusion-vision-mcp ]
    enabled: true
    type: stdio
```

For more details on configuring MCP servers in Goose, refer to the documentation:
[Using Extensions | goose](https://block.github.io/goose/docs/getting-started/using-extensions#mcp-servers).

### [LM Studio](https://lmstudio.ai/)

Add an MCP server entry pointing at this package, using the same `command`/`args` shown in the manual
configuration above.

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
