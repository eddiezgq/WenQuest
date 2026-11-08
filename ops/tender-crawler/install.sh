#!/usr/bin/env bash
# 招标信息抓取 一键安装（Ubuntu 20.04 / 22.04 / 24.04，root 运行）
# 用法：sudo bash install.sh
# 重复运行即升级：保留已有 config.yaml 与 data/，只更新程序。
set -euo pipefail
APP=/opt/tender-crawler
HERE="$(cd "$(dirname "$0")" && pwd)"
PIP_INDEX="${PIP_INDEX:-https://mirrors.aliyun.com/pypi/simple/}"

[ "$(id -u)" = 0 ] || { echo "请用 root 运行：sudo bash install.sh"; exit 1; }
echo "==> 安装系统依赖"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq python3 python3-venv python3-pip tzdata >/dev/null

echo "==> 创建运行用户与目录"
id tender >/dev/null 2>&1 || useradd --system --home "$APP" --shell /usr/sbin/nologin tender
mkdir -p "$APP/data"
rm -rf "$APP/tender_crawler"
cp -r "$HERE/tender_crawler" "$HERE/requirements.txt" "$HERE/README.md" "$APP/"
if [ -f "$APP/config.yaml" ]; then
  echo "    保留已有 config.yaml（新版示例另存为 config.yaml.new）"
  cp "$HERE/config.yaml" "$APP/config.yaml.new"
else
  cp "$HERE/config.yaml" "$APP/config.yaml"
fi
[ -f /etc/tender-crawler.env ] || { install -m 600 /dev/null /etc/tender-crawler.env; echo "# 密钥放这里，例如 OSS_ACCESS_KEY_ID=..." > /etc/tender-crawler.env; }

echo "==> 安装 Python 依赖（镜像：$PIP_INDEX）"
python3 -m venv "$APP/venv"
"$APP/venv/bin/pip" install -q -i "$PIP_INDEX" --upgrade pip
"$APP/venv/bin/pip" install -q -i "$PIP_INDEX" -r "$APP/requirements.txt"
chown -R tender:tender "$APP"

echo "==> 安装命令与定时任务"
cat > /usr/local/bin/tender-crawler <<'SH'
#!/bin/sh
cd /opt/tender-crawler && exec sudo -u tender env TENDER_CONFIG=/opt/tender-crawler/config.yaml \
  /opt/tender-crawler/venv/bin/python -m tender_crawler.main "$@"
SH
chmod 755 /usr/local/bin/tender-crawler
cp "$HERE/deploy/tender-crawler.service" "$HERE/deploy/tender-crawler.timer" /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now tender-crawler.timer

tender-crawler check
echo
echo "安装完成。每天北京时间 06:30 左右自动运行，结果在 $APP/data/latest.json 和 latest.md。"
echo "立即试跑一次：sudo systemctl start tender-crawler.service && journalctl -u tender-crawler -f"
systemctl list-timers tender-crawler.timer --no-pager | head -3
