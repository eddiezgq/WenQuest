# 问渠数字工厂 · 本地版（第 30 轮 H-5）：学校机房没有外网时，在一台 Windows 电脑上用 Docker Desktop 启动整座工厂。
# 缺省：教学模式、演示工厂“问渠减速器厂”、模拟 ERPNext。说明见同目录 README.md。
#
# 用法（PowerShell，在仓库根目录）：.\factory\local\start.ps1 [-Plant 清单.yaml] [-ErpNext URL] [-Offline]
#   -Plant 清单.yaml：按这份工厂清单建车间（不填 = 演示工厂；实验、情景只在演示工厂有）
#   -ErpNext URL    ：接学校自己的 ERPNext（同时在 factory\digital\.env 填 WQ_ERP_API_KEY、WQ_ERP_API_SECRET）
#   -Offline        ：机房没有外网：不构建、不下载，只用已导入的镜像（导入办法见 README.md“没有外网的机房”）
# 本文件存成带 BOM 的 UTF-8：Windows PowerShell 5.1 读不带 BOM 的文件会按本机代码页，中文变乱码
param([string]$Plant = "", [string]$ErpNext = "", [switch]$Offline)
$ErrorActionPreference = "Stop"
$fac = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$dig = Join-Path $fac "digital"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw "没有找到 docker：请先安装 Docker Desktop（https://www.docker.com/products/docker-desktop/）" }
& docker info *> $null
if ($LASTEXITCODE -ne 0) { throw "Docker 没有在运行：请先打开 Docker Desktop，等左下角显示 Engine running，再运行本脚本" }

$envFile = Join-Path $dig ".env"
# .env 按 UTF-8（不带 BOM）读写：PowerShell 5.1 的 Get-Content / Set-Content 缺省用本机代码页，Set-Content -Encoding utf8 又会加 BOM
function Read-Env { [IO.File]::ReadAllLines($envFile, [Text.Encoding]::UTF8) }
function Write-Env($lines) { [IO.File]::WriteAllLines($envFile, [string[]]$lines, (New-Object Text.UTF8Encoding $false)) }
function Set-Env($key, $value) {
  $lines = @(Read-Env)
  if ($lines -match "^$key=") { $lines = $lines | ForEach-Object { if ($_ -match "^$key=") { "$key=$value" } else { $_ } } } else { $lines += "$key=$value" }
  Write-Env $lines
}
function Get-EnvValue($key) {
  $hit = @(Read-Env | Where-Object { $_ -match "^$key=" }) | Select-Object -Last 1
  if ($hit) { return $hit.Substring($key.Length + 1) } else { return "" }
}
function New-Random($chars, $n) {
  $rng = New-Object Security.Cryptography.RNGCryptoServiceProvider
  $bytes = New-Object byte[] $n
  $rng.GetBytes($bytes)
  -join ($bytes | ForEach-Object { $chars[$_ % $chars.Length] })
}

if (-not (Test-Path $envFile)) {
  [IO.File]::WriteAllLines($envFile, [IO.File]::ReadAllLines((Join-Path $dig ".env.example"), [Text.Encoding]::UTF8), (New-Object Text.UTF8Encoding $false))
  Set-Env "WQ_SECRET" (New-Random "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789" 32)
  # 时区：中国时区的电脑设 Asia/Shanghai（看板按它分日、分班；AI 只用已备案的 DeepSeek）
  try { if ((Get-TimeZone).Id -eq "China Standard Time") { Set-Env "WQ_TZ" "Asia/Shanghai" } } catch { }
  Write-Host "已生成 $envFile（登录签名密钥随机生成；AI 助手的密钥可选，填在里面）"
}
# 老师密码：第一次启动时生成，只在这里显示一次；忘了就看 .env 里的 WQ_TEACHER_PASSWORD
$newPw = ""
if (-not (Get-EnvValue "WQ_TEACHER_PASSWORD")) {
  $newPw = New-Random "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789" 10
  Set-Env "WQ_TEACHER_PASSWORD" $newPw
}
Set-Env "WQ_EDITION" "local"
Set-Env "WQ_MODE" "teach"

# 工厂清单：容器里是 /app/plants/<文件名>。不在 factory\plants 里的清单先复制到 factory\plants\_local\（不进 git）
if ($Plant) {
  if (-not (Test-Path $Plant)) { throw "找不到清单文件：$Plant" }
  $src = (Resolve-Path $Plant).Path
  $plants = (Join-Path $fac "plants") + [IO.Path]::DirectorySeparatorChar
  if ($src.StartsWith($plants, [StringComparison]::OrdinalIgnoreCase)) { $rel = $src.Substring($plants.Length) -replace '\\', '/' }
  else {
    $dst = Join-Path $fac "plants\_local"
    New-Item -ItemType Directory -Force $dst | Out-Null
    Copy-Item $src $dst -Force
    $rel = "_local/" + (Split-Path $src -Leaf)
  }
  Set-Env "WQ_PLANT_FILE" "/app/plants/$rel"
  Write-Host "工厂清单：$rel（教学页面、实验、情景只在演示工厂有）"
} else { Set-Env "WQ_PLANT_FILE" "" }

$profileArgs = @()
if ($ErpNext) { Set-Env "WQ_ERPNEXT_API" $ErpNext; Set-Env "WQ_ERPNEXT_URL" $ErpNext }
else {
  Set-Env "WQ_ERPNEXT_API" "http://mock-erpnext:8091"; Set-Env "WQ_ERPNEXT_URL" "http://localhost:8091"
  $profileArgs = @("--profile", "mock")
}

if ($Offline) { Write-Host "启动工厂（不联网，用已导入的镜像）…"; $upArgs = @("up", "-d", "--no-build", "--pull", "never") }
else { Write-Host "启动工厂（第一次要下载、构建镜像，约 10–30 分钟；以后几十秒）…"; $upArgs = @("up", "-d", "--build") }
Push-Location $dig
try { & docker compose @profileArgs @upArgs; if ($LASTEXITCODE -ne 0) { throw "docker compose 启动失败" } } finally { Pop-Location }

Write-Host "等工厂枢纽启动（最多 4 分钟）…"
$deadline = (Get-Date).AddSeconds(240)
$ok = $false
while ((Get-Date) -lt $deadline) {
  try { Invoke-RestMethod -TimeoutSec 5 http://localhost:8100/api/health | Out-Null; $ok = $true; break } catch { Start-Sleep 3 }
}
if (-not $ok) { throw "枢纽 4 分钟内没有就绪。看日志：cd factory\digital; docker compose logs hub" }

Write-Host ""
Write-Host "已启动（本地版）：这台电脑打开 http://localhost:8100"
try {
  $ips = @(Get-NetIPAddress -AddressFamily IPv4 -ErrorAction Stop | Where-Object { $_.IPAddress -notmatch '^(127\.|169\.254\.)' -and $_.InterfaceAlias -notmatch 'vEthernet|WSL|Docker|Loopback' } | ForEach-Object { $_.IPAddress })
  foreach ($ip in $ips) { Write-Host "机房里学生的电脑打开：http://${ip}:8100" }
} catch { Write-Host "学生的电脑打开：http://<这台电脑的 IP>:8100（IP 用 ipconfig 查）" }
if ($newPw) {
  Write-Host ""
  Write-Host "老师密码：$newPw" -ForegroundColor Yellow
  Write-Host "  登录时勾「我是老师」并输这个密码，才能当厂长、用教师控制台。只显示这一次；忘了看 factory\digital\.env 的 WQ_TEACHER_PASSWORD"
}
Write-Host "停止：.\factory\local\stop.ps1（数据保留）；.\factory\local\stop.ps1 -Reset（连数据一起清空）"
try { Start-Process "http://localhost:8100" } catch { }
