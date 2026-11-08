#!/usr/bin/env bash
# 在国内服务器上以 deploy 用户安装 / 升级招标抓取（第 119 轮）。不需要 sudo：
# 用平台已有的网关镜像（Python 3.12）在容器里运行，依赖装到 ~/tender-crawler/pylib，定时用 deploy 用户自己的 crontab。
# 由 .github/workflows/tender-crawler.yml 调用；也可以在服务器上手动运行：bash ~/tender-crawler/server-install.sh
set -euo pipefail
APP="$HOME/tender-crawler"
cd "$APP"
mkdir -p data pylib
[ -f config.local.yaml ] || cp config.yaml config.local.yaml   # 服务器上的配置；以后升级不覆盖
# 1.0.2 迁移：旧配置里的来源已失效（交易平台换域名、政府采购网检索被拦），备份后换成新配置
if ! grep -q "type: ccgp_list" config.local.yaml; then
  cp config.local.yaml "config.local.yaml.bak-$(date +%Y%m%d%H%M%S)"; cp config.yaml config.local.yaml; echo "配置已迁移到 1.0.2（旧配置已备份）"
fi
IMG=$(docker ps --format '{{.Image}}' | grep -m1 gateway || true)
[ -n "$IMG" ] || IMG=$(docker image ls --format '{{.Repository}}:{{.Tag}}' | grep -m1 gateway || true)
[ -n "$IMG" ] || { echo "找不到网关镜像（平台是否已部署？）"; exit 1; }
echo "$IMG" > image.txt
echo "用镜像 $IMG"
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$APP":/app -w /app "$IMG" \
  python -m pip install -q --disable-pip-version-check --target /app/pylib \
  -i https://mirrors.aliyun.com/pypi/simple/ -r /app/requirements.txt
chmod +x cron.sh
# 每小时 :37 检查一次，到北京时间 06 点那一档才真正运行，一天一次（与服务器时区无关）
( crontab -l 2>/dev/null | grep -v 'tender-crawler/cron.sh' ; echo "37 * * * * $APP/cron.sh >> $APP/data/cron.log 2>&1" ) | crontab -
crontab -l | grep tender-crawler
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -e PYTHONPATH=/app/pylib -v "$APP":/app -w /app "$IMG" \
  python -m tender_crawler.main -c /app/config.local.yaml check
echo "安装完成"
