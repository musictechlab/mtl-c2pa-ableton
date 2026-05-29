#!/usr/bin/env bash
# Install the launchd plist that auto-starts the local C2PA HTTP server on macOS login.
#
# Run from the repo root after `poetry install`:
#   bash install/install.sh

set -euo pipefail

POETRY_BIN="$(command -v poetry || echo /opt/homebrew/bin/poetry)"
LAUNCH_AGENTS_DIR="${HOME}/Library/LaunchAgents"
LOG_DIR="${HOME}/Library/Logs/musictechlab"
LABEL="io.musictechlab.c2pa-http"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PLIST_SRC="${SCRIPT_DIR}/${LABEL}.plist"
PLIST_DEST="${LAUNCH_AGENTS_DIR}/${LABEL}.plist"

if [[ ! -x "${POETRY_BIN}" ]]; then
    echo "ERROR: poetry not found on PATH and not at /opt/homebrew/bin/poetry" >&2
    echo "       Install Poetry: https://python-poetry.org/docs/#installation" >&2
    exit 1
fi

if [[ ! -d "${REPO_DIR}/.venv" ]] && [[ ! -f "${REPO_DIR}/poetry.lock" ]]; then
    echo "ERROR: no poetry env detected in ${REPO_DIR}." >&2
    echo "       Run 'poetry install' from the repo root first." >&2
    exit 1
fi

mkdir -p "${LAUNCH_AGENTS_DIR}" "${LOG_DIR}"

echo "Installing ${LABEL} with:"
echo "  REPO_DIR    = ${REPO_DIR}"
echo "  POETRY_BIN  = ${POETRY_BIN}"
echo "  LOG_DIR     = ${LOG_DIR}"
echo "  PLIST_DEST  = ${PLIST_DEST}"

sed \
    -e "s|__REPO_DIR__|${REPO_DIR}|g" \
    -e "s|__POETRY_BIN__|${POETRY_BIN}|g" \
    -e "s|__LOG_DIR__|${LOG_DIR}|g" \
    "${PLIST_SRC}" > "${PLIST_DEST}"

launchctl unload "${PLIST_DEST}" 2>/dev/null || true
launchctl load -w "${PLIST_DEST}"

echo
echo "Installed. Verify with:"
echo "  launchctl list | grep ${LABEL}"
echo "  curl http://127.0.0.1:8765/health"
echo
echo "Logs: ${LOG_DIR}/c2pa-http.{out,err}.log"
