# -*- coding: utf-8 -*-
"""数字孪生服务（第 15 轮）：建档、接收现场运行摘要、累加寿命、客户现场模拟器。

- 建档（T1）：跑合试验台发来一台 WQR-105 的转矩记录（test.torque）= 这台出厂，建孪生：序列号、工单、输出轴（按先进先出
  分配一根检验合格的 SH-301，记下它的检测值）、设计版本（输出轴现行参数）、跑合记录。
- 现场数据（T2）：主题 wq/gearbox/field/<序列号>/telemetry，消息 twin.telemetry；模拟器和真设备发的一样。
  没建过档的序列号（真设备先接上来）也收，自动建一个“现场接入”的档。
- 客户现场模拟器：跑在枢纽进程里（要记住每台在哪个客户、出过什么故障），只经总线发数据，和真设备一样。
  现场时钟比真实时间快（默认 1 分钟 = 1 个现场日），30 分钟没人看“数字孪生”页就暂停，免得历史库白白变大。
"""
import datetime as dt
import json
import logging
import os
import random
import threading
import time
import zlib

from psycopg.types.json import Jsonb

from twin import engine as E
from twin import field as F
from twin import models as M
from wqbus.topics import topic

log = logging.getLogger("twin")

SCHEMA = """
create table if not exists twin (
    serial   text not null,
    mode     text not null,
    item     text not null,
    created  timestamptz not null default now(),
    source   text,
    site     text,
    customer text,
    start_day date,
    as_built jsonb not null default '{}',
    state    jsonb not null,
    updated  timestamptz not null default now(),
    primary key (serial, mode)
);
create table if not exists twin_log (
    serial text not null,
    mode   text not null,
    day    date not null,
    data   jsonb not null,
    primary key (serial, mode, day)
);
create table if not exists twin_event (
    id      bigserial primary key,
    serial  text not null,
    mode    text not null,
    ts      timestamptz not null default now(),
    day     date,
    kind    text not null,
    level   text,
    title   text,
    detail  jsonb,
    status  text not null default 'open'
);
create index if not exists twin_event_serial on twin_event (serial, mode, ts);
create table if not exists field_unit (
    serial    text not null,
    mode      text not null,
    site      text not null,
    start_day date not null,
    last_day  date,
    faults    jsonb not null default '[]',
    primary key (serial, mode)
);
create table if not exists field_clock (
    mode        text primary key,
    anchor_real timestamptz not null,
    anchor_day  date not null,
    days_per_min double precision not null default 1,
    last_seen   timestamptz not null default now(),
    paused      boolean not null default false
);
"""

FIELD_MODES = [m for m in os.environ.get("WQ_FIELD_SIM", "teach").split(",") if m]
DAYS_PER_MIN = float(os.environ.get("WQ_FIELD_DAYS_PER_MIN", "1"))
IDLE_MIN = float(os.environ.get("WQ_FIELD_IDLE_MIN", "30"))
MAX_DAYS_PER_TICK = 60
SEED = [   # 情景里已经在用的 12 台：(客户, 出厂距今月数, 故障)
    ("mine", 30, None), ("mine", 22, "bearing"), ("mine", 14, None), ("mine", 5, None),
    ("port", 26, None), ("port", 18, "cooling"), ("port", 10, None), ("port", 3, None),
    ("food", 28, None), ("food", 20, None), ("food", 12, None), ("food", 6, None),
]


def _today():
    return dt.datetime.now(dt.timezone.utc).date()


class TwinService:
    def __init__(self, db, publish):
        self.db = db
        self.publish = publish          # publish(topic, type, source, data, corr, mode)
        self.lock = threading.RLock()
        self.stop = threading.Event()

    def init(self):
        self.db.x(SCHEMA)

    # ------------------------------------------------------------ 消息
    def on_message(self, tp, msg):
        t, d = msg["type"], msg["data"]
        if t == "test.torque" and d.get("item") == "WQR-105":
            self.create_from_runin(msg)
        elif t == "twin.telemetry":
            self.ingest(msg)

    def create_from_runin(self, msg):
        d, mode = msg["data"], msg["mode"]
        with self.lock:
            if self.db.one("select 1 as x from twin where serial=%s and mode=%s", (d["part_serial"], mode)):
                return
            ab = {"work_order": d.get("work_order"), "runin": _runin_summary(d), "runin_samples": d.get("samples_nm"),
                  "runin_rate_hz": d.get("rate_hz"), "runin_ts": msg["ts"], "shaft": self._assign_shaft(mode),
                  "design": self._design(mode)}
            self.db.x("insert into twin (serial, mode, item, source, as_built, state) values (%s,%s,%s,'factory',%s,%s) "
                      "on conflict do nothing", (d["part_serial"], mode, "WQR-105", Jsonb(ab), Jsonb(E.new_state())))
            if mode in FIELD_MODES:
                n = self.db.one("select count(*) as n from field_unit where mode=%s", (mode,))["n"]
                site = ("mine", "port", "food")[n % 3]
                start = self.field_today(mode) + dt.timedelta(days=3)          # 运输、安装 3 天
                self.db.x("insert into field_unit (serial, mode, site, start_day) values (%s,%s,%s,%s) on conflict do nothing",
                          (d["part_serial"], mode, site, start))
                self.db.x("update twin set site=%s, customer=%s, start_day=%s where serial=%s and mode=%s",
                          (site, F.SITES[site]["customer"], start, d["part_serial"], mode))

    def _assign_shaft(self, mode):
        """装配追溯：按先进先出分配一根全部特性合格、还没装过的 SH-301"""
        used = {r["s"] for r in self.db.q("select as_built->'shaft'->>'serial' as s from twin where mode=%s", (mode,)) if r["s"]}
        rows = self.db.messages(["quality.measurement"], mode=mode, order="asc", limit=5000)
        parts = {}
        for m in rows:
            x = m["data"]
            if x.get("item") != "SH-301":
                continue
            p = parts.setdefault(x["part_serial"], {"serial": x["part_serial"], "work_order": x.get("work_order"), "ok": True, "meas": {}})
            p["meas"][x["characteristic"]] = {"name": x.get("name"), "value": x["value_mm"], "lo": x["lower_tol_mm"], "hi": x["upper_tol_mm"]}
            p["ok"] = p["ok"] and x["result"] == "pass"
        for p in parts.values():
            if p["ok"] and p["serial"] not in used:
                return dict(p, how="按先进先出分配的检验合格输出轴")
        return None

    def _design(self, mode):
        try:
            from hub.cam_api import shaft_params
            from hub import plm
            p = shaft_params(self.db, mode)
            rev = plm.current_revision(self.db, mode, "SH-301")
            return {"item": "SH-301", "revision": rev, "segments": [list(x) for x in p["segments"]],
                    "material": p.get("material") or "45-QT"}
        except Exception:  # noqa: BLE001
            return {"item": "SH-301", "revision": None, "segments": [[30, 40], [35, 12], [40, 60], [35, 25], [30, 30]]}

    def ingest(self, msg):
        d, mode = msg["data"], msg["mode"]
        serial = d["serial"]
        with self.lock:
            r = self.db.one("select * from twin where serial=%s and mode=%s", (serial, mode))
            if r is None:
                self.db.x("insert into twin (serial, mode, item, source, site, customer, as_built, state) values "
                          "(%s,%s,%s,'field',%s,%s,%s,%s) on conflict do nothing",
                          (serial, mode, d.get("item") or "WQR-105", d.get("site"), d.get("customer"),
                           Jsonb({"note": "现场先接入、没有出厂档案的设备"}), Jsonb(E.new_state())))
                r = self.db.one("select * from twin where serial=%s and mode=%s", (serial, mode))
            st = r["state"]
            if st.get("last_day") and d["day"] <= st["last_day"]:
                return None                                              # 重复或乱序的旧数据
            design = (r["as_built"] or {}).get("design")
            st, row = E.update(st, d, design)
            self.db.x("insert into twin_log (serial, mode, day, data) values (%s,%s,%s,%s) "
                      "on conflict (serial, mode, day) do update set data=excluded.data", (serial, mode, d["day"], Jsonb(row)))
            self.db.x("update twin set state=%s, updated=now(), site=coalesce(site, %s), customer=coalesce(customer, %s), "
                      "start_day=coalesce(start_day, %s) where serial=%s and mode=%s",
                      (Jsonb(st), d.get("site"), d.get("customer"), st["first_day"], serial, mode))
            return st

    # ------------------------------------------------------------ 现场时钟
    def field_today(self, mode):
        c = self._clock(mode)
        if c["paused"]:
            return c["anchor_day"]
        mins = (dt.datetime.now(dt.timezone.utc) - c["anchor_real"]).total_seconds() / 60
        return c["anchor_day"] + dt.timedelta(days=int(mins * c["days_per_min"]))

    def _clock(self, mode):
        c = self.db.one("select * from field_clock where mode=%s", (mode,))
        if c is None:
            self.db.x("insert into field_clock (mode, anchor_real, anchor_day, days_per_min) values (%s, now(), %s, %s) "
                      "on conflict do nothing", (mode, _today(), DAYS_PER_MIN))
            c = self.db.one("select * from field_clock where mode=%s", (mode,))
        return c

    def touch(self, mode):
        """有人看“数字孪生”页：现场时钟接着走（暂停时从暂停处续上）"""
        c = self._clock(mode)
        if c["paused"] and c["days_per_min"] > 0:            # 老师设成 0（停住）的不自动续
            self.db.x("update field_clock set paused=false, anchor_real=now(), last_seen=now() where mode=%s", (mode,))
        else:
            self.db.x("update field_clock set last_seen=now() where mode=%s", (mode,))

    def set_rate(self, mode, days_per_min):
        today = self.field_today(mode)
        self.db.x("update field_clock set anchor_real=now(), anchor_day=%s, days_per_min=%s, paused=false, last_seen=now() "
                  "where mode=%s", (today, float(days_per_min), mode))

    def _idle_check(self, mode):
        c = self._clock(mode)
        if not c["paused"] and (dt.datetime.now(dt.timezone.utc) - c["last_seen"]).total_seconds() > IDLE_MIN * 60:
            today = self.field_today(mode)
            self.db.x("update field_clock set paused=true, anchor_day=%s where mode=%s", (today, mode))
            log.info("现场时钟暂停（%s）：%s 分钟没人看数字孪生页", mode, IDLE_MIN)

    # ------------------------------------------------------------ 模拟器
    def seed(self, mode):
        """情景里已经在用的 12 台：建档、补发历史运行摘要（按周）"""
        if self.db.one("select 1 as x from field_unit where mode=%s limit 1", (mode,)):
            return 0
        from sim.engine import torque_record
        today = self.field_today(mode)
        n = 0
        for i, (site, months, fault) in enumerate(SEED):
            start = today - dt.timedelta(days=int(months * 30.4))
            serial = "WQR105-H{:%y%m}-{:02d}".format(start, i + 1)
            wo = "MFG-WO-H{:%y%m}".format(start)
            rec = torque_record(serial, wo, "WQR-105")
            ab = {"work_order": wo, "runin": _runin_summary(rec), "runin_samples": rec["samples_nm"], "runin_rate_hz": rec["rate_hz"],
                  "shaft": _seed_shaft(serial, start), "design": {"item": "SH-301", "revision": 1,
                                                                 "segments": [[30, 40], [35, 12], [40, 60], [35, 25], [30, 30]],
                                                                 "material": "45-QT"},
                  "note": "情景数据：实验开始前已经在客户现场运行"}
            faults = []
            if fault == "bearing":
                faults = [{"kind": "bearing", "start": (today - dt.timedelta(days=18)).isoformat()}]
            elif fault == "cooling":
                faults = [{"kind": "cooling", "start": (today - dt.timedelta(days=4)).isoformat()}]
            self.db.x("insert into twin (serial, mode, item, source, site, customer, start_day, as_built, state) values "
                      "(%s,%s,'WQR-105','seed',%s,%s,%s,%s,%s) on conflict do nothing",
                      (serial, mode, site, F.SITES[site]["customer"], start, Jsonb(ab), Jsonb(E.new_state())))
            self.db.x("insert into field_unit (serial, mode, site, start_day, faults) values (%s,%s,%s,%s,%s) on conflict do nothing",
                      (serial, mode, site, start, Jsonb(faults)))
            # 历史：按周补发，最后 14 天按天
            day = start + dt.timedelta(days=6)
            daily_from = today - dt.timedelta(days=14)
            neglect = i == 4                                    # 这一台磨合后换过一次油就再没换过（练“换油到期”）
            while day < daily_from:
                self._emit(mode, serial, site, day, faults, 7)
                self._seed_service(mode, serial, day, neglect)
                n += 1
                day += dt.timedelta(days=7)
            day = day - dt.timedelta(days=6)
            while day < today:
                self._emit(mode, serial, site, day, faults, 1)
                self._seed_service(mode, serial, day, neglect)
                n += 1
                day += dt.timedelta(days=1)
            self.db.x("update field_unit set last_day=%s where serial=%s and mode=%s", (today - dt.timedelta(days=1), serial, mode))
        log.info("数字孪生：已建 %s 台情景设备，补发 %s 条历史运行摘要（%s）", len(SEED), n, mode)
        return n

    def _seed_service(self, mode, serial, day, neglect):
        """情景设备的历史保养：换油到期就换（记一条已完成的维修记录）"""
        st = self.db.one("select state from twin where serial=%s and mode=%s", (serial, mode))["state"]
        if neglect and st.get("oil_first_done"):
            return
        sm = E.summary(st)
        if sm["oil"]["left_h"] <= 0:
            self.db.x("update twin set state=%s where serial=%s and mode=%s", (Jsonb(E.maintain(st, "oil", day.isoformat())), serial, mode))
            self.db.x("insert into twin_event (serial, mode, day, kind, level, title, status, detail) values (%s,%s,%s,'maint','info',%s,'done',%s)",
                      (serial, mode, day, "换油（例行保养）", Jsonb({"action": "oil", "eq_h": round(sm["oil"]["eq_h"])})))

    def _emit(self, mode, serial, site, day, faults, period_days):
        data = F.day_summary(serial, site, day, faults, period_days)
        self.publish(topic("field", serial, "telemetry"), "twin.telemetry", "field-sim/" + site, data, serial, mode)

    def tick(self, mode):
        """现场时钟到了哪天，就把每台缺的日子补上（每次最多 60 天）"""
        self._idle_check(mode)
        today = self.field_today(mode)
        n = 0
        for u in self.db.q("select * from field_unit where mode=%s and start_day < %s", (mode, today)):
            day = max(u["start_day"], (u["last_day"] or u["start_day"] - dt.timedelta(days=1)) + dt.timedelta(days=1))
            k = 0
            while day < today and k < MAX_DAYS_PER_TICK:
                self._emit(mode, u["serial"], u["site"], day, u["faults"], 1)
                self.db.x("update field_unit set last_day=%s where serial=%s and mode=%s", (day, u["serial"], mode))
                day += dt.timedelta(days=1)
                k += 1
                n += 1
        return n

    def run(self, every_s=5.0):
        for mode in FIELD_MODES:
            try:
                self.seed(mode)
            except Exception:  # noqa: BLE001
                log.exception("数字孪生情景建档失败（%s）", mode)
        while not self.stop.wait(every_s):
            for mode in FIELD_MODES:
                try:
                    self.tick(mode)
                except Exception:  # noqa: BLE001
                    log.exception("现场模拟出错（%s）", mode)

    def reset(self, mode, reseed=True):
        """教学情景重置：孪生、现场、日志全部清空，重新建情景设备"""
        with self.lock:
            for t in ("twin", "twin_log", "twin_event", "field_unit", "field_clock"):
                self.db.x("delete from {} where mode=%s".format(t), (mode,))
        if reseed and mode in FIELD_MODES:
            threading.Thread(target=self.seed, args=(mode,), daemon=True).start()


def _runin_summary(d):
    s = d.get("samples_nm") or []
    if not s:
        return {}
    run = [v for v in s if v > 0.3 * (d.get("rated_nm") or M.RATED_T_NM)]
    return {"peak_nm": round(max(s), 1), "mean_run_nm": round(sum(run) / len(run), 1) if run else None,
            "duration_s": d.get("duration_s"), "program": d.get("program"), "rated_nm": d.get("rated_nm")}


def _seed_shaft(serial, start):
    from sim.errors import CHARS
    r = random.Random(zlib.crc32(serial.encode()))
    meas = {}
    for code, name, nom, lo, hi in CHARS:
        v = min(hi, max(lo, nom + r.gauss(0, (hi - lo) / 10)))
        meas[code] = {"name": name, "value": round(v, 4), "lo": lo, "hi": hi}
    return {"serial": serial.replace("WQR105", "SH301"), "work_order": "MFG-WO-S{:%y%m}".format(start), "ok": True, "meas": meas,
            "how": "情景数据"}


def fleet(db, mode):
    out = []
    for r in db.q("select serial, item, source, site, customer, start_day, state, created from twin where mode=%s order by serial", (mode,)):
        sm = E.summary(r["state"])
        out.append({"serial": r["serial"], "item": r["item"], "source": r["source"], "site": r["site"], "customer": r["customer"],
                    "start_day": r["start_day"].isoformat() if r["start_day"] else None, "run_h": r["state"]["run_h"],
                    "last": r["state"].get("last"), "summary": sm})
    return out


def detail(db, mode, serial, days=400):
    r = db.one("select * from twin where serial=%s and mode=%s", (serial, mode))
    if r is None:
        return None
    logs = db.q("select day, data from twin_log where serial=%s and mode=%s order by day desc limit %s", (serial, mode, days))
    ab = dict(r["as_built"] or {})
    ab.pop("runin_samples", None)
    return {"serial": serial, "item": r["item"], "source": r["source"], "site": r["site"], "customer": r["customer"],
            "start_day": r["start_day"].isoformat() if r["start_day"] else None, "as_built": ab, "state": r["state"],
            "summary": E.summary(r["state"]), "log": [x["data"] for x in reversed(logs)],
            "events": [dict(e, ts=e["ts"].isoformat(), day=e["day"].isoformat() if e["day"] else None)
                       for e in db.q("select * from twin_event where serial=%s and mode=%s order by ts desc limit 50", (serial, mode))]}


def json_safe(x):
    return json.loads(json.dumps(x, default=str))
