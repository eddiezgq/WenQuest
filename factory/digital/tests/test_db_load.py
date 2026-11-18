# -*- coding: utf-8 -*-
"""第 173 轮：教育服务器减负——改表限时（备份锁着表时枢纽照样起来）、轮询走索引、本体事件只留 30 天。"""
import datetime as dt
import os
import time

import pytest

DSN = os.environ.get("WQ_DB", "postgresql://postgres@localhost:5433/wq_factory").rsplit("/", 1)[0] + "/wq_load_test"


@pytest.fixture(scope="module")
def db():
    psycopg = pytest.importorskip("psycopg")
    try:
        with psycopg.connect(DSN.rsplit("/", 1)[0] + "/postgres", autocommit=True) as c:
            c.execute("drop database if exists wq_load_test with (force)")
            c.execute("create database wq_load_test")
    except Exception:  # noqa: BLE001
        pytest.skip("没有可用的 PostgreSQL")
    from hub.db import DB
    d = DB(DSN)
    d.init()
    return d


def test_startup_does_not_wait_for_backup_locks(db):
    """另一个连接像 pg_dump 那样对所有表持共享锁：建表、加索引照做，改表句跳过，几秒内起来"""
    import psycopg
    from hub.db import DB
    c2 = psycopg.connect(DSN)
    cur = c2.cursor()
    cur.execute("select string_agg(quote_ident(tablename), ',') from pg_tables where schemaname='public'")
    cur.execute("lock table {} in access share mode".format(cur.fetchone()[0]))
    try:
        DB._ddl_blocked = False
        t = time.time()
        d2 = DB(DSN)
        d2.init()
        n = d2.x("alter table bus_message add column if not exists zz_test int;\ncreate table if not exists zz_new (a int);")
        assert time.time() - t < 15
        assert n == 1 and d2.one("select to_regclass('zz_new') as r")["r"]
    finally:
        c2.rollback()
        c2.close()
        DB._ddl_blocked = False


def test_polling_queries_use_indexes(db):
    db.x("insert into bus_message (id, ts, topic, type, source, mode, corr, payload) "
         "select gen_random_uuid(), now() - (g || ' seconds')::interval, 'wq/x/' || (g % 40), "
         "(array['machine.event','machine.status','quality.measurement','erp.doc'])[1 + g % 4], 'sim', "
         "case when g % 5 = 0 then 'prod' else 'teach' end, case when g % 3 = 0 then 'MFG-WO-' || g else 'X' end, '{}'::jsonb "
         "from generate_series(1, 30000) g")
    db.x("analyze bus_message")
    for q in ("select max(seq) as s from bus_message where mode='teach'",
              "select seq from bus_message where type='machine.event' and mode='teach' and seq > 29000 order by seq",
              "select corr from bus_message where type='machine.event' and mode='teach' and corr like 'MFG-WO-%' order by seq desc limit 1"):
        plan = " ".join(r["QUERY PLAN"] for r in db.q("explain " + q))
        assert "Seq Scan on bus_message" not in plan, (q, plan)


def test_ont_events_older_than_30_days_are_pruned(db):
    from hub.db import prune_ont_events
    from hub.ont.store import Store
    Store(db).init()
    now = dt.datetime.now(dt.timezone.utc)
    db.x("insert into ont_event (mode, type, key, ts, kind) select 'teach', 'Machine', 'm' || g, %s + (g || ' hours')::interval, 'state' "
         "from generate_series(0, 24 * 60) g", (now - dt.timedelta(days=60),))
    n = prune_ont_events(db, 30, batch=100, pause=0)
    left = db.one("select count(*) as n, min(ts) as t from ont_event")
    assert n > 0 and left["t"] >= now - dt.timedelta(days=30, minutes=5)
    assert left["n"] >= 24 * 29                                         # 30 天以内的都在
