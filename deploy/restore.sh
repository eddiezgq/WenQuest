#!/usr/bin/env bash
# Restore the database and uploaded files from a backup directory made by backup.sh.
# Usage: deploy/restore.sh backups/20261001-033000
# To restore an off-site copy, download that folder into backups/ first (see the runbook).
. "$(dirname "$0")/lib.sh"

SRC="${1:?Usage: deploy/restore.sh backups/<timestamp>}"
[ -f "$SRC/db.dump" ] && [ -f "$SRC/moodledata.tgz" ] || { echo "No db.dump / moodledata.tgz in $SRC" >&2; exit 1; }
( cd "$SRC" && sha256sum -c --quiet SHA256SUMS ) || { echo "Checksum mismatch in $SRC" >&2; exit 1; }

DB_NAME=$(envval DB_NAME); DB_NAME=${DB_NAME:-moodle}
DB_USER=$(envval DB_USER); DB_USER=${DB_USER:-moodle}

echo "This replaces ALL current courses, users and files with the backup in $SRC."
if [ -f "$SRC/engine-image.txt" ] && [ "$(cat "$SRC/engine-image.txt")" != "$(envval ENGINE_IMAGE)" ]; then
    echo "Note: the backup was made with $(cat "$SRC/engine-image.txt");"
    echo "      the server now runs $(envval ENGINE_IMAGE). Use deploy/rollback.sh first if the backup is older."
fi
read -r -p "Type RESTORE to continue: " answer
[ "$answer" = "RESTORE" ] || { echo "Cancelled."; exit 1; }

log "Stopping the learning platform..."
dc stop moodle cron

log "Restoring database..."
dc exec -T db pg_restore -U "$DB_USER" -d "$DB_NAME" --clean --if-exists --no-owner < "$SRC/db.dump"

log "Restoring uploaded files..."
dc run --rm --no-deps -T --entrypoint sh moodle -c \
    'find /var/www/moodledata -mindepth 1 -maxdepth 1 -exec rm -rf {} + && tar xzf - -C /var/www/moodledata && chown -R www-data:www-data /var/www/moodledata' \
    < "$SRC/moodledata.tgz"

if [ -s "$SRC/gateway.tgz" ]; then
    log "Restoring sign-up records (teacher applications, course catalogue)..."
    dc exec -T gateway sh -c 'rm -rf /data/accounts && tar xzf - -C /data' < "$SRC/gateway.tgz" || true
    dc restart gateway
fi

log "Starting the learning platform..."
dc up -d --no-build
dc exec -T moodle su -s /bin/sh www-data -c 'php admin/cli/purge_caches.php' || true
log "Restore finished."
