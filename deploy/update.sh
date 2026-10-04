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
dc pull --quiet moodle gateway web animator labcheck voice

# The web server also serves the digital factory (factory./erp.), reached over this network; create it
# if the factory has not been installed yet, so the web server can start either way.
docker network inspect factory-edge >/dev/null 2>&1 || docker network create factory-edge >/dev/null 2>&1 || true

# Digital factory course API (factory round 4, C2): copy its read-only key so the gateway can call
# https://factory.<domain>/api/course/*. The factory generates the key on its own deploys.
FACTORY_ENV="${FACTORY_DIR:-$WQ_DIR/factory}/.env"
if [ -r "$FACTORY_ENV" ]; then
    fk=$(grep -E '^WQ_FACTORY_READ_KEY=' "$FACTORY_ENV" | tail -n 1 | cut -d= -f2- || true)
    if [ -n "$fk" ] && [ "$fk" != "$(envval WQ_FACTORY_READ_KEY)" ]; then
        envset WQ_FACTORY_READ_KEY "$fk"
        log "Digital factory read key updated."
    fi
    [ -n "$(envval WQ_FACTORY_URL)" ] || envset WQ_FACTORY_URL "https://factory.$(envval SITE_DOMAIN)"
    # 工程任务单（第 11 轮 2.7（5））：任务单钥匙和班级工厂清单（编号:名称,…），课程里下达任务单时选班级工厂
    tk=$(grep -E '^WQ_FACTORY_TASK_KEY=' "$FACTORY_ENV" | tail -n 1 | cut -d= -f2- || true)
    if [ -n "$tk" ] && [ "$tk" != "$(envval WQ_FACTORY_TASK_KEY)" ]; then
        envset WQ_FACTORY_TASK_KEY "$tk"
        log "Digital factory task key updated."
    fi
    CLASSES_FILE="$(dirname "$FACTORY_ENV")/classes.names"
    if [ -r "$CLASSES_FILE" ]; then
        cn=$(tr -d '\n' < "$CLASSES_FILE")
        [ "$cn" = "$(envval WQ_FACTORY_CLASSES)" ] || envset WQ_FACTORY_CLASSES "$cn"
    fi
fi

log "Starting services..."
dc up -d --no-build --remove-orphans

# Caddy keeps running with its old settings when only the Caddyfile changed: check the new file and
# load it; a broken file is reported and the running settings are kept, so the site stays up.
if [ -n "$(dc ps -q caddy 2>/dev/null)" ]; then
    if dc exec -T caddy caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile >/dev/null 2>&1; then
        dc exec -T caddy caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile >/dev/null 2>&1 \
            && log "Web server settings reloaded." || log "WARNING: web server settings could not be reloaded."
    else
        log "WARNING: deploy/Caddyfile has an error; the web server keeps its previous settings:"
        dc exec -T caddy caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile 2>&1 | tail -5
    fi
fi

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
