#!/usr/bin/env bash
# Switch the platform to new images (engine, gateway, web from one build) and restart the stack.
# Usage: deploy/update.sh [image]     (no image: restart with the current one, e.g. after editing .env)
# Called by the GitHub Actions deploy job; can also be run by hand on the server.
. "$(dirname "$0")/lib.sh"

NEW_IMAGE="${1:-}"
CURRENT=$(envval ENGINE_IMAGE)

if [ -n "$NEW_IMAGE" ] && [ "$NEW_IMAGE" != "$CURRENT" ]; then
    # A new image may upgrade the database; take a backup first if the site is already running.
    if [ -n "$(dc ps -q moodle 2>/dev/null)" ]; then
        log "Backing up before the update..."
        "$(dirname "$0")/backup.sh"
    fi
    log "Engine image: ${CURRENT:-none} -> $NEW_IMAGE"
    [ -n "$CURRENT" ] && echo "$CURRENT" >> .deploy-history
    set_images "$NEW_IMAGE"
fi

log "Pulling images..."
dc pull --quiet --ignore-buildable
dc pull --quiet moodle gateway web

log "Starting services..."
dc up -d --no-build --remove-orphans

# Wait for Moodle to finish installing or upgrading. First install can take several minutes.
log "Waiting for the learning platform to become healthy..."
for _ in $(seq 1 90); do
    status=$(docker inspect -f '{{.State.Health.Status}}' "$(dc ps -q moodle)" 2>/dev/null || echo unknown)
    if [ "$status" = "healthy" ]; then
        log "Learning platform is healthy."
        docker image prune -f >/dev/null
        exit 0
    fi
    sleep 10
done

log "Learning platform did not become healthy within 15 minutes. Recent logs:"
dc logs --tail 80 moodle
log "To roll back: deploy/rollback.sh"
exit 1
