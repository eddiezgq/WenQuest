#!/usr/bin/env bash
# 服务器磁盘清理（第 119 轮，国内服务器 2026-11-09 磁盘满到 100%：143 个镜像占 84 GB，只有 21 个在用）。
# 用 deploy 用户运行（ssh deploy@主机 'bash -s' < deploy/free-disk.sh）。只清能重新取回的东西：
#   用量 ≥85%：构建缓存、停用的容器、不在用且 3 天以上的镜像、deploy 用户 /tmp 里 2 天前的文件（与美国服务器同一做法）；
#   清完仍 ≥90%：所有不在用的镜像（回滚时从镜像仓库重新拉取）。
# 不碰数据卷、数据库、备份、教材。
set +e
pct() { df -P / | awk 'NR==2 {sub("%", "", $5); print $5}'; }
before=$(pct)
echo "磁盘用量（清理前）：${before}%"
if [ "${before:-0}" -ge 85 ]; then
  docker builder prune -af >/dev/null 2>&1
  docker container prune -f >/dev/null 2>&1
  docker image prune -af --filter "until=72h" >/dev/null 2>&1
  find /tmp -maxdepth 1 -user "$(id -un)" -mtime +2 -exec rm -rf {} + 2>/dev/null
  if [ "$(pct)" -ge 90 ]; then
    echo "仍然 ≥90%，清掉所有不在用的镜像"
    docker image prune -af >/dev/null 2>&1
  fi
  echo "磁盘用量（清理后）：$(pct)%"
  docker system df 2>/dev/null
fi
