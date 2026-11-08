#!/usr/bin/env bash
# 卸载程序（保留 /opt/tender-crawler/data 里的历史结果）
set -euo pipefail
systemctl disable --now tender-crawler.timer 2>/dev/null || true
rm -f /etc/systemd/system/tender-crawler.service /etc/systemd/system/tender-crawler.timer /usr/local/bin/tender-crawler
systemctl daemon-reload
rm -rf /opt/tender-crawler/venv /opt/tender-crawler/tender_crawler
echo "已卸载；历史结果仍在 /opt/tender-crawler/data"
