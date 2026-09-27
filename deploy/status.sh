#!/usr/bin/env bash
# One-screen health summary for remote maintenance.
. "$(dirname "$0")/lib.sh"

echo "== Services"
dc ps --format 'table {{.Service}}\t{{.State}}\t{{.Status}}'
echo
echo "== Engine image: $(envval ENGINE_IMAGE)"
echo "== Disk"
df -h / | tail -n 1
echo "== Memory"
free -h | sed -n 2p
echo "== Latest backup"
find backups -mindepth 1 -maxdepth 1 -type d | sort | tail -n 1
echo "== Websites"
DOMAIN=$(envval SITE_DOMAIN)
for url in "https://$DOMAIN/" "https://learn.$DOMAIN/api/health" "https://classic.$DOMAIN/login/index.php"; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$url" || echo "---")
    echo "$code  $url"
done
