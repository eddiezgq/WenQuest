#!/usr/bin/env bash
# 在线文档（第 121 轮）上线后的检查：OnlyOffice 健康、经 learn./docs/ 能打开、网关报 ok、Moodle 插件已配好、内存。
# 用法（服务器上）：deploy/check-docs.sh   最后一行是 "docs ok" 或 "docs FAIL ..."。部署任务经 ssh 调用。
. "$(dirname "$0")/lib.sh"
D=$(envval SITE_DOMAIN)
fail=""

# OnlyOffice 启动要一两分钟：最多等 5 分钟。
for i in $(seq 1 30); do
    b=$(curl -s --resolve "learn.$D:443:127.0.0.1" "https://learn.$D/docs/healthcheck")
    [ "$b" = "true" ] && break
    sleep 10
done
echo "learn.$D/docs/healthcheck -> ${b:-（无响应）}"
[ "$b" = "true" ] || fail="$fail healthcheck"

h=$(curl -s --resolve "learn.$D:443:127.0.0.1" "https://learn.$D/api/health")
echo "api/health -> $h"
echo "$h" | grep -q '"docs": *"ok"' || fail="$fail gateway"

url=$(dc exec -T moodle su -s /bin/sh www-data -c 'c=admin/cli/cfg.php; [ -f $c ] || c=public/$c; php $c --component=onlyofficeeditor --name=documentserverurl' 2>/dev/null | tr -d '\r')
echo "Moodle documentserverurl -> ${url:-（未设置）}"
[ "$url" = "https://learn.$D/docs" ] || fail="$fail moodle-config"

# 在线实验报告导出 PDF（第 122 轮）：用真实报告模板生成 Word，经 OnlyOffice 转成 PDF 并检查。
pdf=$(dc exec -T gateway python -m app.production.pdf_selftest 2>&1 | tail -5)
echo "$pdf"
echo "$pdf" | tail -1 | grep -q '^pdf ok' || fail="$fail report-pdf"

docker stats --no-stream --format '{{.Name}} {{.MemUsage}} {{.CPUPerc}}' | grep -E 'docs|moodle|gateway' || true
free -m | sed -n 1,2p

if [ -z "$fail" ]; then echo "docs ok"; else
    dc ps -a docs; dc logs --tail 60 docs
    echo "docs FAIL$fail"
fi
