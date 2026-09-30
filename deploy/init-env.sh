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

DOMAIN=$(ask "Main domain, without www (e.g. myacademy.com)" "")
[ -n "$DOMAIN" ] || { echo "A domain is required." >&2; exit 1; }
EMAIL=$(ask "Administrator email" "admin@$DOMAIN")
SITE_NAME=$(ask "Learning platform name" "Robotics Academy 机器人学院")
LANG_DEFAULT=$(ask "Default language: en or zh_cn (users can switch)" "en")
TZ_DEFAULT=$(ask "Time zone" "America/New_York")
ANTHROPIC=$(ask "Anthropic API key (can be added later)" "")

ADMIN_PASS=$(genpass)
DB_PASS=$(genpass)
SESSION_KEY=$(genpass)$(genpass)

cp .env.example .env
chmod 600 .env
set_env() { sed -i "s|^$1=.*|$1=$2|" .env; }
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
set_env MOODLE_NOREPLY_EMAIL "noreply@$DOMAIN"
set_env ENGINE_IMAGE ""   # filled in by the first deployment
set_env GATEWAY_IMAGE ""
set_env WEB_IMAGE ""
set_env ANIMATOR_IMAGE ""
set_env LABCHECK_IMAGE ""

echo
echo "Created .env. Save these somewhere safe (a password manager):"
echo "  Admin login:     admin / $ADMIN_PASS"
echo "  Database:        moodle / $DB_PASS"
echo "Email (SMTP_*) and off-site backup (BACKUP_S3_*) settings can be added later with: nano .env"
