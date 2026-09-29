#!/bin/bash
# Start (or restart) the whole local environment after the sandbox stopped background processes:
# PostgreSQL, Moodle (PHP built-in server), gateway and the web app. Safe to run repeatedly.
L=/home/claude/local
PG="/usr/lib/postgresql/16/bin/pg_ctl -D $L/pg -o '-p 5433 -k /tmp' -l $L/pglog/pg.log"
su postgres -c "$PG status" >/dev/null 2>&1 || { rm -f $L/pg/postmaster.pid; su postgres -c "$PG start" >/dev/null; }
if ! curl -s -o /dev/null localhost:8080/login/index.php; then
  (cd $L/moodle/public && setsid nohup php -d max_input_vars=5000 -d upload_max_filesize=200M -d post_max_size=200M \
    -d memory_limit=512M -S 0.0.0.0:8080 -t . $L/router.php > $L/php-server.log 2>&1 < /dev/null &)
fi
curl -s -o /dev/null localhost:8090/api/health || $L/start-gateway.sh
curl -s -o /dev/null localhost:8095/health || $L/start-animator.sh
curl -s -o /dev/null localhost:8088/ || (setsid nohup node $L/serve-web.js > $L/web.log 2>&1 < /dev/null &)
sleep 3
printf "moodle %s · gateway %s · web %s\n" "$(curl -s -o /dev/null -w '%{http_code}' localhost:8080/login/index.php)" \
  "$(curl -s localhost:8090/api/health)" "$(curl -s -o /dev/null -w '%{http_code}' localhost:8088/)"
