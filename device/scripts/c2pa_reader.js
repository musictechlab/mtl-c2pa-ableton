autowatch = 1;
outlets = 1;

var clipObserver = null;

function init() {
    try {
        clipObserver = new LiveAPI(onSelectedClipChanged, "live_set view");
        clipObserver.property = "detail_clip";
        post("c2pa_reader: observing live_set view detail_clip\n");
        bang();
    } catch (e) {
        post("c2pa_reader init ERROR: " + e.toString() + "\n");
    }
}

function onSelectedClipChanged() {
    bang();
}

function bang() {
    try {
        var clip = new LiveAPI("live_set view detail_clip");
        if (!clip || clip.id === 0 || clip.id === "0" || clip.id === "id 0") {
            outlet(0, "result", JSON.stringify({ info: "no clip selected" }));
            return;
        }

        var isAudio = clip.get("is_audio_clip");
        isAudio = Array.isArray(isAudio) ? isAudio[0] : isAudio;
        if (Number(isAudio) !== 1) {
            outlet(0, "result", JSON.stringify({ info: "MIDI clip — no C2PA manifest applicable" }));
            return;
        }

        var filePath = clip.get("file_path");
        filePath = Array.isArray(filePath) ? filePath[0] : filePath;
        if (!filePath || filePath === "") {
            outlet(0, "result", JSON.stringify({ info: "audio clip has no file path (recorded in session?)" }));
            return;
        }

        post("c2pa_reader: fetching for " + filePath + "\n");
        outlet(0, "fetch", filePath);
    } catch (e) {
        post("c2pa_reader bang ERROR: " + e.toString() + "\n");
        outlet(0, "result", JSON.stringify({ error: e.toString(), error_type: "JSError" }));
    }
}

function msg_int(v) {
    if (v === 1) bang();
}

init();
