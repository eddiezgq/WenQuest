#!/bin/bash
# Local full-stack test environment: Moodle 5.2 (PHP built-in server) + PostgreSQL 16 + gateway + web build.
# Run from anywhere; everything lives in /home/claude/local. See docs/帮助/本地测试环境.md.
set -e
L=/home/claude/local; R=$(cd "$(dirname "$0")/../.." && pwd)
mkdir -p $L && cd $L
[ -d moodle ] || git clone -q --depth 1 -b MOODLE_502_STABLE https://github.com/moodle/moodle.git moodle
(cd moodle && [ -d vendor ] || COMPOSER_ALLOW_SUPERUSER=1 composer install --no-dev --no-interaction --prefer-dist --classmap-authoritative --ignore-platform-req=ext-soap)
id postgres >/dev/null 2>&1 || useradd -m postgres
mkdir -p $L/pg $L/pglog && chown postgres $L/pg $L/pglog
[ -f $L/pg/PG_VERSION ] || su postgres -c "/usr/lib/postgresql/16/bin/initdb -D $L/pg -E UTF8 --locale=C.UTF-8 -A trust" >/dev/null
su postgres -c "/usr/lib/postgresql/16/bin/pg_ctl -D $L/pg -o '-p 5433 -k /tmp' -l $L/pglog/pg.log status" >/dev/null 2>&1 || \
  su postgres -c "/usr/lib/postgresql/16/bin/pg_ctl -D $L/pg -o '-p 5433 -k /tmp' -l $L/pglog/pg.log start"
sleep 2
cd $L/moodle/public
ln -sfn $R/plugins/local_wenquest local/wenquest
mkdir -p ai/provider && ln -sfn $R/plugins/aiprovider_claude ai/provider/claude
[ -d filter/multilang2 ] || git clone -q https://github.com/iarenaza/moodle-filter_multilang2.git filter/multilang2
cd $L/moodle
if ! psql -h /tmp -p 5433 -U postgres -lqt | cut -d'|' -f1 | grep -qw moodle; then
  psql -h /tmp -p 5433 -U postgres -c "create database moodle encoding 'UTF8'"
  mkdir -p $L/moodledata && chmod 777 $L/moodledata
  php -d max_input_vars=5000 admin/cli/install.php --non-interactive --agree-license --lang=en \
    --wwwroot=http://localhost:8080 --dataroot=$L/moodledata --dbtype=pgsql --dbhost=/tmp --dbport=5433 \
    --dbname=moodle --dbuser=postgres --dbpass= --fullname="WenQuest Local" --shortname=wqlocal \
    --adminuser=admin --adminpass='Admin#2026' --adminemail=admin@example.com
  cp $R/moodle/setup_wenquest.php . && php setup_wenquest.php
  cp $R/tools/local/*.php $R/tools/local/*.py $R/tools/local/*.js $R/tools/local/*.sh $R/tools/local/gateway.env $L/
  php $L/mkusers.php
fi
cd $L/moodle/public && (nohup php -d max_input_vars=5000 -d upload_max_filesize=200M -d post_max_size=200M -d memory_limit=512M \
  -S 0.0.0.0:8080 -t . $L/router.php > $L/php-server.log 2>&1 &)
cp -n $R/tools/local/*.sh $R/tools/local/*.js $R/tools/local/gateway.env $L/ 2>/dev/null || true
$L/start-gateway.sh
(cd $R/apps/web && npm ci --no-audit --no-fund && npm run build:h5)
(nohup node $L/serve-web.js > $L/serve-web.log 2>&1 &)
echo "Moodle http://localhost:8080 · gateway :8090 · app http://localhost:8088 · users teacher1 / student1-3, password Test#2026"
echo "Sample course: python3 $L/import_physics.py && php $L/enrol.php <courseid>"
