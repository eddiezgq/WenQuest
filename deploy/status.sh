#!/usr/bin/env bash
# One-screen health summary for remote maintenance.
. "$(dirname "$0")/lib.sh"

echo "== Services"
dc ps --format 'table {{.Service}}\t{{.State}}\t{{.Status}}'
echo
echo "== Engine image: $(envval ENGINE_IMAGE)"
echo "== Disk"
df -h / | tail -n 1
used=$(df -P / | awk 'NR==2 {sub("%", "", $5); print $5}')
if [ "$used" -gt 85 ]; then
    echo "!!!!!!!! WARNING: the disk is ${used}% full - please free some space !!!!!!!!"
    echo "   Backups:       $(du -sh backups 2>/dev/null | cut -f1)  ($(find backups -mindepth 1 -maxdepth 1 -type d -name '2*' | wc -l) folders; kept by count, see deploy/backup.sh)"
    docker system df 2>/dev/null | sed 's/^/   /'
    echo "   Unused images can be removed with: docker image prune -a"
fi
echo "== Memory"
free -h | sed -n 2p
echo "== Latest backups"
echo "   daily:      $(find backups -mindepth 1 -maxdepth 1 -type d -name '2*-daily' | sort | tail -n 1)"
echo "   pre-deploy: $(find backups -mindepth 1 -maxdepth 1 -type d -name '2*' ! -name '*-daily' | sort | tail -n 1)"
echo "   off-site:   $([ -n "$(envval BACKUP_S3_BUCKET)" ] && echo "s3://$(envval BACKUP_S3_BUCKET)/wenquest (daily backups)" || echo "not configured (BACKUP_S3_*)")"
echo "== Websites"
DOMAIN=$(envval SITE_DOMAIN)
for url in "https://$DOMAIN/" "https://learn.$DOMAIN/api/health" "https://classic.$DOMAIN/login/index.php"; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$url" || echo "---")
    echo "$code  $url"
done
