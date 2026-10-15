#!/usr/bin/env bash
# Create /opt/wenquest/.env for a production server, generating strong passwords.
# Run once on the server as the deploy user:  cd /opt/wenquest && deploy/init-env.sh
set -euo pipefail
cd "${WQ_DIR:-/opt/wenquest}"

[ ! -f .env ] || { echo ".env already exists; edit it with: nano .env" >&2; exit 1; }
[ -f .env.example ] || { echo "Missing .env.example; run the GitHub deploy workflow once first." >&2; exit 1; }

ask() {  # ask <prompt> <default>
    local reply
    read -r -p "$1 [${2}]: " reply
    printf '%s' "${reply:-$2}"
}
genpass() { local p; p=$(head -c 256 /dev/urandom | LC_ALL=C tr -dc 'A-Za-z0-9'); printf '%s' "${p:0:24}"; }

# 第 34 轮：先问部署地区。us = 美国（原来的默认值，不变）；cn = 中国大陆（中文、北京时间、只用 DeepSeek、国内镜像仓库）
REGION=$(ask "Where is this server: us (United States) or cn (mainland China / 中国大陆)" "us")
case "$REGION" in cn|CN|china|China|中国*) REGION=cn ;; *) REGION=us ;; esac

DOMAIN=$(ask "Main domain, without www (e.g. myacademy.com)" "")
[ -n "$DOMAIN" ] || { echo "A domain is required." >&2; exit 1; }
EMAIL=$(ask "Administrator email" "admin@$DOMAIN")
SITE_NAME=$(ask "Learning platform name" "Robotics Academy 机器人学院")
if [ "$REGION" = cn ]; then
    LANG_DEFAULT=$(ask "Default language: en or zh_cn (users can switch)" "zh_cn")
    TZ_DEFAULT=$(ask "Time zone" "Asia/Shanghai")
    ANTHROPIC=""   # only registered models in China
    DEEPSEEK=$(ask "DeepSeek API key (can be added later)" "")
    CN_REG=$(ask "China image registry prefix, e.g. registry.cn-hangzhou.aliyuncs.com/wenquest (empty = Docker Hub)" "")
else
    LANG_DEFAULT=$(ask "Default language: en or zh_cn (users can switch)" "en")
    TZ_DEFAULT=$(ask "Time zone" "America/New_York")
    ANTHROPIC=$(ask "Anthropic API key (can be added later)" "")
    DEEPSEEK=""
    CN_REG=""
fi

ADMIN_PASS=$(genpass)
DB_PASS=$(genpass)
SESSION_KEY=$(genpass)$(genpass)

cp .env.example .env
chmod 600 .env
set_env() {
    if grep -qE "^$1=" .env; then sed -i "s|^$1=.*|$1=$2|" .env; else printf '%s=%s\n' "$1" "$2" >> .env; fi
}
set_env MOODLE_WWWROOT "https://classic.$DOMAIN"
set_env APP_URL "https://learn.$DOMAIN"
set_env WQ_SECRET_KEY "$SESSION_KEY"
case "$LANG_DEFAULT" in zh*) set_env WQ_DEFAULT_LANG zh ;; *) set_env WQ_DEFAULT_LANG en ;; esac
set_env MOODLE_SSLPROXY true
set_env MOODLE_SITE_NAME "$SITE_NAME"
set_env MOODLE_LANG "$LANG_DEFAULT"
set_env MOODLE_TIMEZONE "$TZ_DEFAULT"
set_env SITE_DOMAIN "$DOMAIN"
set_env ACME_EMAIL "$EMAIL"
set_env MOODLE_ADMIN_EMAIL "$EMAIL"
set_env MOODLE_ADMIN_PASSWORD "$ADMIN_PASS"
set_env DB_PASSWORD "$DB_PASS"
set_env ANTHROPIC_API_KEY "$ANTHROPIC"
if [ "$REGION" = cn ]; then
    set_env WQ_REGION cn
    set_env DEEPSEEK_API_KEY "$DEEPSEEK"
    set_env BACKUP_S3_PROVIDER Alibaba
    set_env WQ_LIBRARY_URL "https://factory.$DOMAIN"   # the parts library of this server's own digital factory
    if [ -n "$CN_REG" ]; then
        CN_REG="${CN_REG%/}"
        set_env DB_IMAGE "$CN_REG/postgres:16-alpine"
        set_env REDIS_IMAGE "$CN_REG/redis:7-alpine"
        set_env CADDY_IMAGE "$CN_REG/caddy:2"
        set_env RCLONE_IMAGE "$CN_REG/rclone:1"
    fi
fi
set_env MOODLE_NOREPLY_EMAIL "noreply@$DOMAIN"
set_env ENGINE_IMAGE ""   # filled in by the first deployment
set_env GATEWAY_IMAGE ""
set_env WEB_IMAGE ""
set_env ANIMATOR_IMAGE ""
set_env LABCHECK_IMAGE ""
set_env MICROSYNTH_IMAGE ""
set_env VOICE_IMAGE ""

echo
echo "Created .env. Save these somewhere safe (a password manager):"
echo "  Admin login:     admin / $ADMIN_PASS"
echo "  Database:        moodle / $DB_PASS"
echo "Email (SMTP_*) and off-site backup (BACKUP_S3_*) settings can be added later with: nano .env"
if [ "$REGION" = cn ]; then
    echo "China deployment (WQ_REGION=cn): see docs/帮助/国内部署指南.html. First deploy:"
    echo "  deploy/update.sh ${CN_REG:-<registry prefix>}/engine:<version>"
fi
