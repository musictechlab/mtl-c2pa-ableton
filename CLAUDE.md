# mtl-c2pa-ableton

Max for Live device + local HTTP server, all in one repo. Displays C2PA manifest info for the currently selected audio clip in Ableton Live.

## Tech stack

- **Host**: Ableton Live 11+ with Max for Live
- **Device shell**: Max 8+ (`.amxd`, frozen)
- **Scripting**: JavaScript (`js` object) + Node for Max (`node.script`)
- **HTTP server**: Python 3.10+ with Poetry. FastAPI + `c2pa-python`. Module: `mtl_c2pa_server`. Binds `127.0.0.1:8765`.
- **Autostart**: launchd plist (macOS), in `install/`

## Repo layout

```
pyproject.toml                  <- Poetry project for the HTTP server
src/mtl_c2pa_server/
  __init__.py
  __main__.py                   <- `python -m mtl_c2pa_server`
  c2pa.py                       <- C2PA parser around c2pa-python
  http.py                       <- FastAPI app, entry point `mtl-c2pa-http`
tests/
  test_c2pa.py
  test_http.py
device/
  MTL_C2PA_Ableton_PoC.amxd     <- built in Max, exported, version-controlled
  scripts/
    c2pa_reader.js              <- runs in `js` object; LiveAPI observer
    c2pa_node.js                <- runs in `node.script`; HTTP client
    package.json                <- Node for Max manifest
  PATCHER.md                    <- patcher object layout & wiring
install/
  io.musictechlab.c2pa-http.plist  <- launchd template (sed-substituted by install.sh)
  install.sh / uninstall.sh
fixtures/                       <- C2PA-signed test assets
docs/
  architecture.md               <- Mermaid diagrams + design rationale
  article-draft.md              <- blog post outline (musictechlab.io)
  img/                          <- rendered SVGs
```

## How the pieces talk

1. `c2pa_reader.js` observes `live_set view detail_clip`. On change, reads `file_path` and outputs `fetch <path>`.
2. `route fetch result` in the patcher splits the JS output.
3. `c2pa_node.js` (Node for Max) receives `fetch <path>`, POSTs to `http://127.0.0.1:8765/summary`, outputs `result <json>`.
4. The textedit displays the JSON.

## Commands

| Action | Command |
|--------|---------|
| Install dependencies | `poetry install` |
| Run server manually | `poetry run mtl-c2pa-http` |
| Run tests | `poetry run pytest` |
| Lint | `poetry run ruff check .` |
| Format | `poetry run ruff format .` |
| Install launchd autostart | `bash install/install.sh` |
| Uninstall | `bash install/uninstall.sh` |
| Verify service running | `curl http://127.0.0.1:8765/health` |
| Tail logs | `tail -f ~/Library/Logs/musictechlab/c2pa-http.{out,err}.log` |

## Important constraints

- The HTTP server binds `127.0.0.1` only — no external exposure.
- The device requires Ableton Live Suite (Max for Live included) or Standard + Max for Live add-on.
- macOS-only for the launchd plist; Windows / Linux users start the HTTP server manually with `poetry run mtl-c2pa-http`.

## Related repos

- [mtl-c2pa-mcp](https://github.com/musictechlab/mtl-c2pa-mcp) — sibling MCP server that exposes the same C2PA reader to Claude Code.
- [musictechlab/mtl-madebyikigai-ableton-api](https://github.com/musictechlab/mtl-madebyikigai-ableton-api) — reference architecture for M4L → HTTP patterns.
