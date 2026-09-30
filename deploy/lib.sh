# shellcheck shell=bash
# Shared helpers for the deploy scripts. Source it; do not run it.
# All scripts run from the install directory (default /opt/wenquest).

set -euo pipefail

WQ_DIR="${WQ_DIR:-/opt/wenquest}"
cd "$WQ_DIR"

# Read one value from .env without sourcing it (values may contain spaces or Chinese text).
envval() {
    local line
    line=$(grep -E "^$1=" .env 2>/dev/null | tail -n 1 || true)
    printf '%s' "${line#*=}"
}

# Set or replace one value in .env.
envset() {
    if grep -qE "^$1=" .env; then
        sed -i "s|^$1=.*|$1=$2|" .env
    else
        printf '%s=%s\n' "$1" "$2" >> .env
    fi
}

# All three images are built from one commit and share a tag; derive the others from the engine image.
#   ghcr.io/owner/repo/engine:abc123 -> ghcr.io/owner/repo/gateway:abc123
set_images() {
    envset ENGINE_IMAGE "$1"
    envset GATEWAY_IMAGE "${1/\/engine:/\/gateway:}"
    envset WEB_IMAGE "${1/\/engine:/\/web:}"
    envset ANIMATOR_IMAGE "${1/\/engine:/\/animator:}"
    envset LABCHECK_IMAGE "${1/\/engine:/\/labcheck:}"
}

dc() {
    docker compose -f docker-compose.yml -f docker-compose.prod.yml "$@"
}

log() {
    printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

[ -f .env ] || { echo "Missing $WQ_DIR/.env - copy .env.example and fill it in first." >&2; exit 1; }
