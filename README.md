# Florence-2 MCP Server

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Python Application](https://github.com/jkawamoto/mcp-florence2/actions/workflows/python-app.yaml/badge.svg)](https://github.com/jkawamoto/mcp-florence2/actions/workflows/python-app.yaml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![GitHub License](https://img.shields.io/github/license/jkawamoto/mcp-florence2)](https://github.com/jkawamoto/mcp-florence2/blob/main/LICENSE)

[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/jkawamoto-mcp-florence2-badge.png)](https://mseep.ai/app/jkawamoto-mcp-florence2)

**Florence-2 MCP Server** brings local vision intelligence and Optical Character Recognition (OCR) to your AI assistants via the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/). Powered by Microsoft's [Florence-2](https://huggingface.co/microsoft/Florence-2-large) foundation model, it lets your LLMs inspect, caption, and extract text from local images, web URLs, and multi-page PDF documents — entirely offline and on your own machine.

---

## ✨ Key Features

- 🔒 **100% Local & Private**: All image and document processing runs on your local machine. No external vision API fees, token limits, or data sharing.
- 📄 **Multi-Page PDF & Image Support**: Process common image formats (JPEG, PNG, WebP, etc.) as well as multi-page PDF documents page-by-page.
- ⚡ **Native Hardware Acceleration**: Automatically detects and leverages **Apple Silicon (MPS)**, **NVIDIA GPU (CUDA)**, or **CPU**.
- 🧹 **Zero VRAM Waste**: By default, inference runs in an on-demand subprocess to release VRAM immediately after completion. A `--cache-model` flag is available for low-latency continuous usage.
- 🎯 **Rich Vision Tasks**: Perform high-precision text OCR, detailed descriptive captioning, and open-ended visual queries using native Florence-2 prompt tokens (e.g. object detection, region descriptions).
- 📦 **One-Click Installs**: Ready-to-use `.mcpb` bundle for Claude Desktop, 1-click deeplink for LM Studio, and extension support for Goose.

---

## 🚀 Quick Installation

Choose your preferred MCP client below:

### Claude Desktop

#### Option 1: One-Click Extension Bundle (Recommended)

1. Download the latest `mcp-florence2.mcpb` bundle from the [Releases](https://github.com/jkawamoto/mcp-florence2/releases) page.
2. Double-click the downloaded `.mcpb` file, or drag-and-drop it into Claude Desktop's Settings window.

#### Option 2: Manual Configuration

Add the following configuration to your `claude_desktop_config.json`:

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

> [!NOTE]
> Config file locations:
> - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
> - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

For more details, see [Connect to local MCP servers](https://modelcontextprotocol.io/docs/develop/connect-local-servers).

---

### Goose

#### Option 1: One-Click URL

Click the link below to launch the Goose extension installer:

```text
goose://extension?cmd=uvx&arg=--from&arg=git%2Bhttps%3A%2F%2Fgithub.com%2Fjkawamoto%2Fmcp-florence2&arg=mcp-florence2&id=florence2&name=Florence-2&description=An%20MCP%20server%20for%20processing%20images%20using%20Florence-2
```

#### Option 2: Manual Configuration

Add the following to `~/.config/goose/config.yaml`:

```yaml
extensions:
  florence2:
    name: Florence-2
    cmd: uvx
    args: [ --from, git+https://github.com/jkawamoto/mcp-florence2, mcp-florence2 ]
    enabled: true
    type: stdio
```

For more details, refer to [Using Extensions | goose](https://block.github.io/goose/docs/getting-started/using-extensions#mcp-servers).

---

### LM Studio

Click the button below to install directly into LM Studio:

[![Add MCP Server florence-2 to LM Studio](https://files.lmstudio.ai/deeplink/mcp-install-light.svg)](https://lmstudio.ai/install-mcp?name=florence-2&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyItLWZyb20iLCJnaXQraHR0cHM6Ly9naXRodWIuY29tL2prYXdhbW90by9tY3AtZmxvcmVuY2UyIiwibWNwLWZsb3JlbmNlMiJdfQ%3D%3D)

---

### Claude Code, Cursor, Cline & Other MCP Clients

You can connect any client that supports `stdio` MCP servers using `uvx`:

```bash
uvx --from git+https://github.com/jkawamoto/mcp-florence2 mcp-florence2
```

---

## 🛠️ Tools

The server automatically equips your AI assistant with the following vision capabilities. You can interact with them using natural language:

### 1. `ocr`
Extracts all visible text from images or multi-page PDF documents.

- **Example user request:** *"Please extract all text from `/path/to/invoice.pdf`."*
- **Multi-page support:** Automatically iterates through every page in a PDF document.

<details>
<summary><b>Tool schema & parameters</b></summary>

| Parameter | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `src` | `string` | **Yes** | Local file path or HTTP/HTTPS URL of an image or PDF file. |

</details>

---

### 2. `caption`
Generates comprehensive, detailed captions describing what is depicted in the image.

- **Example user request:** *"Describe what is shown in `https://example.com/photo.jpg`."*
- Returns granular descriptions of objects, spatial relationships, colors, and background scenery.

<details>
<summary><b>Tool schema & parameters</b></summary>

| Parameter | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `src` | `string` | **Yes** | Local file path or HTTP/HTTPS URL of an image or PDF file. |

</details>

---

### 3. `process`
Executes custom Florence-2 task prompts directly against the input image or PDF for advanced computer vision workflows (such as object detection or region captioning).

- **Example user request:** *"Detect all objects in this image and return their bounding boxes."*

<details>
<summary><b>Tool schema & supported task prompts</b></summary>

#### Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `src` | `string` | **Yes** | Local file path or HTTP/HTTPS URL of an image or PDF file. |
| `prompt` | `string` | **Yes** | Task prompt specifying the operation to perform. |

#### Supported Florence-2 Task Prompts

| Task Prompt | Description |
| :--- | :--- |
| `<CAPTION>` | Concise one-sentence summary of the image. |
| `<DETAILED_CAPTION>` | Moderate-length description of the image content. |
| `<MORE_DETAILED_CAPTION>` | Highly detailed and exhaustive scene description. |
| `<OCR>` | Plain text extraction from the image. |
| `<OCR_WITH_REGION>` | Text extraction along with bounding box coordinates. |
| `<OD>` | Object detection (identifies objects and their bounding boxes). |
| `<DENSE_REGION_CAPTION>` | Generates descriptions for multiple distinct regions. |
| `<REGION_PROPOSAL>` | Identifies candidate bounding boxes for prominent visual regions. |

</details>

---

## ⚙️ Configuration & CLI Options

The server can be customized using command-line arguments:

```bash
mcp-florence2 [OPTIONS]
```

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--model` | `string` | `florence-community/Florence-2-large` | Hugging Face model identifier to load. |
| `--cache-model` | `flag` | `false` | Keeps the model in VRAM for faster repeated calls (by default, models run in subprocesses to free memory when idle). |
| `--version` | `flag` | - | Show version information. |
| `--help` | `flag` | - | Show help message and exit. |

### Using a Smaller / Faster Model
If you have limited GPU memory or want faster execution, switch to `Florence-2-base`:

```json
{
  "mcpServers": {
    "florence-2": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/jkawamoto/mcp-florence2",
        "mcp-florence2",
        "--model",
        "florence-community/Florence-2-base"
      ]
    }
  }
}
```

---

## 🛡️ Security Considerations

When processing URLs starting with `http://` or `https://`, outbound HTTP requests are initiated directly from the server process. In environments where untrusted users or prompts may supply URLs, this could potentially expose the server to **Server-Side Request Forgery (SSRF)** targeting internal network services or cloud metadata endpoints.

> [!WARNING]
> In multi-tenant or untrusted environments, route outgoing HTTP(S) traffic through an SSRF-safe forward proxy (such as [Smokescreen](https://github.com/stripe/smokescreen) or Squid configured to block private/internal IP ranges).

Since Python's `requests` library automatically respects standard environment variables, proxy settings can be configured directly in your client configuration:

- `HTTP_PROXY` / `http_proxy`: Proxy URL for HTTP requests.
- `HTTPS_PROXY` / `https_proxy`: Proxy URL for HTTPS requests.
- `NO_PROXY` / `no_proxy`: Comma-separated list of hosts to bypass the proxy.

<details>
<summary><b>Proxy Configuration Examples</b></summary>

#### Claude Desktop
Add the `env` block to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "florence-2": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/jkawamoto/mcp-florence2",
        "mcp-florence2"
      ],
      "env": {
        "HTTP_PROXY": "http://proxy.example.com:8080",
        "HTTPS_PROXY": "http://proxy.example.com:8080"
      }
    }
  }
}
```

#### Goose
Add the `env` block to `~/.config/goose/config.yaml`:

```yaml
extensions:
  florence2:
    name: Florence-2
    cmd: uvx
    args: [ --from, git+https://github.com/jkawamoto/mcp-florence2, mcp-florence2 ]
    env:
      HTTP_PROXY: "http://proxy.example.com:8080"
      HTTPS_PROXY: "http://proxy.example.com:8080"
    enabled: true
    type: stdio
```

</details>

---

## 💻 Development

### Setup & Run Tests

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable dependency management.

```bash
# Clone the repository
git clone https://github.com/jkawamoto/mcp-florence2.git
cd mcp-florence2

# Install dependencies and run tests
uv run pytest

# Run pre-commit checks
uv run pre-commit run --all-files
```

---

## 📄 License

This application is released under the [MIT License](LICENSE).
