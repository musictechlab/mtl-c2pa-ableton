#!/usr/bin/env bash
# Remove the launchd plist for mtl-c2pa-http.

set -euo pipefail

LABEL="io.musictechlab.c2pa-http"
PLIST="${HOME}/Library/LaunchAgents/${LABEL}.plist"

if [[ -f "${PLIST}" ]]; then
    launchctl unload "${PLIST}" 2>/dev/null || true
    rm "${PLIST}"
    echo "Removed: ${PLIST}"
else
    echo "Not installed: ${PLIST} does not exist"
fi
