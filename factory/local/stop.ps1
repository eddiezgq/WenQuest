# 问渠数字工厂 · 本地版：停止（数据保留在 Docker 卷里，下次启动接着用）；加 -Reset 连数据一起清空（成绩、订单、车间历史都没了）。
param([switch]$Reset)
Push-Location (Join-Path $PSScriptRoot "..\digital")
try { if ($Reset) { docker compose --profile mock down -v } else { docker compose --profile mock down } } finally { Pop-Location }
