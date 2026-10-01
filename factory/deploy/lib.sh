# shellcheck shell=bash
# 数字工厂服务器脚本的公共部分。只供 source，不单独运行。
# 服务器目录默认 /opt/wenquest/factory（学习平台在上一级 /opt/wenquest）。
set -euo pipefail

FD="${FACTORY_DIR:-/opt/wenquest/factory}"
LEARN_DIR="${LEARN_DIR:-$(dirname "$FD")}"
cd "$FD"
mkdir -p library        # 零件库文件；先建好，免得 docker 以 root 身份建目录

# 从 .env 读一项（不 source，值里可能有空格）
envval() {
    local f="${2:-.env}" line
    line=$(grep -E "^$1=" "$f" 2>/dev/null | tail -n 1 || true)
    printf '%s' "${line#*=}"
}

envset() {
    touch .env
    if grep -qE "^$1=" .env; then
        sed -i "s|^$1=.*|$1=$2|" .env
    else
        printf '%s=%s\n' "$1" "$2" >> .env
    fi
}

learnval() { envval "$1" "$LEARN_DIR/.env"; }

dc() {
    local args=() f
    for f in ${FACTORY_COMPOSE:-docker-compose.yml}; do args+=(-f "$f"); done
    docker compose -p wq-factory "${args[@]}" "$@"
}

log() { printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"; }

# 在 ERPNext 里执行一个 Python 函数（bench execute），输出其返回值
bench_exec() {
    dc exec -T erp-backend bench --site "${ERP_SITE:-frontend}" execute "$@"
}

# 企业版演示工厂（第 9 轮）：ERPNext demo 站点、历史库 wq_demo、钥匙、数据、单点登录。可重复执行（已有的跳过）
demo_setup() {
    local domain year keys setup
    domain=$(envval SITE_DOMAIN)
    [ -n "$(envval WQ_DEMO_SECRET)" ] || envset WQ_DEMO_SECRET "$(tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 32 || true)"
    [ -n "$(envval WQ_DEMO_ERP_OAUTH_SECRET)" ] || envset WQ_DEMO_ERP_OAUTH_SECRET "$(tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 40 || true)"
    dc exec -T db psql -U wq -d wq_factory -tAc "select 1 from pg_database where datname='wq_demo'" | grep -q 1 \
        || { log "演示工厂：新建历史库 wq_demo..."; dc exec -T db psql -U wq -d wq_factory -c "create database wq_demo" >/dev/null; }
    if ! dc exec -T erp-backend test -d sites/demo; then
        log "演示工厂：新建 ERPNext 站点 demo（约 3–5 分钟）..."
        dc exec -T erp-backend bench new-site --mariadb-user-host-login-scope='%' \
            --admin-password="$(envval ERP_ADMIN_PASSWORD)" \
            --db-root-username=root --db-root-password="$(envval ERP_DB_ROOT_PASSWORD)" \
            --install-app erpnext demo
    fi
    setup=$(ERP_SITE=demo bench_exec frappe.is_setup_complete 2>/dev/null | tail -n 1 || true)
    if [ "$setup" != "true" ] && [ "$setup" != "True" ] && [ "$setup" != "1" ]; then
        log "演示工厂：完成 ERPNext 设置向导..."
        year=$(date +%Y)
        ERP_SITE=demo bench_exec frappe.desk.page.setup_wizard.setup_wizard.initialize_system_settings_and_user --kwargs \
            "{'system_settings_data': {'language': 'en', 'country': 'United States', 'currency': 'USD', 'time_zone': 'America/New_York'}, 'user_data': {}}"
        ERP_SITE=demo bench_exec frappe.desk.page.setup_wizard.setup_wizard.setup_complete --kwargs \
            "{'args': {'language': 'English', 'country': 'United States', 'timezone': 'America/New_York', 'currency': 'USD',
              'company_name': '问渠减速器厂 WenQuest Gearbox', 'company_abbr': 'WQ', 'chart_of_accounts': 'Standard',
              'fy_start_date': '$year-01-01', 'fy_end_date': '$year-12-31', 'setup_demo': 0, 'enable_telemetry': 0}}"
    fi
    dc exec -T erp-backend bench --site demo set-config host_name "https://demo-erp.$domain" >/dev/null
    if [ -z "$(envval WQ_DEMO_ERP_API_KEY)" ]; then
        log "演示工厂：生成 ERPNext 钥匙..."
        keys=$(ERP_SITE=demo bench_exec frappe.core.doctype.user.user.generate_keys --args "['Administrator']" | tail -n 1)
        envset WQ_DEMO_ERP_API_KEY "$(printf '%s' "$keys" | python3 -c 'import json,sys; print(json.load(sys.stdin)["api_key"])')"
        envset WQ_DEMO_ERP_API_SECRET "$(printf '%s' "$keys" | python3 -c 'import json,sys; print(json.load(sys.stdin)["api_secret"])')"
    fi
    dc up -d erp-frontend-demo
    local seedargs=(python seed.py --url http://erp-frontend-demo:8080 --user Administrator --password "$(envval ERP_ADMIN_PASSWORD)"
                    --factory-url "https://demo.$domain")
    if [ "$(envval DEMO_SEEDED)" != 1 ]; then
        log "演示工厂：导入减速器厂数据..."
        local i
        for i in 1 2 3 4 5 6; do
            if dc run --rm seed "${seedargs[@]}" --opening-stock --teach-stock; then envset DEMO_SEEDED 1; break; fi
            log "导入没成功，20 秒后重试（第 $i 次）..."; sleep 20
        done
    fi
    dc run --rm seed "${seedargs[@]}" --erp-sso-only --sso-secret "$(envval WQ_DEMO_ERP_OAUTH_SECRET)" \
        --hub-internal http://wqf-hub-demo:8100 > /tmp/wq-demo-sso.log 2>&1 \
        && log "演示工厂：单点登录已配置。" || { log "警告：演示工厂单点登录没配置成功："; tail -5 /tmp/wq-demo-sso.log; }
    dc up -d hub-demo sim-demo bridge-demo bus-demo        # 钥匙刚生成时让它们带上新配置
}
