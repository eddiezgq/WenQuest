#!/usr/bin/env bash
# 问渠数字工厂 · 本地版（第 30 轮 H-5）：学校机房没有外网时，在一台电脑上用 Docker 启动整座工厂。
# 缺省：教学模式、演示工厂“问渠减速器厂”、模拟 ERPNext。说明见同目录 README.md。
#
# 用法（在仓库根目录）：factory/local/start.sh [--plant 清单.yaml] [--erpnext URL] [--offline]
#   --plant 清单.yaml：按这份工厂清单建车间（不填 = 演示工厂；实验、情景只在演示工厂有）
#   --erpnext URL    ：接学校自己的 ERPNext（同时在 factory/digital/.env 填 WQ_ERP_API_KEY、WQ_ERP_API_SECRET）
#   --offline        ：机房没有外网：不构建、不下载，只用已导入的镜像（导入办法见 README.md“没有外网的机房”）
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
fac="$(cd "$here/.." && pwd)"
dig="$fac/digital"
plant=""
erp=""
offline=0
while [ $# -gt 0 ]; do
  case "$1" in
    --plant) plant="${2:?--plant 后面要跟清单文件}"; shift ;;
    --erpnext) erp="${2:?--erpnext 后面要跟 ERPNext 地址}"; shift ;;
    --offline) offline=1 ;;
    -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
    *) echo "不认识的参数：$1（可用 --plant 清单.yaml、--erpnext URL、--offline）" >&2; exit 2 ;;
  esac
  shift
done

command -v docker >/dev/null || { echo "没有找到 docker：请先安装 Docker（Windows / macOS 装 Docker Desktop，Linux 装 Docker Engine）" >&2; exit 1; }
docker info >/dev/null 2>&1 || { echo "Docker 没有在运行：请先启动 Docker Desktop（或 Linux 上 sudo systemctl start docker），再运行本脚本" >&2; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "没有 docker compose：请装 Docker Desktop，或 Linux 上装 docker-compose-plugin" >&2; exit 1; }

rand() { LC_ALL=C tr -dc "$1" </dev/urandom | head -c "$2" || true; }
env="$dig/.env"
set_env() {  # 改写或追加一行 KEY=VALUE
  if grep -q "^$1=" "$env"; then sed -i.bak -e "s|^$1=.*|$1=$2|" "$env" && rm -f "$env.bak"; else echo "$1=$2" >> "$env"; fi
}
get_env() { sed -n "s/^$1=//p" "$env" | tail -n 1; }

if [ ! -f "$env" ]; then
  cp "$dig/.env.example" "$env"
  set_env WQ_SECRET "$(rand 'A-Za-z0-9' 32)"
  # 时区：取这台电脑的（看板按它分日、分班；中国时区时 AI 只用已备案的 DeepSeek）
  tz="$(readlink /etc/localtime 2>/dev/null | sed -n 's|.*zoneinfo/||p')"
  [ -n "$tz" ] && set_env WQ_TZ "$tz"
  echo "已生成 $env（登录签名密钥随机生成；AI 助手的密钥可选，填在里面）"
fi
# 老师密码：第一次启动时生成，只在这里显示一次；忘了就看 .env 里的 WQ_TEACHER_PASSWORD
new_pw=""
if [ -z "$(get_env WQ_TEACHER_PASSWORD)" ]; then
  new_pw="$(rand 'A-HJ-NP-Za-km-z2-9' 10)"
  set_env WQ_TEACHER_PASSWORD "$new_pw"
fi
set_env WQ_EDITION local
set_env WQ_MODE teach

# 工厂清单：容器里是 /app/plants/<文件名>。不在 factory/plants 里的清单先复制到 factory/plants/_local/（不进 git）
if [ -n "$plant" ]; then
  [ -f "$plant" ] || { echo "找不到清单文件：$plant" >&2; exit 1; }
  src="$(cd "$(dirname "$plant")" && pwd)/$(basename "$plant")"
  case "$src" in
    "$fac/plants/"*) rel="${src#"$fac/plants/"}" ;;
    *) mkdir -p "$fac/plants/_local"; cp "$src" "$fac/plants/_local/"; rel="_local/$(basename "$src")" ;;
  esac
  set_env WQ_PLANT_FILE "/app/plants/$rel"
  echo "工厂清单：$rel（教学页面、实验、情景只在演示工厂有）"
else
  set_env WQ_PLANT_FILE ""
fi

profile=()
if [ -n "$erp" ]; then
  set_env WQ_ERPNEXT_API "$erp"
  set_env WQ_ERPNEXT_URL "$erp"
else
  set_env WQ_ERPNEXT_API http://mock-erpnext:8091
  set_env WQ_ERPNEXT_URL http://localhost:8091
  profile=(--profile mock)
fi

cd "$dig"
if [ "$offline" = 1 ]; then
  echo "启动工厂（不联网，用已导入的镜像）…"
  docker compose "${profile[@]}" up -d --no-build --pull never
else
  echo "启动工厂（第一次要下载、构建镜像，约 10–30 分钟；以后几十秒）…"
  docker compose "${profile[@]}" up -d --build
fi

health() {
  if command -v curl >/dev/null; then curl -fsS -o /dev/null --max-time 5 http://localhost:8100/api/health
  else python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8100/api/health', timeout=5)" 2>/dev/null; fi
}
echo "等工厂枢纽启动（最多 4 分钟）…"
t0=$(date +%s)
until health; do
  if [ $(( $(date +%s) - t0 )) -ge 240 ]; then
    echo "枢纽 4 分钟内没有就绪。看日志：cd factory/digital && docker compose logs hub" >&2
    exit 1
  fi
  sleep 3
done

ip=""
if command -v hostname >/dev/null && hostname -I >/dev/null 2>&1; then ip="$(hostname -I | awk '{print $1}')"; fi
[ -z "$ip" ] && command -v ipconfig >/dev/null && ip="$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || true)"
echo
echo "已启动（本地版）：这台电脑打开 http://localhost:8100"
[ -n "$ip" ] && echo "机房里学生的电脑打开：http://$ip:8100"
if [ -n "$new_pw" ]; then
  echo
  echo "老师密码：$new_pw"
  echo "  登录时勾「我是老师」并输这个密码，才能当厂长、用教师控制台。只显示这一次；忘了看 factory/digital/.env 的 WQ_TEACHER_PASSWORD"
fi
echo "停止：factory/local/stop.sh（数据保留）；factory/local/stop.sh --reset（连数据一起清空）"
