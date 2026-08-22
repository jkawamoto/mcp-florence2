# FusionVisionMCP

> **🚧 Work in progress — not ready for use.** This project is still being built out and is not
> published as a release. Nothing here is stable yet; expect breaking changes without notice.

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Python Application](https://github.com/Whoawhen/FusionVisionMCP/actions/workflows/python-app.yaml/badge.svg)](https://github.com/Whoawhen/FusionVisionMCP/actions/workflows/python-app.yaml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![GitHub License](https://img.shields.io/github/license/Whoawhen/FusionVisionMCP)](https://github.com/Whoawhen/FusionVisionMCP/blob/main/LICENSE)

An MCP server fusing [Florence-2](https://huggingface.co/microsoft/Florence-2-large),
[Moondream2](https://huggingface.co/vikhyatk/moondream2) and [SAM2](https://huggingface.co/facebook/sam2.1-hiera-small)
into one computer-vision toolset. Fork of
[jkawamoto/mcp-florence2](https://github.com/jkawamoto/mcp-florence2), which provides exactly three tools —
`ocr`, `caption`, `process` — all against Florence-2. This fork adds everything else: Florence-2's other task
heads exposed as their own tools (`detect_objects`, `point_objects`, `dense_region_caption`), Moondream2 for
open-ended visual question answering (`query_image`, since Florence-2 has none), two dispatch conveniences
(`analyze_image`, `batch_analyze_images`), and idle-timeout memory release. One tool, `spatial_relations`, isn't
just a new model wired in — no model here answers "does this actually touch that" on its own, so it's built from
Florence-2 boxes, SAM2 masks, and a from-scratch geometry module. See the tags on each tool below.

**Legend:** 🔼 upstream (unchanged from `mcp-florence2`) · ➕ added in this fork (wraps a model already in the
stack) · ✦ novel (new capability — see [spatial_relations](#spatial_relations-)).

You can process images or PDF files stored on a local or web server to extract text using OCR (Optical Character
Recognition), generate descriptive captions summarizing the content of the images, locate named objects and
return their bounding boxes or centre points, caption every salient region, and ask free-form questions about an
image.

Florence-2 handles captioning, OCR, detection and grounding. Moondream2 backs the `query_image` tool, because
Florence-2 has no open-ended visual question answering task. SAM2 backs `spatial_relations`, because bounding
boxes cannot answer questions about contact or containment.

Each model loads on first use and is released independently, so a request only pays for what it needs: OCR never
loads Moondream2 or SAM2. Weights are not bundled in this repository — each model downloads from the Hugging
Face Hub on first use and is cached locally by `transformers`, the same as any other Hugging Face model.

> **OCR vs. query_image**: Florence-2's OCR head is built for dense, printed, document-style text and can
> confidently misread stylized, cursive, or low-contrast text (watermarks, logos, signage) rather than failing
> visibly. For that kind of text, prefer `query_image` with a question like *"What does the text/watermark say,
> exactly?"* — see the routing note in each tool's description below.

## Installation

### [Claude](https://claude.com/download)
Download the latest MCP bundle `fusion-vision-mcp.mcpb` from
the [Releases](https://github.com/Whoawhen/FusionVisionMCP/releases) page,
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
        "git+https://github.com/Whoawhen/FusionVisionMCP",
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
    args: [ --from, git+https://github.com/Whoawhen/FusionVisionMCP, fusion-vision-mcp ]
    enabled: true
    type: stdio
```

For more details on configuring MCP servers in Goose, refer to the documentation:
[Using Extensions | goose](https://block.github.io/goose/docs/getting-started/using-extensions#mcp-servers).

### [LM Studio](https://lmstudio.ai/)

Add an MCP server entry pointing at this package, using the same `command`/`args` shown in the manual
configuration above.

## Tools

### ocr 🔼

Process an image file or URL using OCR to extract text.

#### Arguments:

- **src**: A file path or URL to the image file that needs to be processed.

### caption 🔼

Processes an image file and generates captions for the image.

#### Arguments:

- **src**: A file path or URL to the image file that needs to be processed.

### detect_objects ➕

Detect instances of a named object in an image, returning bounding boxes and labels.

#### Arguments:

- **src**: A file path or URL to the image file that needs to be processed.
- **object_name**: Name of the object to locate, e.g. `person`, `car`, `face`.

> **Box count ≠ object count** on an ambiguous class name. Tested live on `wing`: a griffin with
> one wing missing still returned 3 overlapping boxes (a whole-body box plus two sub-part boxes,
> all labelled `wing`). Tested on `sword blade` against an image with two fused blades: one box
> spanning both, not two. Prefer a more specific `object_name`, and treat results as candidates to
> inspect, not a reliable count.

### point_objects ➕

Locate instances of a named object in an image, returning the centre coordinates of each match.

#### Arguments:

- **src**: A file path or URL to the image file that needs to be processed.
- **object_name**: Name of the object to locate, e.g. `person`, `car`, `face`.

> Same caveat as `detect_objects`: point count is not a reliable proxy for object count on an
> ambiguous class name.

### dense_region_caption ➕

Generate a caption for every salient region of an image, with bounding boxes.

#### Arguments:

- **src**: A file path or URL to the image file that needs to be processed.

### query_image ➕

Ask a free-form question about an image (visual question answering). Backed by Moondream2.

#### Arguments:

- **src**: A file path or URL to the image file that needs to be processed.
- **question**: A free-form question to ask about the image.

### analyze_image ➕

Multi-purpose tool that dispatches to any of the operations above. Useful for agents that would rather choose an
operation by name than pick between tools.

#### Arguments:

- **src**: A file path or URL to the image file that needs to be processed.
- **operation**: One of `caption`, `ocr`, `detect`, `point`, `dense_caption`, `query`.
- **question**: Required when the operation is `query`.
- **object_name**: Required when the operation is `detect` or `point`.

### batch_analyze_images ➕

Runs `analyze_image`'s operation over several images. Each image reports its own success or failure, so one bad
file does not abort the batch.

#### Arguments:

- **srcs**: File paths or URLs of the images to process.
- **operation**: One of `caption`, `ocr`, `detect`, `point`, `dense_caption`, `query`.
- **question**: Required when the operation is `query`.
- **object_name**: Required when the operation is `detect` or `point`.

### spatial_relations ✦

Measures how named objects sit relative to one another: whether they touch, how far apart they are, how much of
one lies inside the other and how deeply, plus each object's elongation, straightness and end-to-end width
profile. Florence-2 locates the objects, SAM2 segments them, and the geometry is computed from the masks.

This answers questions a bounding box cannot. Two boxes overlap as soon as one object is merely *in front of*
another, so boxes cannot tell contact from occlusion; silhouettes can. It reports measurements rather than
verdicts — the caller decides what the numbers mean for the scene at hand.

#### Arguments:

- **src**: A file path or URL to the image file that needs to be processed.
- **objects**: Names of the objects to locate and compare, e.g. `["hand", "sword", "shield"]`.

#### Returns:

Per object — `area`, `elongation`, `straightness` (`max_deviation` from a straight line, `kink` from a smooth
curve) and `width_profile` (`end_a_width`, `mid_width`, `end_b_width`, `end_symmetry`).

Per pair — `state` (`separate` / `touching` / `overlapping`), `gap` in pixels, `a_inside_b` and `b_inside_a`
area fractions, and `embed_depth`, how far the overlap reaches from the other object's boundary.

Worked examples, measured on real images:

| Situation | Signal |
| --- | --- |
| A sword that should be held, but floats free of the hand | `state: separate`, `gap: 54px` |
| A hand gripping a shield's rim | `a_inside_b: 15%`, `embed_depth: 3.3px` |
| A hand pushed through a shield | `a_inside_b: 52%`, `embed_depth: 4.2px` |
| A hand fused into the middle of a shield face | `a_inside_b: 97%`, `embed_depth: 12.6px` |
| A blade with a point at *both* ends | `end_symmetry: 0.94`, versus 0.75–0.83 for blades with one tip and a hilt |

The containment figures separate cleanly and in order. `end_symmetry` separates too, but by a narrower margin —
0.94 against 0.83 — so it is better read as evidence alongside the width numbers themselves than as a threshold
to trust on its own.

Note that `spatial_relations` is the only tool that loads SAM2, and it loads it on first use — a server that is
only ever asked for captions or OCR never pays for it.

#### Limits

Masks are decoded on a fixed 256×256 grid before being upscaled to the image, so detail finer than roughly
`max(image side) / 256` pixels is not resolved. The measurements are also only as good as the detection they
start from: `detect_objects` returns nothing useful for vague classes, and can label the same region two
different ways in an ambiguous pose, which the geometry then faithfully measures.

`straightness` reliably separates a straight rod from a curved one, but it does not distinguish a naturally
curved object from an unnaturally bent one — on two branch-like staffs it scored 0.057 and 0.065, too close to
threshold on. Treat it as a shape description, not a defect detector.

### process 🔼

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
- **--sam2-model**: The SAM2 model backing `spatial_relations`. Defaults to `sam2.1-hiera-small`; measured on
  CPU, `tiny` is ~0.06s faster per call for a slightly worse mask, and `base-plus` roughly doubles inference
  time for a marginal gain.
- **--idle-timeout**: Minutes of inactivity after which both models are unloaded and their memory released; they
  reload automatically on the next request. `0`, the default, keeps them loaded for the lifetime of the server.
- **--device**: Torch device all three models load onto, e.g. `cpu`, `cuda`, `cuda:1`, `mps`. Auto-detected (MPS,
  then CUDA, then CPU) when unset. Set this to pin the server to a specific accelerator, force CPU on a shared
  GPU box, or target a non-default GPU index — including a GPU-equipped cloud VM, since this is a plain local
  process with no separate cloud deployment path of its own.

The models are large, so a server left running holds several gigabytes of memory. Setting `--idle-timeout 10`
keeps repeat calls fast during a burst of work while handing the memory back once the work stops.


## License

This application is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
