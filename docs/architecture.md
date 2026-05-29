# Architecture

## Overview

The device displays a C2PA manifest summary for the audio clip currently selected in Ableton Live's Detail View. It does so by:

1. Observing the `live_set view detail_clip` property via the Live Object Model (LOM).
2. Resolving the selected clip's `file_path`.
3. POSTing the path to the local FastAPI server (`mtl-c2pa-http`, shipped in this repo as `src/mtl_c2pa_server/`) on `127.0.0.1:8765`.
4. Rendering the JSON response in a `textedit` UI element.

The local server (`mtl_c2pa_server`, shipped in this same repo) wraps the official `c2pa-python` Rust binding. One clone, one `poetry install`, no separate dependency on the sibling MCP server.

## Component diagram

```mermaid
flowchart TB
    subgraph Ableton["Ableton Live"]
        device["MTL_C2PA_Ableton_PoC.amxd"]
        livepi["LiveAPI observer<br/>(detail_clip)"]
        js["c2pa_reader.js"]
        node["c2pa_node.js<br/>(Node for Max)"]
        ui["UI textedit<br/>summary display"]
        device --> livepi --> js --> node --> ui
    end

    subgraph LocalServer["mtl-c2pa-http (127.0.0.1:8765)"]
        fastapi["FastAPI app"]
        summary["/summary"]
        verify["/verify"]
        scan["/scan"]
        info["/info"]
        fastapi --> summary
        fastapi --> verify
        fastapi --> scan
        fastapi --> info
    end

    subgraph PythonPkg["mtl_c2pa_server (in this repo)"]
        c2pamod["c2pa.py (parser)"]
        reader["c2pa-python Reader<br/>(Rust binding)"]
        c2pamod --> reader
    end

    node -->|POST /summary| fastapi
    fastapi -->|import| c2pamod

    launchd["launchd plist<br/>auto-start on login"]
    launchd -.->|spawn| fastapi
```

## Selection-to-display sequence

```mermaid
sequenceDiagram
    actor User
    participant Live as Ableton Live
    participant Device as M4L Device
    participant Reader as c2pa_reader.js
    participant Node as c2pa_node.js
    participant HTTP as mtl-c2pa-http :8765
    participant Lib as c2pa-python

    User->>Live: click audio clip
    Live->>Device: detail_clip changed
    Device->>Reader: observer fires
    Reader->>Live: get detail_clip.file_path
    Live-->>Reader: /path/to/lyria.mp3
    Reader->>Node: outlet "fetch" path
    Node->>HTTP: POST /summary {path}
    HTTP->>Lib: Reader(mime, stream).json()
    Lib-->>HTTP: manifest store
    HTTP-->>Node: summary JSON
    Node->>Device: outlet "result" json
    Device-->>User: display summary
```

The manual "Refresh" `textbutton` short-circuits the observer and triggers the same `POST /summary` call — same pipeline, different trigger source.

## Why a local HTTP server (and not alternatives)

| Option | Why not |
|--------|---------|
| CLI shell-out per request | Python startup cost (~300 ms) is noticeable on every clip selection. |
| Embed `c2pa-python` in Max JS | Max's `js` object can't host the Rust binding; would need a JS rewrite or a native external. |
| Cloud Run | Adds network dependency to inspect a local file the user already has on disk. Right for *generation*, wrong for *reading*. |

A persistent local FastAPI server keeps `c2pa-python` warm, runs on loopback only (no external attack surface), and is shipped in this same repo as the device.
