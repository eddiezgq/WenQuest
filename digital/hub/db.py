# -*- coding: utf-8 -*-
"""历史库（PostgreSQL）。bus_message 存总线上的每一条消息；其余几张小表存状态变化、
AI 提议、教学任务得分和 FreeCAD 上传的文件。"""
import json
import os
import threading

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

DSN = os.environ.get("WQ_DB", "postgresql://postgres@localhost:5433/wq_factory")

SCHEMA = """
create table if not exists bus_message (
    seq         bigserial primary key,
    id          uuid unique,
    ts          timestamptz not null,
    topic       text not null,
    type        text,
    source      text,
    mode        text,
    corr        text,
    payload     jsonb not null,
    valid       boolean not null default true,
    received_at timestamptz not null default now()
);
create index if not exists bus_message_type_ts on bus_message (type, ts);
create index if not exists bus_message_topic_ts on bus_message (topic, ts);
create index if not exists bus_message_corr on bus_message (corr);

-- 设备状态变化（从 machine.status 提取，只记变化点），算 OEE 用
create table if not exists machine_state_log (
    unit  text not null,
    ts    timestamptz not null,
    state text not null,
    mode  text,
    primary key (unit, ts)
);

create table if not exists ai_proposal (
    proposal_id  text primary key,
    created_at   timestamptz not null default now(),
    mode         text not null,
    action       text not null,
    title        text,
    preview      jsonb not null,
    status       text not null default 'pending',   -- pending / confirmed / rejected / executed / failed
    requested_by text,
    confirmed_by text,
    decided_at   timestamptz,
    result       jsonb
);

create table if not exists ncr (
    ncr_id      text primary key,
    created_at  timestamptz not null,
    part_serial text not null,
    item        text,
    work_order  text,
    detail      jsonb,
    status      text not null default 'open',       -- open / rework / scrap / use_as_is
    decided_by  text,
    decided_at  timestamptz,
    mode        text
);

create table if not exists task_result (
    user_name  text not null,
    task_id    text not null,
    score      integer not null,
    done_at    timestamptz not null default now(),
    evidence   jsonb,
    primary key (user_name, task_id)
);

create table if not exists stored_file (
    sha256     text primary key,
    name       text not null,
    mime       text,
    size       integer,
    content    bytea not null,
    created_at timestamptz not null default now()
);
"""


class DB:
    def __init__(self, dsn=DSN):
        self.dsn = dsn
        self._local = threading.local()

    def conn(self):
        c = getattr(self._local, "c", None)
        if c is None or c.closed:
            c = psycopg.connect(self.dsn, autocommit=True, row_factory=dict_row)
            self._local.c = c
        return c

    def init(self):
        with self.conn().cursor() as cur:
            cur.execute(SCHEMA)

    def q(self, sql, args=None):
        with self.conn().cursor() as cur:
            cur.execute(sql, args)
            return cur.fetchall() if cur.description else []

    def one(self, sql, args=None):
        rows = self.q(sql, args)
        return rows[0] if rows else None

    def x(self, sql, args=None):
        with self.conn().cursor() as cur:
            cur.execute(sql, args)
            return cur.rowcount

    # ------------------------------------------------------------ 消息
    def insert_message(self, topic, msg, valid=True):
        """返回 True 表示新消息（id 未见过）。"""
        n = self.x(
            "insert into bus_message (id, ts, topic, type, source, mode, corr, payload, valid) "
            "values (%s,%s,%s,%s,%s,%s,%s,%s,%s) on conflict (id) do nothing",
            (msg.get("id"), msg.get("ts"), topic, msg.get("type"), msg.get("source"), msg.get("mode"),
             msg.get("corr"), Jsonb(msg), valid))
        return n == 1

    def insert_invalid(self, topic, raw, reason):
        try:
            body = json.loads(raw)
        except Exception:  # noqa: BLE001
            body = {"raw": raw.decode("utf-8", "replace") if isinstance(raw, bytes) else str(raw)}
        self.x("insert into bus_message (id, ts, topic, type, source, mode, corr, payload, valid) "
               "values (gen_random_uuid(), now(), %s, null, %s, %s, null, %s, false)",
               (topic, body.get("source") if isinstance(body, dict) else None,
                body.get("mode") if isinstance(body, dict) else None, Jsonb({"invalid": reason, "body": body})))

    def messages(self, types=None, since=None, until=None, mode=None, topic_like=None, corr=None,
                 limit=None, order="asc"):
        where, args = ["valid"], []
        if types:
            where.append("type = any(%s)")
            args.append(list(types))
        if since is not None:
            where.append("ts >= %s")
            args.append(since)
        if until is not None:
            where.append("ts <= %s")
            args.append(until)
        if mode:
            where.append("mode = %s")
            args.append(mode)
        if topic_like:
            where.append("topic like %s")
            args.append(topic_like)
        if corr:
            where.append("corr = %s")
            args.append(corr)
        sql = "select seq, topic, payload from bus_message where {} order by ts {}, seq {}".format(
            " and ".join(where), order, order)
        if limit:
            sql += " limit %d" % int(limit)
        return [dict(r["payload"], _topic=r["topic"], _seq=r["seq"]) for r in self.q(sql, args)]

    def latest_per_topic(self, types, mode=None, topic_like=None):
        where, args = ["valid", "type = any(%s)"], [list(types)]
        if mode:
            where.append("mode = %s")
            args.append(mode)
        if topic_like:
            where.append("topic like %s")
            args.append(topic_like)
        sql = ("select distinct on (topic) topic, payload from bus_message where {} "
               "order by topic, ts desc, seq desc").format(" and ".join(where))
        return {r["topic"]: r["payload"] for r in self.q(sql, args)}

    def erp_docs(self, doctype, mode=None):
        """ERPNext 单据的最新快照：每个单号取最后一条 erp.doc。"""
        where, args = ["valid", "type = 'erp.doc'", "payload->'data'->>'doctype' = %s",
                       "payload->'data'->>'action' <> 'failed'"], [doctype]
        if mode:
            where.append("mode = %s")
            args.append(mode)
        sql = ("select distinct on (payload->'data'->>'name') payload from bus_message where {} "
               "order by payload->'data'->>'name', ts desc, seq desc").format(" and ".join(where))
        return [r["payload"] for r in self.q(sql, args)]
