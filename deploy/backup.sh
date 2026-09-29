#!/usr/bin/env bash
# Back up the database and uploaded files; optionally copy them to S3-compatible storage.
# Runs daily from cron (installed by bootstrap.sh) and before every update.
# Output: backups/<timestamp>/db.dump and moodledata.tgz
. "$(dirname "$0")/lib.sh"

DB_NAME=$(envval DB_NAME); DB_NAME=${DB_NAME:-moodle}
DB_USER=$(envval DB_USER); DB_USER=${DB_USER:-moodle}
KEEP_DAYS=$(envval BACKUP_KEEP_DAYS); KEEP_DAYS=${KEEP_DAYS:-7}

TS=$(date +%Y%m%d-%H%M%S)
OUT="backups/$TS"
mkdir -p "$OUT"

log "Dumping database..."
dc exec -T db pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc > "$OUT/db.dump"

log "Archiving uploaded files (moodledata)..."
dc exec -T moodle tar czf - -C /var/www/moodledata \
    --exclude=./cache --exclude=./localcache --exclude=./sessions --exclude=./temp --exclude=./trashdir . \
    > "$OUT/moodledata.tgz"

log "Archiving sign-up records (teacher applications, course catalogue)..."
dc exec -T gateway tar czf - -C /data accounts settings.json 2>/dev/null > "$OUT/gateway.tgz" || true

# Record which engine image produced this backup, for restores and rollbacks.
envval ENGINE_IMAGE > "$OUT/engine-image.txt"
( cd "$OUT" && sha256sum db.dump moodledata.tgz gateway.tgz > SHA256SUMS )
log "Local backup: $OUT ($(du -sh "$OUT" | cut -f1))"

ENDPOINT=$(envval BACKUP_S3_ENDPOINT)
BUCKET=$(envval BACKUP_S3_BUCKET)
if [ -n "$ENDPOINT" ] && [ -n "$BUCKET" ]; then
    log "Uploading to s3://$BUCKET/wenquest/$TS ..."
    docker run --rm \
        -v "$WQ_DIR/$OUT:/data:ro" \
        -e RCLONE_CONFIG_OFFSITE_TYPE=s3 \
        -e RCLONE_CONFIG_OFFSITE_PROVIDER=Other \
        -e RCLONE_CONFIG_OFFSITE_ENDPOINT="$ENDPOINT" \
        -e RCLONE_CONFIG_OFFSITE_ACCESS_KEY_ID="$(envval BACKUP_S3_ACCESS_KEY)" \
        -e RCLONE_CONFIG_OFFSITE_SECRET_ACCESS_KEY="$(envval BACKUP_S3_SECRET_KEY)" \
        -e RCLONE_CONFIG_OFFSITE_ACL=private \
        rclone/rclone:1 copy /data "offsite:$BUCKET/wenquest/$TS" --quiet
    log "Off-site copy done."
else
    log "BACKUP_S3_* not set; keeping the backup on this server only."
fi

# Local retention.
find backups -mindepth 1 -maxdepth 1 -type d -mtime +"$KEEP_DAYS" -exec rm -rf {} +
log "Backup finished."
