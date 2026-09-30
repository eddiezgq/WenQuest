# shellcheck shell=bash
# 数字工厂服务器脚本的公共部分。只供 source，不单独运行。
# 服务器目录默认 /opt/wenquest/factory（学习平台在上一级 /opt/wenquest）。
set -euo pipefail

FD="${FACTORY_DIR:-/opt/wenquest/factory}"
LEARN_DIR="${LEARN_DIR:-$(dirname "$FD")}"
cd "$FD"

# 从 .env 读一项（不 source，值里可能有空格）
envval() {
    local f="${2:-.env}" line
    line=$(grep -E "^$1=" "$f" 2>/dev/null | tail -n 1 || true)
    printf '%s' "${line#*=}"
}

envset() {
    touch .env
    if grep -qE "^$1=" .env; then
        sed -i "s|^$1=.*|$1=$2|" .env
    else
        printf '%s=%s\n' "$1" "$2" >> .env
    fi
}

learnval() { envval "$1" "$LEARN_DIR/.env"; }

dc() {
    local args=() f
    for f in ${FACTORY_COMPOSE:-docker-compose.yml}; do args+=(-f "$f"); done
    docker compose -p wq-factory "${args[@]}" "$@"
}

log() { printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"; }

# 在 ERPNext 里执行一个 Python 函数（bench execute），输出其返回值
bench_exec() {
    dc exec -T erp-backend bench --site frontend execute "$@"
}
