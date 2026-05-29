# mtl-c2pa-ableton

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/musictechlab/mtl-c2pa-ableton/actions/workflows/ci.yml/badge.svg)](https://github.com/musictechlab/mtl-c2pa-ableton/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)
[![Built by MusicTech Lab](https://musictechlab.io/oss/build-by-musictechlab.io.svg)](https://musictechlab.io)

Max for Live device that displays the [C2PA](https://c2pa.org/) manifest summary for the currently selected audio clip in Ableton Live. Click a clip — see who made it, what tool generated it, whether it's AI, what watermarks were applied, and who signed the claim.

> **⚠️ Experimental** — Read-side only. Doesn't sign or modify anything. The C2PA spec and tooling are still evolving.

## Why

Google Lyria ships every generated MP3 with a signed C2PA manifest. Producers mixing AI stems with hand-recorded audio have no way to *see* that information inside Ableton today. This device puts it one click away.

## Architecture

```
[Ableton clip selection] -> [Max for Live JS, LiveAPI observer]
                                |
                                v
                  [Node for Max HTTP client]
                                |
                                v
           [localhost:8765 FastAPI server (in this repo)]
                                |
                                v
                  [c2pa-python (Adobe Rust binding)]
```

The repo is self-contained: M4L device + Python HTTP server. One clone, one install. Full diagrams in [`docs/architecture.md`](docs/architecture.md).

## Install

### 1. Clone and install dependencies

```bash
git clone https://github.com/musictechlab/mtl-c2pa-ableton.git
cd mtl-c2pa-ableton
poetry install
```

### 2. Auto-start the server on login (macOS)

```bash
bash install/install.sh
```

Verify:

```bash
launchctl list | grep io.musictechlab.c2pa-http
curl http://127.0.0.1:8765/health
```

### 3. Drop the device on a track

Drag `device/MTL_C2PA_Ableton_PoC.amxd` onto any audio track in Ableton. The device displays the C2PA summary for whichever clip is currently selected.

## Usage

| Clip type | What you see |
|-----------|--------------|
| Lyria-signed MP3 | Generator, `is_ai_generated: true`, actions (created/edited), SynthID watermark, signature issuer (`Google LLC`), validation state |
| Unsigned audio | `{"error": "No C2PA manifest found"}` |
| MIDI clip | `{"info": "MIDI clip — no C2PA manifest applicable"}` |
| Nothing selected | `{"info": "no clip selected"}` |

Press the **Refresh** button to re-fetch manually (e.g. after moving the underlying file).

## Uninstall

```bash
bash install/uninstall.sh
```

## Manual server start (without launchd)

If you skipped the launchd install or are on Windows / Linux:

```bash
poetry run mtl-c2pa-http
```

## Building the device from source

The `.amxd` is a binary Max file. To reproduce or modify, see [`device/PATCHER.md`](device/PATCHER.md) for the object layout and wiring, then build in Max.

## Tech stack

- Ableton Live 11+ with Max for Live (Live Suite, or Standard + M4L add-on)
- Max 8+
- JavaScript (`js` object) + Node for Max (`node.script`)
- Python 3.10+ with Poetry (FastAPI + `c2pa-python`)

## Roadmap

- [ ] Generation-side: sign the Ableton project at bounce time and emit a manifest describing the session ingredients (sample sources, MIDI inputs, plugin chain). Part of the [C2PA community DAW PoC](https://c2pa.org/community/) conversation.
- [ ] Windows / Linux equivalents of the launchd plist.
- [ ] Configurable port / host via a device parameter.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

The HTTP server binds `127.0.0.1` only — no external network exposure. To report a vulnerability, see [SECURITY.md](SECURITY.md).

## License

MIT — see [LICENSE](LICENSE).

## Related

- [mtl-c2pa-mcp](https://github.com/musictechlab/mtl-c2pa-mcp) — sibling MCP server that exposes the same C2PA reader to Claude Code
- [Article: C2PA in Music — A Claude MCP for Reading Content Provenance](https://musictechlab.io/blog/music-data/c2pa-in-music-mcp) (2026-05-28)
- [Article: Connecting Your Max for Live Device to a Cloud API](https://musictechlab.io/blog/software-development/connecting-your-max-for-live-device-to-a-cloud-api) — the reference architecture this device borrows from

---

<div align="center">
  MusicTech Lab - Rockstars Developers dedicated to the Music Industry<br>
  <a href="https://musictechlab.io">Website</a>
  <span> | </span>
  <a href="https://linkedin.com/company/musictechlab">LinkedIn</a>
  <span> | </span>
  <a href="https://musictechlab.io/contact">Let's talk</a><br>
  Crafted by <a href="https://musictechlab.io">musictechlab.io</a>
</div>
