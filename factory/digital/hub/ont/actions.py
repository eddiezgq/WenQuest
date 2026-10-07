# -*- coding: utf-8 -*-
"""动作框架（第 17 轮 C 期 C6、C7）：草稿 → 已提交（附试运行）→ 已批准 / 已驳回 → 执行中 → 已完成 / 执行失败。

执行器：
- 改派、调序、维修加急、外协：发给车间（MES 指令；生产模式的维修加急只记录承诺）；
- 加班：写班次日历并发给车间；
- 紧急采购：走“提议 → 桥接 → ERPNext”（请购单，到货日提前）；
- 分批交货：走同一通道，在 ERPNext 销售订单上留交货安排的备注。
审批：花钱的（加班、紧急采购、外协、维修加急）厂长批；不花钱的（改派、调序、分批交货）计划员或厂长批；
生产模式不能批自己发起的；教学模式老师可以自批（课堂演示），学生不能自批。"""
import datetime as dt

from psycopg.types.json import Jsonb

from hub.ont import plan as P

SCHEMA = """
create table if not exists action (
    id          bigserial primary key,
    mode        text not null,
    type        text not null,
    title       text not null,
    params      jsonb not null,
    status      text not null default 'draft',
    scenario_id bigint,
    anomaly_id  bigint,
    initiator   text,
    initiator_role text,
    approver    text,
    trial       jsonb,
    result      jsonb,
    created_at  timestamptz not null default now(),
    decided_at  timestamptz,
    executed_at timestamptz
);
create index if not exists action_mode on action (mode, status);
create table if not exists action_log (
    id        bigserial primary key,
    action_id bigint not null,
    ts        timestamptz not null default now(),
    who       text,
    kind      text not null,
    text      text
);
"""
TYPES = {
    "reassign": {"label": "改派", "costly": False},
    "reorder": {"label": "调序", "costly": False},
    "overtime": {"label": "加班", "costly": True},
    "expedite": {"label": "维修加急", "costly": True},
    "urgent_purchase": {"label": "紧急采购", "costly": True},
    "outsource": {"label": "外协", "costly": True},
    "split_delivery": {"label": "分批交货", "costly": False},
    # 第 18 轮 E1：客户与服务（发起：售后、厂长；批量 / 过保免费 / 备件花钱，要厂长批）
    "service_batch": {"label": "服务派工", "costly": True, "service": True},
    "spare_ship": {"label": "备件出库", "costly": True, "service": True},
    "customer_notice": {"label": "客户通知", "costly": False, "service": True},
    # 第 18 轮 E2：安全环保（发起：安全员、厂长；停机挂牌、整改工单花钱要厂长批；解锁、培训安全员批，不能自批）
    "lockout": {"label": "停机挂牌整改", "costly": True, "ehs": True},
    "rectify_order": {"label": "整改工单", "costly": True, "ehs": True, "nosim": True},
    "unlock": {"label": "验收解锁", "costly": False, "ehs": True, "nosim": True},
    "training_plan": {"label": "安排培训", "costly": False, "ehs": True, "nosim": True},
}
SERVICE_INITIATORS = ("service", "manager", "sales")
EHS_INITIATORS = ("safety", "manager")


def no_sim(t):
    """不进车间推演的动作（服务类、整改工单、解锁、培训）"""
    x = TYPES.get(t, {})
    return bool(x.get("service") or x.get("nosim"))
STATUS = {"draft": "草稿", "submitted": "待批准", "approved": "已批准", "rejected": "已驳回", "executing": "执行中",
          "done": "已完成", "failed": "执行失败"}
INITIATORS = ("planner", "manager")


class ActionError(ValueError):
    pass


def init(db):
    db.x(SCHEMA)


def title_of(t, p):
    if t == "reassign":
        return "改派 {} {}：{} → {}".format(p["work_order"], p["operation"].split(" ")[0], p["from_unit"].upper(), p["to_unit"].upper())
    if t == "reorder":
        return "调序：{} 在 {} 上排到最前".format(p["work_order"], p["unit"].upper())
    if t == "overtime":
        return "加班：{} {} {} 分钟".format(p["day"], "全厂" if p.get("unit") in (None, "*") else p["unit"].upper(), p["minutes"])
    if t == "expedite":
        return "维修加急：{} 剩余停机缩短到 {:.0%}".format(p["unit"].upper(), float(p.get("factor", 0.5)))
    if t == "urgent_purchase":
        return "紧急采购：{} × {}，{} 到货".format(p["item"], p["qty"], p["arrive"])
    if t == "outsource":
        return "外协：{} {} {} 件".format(p["work_order"], p["operation"].split(" ")[0], p["qty"])
    if t == "split_delivery":
        return "分批交货：{} 先交 {} 台（{}）".format(p["sales_order"], p["first_qty"], p["first_date"])
    if t == "service_batch":
        jobs = p.get("jobs") or []
        rep = sum(1 for j in jobs if j["kind"] != "inspect")
        return "服务派工：{} 台（维修 {}、点检 {}）{}".format(len(jobs), rep, len(jobs) - rep, "：" + jobs[0]["serial"] if len(jobs) == 1 else "")
    if t == "spare_ship":
        return "备件出库：" + "、".join("{} × {}".format(i["item_code"], i["qty"]) for i in p.get("items") or [])
    if t == "customer_notice":
        return "预防性服务通知：{} 个客户".format(len(p.get("customers") or []))
    if t == "lockout":
        return "停机挂牌整改：{} {}，整改约 {} 分钟".format((p.get("unit") or "").upper(),
                                                "{} 分钟后停".format(p["delay_minutes"]) if p.get("delay_minutes") else "立即停", p.get("minutes"))
    if t == "rectify_order":
        return "整改工单：{} {}".format((p.get("unit") or "").upper(), p.get("subject") or "")
    if t == "unlock":
        return "验收解锁：{}".format((p.get("unit") or "").upper())
    if t == "training_plan":
        return "安排培训：{} {} 人".format(p.get("kind"), len(p.get("people") or []))
    return t


def is_costly(a):
    """单张、保修期内的服务派工不算花钱（售后主管就能批）；其余按动作种类"""
    t, p = a["type"], a.get("params") or {}
    if t == "service_batch":
        jobs = p.get("jobs") or []
        return not (len(jobs) == 1 and p.get("in_warranty"))
    return TYPES[t]["costly"]


def log(db, aid, who, kind, text):
    db.x("insert into action_log (action_id, who, kind, text) values (%s,%s,%s,%s)", (aid, who, kind, text))


def can_initiate(u, t=None):
    if u.get("teacher"):
        return True
    if t and TYPES.get(t, {}).get("service"):
        return u.get("role") in SERVICE_INITIATORS
    if t and TYPES.get(t, {}).get("ehs"):
        return u.get("role") in EHS_INITIATORS
    return u.get("role") in INITIATORS or (t is None and u.get("role") in SERVICE_INITIATORS)


def can_approve(u, a):
    """返回 (能否, 原因)"""
    costly = is_costly(a)
    service = TYPES[a["type"]].get("service")
    if costly and u.get("role") != "manager":
        return False, "这是要花钱的动作，要厂长批准"
    if not costly and service and u.get("role") not in ("manager", "service", "sales"):
        return False, "要售后或厂长批准"
    ehs = TYPES[a["type"]].get("ehs")
    if not costly and ehs and u.get("role") not in ("manager", "safety"):
        return False, "要安全员或厂长批准"
    if not costly and not service and not ehs and u.get("role") not in ("manager", "planner"):
        return False, "要计划员或厂长批准"
    if a["initiator"] == u.get("name"):
        if a["mode"] == "prod":
            return False, "生产模式下不能批准自己发起的动作"
        if not u.get("teacher"):
            return False, "不能批准自己发起的动作（请老师或另一位同学批准）"
    return True, ""


def create(db, mode, u, type_, params, scenario_id=None, anomaly_id=None, trial=None):
    if type_ not in TYPES:
        raise ActionError("不认识的动作 " + str(type_))
    if not can_initiate(u, type_):
        raise ActionError("服务类动作由售后或厂长发起" if TYPES[type_].get("service") else "动作由计划员或厂长发起")
    p = dict(params)
    p["type"] = type_
    r = db.one("insert into action (mode, type, title, params, scenario_id, anomaly_id, initiator, initiator_role, trial) "
               "values (%s,%s,%s,%s,%s,%s,%s,%s,%s) returning id",
               (mode, type_, title_of(type_, p), Jsonb(p), scenario_id, anomaly_id, u.get("name"), u.get("role"), Jsonb(trial) if trial else None))
    log(db, r["id"], u.get("name"), "create", "起草")
    return r["id"]


def get(db, aid):
    return db.one("select * from action where id=%s", (aid,))


def submit(db, aid, u, trial):
    a = get(db, aid)
    if a["status"] not in ("draft", "rejected"):
        raise ActionError("只有草稿或被驳回的动作可以提交")
    db.x("update action set status='submitted', trial=%s where id=%s", (Jsonb(trial), aid))
    log(db, aid, u.get("name"), "submit", "提交，试运行：{}".format(_trial_text(trial)))
    _notify(db, a, "submitted")


def reject(db, aid, u, text):
    a = get(db, aid)
    if a["status"] != "submitted":
        raise ActionError("只有待批准的动作可以驳回")
    ok, why = can_approve(u, dict(a, initiator=None))
    if not ok:
        raise ActionError(why)
    if not (text or "").strip():
        raise ActionError("驳回要写原因")
    db.x("update action set status='rejected', approver=%s, decided_at=now() where id=%s", (u.get("name"), aid))
    log(db, aid, u.get("name"), "reject", text.strip())
    _notify(db, a, "rejected", u.get("name"), text.strip())


def approve(H, aid, u, who):
    """批准并执行"""
    db = H.db
    a = get(db, aid)
    if a["status"] != "submitted":
        raise ActionError("只有待批准的动作可以批准")
    ok, why = can_approve(u, a)
    if not ok:
        raise ActionError(why)
    db.x("update action set status='approved', approver=%s, decided_at=now() where id=%s", (u.get("name"), aid))
    log(db, aid, u.get("name"), "approve", "批准")
    try:
        res, status = execute(H, a, u, who)
    except Exception as e:  # noqa: BLE001
        db.x("update action set status='failed', result=%s, executed_at=now() where id=%s", (Jsonb({"error": str(e)}), aid))
        log(db, aid, "system", "fail", "执行失败：{}".format(e))
        _notify(db, a, "failed", u.get("name"), str(e))
        raise ActionError("执行失败：{}".format(e))
    db.x("update action set status=%s, result=%s, executed_at=now() where id=%s", (status, Jsonb(res), aid))
    log(db, aid, "system", "execute", res.get("text", "已执行"))
    _notify(db, a, "done" if status == "done" else "approved", u.get("name"), res.get("text"))
    return get(db, aid)


def _notify(db, a, event, who=None, text=None):
    """动作状态变化 → 通知（第 17 轮 D 期）；通知出错不影响动作本身"""
    try:
        from hub.ont import notify as NT
        NT.on_action(db, a["mode"], a, event, who, text)
    except Exception:  # noqa: BLE001
        import logging
        logging.getLogger("actions").exception("动作通知失败")


def execute(H, a, u, who):
    p, mode, db = a["params"], a["mode"], H.db
    t = a["type"]
    if t == "reassign":
        H.mes.command(p["from_unit"], "reassign", mode, who, p["work_order"], p["operation"], to_unit=p["to_unit"])
        return {"text": "已发给车间：{} 的 {} 改到 {}".format(p["work_order"], p["operation"].split(" ")[0], p["to_unit"].upper())}, "done"
    if t == "reorder":
        H.mes.command(p["unit"], "reorder", mode, who, p["work_order"], p.get("operation"))
        return {"text": "已发给车间：{} 上 {} 排到最前".format(p["unit"].upper(), p["work_order"])}, "done"
    if t == "outsource":
        H.mes.command(p["unit"], "outsource", mode, who, p["work_order"], p["operation"], qty=int(p["qty"]), days=float(p.get("days", 1)))
        return {"text": "已发给车间：{} 件外协".format(p["qty"])}, "done"
    if t == "expedite":
        if mode == "teach":
            H.mes.command(p["unit"], "expedite_repair", mode, who, factor=float(p.get("factor", 0.5)))
            return {"text": "已发给车间：{} 维修加急".format(p["unit"].upper())}, "done"
        return {"text": "已记录维修加急的承诺（真实车间的修理时间以维修部门为准）"}, "done"
    if t == "overtime":
        cal = P.calendar(db, mode)
        if cal.mode != "shift":
            raise ActionError("车间是 24 小时连续运转，加班没有意义")
        cal.add_overtime(p["day"], p.get("unit") or "*", int(p["minutes"]))
        P.save_calendar(db, mode, cal, who)
        P.push_calendar(H.mes, db, mode, who)
        return {"text": "班次表已改：{} 加班 {} 分钟，已发给车间".format(p["day"], p["minutes"]), "calendar": cal.to_dict()}, "done"
    if t == "urgent_purchase":
        pid = H.ai.propose("purchase_request", {"material_requests": [{"item_code": p["item"], "qty": float(p["qty"]), "schedule_date": p["arrive"],
                                                                       "uom": "Nos", "urgent": True}]},
                           mode, u.get("name"), "紧急采购 {} × {}（{} 到货）".format(p["item"], p["qty"], p["arrive"]), source="ont", role=u.get("role"))
        H.ai.decide(pid, u.get("name"), True, role=u.get("role"))
        return {"text": "已交 ERPNext 生成请购单（提议 {}）".format(pid), "proposal_id": pid}, "executing"
    if t == "split_delivery":
        pid = H.ai.propose("so_comment", {"sales_order": p["sales_order"],
                                          "content": "分批交货：先交 {} 台，交期 {}；其余按原交期。（问渠厂情中枢 · 动作 {}）".format(p["first_qty"], p["first_date"], a["id"])},
                           mode, u.get("name"), "分批交货 {}".format(p["sales_order"]), source="ont", role=u.get("role"))
        H.ai.decide(pid, u.get("name"), True, role=u.get("role"))
        return {"text": "已交 ERPNext 在订单上留交货安排（提议 {}）".format(pid), "proposal_id": pid}, "executing"
    if t == "service_batch":
        from hub import service as SV
        r = SV.create_jobs(H, mode, p.get("jobs") or [], u.get("name"), anomaly_id=a["anomaly_id"], action_id=a["id"],
                           complaint_id=p.get("complaint_id"), batch_kind=p.get("kind") or "repair_one")
        if p.get("complaint_id"):
            SV.respond(db, int(p["complaint_id"]), u.get("name"), "doing", "已派服务工单")
        names = sorted({x["engineer_name"] for x in r["plan"] if x.get("engineer_name")})
        return {"text": "已派 {} 张服务工单（工程师 {}），交 ERPNext 开服务工单（提议 {}）".format(len(r["jobs"]), "、".join(names) or "待定", r["proposal_id"]),
                "proposal_id": r["proposal_id"], "jobs": r["jobs"], "batch_id": r["batch_id"]}, "executing" if r["proposal_id"] else "done"
    if t == "spare_ship":
        from hub import service as SV
        pid = SV.ship_spares(H, mode, p.get("items") or [], u.get("name"), "服务备件（动作 ACT-{:05d}）".format(a["id"]))
        return {"text": "已交 ERPNext 出库（提议 {}）".format(pid), "proposal_id": pid}, "executing"
    if t == "customer_notice":
        from hub import service as SV
        rows = SV.notice(H, mode, p.get("customers") or [], u.get("name"), a["id"], send=True, emails=p.get("emails"))
        sent = sum(1 for x in rows if x["status"] == "sent")
        return {"text": "通知 {} 个客户：{}".format(len(rows), "已发邮件 {} 封".format(sent) if sent else
                                                ("教学模式只记录、不发出" if mode == "teach" else "没有邮箱，已记录，请人工联系")), "notices": rows}, "done"
    if t in ("lockout", "rectify_order", "unlock", "training_plan"):
        from hub import ehs as EH
        fn = {"lockout": EH.exec_lockout, "rectify_order": EH.exec_rectify, "unlock": EH.exec_unlock, "training_plan": EH.exec_training}[t]
        res = fn(H, mode, p, u)
        return res, "executing" if res.get("proposal_id") else "done"
    raise ActionError("没有执行器：" + t)


def sync(db, a):
    """经 ERPNext 执行的动作：看提议的结果，更新状态"""
    if a["status"] != "executing" or not (a["result"] or {}).get("proposal_id"):
        return a
    pr = db.one("select status, result from ai_proposal where proposal_id=%s", (a["result"]["proposal_id"],))
    if pr and pr["status"] in ("executed", "failed"):
        st = "done" if pr["status"] == "executed" else "failed"
        res = dict(a["result"], erp=pr["result"])
        db.x("update action set status=%s, result=%s where id=%s and status='executing'", (st, Jsonb(res), a["id"]))
        log(db, a["id"], "system", st, "ERPNext：{}".format(pr["result"]))
        _notify(db, a, st, "ERPNext")
        return get(db, a["id"])
    return a


def _trial_text(tr):
    if not tr:
        return "（没有）"
    rows = tr.get("sales_orders") or []
    s = "；".join("{} {}".format(r["name"], "按时" if (r.get("late_days") or 0) <= 0 else "晚 {} 天".format(r["late_days"])) for r in rows if r.get("late_days") is not None)
    return "{}，多花 ${:,.0f}".format(s or "没有受影响的订单", tr.get("cost_total") or 0)


def notes(db, aid):
    return [{"ts": r["ts"].isoformat(), "who": r["who"], "kind": r["kind"], "text": r["text"]}
            for r in db.q("select * from action_log where action_id=%s order by id", (aid,))]


def row(a):
    return {"id": a["id"], "key": "ACT-{:05d}".format(a["id"]), "type": a["type"], "type_label": TYPES[a["type"]]["label"],
            "costly": is_costly(a), "title": a["title"], "params": a["params"], "status": a["status"],
            "status_label": STATUS[a["status"]], "scenario_id": a["scenario_id"], "anomaly_id": a["anomaly_id"],
            "initiator": a["initiator"], "approver": a["approver"], "trial": a["trial"], "result": a["result"],
            "created_at": a["created_at"].isoformat(), "decided_at": a["decided_at"].isoformat() if a["decided_at"] else None,
            "executed_at": a["executed_at"].isoformat() if a["executed_at"] else None}


def trial(db, snaps, mode, changes, scenario_snapshot=None):
    """试运行：用最新快照推演“做”与“不做”"""
    svc = [c for c in changes if TYPES.get(c.get("type"), {}).get("service")]
    if svc and len(svc) == len(changes):
        return service_trial(db, mode, svc)
    if changes and all(no_sim(c.get("type")) for c in changes):
        return plain_trial(changes)
    changes = [c for c in changes if not no_sim(c.get("type"))]
    sid = None
    if scenario_snapshot is not None:
        snap = scenario_snapshot
    else:
        sid, snap, _ = snaps.take(mode)
    ctx = P.context(db, mode, dt.datetime.fromisoformat(snap["factory_now"]))
    base = P.simulate(snap, [], ctx)
    r = P.simulate(snap, changes, ctx)
    keep = ("sales_orders", "cost_total", "costs", "overtime_min", "overtime_units", "checks", "ok")
    return dict({k: r[k] for k in keep}, base={k: base[k] for k in ("sales_orders", "cost_total")}, at=snap["factory_now"], snapshot_id=sid)


def service_trial(db, mode, changes):
    """服务类动作的“试运行”：按排班估算（不进车间仿真，E1-7）"""
    from hub import service as SV
    costs, checks, est = [], [], None
    for c in changes:
        if c["type"] == "service_batch":
            est = SV.estimate(db, mode, c.get("jobs") or [])
            costs += [{"what": "人工 {} 人天".format(est["person_days"]), "usd": est["cost"]["labor"]},
                      {"what": "差旅", "usd": est["cost"]["travel"]}, {"what": "备件", "usd": est["cost"]["parts"]}]
            if est["unplanned"]:
                checks.append({"ok": False, "text": "{} 台 21 天内排不进".format(len(est["unplanned"]))})
            else:
                checks.append({"ok": True, "text": "{} 天做完（到 {}），工程师 {}".format(est["days"], est["finish"], "、".join(est["engineers"]))})
        elif c["type"] == "spare_ship":
            checks.append({"ok": True, "text": "出库 " + "、".join("{} × {}".format(i["item_code"], i["qty"]) for i in c.get("items") or [])})
    total = round(sum(x["usd"] for x in costs), 2)
    return {"sales_orders": [], "cost_total": total, "costs": [x for x in costs if x["usd"]], "overtime_min": 0, "overtime_units": 0,
            "checks": checks, "ok": all(x["ok"] for x in checks), "base": {"sales_orders": [], "cost_total": 0},
            "at": SV.field_today(db, mode).isoformat(), "snapshot_id": None, "service": est}


def plain_trial(changes):
    """不进推演的动作（整改工单、解锁、培训）：只列出要做的事"""
    return {"sales_orders": [], "cost_total": 0.0, "costs": [], "overtime_min": 0, "overtime_units": 0,
            "checks": [{"ok": True, "text": title_of(c["type"], c)} for c in changes], "ok": True, "base": {"sales_orders": [], "cost_total": 0},
            "at": dt.datetime.now(dt.timezone.utc).isoformat(), "snapshot_id": None}
