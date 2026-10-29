#!/usr/bin/env bash
# Back up the database and uploaded files; optionally copy them to S3-compatible storage.
#   deploy/backup.sh                 daily backup (cron, 03:30) -> backups/<timestamp>-daily/
#   deploy/backup.sh --pre-update    before a deploy (update.sh) -> backups/<timestamp>-predeploy/
# Output in each folder: db.dump, moodledata.tgz, gateway.tgz, studio.tgz, engine-image.txt, SHA256SUMS
#
# Round 19 (disk protection):
#   - kept by count, not by age: the last BACKUP_KEEP_COUNT (10) pre-deploy backups and the last
#     BACKUP_KEEP_DAILY (7) daily backups; folders without a suffix (older backups) count as pre-deploy;
#   - a pre-deploy backup is skipped when any backup is less than an hour old;
#   - below BACKUP_MIN_FREE_PCT (15 %) free space the oldest backups are removed first; if that is not
#     enough the backup is skipped with a warning instead of filling the disk;
#   - only daily backups go off-site; off-site copies older than BACKUP_S3_KEEP_DAYS (30) are removed.
# A skipped backup exits 0, so a deploy goes on.
. "$(dirname "$0")/lib.sh"

MODE=daily
[ "${1:-}" = "--pre-update" ] && MODE=predeploy

num() { local v; v=$(envval "$1"); case "$v" in ''|*[!0-9]*) echo "$2" ;; *) echo "$v" ;; esac; }
KEEP_COUNT=$(num BACKUP_KEEP_COUNT 10)
KEEP_DAILY=$(num BACKUP_KEEP_DAILY 7)
MIN_FREE=$(num BACKUP_MIN_FREE_PCT 15)
S3_KEEP_DAYS=$(num BACKUP_S3_KEEP_DAYS 30)
DB_NAME=$(envval DB_NAME); DB_NAME=${DB_NAME:-moodle}
DB_USER=$(envval DB_USER); DB_USER=${DB_USER:-moodle}

mkdir -p backups

# A warning shows in the log and, when run by the deploy workflow, on the GitHub run page.
warn() { log "WARNING: $*"; echo "::warning title=Backup::$*"; }

free_pct() { df -P "${BACKUP_DF_PATH:-backups}" | awk 'NR==2 {sub("%", "", $5); print 100 - $5}'; }

# Backup folders, oldest first. Daily ones end in -daily; everything else counts as pre-deploy.
daily_dirs()  { find backups -mindepth 1 -maxdepth 1 -type d -name '2*-daily' | sort; }
deploy_dirs() { find backups -mindepth 1 -maxdepth 1 -type d -name '2*' ! -name '*-daily' | sort; }

remove() { log "Removing old backup $1"; rm -rf "$1"; }

# Keep the newest N of a list (oldest first on stdin), remove the rest.
keep_newest() {
    local n=$1 all
    all=$(cat)
    [ -z "$all" ] && return 0
    local total; total=$(printf '%s\n' "$all" | wc -l)
    [ "$total" -le "$n" ] && return 0
    printf '%s\n' "$all" | head -n $((total - n)) | while read -r d; do remove "$d"; done
}

prune() {
    deploy_dirs | keep_newest "$KEEP_COUNT"
    daily_dirs | keep_newest "$KEEP_DAILY"
}

# Free space: remove the oldest pre-deploy backups, then old daily ones (the newest daily one stays).
make_room() {
    local d
    while [ "$(free_pct)" -lt "$MIN_FREE" ]; do
        d=$(deploy_dirs | head -n 1)
        if [ -z "$d" ] && [ "$(daily_dirs | wc -l)" -gt 1 ]; then
            d=$(daily_dirs | head -n 1)
        fi
        [ -z "$d" ] && return 1
        remove "$d"
    done
}

prune

if [ "$MODE" = predeploy ]; then
    recent=$(find backups -mindepth 1 -maxdepth 1 -type d -name '2*' -mmin -60 | sort | tail -n 1)
    if [ -n "$recent" ]; then
        log "A backup less than an hour old exists ($recent); skipping the pre-deploy backup."
        exit 0
    fi
fi

if ! make_room; then
    warn "Only $(free_pct)% of the disk is free (minimum ${MIN_FREE}%), even after removing old backups; this backup was skipped. Free some space (deploy/status.sh shows what uses it)."
    exit 0
fi

TS=$(date +%Y%m%d-%H%M%S)
OUT="backups/$TS-$MODE"
mkdir -p "$OUT"
# A backup that fails half-way (e.g. the disk fills up) is removed rather than left looking complete.
trap 'rc=$?; if [ $rc -ne 0 ]; then rm -rf "$OUT"; warn "Backup failed (exit $rc); the incomplete folder $OUT was removed."; fi' EXIT

log "Dumping database..."
dc exec -T db pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc > "$OUT/db.dump"

log "Archiving uploaded files (moodledata)..."
dc exec -T moodle tar czf - -C /var/www/moodledata \
    --exclude=./cache --exclude=./localcache --exclude=./sessions --exclude=./temp --exclude=./trashdir . \
    > "$OUT/moodledata.tgz"

log "Archiving sign-up records (teacher applications, course catalogue) and the sewing software's company data..."
# 第 49 轮：缝纫机设计软件的企业项目、开通记录、FreeCAD 钥匙（sewing.db）、本单位零件库的 STEP（sewing_parts/）、AI 调用记录
dc exec -T gateway tar czf - --ignore-failed-read --exclude='sewing_parts/*.mesh.json' \
    -C /data accounts settings.json sewing.db sewing_ai.db sewing_parts 2>/dev/null > "$OUT/gateway.tgz" || true

log "Archiving AI course projects and teachers' materials..."
# Everything the AI course builder made (lessons, videos, labs, chat, decisions) and the materials teachers uploaded.
# Left out: caches that are made again on demand (spoken sentences, video pieces, converted slides, file cache).
dc exec -T gateway tar czf - -C /data \
    --exclude='./projects/*/voice_cache' --exclude='./projects/*/uploads' --exclude='./projects/*/lessons/*/lecture/slides' \
    ./projects ./imports 2>/dev/null > "$OUT/studio.tgz" || true

# Record which engine image produced this backup, for restores and rollbacks.
envval ENGINE_IMAGE > "$OUT/engine-image.txt"
( cd "$OUT" && sha256sum db.dump moodledata.tgz gateway.tgz studio.tgz > SHA256SUMS )
log "Local backup: $OUT ($(du -sh "$OUT" | cut -f1))"
trap - EXIT

ENDPOINT=$(envval BACKUP_S3_ENDPOINT)
BUCKET=$(envval BACKUP_S3_BUCKET)
offsite() {
    docker run --rm \
        -v "$WQ_DIR/backups:/backups:ro" \
        -e RCLONE_CONFIG_OFFSITE_TYPE=s3 \
        -e RCLONE_CONFIG_OFFSITE_PROVIDER="$(envval BACKUP_S3_PROVIDER | grep . || echo DigitalOcean)" \
        -e RCLONE_CONFIG_OFFSITE_ENDPOINT="$ENDPOINT" \
        -e RCLONE_CONFIG_OFFSITE_ACCESS_KEY_ID="$(envval BACKUP_S3_ACCESS_KEY)" \
        -e RCLONE_CONFIG_OFFSITE_SECRET_ACCESS_KEY="$(envval BACKUP_S3_SECRET_KEY)" \
        -e RCLONE_CONFIG_OFFSITE_ACL=private \
        "$(envval RCLONE_IMAGE | grep . || echo rclone/rclone:1)" "$@"
}
if [ "$MODE" != daily ]; then
    log "Pre-deploy backups stay on this server; only daily backups go off-site."
elif [ -n "$ENDPOINT" ] && [ -n "$BUCKET" ]; then
    log "Uploading to s3://$BUCKET/wenquest/$TS-daily ..."
    if offsite copy "/backups/$TS-daily" "offsite:$BUCKET/wenquest/$TS-daily" --quiet; then
        log "Off-site copy done."
        offsite delete "offsite:$BUCKET/wenquest" --min-age "${S3_KEEP_DAYS}d" --rmdirs --quiet \
            && log "Off-site copies older than $S3_KEEP_DAYS days removed." \
            || warn "Old off-site copies could not be removed."
    else
        warn "Off-site upload failed; the backup is on this server only. Check BACKUP_S3_* in .env."
    fi
else
    log "BACKUP_S3_* not set; keeping the backup on this server only."
fi

# The digital factory (its own folder on this server) is backed up with the daily backup; its own
# deploys take their own backups.
if [ "$MODE" = daily ] && [ -x "$WQ_DIR/factory/deploy/backup.sh" ] && [ -f "$WQ_DIR/factory/.env" ]; then
    "$WQ_DIR/factory/deploy/backup.sh" || log "WARNING: digital factory backup failed (see above)."
fi

prune
log "Backup finished."
