# Changelog

All notable changes to this project are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Initial release of `mtl-c2pa-ableton`.
- Max for Live device (`MTL_C2PA_Ableton_PoC.amxd` — to be built in Max).
- `device/scripts/c2pa_reader.js` — LiveAPI observer on `live_set view detail_clip`; manual Refresh fallback.
- `device/scripts/c2pa_node.js` — Node for Max HTTP client targeting `127.0.0.1:8765`.
- `device/PATCHER.md` — patcher object layout and wiring guide.
- `mtl_c2pa_server` Python package — self-contained FastAPI server on `127.0.0.1:8765` wrapping `c2pa-python`.
- `install/install.sh` + `install/uninstall.sh` — macOS launchd autostart under label `io.musictechlab.c2pa-http`.
- Mermaid architecture + selection-sequence diagrams (`docs/architecture.md`).
- 30 pytest tests, ruff lint + format clean.
