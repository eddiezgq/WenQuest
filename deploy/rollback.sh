#!/usr/bin/env bash
# Go back to the engine image that was running before the last update.
# Note: if the last update upgraded the Moodle database, restore the backup taken before it as well
# (deploy/restore.sh); an older Moodle version refuses to run on a newer database.
. "$(dirname "$0")/lib.sh"

[ -s .deploy-history ] || { echo "No previous image recorded in .deploy-history." >&2; exit 1; }
PREV=$(tail -n 1 .deploy-history)
sed -i '$ d' .deploy-history
log "Rolling back to $PREV"
envset ENGINE_IMAGE "$PREV"
dc up -d --no-build
log "Done. Check: deploy/status.sh"
