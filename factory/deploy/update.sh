#!/usr/bin/env bash
# 把数字工厂换到新镜像并重启（由 GitHub Actions“数字工厂部署”调用，也可在服务器上手动运行）。
# 用法：deploy/update.sh [工厂镜像] [桥接镜像]      不带参数：用现有镜像重启（例如改了 .env 之后）
# 第一次运行会先检查内存，再自动执行 deploy/install.sh。
. "$(dirname "$0")/lib.sh"

APP="${1:-}"; BRIDGE="${2:-}"
[ -n "$APP" ] && envset FACTORY_APP_IMAGE "$APP"
[ -n "$BRIDGE" ] && envset FACTORY_BRIDGE_IMAGE "$BRIDGE"
[ -n "$(envval FACTORY_APP_IMAGE)" ] || { echo "还没有镜像：请通过 GitHub Actions 部署" >&2; exit 1; }

if [ "$(envval FACTORY_INSTALLED)" != 1 ]; then
    # D1：ERPNext 加数字工厂约需 3 GB 内存。不够就停下，提示升级服务器，免得拖垮学习平台
    avail=$(awk '/MemAvailable/ {print int($2/1024)}' /proc/meminfo)
    swap=$(awk '/SwapFree/ {print int($2/1024)}' /proc/meminfo)
    need="${FACTORY_MIN_MEM_MB:-3000}"
    log "可用内存 ${avail} MB，交换空间 ${swap} MB（需要至少 ${need} MB 可用内存）"
    if [ "$avail" -lt "$need" ]; then
        echo "::error::服务器可用内存只有 ${avail} MB，装数字工厂需要 ${need} MB。请在 DigitalOcean 控制台把这台服务器升到 16 GB（Resize），完成后重新运行“数字工厂部署”。学习平台未受影响。"
        exit 3
    fi
    log "第一次部署：执行安装（先生成密码和配置，再拉镜像、启动）..."
    "$(dirname "$0")/install.sh"
fi

log "拉取镜像..."
dc pull --quiet
log "启动数字工厂..."
dc up -d --remove-orphans

log "等待枢纽就绪..."
for _ in $(seq 1 40); do
    st=$(docker inspect -f '{{.State.Health.Status}}' "$(dc ps -q hub)" 2>/dev/null || echo unknown)
    if [ "$st" = healthy ]; then
        log "数字工厂已就绪。"
        docker image prune -f >/dev/null
        "$(dirname "$0")/status.sh" || true
        exit 0
    fi
    sleep 6
done
log "枢纽 4 分钟内没有就绪，最近日志："
dc logs --tail 60 hub bridge sim bus
exit 1
