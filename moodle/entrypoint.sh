#!/bin/sh
set -e
cd /var/www/moodle

php write_config.php

# Copy language packs into moodledata on first start.
mkdir -p /var/www/moodledata/lang
cp -rn /opt/langpacks/* /var/www/moodledata/lang/ 2>/dev/null || true
chown -R www-data:www-data /var/www/moodledata

echo "Waiting for PostgreSQL at ${DB_HOST:-db}..."
until PGPASSWORD="$DB_PASSWORD" psql -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" -U "${DB_USER:-moodle}" -d "${DB_NAME:-moodle}" -c 'select 1' >/dev/null 2>&1; do
    sleep 2
done

# Only the web container installs and upgrades; the cron container waits for it.
if [ "$1" = "apache2-foreground" ]; then
    INSTALLED=$(PGPASSWORD="$DB_PASSWORD" psql -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" -U "${DB_USER:-moodle}" -d "${DB_NAME:-moodle}" -tAc "select to_regclass('mdl_config') is not null")
    if [ "$INSTALLED" != "t" ]; then
        echo "Installing Moodle..."
        su -s /bin/sh www-data -c "php admin/cli/install_database.php --agree-license --lang=en \
            --fullname=\"${MOODLE_SITE_NAME:-问渠 WenQuest}\" --shortname=\"${MOODLE_SITE_SHORTNAME:-wenquest}\" \
            --adminuser=\"${MOODLE_ADMIN_USER:-admin}\" --adminpass=\"${MOODLE_ADMIN_PASSWORD}\" \
            --adminemail=\"${MOODLE_ADMIN_EMAIL:-admin@example.com}\" --supportemail=\"${MOODLE_ADMIN_EMAIL:-admin@example.com}\""
    else
        echo "Upgrading Moodle and plugins if needed..."
        su -s /bin/sh www-data -c "php admin/cli/upgrade.php --non-interactive"
    fi
    su -s /bin/sh www-data -c "php setup_ai.php"
fi

exec "$@"
