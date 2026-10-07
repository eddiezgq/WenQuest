# -*- coding: utf-8 -*-
"""第 17 轮 B 期：20 条规则逐条“该报 / 不该报”（不用数据库：假数据 + 假看板）。"""
import datetime as dt
import itertools

import pytest

from hub.ont import anomaly as A
from hub.ont import rules as R

NOW = dt.datetime(2026, 10, 20, 18, 0, tzinfo=dt.timezone.utc)      # 纽约 14:00
_seq = itertools.count(1)


def msg(type_, topic, data, ts, corr=None):
    return {"type": type_, "_topic": topic, "data": data, "ts": ts.isoformat(), "id": "m{}".format(next(_seq)), "_seq": next(_seq),
            "corr": corr}


class FakeDB:
    def __init__(self, msgs=(), docs=None, tables=None):
        self.msgs, self.docs, self.tables = list(msgs), docs or {}, tables or []

    def messages(self, types=None, since=None, until=None, mode=None, topic_like=None, corr=None, limit=None, order="asc"):
        def t(x):
            return dt.datetime.fromisoformat(x) if isinstance(x, str) else x
        out = [m for m in self.msgs if (not types or m["type"] in types) and (since is None or t(m["ts"]) >= t(since))
               and (until is None or t(m["ts"]) <= t(until)) and (corr is None or m.get("corr") == corr)]
        out.sort(key=lambda m: (m["ts"], m["_seq"]), reverse=order == "desc")
        return out[:limit] if limit else out

    def erp_docs(self, doctype, mode=None):
        return [{"data": d, "id": "d" + d["name"], "_seq": 1, "_topic": "wq/gearbox/office/erp/x"} for d in self.docs.get(doctype, [])]

    def q(self, sql, args=None):
        for pat, fn in self.tables:
            if pat in sql:
                return fn(args)
        raise AssertionError("没想到的查询：" + sql)

    def one(self, sql, args=None):
        r = self.q(sql, args)
        return r[0] if r else None


def run(rid, db=None, ov=None, params=None, now=NOW):
    cat = A.load_catalog()
    r = cat[rid]
    c = A.Ctx(db or FakeDB(), "teach", now)
    if ov is not None:
        c._c["ov"] = ov
    p = dict(r["params"], **(params or {}))
    return R.REG[r["fn"]](c, p, r)


def mach(unit, state="run", **k):
    return dict({"unit": unit, "code": unit.upper(), "state": state, "reason": None, "down_until_s": None, "queue": 0,
                 "bottleneck": False, "tool_life_left": 0.8, "ts": NOW.isoformat()}, **k)


# ---------------------------------------------------------------- 生产
def test_P1_down():
    ov = {"machines": [mach("cnc-l01-b", "fault", reason="主轴报警", down_until_s=600, queue=3), mach("grd-01")]}
    f = run("P1", ov=ov)
    assert [x.fkey for x in f] == ["cnc-l01-b"] and f[0].severity == "critical"
    assert run("P1", ov={"machines": [mach("grd-01")]}) == []


def test_P2_tool_life():
    assert [x.fkey for x in run("P2", ov={"machines": [mach("grd-01", tool_life_left=0.1)]})] == ["grd-01"]
    assert run("P2", ov={"machines": [mach("grd-01", "down", tool_life_left=0.1), mach("saw-01", "idle", tool_life_left=0.05)]}) == []


def test_P3_oee():
    m = {"cnc-l01-a": {"oee": 0.45, "availability": 0.5, "performance": 0.95, "quality": 1.0, "run_s": 9000, "setup_s": 900, "down_s": 5000},
         "saw-01": {"oee": 0.40, "availability": 0.4, "performance": 1, "quality": 1, "run_s": 1000, "setup_s": 0, "down_s": 0},
         "grd-01": {"oee": 0.8, "availability": 0.9, "performance": 0.9, "quality": 1, "run_s": 20000, "setup_s": 0, "down_s": 0}}
    f = run("P3", ov={"oee": {"machines": m}})
    assert [x.fkey for x in f] == ["cnc-l01-a"] and "停机和调整多" in f[0].detail     # saw-01 负荷不足 2 小时，不报


def test_P4_tool_change_rate():
    tc = lambda u, h: msg("machine.event", "wq/gearbox/machining/{}/event".format(u), {"event": "tool_change"}, NOW - dt.timedelta(hours=h))
    evs = [tc("cnc-l01-a", h) for h in (1, 2, 3)] + [tc("cnc-l01-a", 30)] + [tc("key-01", h) for h in (1, 2, 3)] + \
          [tc("key-01", 24 * d) for d in range(1, 7) for _ in range(2)]
    f = run("P4", db=FakeDB(evs))
    assert [x.fkey for x in f] == ["cnc-l01-a"]                       # key-01 平时每天 2 次，今天 3 次不算异常


def test_P5_backlog():
    assert [x.fkey for x in run("P5", ov={"machines": [mach("grd-01", queue=8, bottleneck=True)]})] == ["grd-01"]
    assert run("P5", ov={"machines": [mach("grd-01", queue=5, bottleneck=True), mach("saw-01", queue=9)]}) == []


# ---------------------------------------------------------------- 质量
def meas(char, vals, start=NOW - dt.timedelta(hours=20)):
    from sim.errors import CHARS
    _, name, nom, lo, hi = next(c for c in CHARS if c[0] == char)
    return [msg("quality.measurement", "wq/gearbox/quality/qc-01/measurement",
                {"part_serial": "SH301-T-{:03d}".format(i), "item": "SH-301", "characteristic": char, "name": name, "nominal_mm": nom,
                 "lower_tol_mm": lo, "upper_tol_mm": hi, "value_mm": v, "result": "pass" if lo <= v <= hi else "fail"},
                start + dt.timedelta(minutes=10 * i)) for i, v in enumerate(vals)]


def test_Q1_spc():
    import random
    rnd = random.Random(1)
    stable = [35.010 + rnd.gauss(0, 0.0008) for _ in range(60)]
    f = run("Q1", db=FakeDB(meas("bearing_seat_d35", stable + [35.010 + 0.0045 + rnd.gauss(0, 0.0003) for _ in range(10)])))
    assert [x.values["characteristic"] for x in f] == ["bearing_seat_d35"] and 1 in f[0].values["rules"] and f[0].severity == "critical"
    assert run("Q1", db=FakeDB(meas("bearing_seat_d35", stable))) == []


def test_Q2_near_limit():
    ch = {"points": [{"id": i} for i in range(6)], "upper": 35.018, "lower": 35.002, "margin_um": 2.0, "shift_um": 6.0,
          "characteristic": "bearing_seat_d35", "title": "Ø35", "mean_last5": 35.016, "src": "t"}
    assert len(run("Q2", ov={"quality": {"chart": ch}})) == 1
    assert run("Q2", ov={"quality": {"chart": dict(ch, margin_um=6.0)}}) == []


def test_Q3_ncr_escalates_after_2h():
    n = lambda h: {"ncr_id": "NCR-1", "part_serial": "SH301-1", "detail": {"name": "Ø35"}, "created_at": (NOW - dt.timedelta(hours=h)).isoformat()}
    assert run("Q3", ov={"quality": {"ncr": [n(1)]}})[0].severity == "warn"
    assert run("Q3", ov={"quality": {"ncr": [n(3)]}})[0].severity == "critical"
    assert run("Q3", ov={"quality": {"ncr": []}}) == []


def test_Q4_fpy():
    vals = [35.010] * 18 + [35.020, 35.021]                          # 20 件里 2 件超差：90%
    f = run("Q4", db=FakeDB(meas("bearing_seat_d35", vals)))
    assert len(f) == 1 and f[0].values["fpy"] == 0.9 and len(f[0].values["bad"]) == 2
    assert run("Q4", db=FakeDB(meas("bearing_seat_d35", [35.010] * 20))) == []
    assert run("Q4", db=FakeDB(meas("bearing_seat_d35", [35.010] * 5 + [35.020]))) == []     # 不够 10 件


def test_Q5_8d_stale():
    rows = [{"id": "Q8D-1", "title": "a", "status": "D4", "created_at": NOW - dt.timedelta(days=9), "item": "SH-301"},
            {"id": "Q8D-2", "title": "b", "status": "D2", "created_at": NOW - dt.timedelta(days=2), "item": "SH-301"}]
    assert [x.fkey for x in run("Q5", db=FakeDB(tables=[("quality_8d", lambda a: rows)]))] == ["Q8D-1"]


# ---------------------------------------------------------------- 销售、计划、供应
def order(name, tone, delivery, projected):
    return {"name": name, "tone": tone, "risk": "预计晚", "customer": "峰顶 Peak", "qty": 10, "delivery_date": delivery,
            "projected": projected, "work_orders": "WO-1", "short": None}


def test_S1_order_late():
    f = run("S1", ov={"orders": [order("SO-1", "bad", "2026-10-20", "2026-10-21"), order("SO-2", "bad", "2026-10-20", "2026-10-25"),
                                 order("SO-3", "warn", "2026-10-20", "2026-10-20")]})
    assert {x.fkey: x.severity for x in f} == {"SO-1": "warn", "SO-2": "critical"}


def test_S2_wo_overdue():
    docs = {"Work Order": [{"name": "WO-1", "expected_delivery_date": "2026-10-18", "status": "In Process", "qty": 10, "production_item": "SH-301"},
                           {"name": "WO-2", "expected_delivery_date": "2026-10-18", "status": "Completed", "qty": 10},
                           {"name": "WO-3", "expected_delivery_date": "2026-10-25", "status": "In Process", "qty": 10},
                           {"name": "WO-4", "expected_delivery_date": "2026-10-01", "status": "In Process", "qty": 10, "demo": True}]}
    f = run("S2", db=FakeDB(docs=docs))
    assert [x.fkey for x in f] == ["WO-1"] and f[0].values["days"] == 2


def test_W1_stock():
    mt = lambda c, tone: {"code": c, "tone": tone, "status": "低于安全库存", "name": c, "qty_text": "8", "safety": 10, "need": 20, "qty": 8}
    assert [x.fkey for x in run("W1", ov={"materials": [mt("BRG-6207", "bad"), mt("RM-1", "good")]})] == ["BRG-6207"]


def test_W2_po_late():
    docs = {"Purchase Order": [
        {"name": "PO-1", "supplier": "洛轴", "status": "To Receive and Bill",
         "items": [{"item_code": "BRG-6207", "qty": 20, "received_qty": 0, "schedule_date": "2026-10-15"}]},
        {"name": "PO-2", "supplier": "洛轴", "status": "To Receive and Bill",
         "items": [{"item_code": "BRG-6207", "qty": 20, "received_qty": 20, "schedule_date": "2026-10-15"}]},
        {"name": "PO-3", "supplier": "洛轴", "status": "To Receive and Bill",
         "items": [{"item_code": "BRG-6207", "qty": 20, "received_qty": 0, "schedule_date": "2026-10-28"}]}]}
    f = run("W2", db=FakeDB(docs=docs))
    assert [x.fkey for x in f] == ["PO-1"] and ("Supplier", "洛轴") in f[0].about


# ---------------------------------------------------------------- 服务
def unit(serial, health, customer="港口 Port", kind="bearing"):
    return {"serial": serial, "health": health, "customer": customer, "site": "port",
            "alerts": [{"title": "中间轴轴承 B 损伤加快", "level": health, "kind": kind}] if health != "green" else []}


def test_V1_field_alarm(monkeypatch):
    from hub import twin as TW
    monkeypatch.setattr(TW, "fleet", lambda db, mode: [unit("U1", "red"), unit("U2", "yellow"), unit("U3", "green")])
    f = run("V1")
    assert {x.fkey: x.severity for x in f} == {"U1": "critical", "U2": "warn"}


def test_V2_same_batch(monkeypatch):
    from hub import twin as TW
    shaft = {"U1": "S1", "U2": "S2", "U3": "S3"}
    wheel = {"S1": "grd-01/3", "S2": "grd-01/3", "S3": "grd-01/4"}
    wo = {"S1": "WO-A", "S2": "WO-B", "S3": "WO-B"}
    db = FakeDB(tables=[("PartSerial.installed_in", lambda a: [{"src_key": shaft[a[1]]}] if a[1] in shaft else []),
                        ("PartSerial.processed", lambda a: [{"props": {"tool": wheel[a[1]], "machine": "grd-01"}}]),
                        ("type='PartSerial' and key", lambda a: [{"wo": wo[a[1]]}])])
    monkeypatch.setattr(TW, "fleet", lambda d, mode: [unit("U1", "red"), unit("U2", "yellow"), unit("U3", "green")])
    f = run("V2", db=db)
    assert [(x.subject, x.values["units"]) for x in f] == [(("Tool", "grd-01/3"), ["U1", "U2"])]
    monkeypatch.setattr(TW, "fleet", lambda d, mode: [unit("U1", "red"), unit("U2", "green")])
    assert run("V2", db=db) == []
    monkeypatch.setattr(TW, "fleet", lambda d, mode: [unit("U1", "red"), unit("U2", "yellow", kind="oil")])
    assert run("V2", db=db) == []                                    # 换油过期与批次无关


def test_V3_service_overdue():
    clock = [{"paused": True, "anchor_day": dt.date(2027, 3, 10), "anchor_real": NOW, "days_per_min": 1}]
    ev = [{"id": 1, "serial": "U1", "day": dt.date(2027, 3, 1), "title": "换轴承", "status": "ordered", "detail": {"issue": "ISS-1"}},
          {"id": 2, "serial": "U2", "day": dt.date(2027, 3, 8), "title": "换油", "status": "ordered", "detail": {"issue": "ISS-2"}}]
    f = run("V3", db=FakeDB(tables=[("field_clock", lambda a: clock), ("twin_event", lambda a: ev)]))
    assert [x.fkey for x in f] == ["ISS-1"]


# ---------------------------------------------------------------- 维护、财务、研发
def test_M1_repeat_down():
    ev = lambda u, h, e="alarm": msg("machine.event", "wq/gearbox/machining/{}/event".format(u), {"event": e, "message": "卡料"},
                                     NOW - dt.timedelta(hours=h))
    f = run("M1", db=FakeDB([ev("saw-01", h) for h in (1, 5, 9)] + [ev("grd-01", h) for h in (1, 30, 40)] + [ev("ht-01", 1, "recover")]))
    assert [x.fkey for x in f] == ["saw-01"]


def test_F1_cost_variance(monkeypatch):
    from hub import mrp
    k = {"WO-1": {"std_cost": 500, "actual_cost": 580, "variance_pct": 16.0, "lines": [{"operation": "磨外圆", "variance": 50}]},
         "WO-2": {"std_cost": 500, "actual_cost": 520, "variance_pct": 4.0, "lines": []}}
    monkeypatch.setattr(mrp, "wo_cost", lambda db, w, mode="teach": k.get(w))
    f = run("F1", db=FakeDB(docs={"Work Order": [{"name": "WO-1"}, {"name": "WO-2"}, {"name": "WO-3"}]}))
    assert [x.fkey for x in f] == ["WO-1"] and "磨外圆" in f[0].detail


def test_D1_revision_in_wip():
    rel = msg("design.release", "wq/gearbox/design/sh-301/release", {"item": "SH-301", "revision": 3}, NOW - dt.timedelta(hours=1))
    st = lambda wo, h: msg("machine.event", "wq/gearbox/machining/saw-01/event", {"event": "cycle_start", "part_serial": wo + "-1"},
                           NOW - dt.timedelta(hours=h), corr=wo)
    docs = {"Work Order": [{"name": "WO-A", "production_item": "SH-301", "status": "In Process"},
                           {"name": "WO-B", "production_item": "SH-301", "status": "In Process"},
                           {"name": "WO-C", "production_item": "SH-301", "status": "Completed"}]}
    f = run("D1", db=FakeDB([rel, st("WO-A", 2), st("WO-B", 0.5), st("WO-C", 3)], docs))
    assert [x.fkey for x in f] == ["WO-A:3"]                         # WO-B 是改版后才开工的


def test_every_live_rule_has_a_test():
    import sys
    names = {n for n in dir(sys.modules[__name__]) if n.startswith("test_")}
    for rid, r in A.load_catalog().items():
        if not r["waiting"]:
            assert any(n.startswith("test_{}_".format(rid)) for n in names), rid


# ---------------------------------------------------------------- 第 18 轮 E1：市场与客户、客户服务
CON = {"name": "CON-T-1", "party_name": "重点客户", "start_date": "2020-01-01", "end_date": "2099-12-31", "is_signed": 1, "status": "Active",
       "docstatus": 1, "wq_penalty_per_day": 200, "wq_response_h": 24, "wq_warranty_months": 18}


def _cp(i, customer, severity="normal", hours=1.0, status="open", responded=None, serial=None):
    return {"id": i, "customer": customer, "serial": serial, "subject": "异响", "detail": None, "channel": "电话", "severity": severity,
            "status": status, "responded_at": responded, "created_at": NOW - dt.timedelta(hours=hours)}


def _cdb(complaints=(), follow=(), docs=None, extra=()):
    tables = [("to_regclass", lambda a: [{"ok": True}]),
              ("from complaint where", lambda a: list(complaints)),
              ("from follow_up where", lambda a: list(follow))] + list(extra)
    return FakeDB(docs=dict({"Contract": [CON]}, **(docs or {})), tables=tables)


def test_C1_open_complaints_key_account_is_critical():
    db = _cdb([_cp(1, "普通客户", "urgent"), _cp(2, "重点客户"), _cp(3, "普通客户", serial="WQR105-H2501-01")])
    f = {x.fkey: x for x in run("C1", db)}
    assert set(f) == {"CP-00001", "CP-00002", "CP-00003"}
    assert f["CP-00001"].severity == "critical" and f["CP-00002"].severity == "critical"     # 紧急；合同有违约金的重点客户
    assert f["CP-00003"].severity == "warn" and f["CP-00003"].subject == ("FieldUnit", "WQR105-H2501-01")
    assert f["CP-00003"].values["units"] == ["WQR105-H2501-01"] and f["CP-00002"].subject == ("Complaint", "CP-00002")


def test_C2_satisfaction_drop_needs_last_n_scores():
    fu = [{"customer": "甲", "score": 3}, {"customer": "甲", "score": 3}, {"customer": "甲", "score": 4},
          {"customer": "乙", "score": 5}, {"customer": "乙", "score": 4}, {"customer": "乙", "score": 4},
          {"customer": "丙", "score": 1}, {"customer": "丙", "score": 2}]
    f = run("C2", _cdb(follow=fu))
    assert [x.fkey for x in f] == ["甲"] and f[0].values["avg"] == pytest.approx(3.33, abs=0.01)


def test_C3_complaint_overdue_uses_contract_response_time():
    db = _cdb([_cp(1, "重点客户", hours=30), _cp(2, "重点客户", hours=10), _cp(3, "重点客户", hours=40, responded=NOW),
               _cp(4, "没合同的客户", hours=20), _cp(5, "没合同的客户", hours=26)])
    f = {x.fkey: x for x in run("C3", db)}
    assert set(f) == {"CP-00001", "CP-00005"}                         # 合同 24 小时；没合同按默认 24 小时
    assert f["CP-00001"].values["limit_h"] == 24


def test_C4_batch_complaints_same_wheel():
    wheel = {"WQR105-A-01": ("SH-1", "grd-01/S2", "WO-1"), "WQR105-A-02": ("SH-2", "grd-01/S2", "WO-2"), "WQR105-A-03": ("SH-3", "grd-01/S3", "WO-3")}
    shafts = {v[0]: (k, v) for k, v in wheel.items()}
    extra = [("type='PartSerial.installed_in'", lambda a: [{"src_key": wheel[a[1]][0]}] if a[1] in wheel else []),
             ("type='PartSerial.processed'", lambda a: [{"props": {"tool": shafts[a[1]][1][1], "machine": "grd-01"}}]),
             ("type='PartSerial' and key", lambda a: [{"wo": shafts[a[1]][1][2]}])]
    db = _cdb([_cp(1, "甲", serial="WQR105-A-01"), _cp(2, "乙", serial="WQR105-A-02"), _cp(3, "丙", serial="WQR105-A-03")], extra=extra)
    f = run("C4", db)
    assert [x.fkey for x in f] == ["Tool:grd-01/S2"] and f[0].values["units"] == ["WQR105-A-01", "WQR105-A-02"]
    assert run("C4", _cdb([_cp(1, "甲", serial="WQR105-A-01")], extra=extra)) == []


def test_C5_quote_expiring_within_days():
    from hub import kpi
    today = NOW.astimezone(kpi.TZ).date()
    qs = [{"name": "SAL-QTN-1", "status": "Open", "valid_till": (today + dt.timedelta(days=2)).isoformat(), "party_name": "甲", "grand_total": 6600},
          {"name": "SAL-QTN-2", "status": "Open", "valid_till": (today + dt.timedelta(days=10)).isoformat(), "party_name": "乙"},
          {"name": "SAL-QTN-3", "status": "Ordered", "valid_till": today.isoformat(), "party_name": "丙"},
          {"name": "SAL-QTN-4", "status": "Open", "valid_till": (today - dt.timedelta(days=1)).isoformat(), "party_name": "丁"}]
    f = run("C5", FakeDB(docs={"Quotation": qs}))
    assert [x.fkey for x in f] == ["SAL-QTN-1"] and f[0].values["days_left"] == 2


def test_R3_late_order_with_contract_penalty():
    orders = [{"name": "SO-1", "customer": "重点客户", "tone": "bad", "projected": "2026-10-23", "delivery_date": "2026-10-20"},
              {"name": "SO-2", "customer": "重点客户", "tone": "bad", "projected": "2026-10-21", "delivery_date": "2026-10-20"},
              {"name": "SO-3", "customer": "普通客户", "tone": "bad", "projected": "2026-10-25", "delivery_date": "2026-10-20"},
              {"name": "SO-4", "customer": "重点客户", "tone": "good", "projected": "2026-10-19", "delivery_date": "2026-10-20"}]
    f = {x.fkey: x for x in run("R3", FakeDB(docs={"Contract": [CON]}), ov={"orders": orders})}
    assert set(f) == {"SO-1", "SO-2"}
    assert f["SO-1"].values["penalty"] == 600 and f["SO-1"].severity == "critical"      # 3 天 × $200 ≥ $500
    assert f["SO-2"].severity == "warn"


# ---------------------------------------------------------------- 第 18 轮 E2：安全、健康与环境
def _edb(issues=(), permits=(), people=(), trainings=(), chems=(), wastes=()):
    tables = [("to_regclass", lambda a: [{"ok": True}]),
              ("from safety_issue where", lambda a: list(issues)),
              ("kind='loto'", lambda a: [p for p in permits if p["kind"] == "loto" and p["status"] == "active"]),
              ("from work_permit where", lambda a: [p for p in permits if p["status"] in ("blocked", "requested")]),
              ("from ehs_person where id=", lambda a: [p for p in people if p["id"] == a[0]]),
              ("from ehs_person where mode", lambda a: list(people)),
              ("from ehs_training", lambda a: list(trainings)),
              ("from chemical where", lambda a: list(chems)),
              ("from waste where", lambda a: list(wastes))]
    db = FakeDB(tables=tables)
    db._ehs_ready = True
    return db


def _si(i, level="general", due=None, status="open", unit="grd-01"):
    return {"id": i, "level": level, "status": status, "unit": unit, "subject": "防护罩松动", "area": "外圆磨床", "found_by": "王强",
            "due_day": due, "owner": None, "fix_minutes": 120, "kind": "guard"}


def test_E1_major_issue_open():
    db = _edb([_si(1, "major"), _si(2), _si(3, "major", unit=None)])
    f = {x.fkey: x for x in run("E1", db)}
    assert set(f) == {"SI-00001", "SI-00003"} and f["SI-00001"].severity == "critical"
    assert f["SI-00001"].subject == ("Machine", "grd-01") and f["SI-00001"].values["fix_minutes"] == 120
    assert f["SI-00003"].subject == ("SafetyIssue", "SI-00003")


def test_E2_issue_overdue():
    from hub import kpi
    d0 = NOW.astimezone(kpi.TZ).date()
    db = _edb([_si(1, due=d0 - dt.timedelta(days=2)), _si(2, due=d0), _si(3, due=d0 - dt.timedelta(days=5), status="fixed")])
    f = run("E2", db)
    assert [x.fkey for x in f] == ["SI-00001"] and f[0].values["days"] == 2


def test_E3_permit_without_valid_training():
    from hub import kpi
    d0 = NOW.astimezone(kpi.TZ).date()
    people = [{"id": "P07", "name": "孙磊"}, {"id": "P06", "name": "赵刚"}]
    tr = [{"id": 1, "person_id": "P07", "kind": "confined", "done_day": d0 - dt.timedelta(days=400), "valid_months": 12},
          {"id": 2, "person_id": "P06", "kind": "confined", "done_day": d0 - dt.timedelta(days=30), "valid_months": 12}]
    permits = [{"id": 1, "kind": "confined", "unit": "ht-01", "holder_id": "P07", "status": "blocked", "requested_by": "安全员"},
               {"id": 2, "kind": "confined", "unit": "ht-01", "holder_id": "P06", "status": "requested", "requested_by": "安全员"}]
    f = run("E3", _edb(permits=permits, people=people, trainings=tr))
    assert [x.fkey for x in f] == ["PTW-00001"] and "已过期" in f[0].values["why"] and f[0].severity == "critical"


def test_E4_training_due_or_expired():
    from hub import kpi
    d0 = NOW.astimezone(kpi.TZ).date()
    people = [{"id": "P01", "name": "王强"}, {"id": "P02", "name": "李娜"}, {"id": "P03", "name": "张伟"}]
    tr = [{"id": 1, "person_id": "P01", "kind": "induction", "done_day": d0 - dt.timedelta(days=36 * 30 + 40), "valid_months": 36},
          {"id": 2, "person_id": "P02", "kind": "hot", "done_day": d0 - dt.timedelta(days=350), "valid_months": 12},
          {"id": 3, "person_id": "P03", "kind": "hot", "done_day": d0 - dt.timedelta(days=30), "valid_months": 12}]
    f = {x.fkey: x for x in run("E4", _edb(people=people, trainings=tr))}
    assert set(f) == {"P01:induction", "P02:hot"}
    assert f["P01:induction"].severity == "warn" and f["P02:hot"].severity == "info"


def test_E5_running_while_locked_out():
    permits = [{"id": 1, "kind": "loto", "unit": "grd-01", "status": "active"}, {"id": 2, "kind": "loto", "unit": "key-01", "status": "active"}]
    ov = {"machines": [mach("grd-01", "run"), mach("key-01", "down", locked="PTW-00002")]}
    f = run("E5", _edb(permits=permits), ov=ov)
    assert [x.fkey for x in f] == ["PTW-00001"] and f[0].subject == ("Machine", "grd-01")


def test_E6_chemical_out_of_range():
    chems = [{"code": "CL-01", "name": "乳化切削液", "stock_kg": 20, "min_kg": 50, "max_kg": 400, "sds": ""},
             {"code": "QO-01", "name": "淬火油", "stock_kg": 600, "min_kg": 200, "max_kg": 1000, "sds": ""},
             {"code": "LO-01", "name": "导轨润滑油", "stock_kg": 260, "min_kg": 40, "max_kg": 200, "sds": ""}]
    f = {x.fkey: x for x in run("E6", _edb(chems=chems))}
    assert set(f) == {"CL-01", "LO-01"} and "低于" in f["CL-01"].title and "超过" in f["LO-01"].title


def test_E7_hazardous_waste_over_90_days():
    from hub import kpi
    d0 = NOW.astimezone(kpi.TZ).date()
    ws = [{"id": 1, "kind": "coolant", "qty_kg": 120, "produced_day": d0 - dt.timedelta(days=95)},
          {"id": 2, "kind": "rags", "qty_kg": 10, "produced_day": d0 - dt.timedelta(days=30)}]
    f = run("E7", _edb(wastes=ws))
    assert [x.fkey for x in f] == ["W-00001"] and f[0].values["age_days"] == 95
