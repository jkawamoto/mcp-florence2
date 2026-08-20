# mcp-florence2

Fork of [jkawamoto/mcp-florence2](https://github.com/jkawamoto/mcp-florence2), adding Moondream2 VQA, object grounding (`detect_objects`, `point_objects`, `dense_region_caption`), batch analysis, and an `--idle-timeout` that releases model memory after a period of inactivity. See [README.md](README.md) for the tool and option reference.

## This is an editable install — checking out a branch changes the running server

`mcp-florence2` is installed as an editable `uv` tool pointing at this checkout (`uv tool install --editable . --force ...`). The MCP server both Cline and Claude Code run **is whatever branch is checked out here**, live, with no reinstall needed to pick up source changes.

This bit us once already: checking out `main` to catch up with upstream silently removed `--idle-timeout` and the Moondream tools from the running server, and it came back as `✘ Failed to connect` in both clients because `main` doesn't accept `--idle-timeout`. Always confirm you're on `feature/moondream-vqa-and-idle-release` (or a later feature branch) before assuming the server has this fork's tools, and re-run `uv tool install --editable . --force ...` after any change to `pyproject.toml` — source edits are live immediately, but dependency changes are not until reinstalled.

## `pyvips` is required transitively, not by this package directly

`moondream2`'s `trust_remote_code` module imports `pyvips`, which needs native libvips libraries that plain `pip install pyvips` does not provide. Without them the server fails at startup with `ModuleNotFoundError: No module named '_libvips'`, or `OSError: cannot load library 'libvips-42.dll'` if libvips isn't on `PATH`.

The fix already applied here: `pyproject.toml` declares `pyvips[binary]`, which ships the libvips shared libraries inside the wheel. No system libvips install and no `PATH` entry are needed. If you ever see either error, check that the dependency still reads `pyvips[binary]` rather than plain `pyvips` — this is exactly the failure that broke the upstream project's own test suite for anyone without a system-wide libvips.

## Commands

```powershell
# Reinstall after a dependency change (not needed for source-only edits)
uv tool install --editable . --force --extra-index-url https://download.pytorch.org/whl/cpu --index-strategy unsafe-best-match

# Lint / format / type-check
uvx ruff@0.16.1 check src tests
uvx ruff@0.16.1 format src tests
uv run --with mypy --with types-requests mypy src

# Tests (integration tests spawn the real server and download Florence-2-base on first run)
uv run --with pytest --with anyio pytest tests -q
```

`uv run` and `uv tool install` can fail here in ways specific to the environment, not the code — see the OneDrive note below if this checkout is ever moved back under a synced folder.

## Remotes

`origin` is this fork (`warrens951/mcp-florence2`, public); `upstream` is `jkawamoto/mcp-florence2`. Feature work happens on branches off `main`, which tracks `upstream/main` — keep `main` itself a clean mirror of upstream so a PR can be opened from a branch without carrying unrelated history.

## Two OCR paths — pick by text type, don't default to `ocr`

`ocr` (Florence2's `<OCR>` head) and `query_image` (Moondream2 VQA, asked to transcribe) both read text, but they fail differently, so route by what the text looks like rather than always reaching for `ocr`:

- **`ocr` (Florence2)** for dense, printed, document-style text — receipts, scanned pages, paragraphs. It's built for verbatim character-level transcription over a lot of text.
- **`query_image` (Moondream2)**, e.g. `question="What does the text/watermark say, exactly?"`, for stylized/logo/cursive/low-contrast text — photo watermarks, signage, logotypes. Florence2's OCR head misreads these; it read a real watermark reading "Ride the Sky / Equine Photography / ridetheskyequine.com" as "SQUINT PHOTOGRAPHY / squentphotography.com" (2026-08-20 test on `testpette.jpg`). Moondream2 read the same image correctly.

Don't hard-route `ocr` to always call Moondream instead — Moondream is a VQA model, not a transcription specialist, and is more prone to paraphrasing rather than verbatim-transcribing long or dense text blocks. Keep both tools and choose per call.

## A note on where this lives

This checkout used to live under OneDrive. `uv tool install` failed there with a hardlink error, and `uv run`/`uv sync` separately failed removing a `.dist-info/licenses` directory that OneDrive had turned into a cloud placeholder — neither error message mentions OneDrive. Moving the checkout to `C:\AI\MCP\mcp-florence2` (a plain local path) resolved both. Keep it out of any synced folder.
