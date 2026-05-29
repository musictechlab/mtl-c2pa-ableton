# Building the Max patcher

The `.amxd` device is built in Max. This file documents the patcher layout so it can be reproduced (or reviewed) without opening the binary.

## Objects

| Object | Purpose |
|--------|---------|
| `js c2pa_reader.js` | LiveAPI observer + manual-refresh entry point. Outputs `fetch <path>` (audio clip selected) or `result <json>` (no clip / MIDI / no path / error). |
| `node.script c2pa_node.js` | Node for Max HTTP client. Receives `fetch <path>`, POSTs to `http://127.0.0.1:8765/summary`, sends body back via `result <json>`. |
| `route fetch result` | Splits outputs of the JS into two streams. |
| `textbutton` | Manual "Refresh" button — sends `1` into `js c2pa_reader.js` to trigger `msg_int(1) -> bang()`. |
| `textedit @autoscroll 1` | Display surface for the JSON response. Receives `set <json>` messages. |
| `prepend set` | Prefixes the JSON with `set` so the textedit replaces its content rather than appending. |

## Wiring

```
[textbutton "Refresh"]          (LiveAPI observer fires automatically on selected clip change)
        |
        v
[js c2pa_reader.js] -- output 0 --> [route fetch result]
                                      |        |
                                      v        v
                                [fetch path]  [result json]
                                      |        |
                                      v        |
                            [node.script c2pa_node.js]
                                      |        |
                                      v        v
                                [result json]  |
                                      |        |
                                      +-> [prepend set] -> [textedit]
```

## UI styling (madebyikigai brand)

- Background: `#0E0F11` (`bgcolor 14 15 17 255` in Max color)
- Accent: `#84cc16` (`textcolor 132 204 22 255`)
- Font: Inter (or system mono if Inter unavailable). Size 11 for body, 13 for title.

## Build & export

1. Open Max (8 or later).
2. In Ableton Live, create a new Max Audio Effect device. Save as `device/MTL_C2PA_Ableton_PoC.amxd` in this repo.
3. Add the objects above and wire as described.
4. **Freeze the device** (Device → Freeze Device) so the JS files are bundled.
5. Save. Commit the `.amxd`.

## Smoke test inside Ableton

1. Start the server: `cd ../mcp-c2pa && poetry run mtl-c2pa-http` (or install the launchd plist — see `install/`).
2. Drop a Lyria-signed MP3 onto an audio track in Ableton.
3. Drop `MTL_C2PA_Ableton_PoC.amxd` onto the same track.
4. Click the clip. The textedit should display the C2PA summary JSON within ~100 ms.
5. Click a MIDI clip — should display `{"info":"MIDI clip — no C2PA manifest applicable"}`.
6. Click an unsigned audio clip — should display the error payload with `"No C2PA manifest found"`.
