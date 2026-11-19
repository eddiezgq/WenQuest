# -*- coding: utf-8 -*-
"""历史库（PostgreSQL）。bus_message 存总线上的每一条消息；其余几张小表存状态变化、
AI 提议、教学任务得分和 FreeCAD 上传的文件。"""
import datetime as dt
import json
import logging
import os
import re
import threading
import time

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
-- 第 173 轮：轮询用得上的索引（以前按 mode、seq、ts、corr/source 前缀查都全表扫，教育服务器的数据库一直占 1.4 个核）
create index if not exists bus_message_mode_seq on bus_message (mode, seq);
create index if not exists bus_message_type_mode_seq on bus_message (type, mode, seq);
create index if not exists bus_message_ts on bus_message (ts);
create index if not exists bus_message_mode_type_corr on bus_message (mode, type, corr text_pattern_ops);
create index if not exists bus_message_mode_source on bus_message (mode, source text_pattern_ops);
-- 第 173b 轮：ERPNext 单据快照（erp_docs）按单据类型、厂取每个单号最新一条，以前每次把全部 erp.doc 排一遍序
create index if not exists bus_message_erp_doc on bus_message ((payload->'data'->>'doctype'), mode, (payload->'data'->>'name'), ts desc, seq desc)
    where valid and type = 'erp.doc';

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
-- 第 88 轮：电路板厂功能测试台的复测记录（写进这块板的单件档案，不改车间原始测量值）
create table if not exists fct_retest (
    id         bigserial primary key,
    ts         timestamptz not null default now(),
    mode       text not null,
    user_name  text not null,
    serial     text not null,
    item       text,
    readings   jsonb not null,
    verdict    text not null,
    check_rows jsonb
);
create index if not exists fct_retest_serial on fct_retest (serial);

create table if not exists stored_file (
    sha256     text primary key,
    name       text not null,
    mime       text,
    size       integer,
    content    bytea not null,
    created_at timestamptz not null default now()
);

-- 企业版第一期（第 8 轮）：设计提交与审批、批注、登录过的人、企业成员
create table if not exists design_submission (
    id          text primary key,
    mode        text not null,
    item        text not null,
    status      text not null,             -- pending 待审 / approved 已批准 / rejected 退回 / withdrawn 撤回
    author      text not null,
    author_uid  text,
    ts          timestamptz not null default now(),
    note        text,
    files       jsonb not null,             -- [{kind: step|glb|drawing|gcode|diff, name, url, sha256, size}]
    gcode       jsonb,                      -- {operation, machine, url, sha256, ...}
    params      jsonb,
    base_rev    integer,                    -- 提交时的现行版本
    revision    integer,                    -- 批准后的版本号
    diff        jsonb,                      -- 与现行版的差异统计
    decided_by  text,
    decided_at  timestamptz,
    decision    text
);
create index if not exists design_submission_item on design_submission (mode, item, ts desc);
create table if not exists design_comment (
    id          bigserial primary key,
    sub_id      text not null,
    author      text not null,
    ts          timestamptz not null default now(),
    body        text not null,
    anchor      jsonb,                      -- 三维模型上的点 {x, y, z}（mm），没有就是整体意见
    resolved    boolean not null default false
);
create index if not exists design_comment_sub on design_comment (sub_id, id);
-- 工艺规程（第 13 轮）：与设计提交并列；批注沿用 design_comment（sub_id 前加 P）
create table if not exists process_submission (
    id          text primary key,
    mode        text not null,
    item        text not null,
    status      text not null,
    author      text not null,
    author_uid  text,
    ts          timestamptz not null default now(),
    note        text,
    plan        jsonb not null,
    review      jsonb,
    revision    integer,
    decided_by  text,
    decided_at  timestamptz,
    decision    text
);
create index if not exists process_submission_item on process_submission (mode, item, ts desc);
-- 第 128 轮（阶段 C1）：在页面上改工艺卡——每人每个零件一份草稿（工艺规程数据），提交后仍走 process_submission
create table if not exists process_draft (
    mode        text not null,
    uid         text not null,
    item        text not null,
    plan        jsonb not null,
    ts          timestamptz not null default now(),
    primary key (mode, uid, item)
);
-- 问题情景与 8D 质量异常单（第 13 轮：hub/qproblem.py）
create table if not exists quality_problem (
    id          serial primary key,
    mode        text not null,
    problem     text not null,
    magnitude   double precision,
    injected_by text,
    injected_at timestamptz not null default now(),
    cleared_at  timestamptz,
    cleared_how text
);
create table if not exists quality_8d (
    id          text primary key,
    mode        text not null,
    item        text not null,
    characteristic text,
    title       text not null,
    status      text not null,
    author      text not null,
    author_uid  text,
    created_at  timestamptz not null default now(),
    updated_at  timestamptz not null default now(),
    d           jsonb not null default '{}'::jsonb,
    fix         text,
    fix_by      text,
    fix_at      timestamptz,
    verify      jsonb,
    closed_at   timestamptz
);
create table if not exists known_user (
    uid         text primary key,
    name        text not null,
    teacher     boolean not null default false,
    last_seen   timestamptz not null default now()
);
-- 工程任务单（第 11 轮《机械设计》2.7（5））：学习平台下达，学生在“我的任务”提交，AI 设计评审员出意见，老师批准、评分；
-- 批注沿用 design_comment（sub_id 前加 T），多两列：level（AI 意见的级别）、reply（学生的回复）
create table if not exists task_sheet (
    id          text primary key,
    code        text not null,              -- TS-33-1
    book        text,
    no          text,                       -- 33.1
    spec        jsonb not null,             -- 任务单说明文件的内容（教材构建时生成）
    course_id   integer not null,
    course_name text,
    cmid        integer,                    -- 学习平台课程里对应的作业（成绩回传用）
    due         timestamptz,
    issued_by   text,
    issued_at   timestamptz not null default now(),
    status      text not null default 'open',
    unique (code, course_id)
);
create table if not exists task_submission (
    id           text primary key,
    task_id      text not null references task_sheet (id),
    author       text not null,
    author_uid   text not null,
    status       text not null default 'draft',   -- draft / submitted / returned / approved / graded
    deliverables jsonb not null default '{}'::jsonb,
    review       jsonb,
    submitted_at timestamptz,
    rounds       integer not null default 0,
    decided_by   text,
    decided_at   timestamptz,
    decision     text,
    score        jsonb,
    pushed_at    timestamptz,
    updated_at   timestamptz not null default now(),
    unique (task_id, author_uid)
);
alter table design_comment add column if not exists level text;
alter table design_comment add column if not exists reply text;
create table if not exists enterprise_member (
    uid         text primary key,
    roles       text[] not null,
    added_by    text,
    added_at    timestamptz not null default now()
);
"""


_DDL = re.compile(r"\s*(?:--[^\n]*\n\s*)*(create\s+(?:unique\s+)?(?:table|index)|alter\s+table|drop\s+index)", re.I)


def _split_sql(sql):
    """按分号把一段 SQL 拆成句子；单引号字符串、$$ 函数体、-- 注释里的分号不算（第 173 轮）"""
    out, cur, i, n = [], [], 0, len(sql)
    while i < n:
        c = sql[i]
        if c == "-" and sql.startswith("--", i):
            j = sql.find("\n", i)
            j = n if j < 0 else j
            cur.append(sql[i:j]); i = j
        elif c == "'":
            j = i + 1
            while j < n:
                if sql[j] == "'" and not sql.startswith("''", j):
                    break
                j += 2 if sql.startswith("''", j) else 1
            cur.append(sql[i:j + 1]); i = j + 1
        elif c == "$":
            m = re.match(r"\$[A-Za-z_]*\$", sql[i:])
            if m:
                tag = m.group(0)
                j = sql.find(tag, i + len(tag))
                j = n if j < 0 else j + len(tag)
                cur.append(sql[i:j]); i = j
            else:
                cur.append(c); i += 1
        elif c == ";":
            out.append("".join(cur)); cur = []; i += 1
        else:
            cur.append(c); i += 1
    out.append("".join(cur))
    return out


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
        self.ddl(SCHEMA)

    # 第 173 轮：建表、加索引、改表限时。11-17 枢纽启动时 alter table 等每天备份（pg_dump 对所有表持共享锁）放锁，等了 35 分钟，
    # 网站 502。现在每一句最多等 DDL_WAIT；等不到就跳过这一句（下次启动再做），之后的改表句只等一下，不再卡住启动。
    DDL_WAIT, DDL_WAIT_AFTER = "5s", "200ms"
    _ddl_blocked = False

    def ddl(self, sql):
        """执行一段建表 / 改表语句（可含多句）；拿不到锁的句子跳过并记日志，返回跳过的句数"""
        skipped = 0
        stmts = []
        for s_ in _split_sql(sql):
            body = "\n".join(ln for ln in s_.strip().splitlines() if not ln.strip().startswith("--")).strip()
            if body:
                stmts.append(body)
        with self.conn().cursor() as cur:
            for st in stmts:
                try:
                    cur.execute("set lock_timeout = '{}'".format(self.DDL_WAIT_AFTER if DB._ddl_blocked else self.DDL_WAIT))
                    cur.execute(st)
                except psycopg.errors.LockNotAvailable:
                    DB._ddl_blocked = True
                    skipped += 1
                    logging.getLogger("wq.db").warning("表正被占用（多半是每天的备份），先跳过，下次启动再做：%s", st.split("\n")[0][:120])
                finally:
                    cur.execute("set lock_timeout = 0")
        return skipped

    def q(self, sql, args=None):
        with self.conn().cursor() as cur:
            cur.execute(sql, args)
            return cur.fetchall() if cur.description else []

    def one(self, sql, args=None):
        rows = self.q(sql, args)
        return rows[0] if rows else None

    def x(self, sql, args=None):
        if args is None and _DDL.match(sql):                 # 各模块的建表、改表语句都走限时
            return self.ddl(sql)
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


def prune_ont_events(db, days, batch=20000, pause=0.2):
    """删 ts 早于 days 天的本体事件。ont_event 只有按对象的索引，按时间删会全表扫（主厂 3880 万行）：
    事件按时间先后写入，主键大致随时间增长，先在主键上二分找截止处，再按主键分批删（每批再核对 ts，保险）。返回删掉的条数。"""
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
    r = db.one("select min(id) as lo, max(id) as hi from ont_event")
    if not r or r["lo"] is None:
        return 0
    lo, hi = r["lo"], r["hi"]
    first = db.one("select ts from ont_event where id >= %s order by id limit 1", (lo,))
    if not first or first["ts"] >= cutoff:
        return 0
    while hi - lo > batch:                       # 找最后一个早于截止时间的大致位置
        mid = (lo + hi) // 2
        m = db.one("select ts from ont_event where id >= %s order by id limit 1", (mid,))
        if m and m["ts"] < cutoff:
            lo = mid
        else:
            hi = mid
    end, start, n = hi, r["lo"], 0
    while start <= end:
        n += db.x("delete from ont_event where id >= %s and id < %s and ts < %s", (start, start + batch, cutoff))
        start += batch
        time.sleep(pause)
    logging.getLogger("wq.db").info("本体事件已清理 %s 天以前的 %s 条", int(days), n)
    return n
