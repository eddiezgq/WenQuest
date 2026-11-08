#!/usr/bin/env bash
# 每小时由 crontab 调用；北京时间 06 点那一档运行一次（--force 立即运行）。
set -uo pipefail
APP="$HOME/tender-crawler"
TODAY=$(TZ=Asia/Shanghai date +%F)
HOUR=$(TZ=Asia/Shanghai date +%H)
if [ "${1:-}" != "--force" ]; then
  [ "$HOUR" = "06" ] || exit 0
  [ "$(cat "$APP/data/.last_run" 2>/dev/null)" = "$TODAY" ] && exit 0
fi
IMG=$(cat "$APP/image.txt")
docker image inspect "$IMG" >/dev/null 2>&1 || IMG=$(docker ps --format '{{.Image}}' | grep -m1 gateway)   # 平台升级后旧镜像可能被清理
echo "=== $(TZ=Asia/Shanghai date '+%F %T') 开始（$IMG）"
exec 9>"$APP/data/.lock"; flock -n 9 || { echo "上一次还在运行"; exit 0; }
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -e PYTHONPATH=/app/pylib -v "$APP":/app -w /app \
  --memory 512m --cpus 0.5 "$IMG" python -m tender_crawler.main -c /app/config.local.yaml run
st=$?
[ $st -le 1 ] && echo "$TODAY" > "$APP/data/.last_run"
echo "=== 结束，状态 $st"
exit $st
