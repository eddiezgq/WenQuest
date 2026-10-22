# -*- coding: utf-8 -*-
"""帮助里的“当场动手”（第 30 轮 H-11 第 2 种，细则 §八 8-1）：帮助正文的 ```try``` 块放一个按钮，按下去在演示工厂里真做一件事，
下面的实时数据（```live```）跟着变。

只开放这里登记的几个动作（白名单），每个都复用现成的代码：
- stop-grinder   磨床 GRD-01 停机 2 小时：与教师控制台“注入一次故障”同一条路（MES 指令 inject_fault 发给仿真车间）
- rush-order     下一张急单：与两周情景第 1 幕同一条路（算料 → 计划员的“下单并算料”提议 → 确认，桥接写进 ERPNext）
- overdue-pm     磨床保养逾期：与两周情景第 6 幕同一条路（maint.inject_overdue）
- overdue-invoice 一张应收发票逾期 15 天：与两周情景第 8 幕同一条路（finance.make_overdue）

规矩：
- 只在演示工厂（企业工厂整组接口 404，见 app.py TEACH_ONLY_API）、只在教学模式（生产模式 403）；
- 学生只能按自己岗位能做的（每个动作登记允许的岗位，沿用各领域现成的岗位表）；老师都能做；
- 每人 60 秒一次；老师 5 秒一次（上课演示要连着按，只防连点两下下两张单）；
- 复原：老师在“情景导演”里“重置实验 7 情景”/“开始两周情景”（reset_teach），这些改动一起清掉。"""
import datetime as dt
import time

from fastapi import Body, Depends, HTTPException

MODE = "teach"
RATE_S = 60
RATE_TEACHER_S = 5
GRINDER = "grd-01"


def _stop_grinder(H, u, who):
    H.mes.command(GRINDER, "inject_fault", MODE, who, minutes=120, reason="砂轮主轴故障（帮助里当场动手）")
    return {"text": "已让 GRD-01 停机 2 小时（工厂时间）。几秒后设备变红，厂情中枢报“设备停机”，因果链连到受影响的订单。"}


def _rush_order(H, u, who):
    from hub import mrp
    from hub import story as ST
    from hub.ai import _order_title
    sc = ST.scenario()
    qty, days = 5, 5
    due = (dt.date.today() + dt.timedelta(days=days)).isoformat()
    pv = mrp.plan_order(H.db, sc["customer"], sc["item"], qty, due, MODE)
    pv["help_try"] = True
    pid = H.ai.propose("create_order_and_plan", pv, MODE, who, "帮助：" + _order_title(pv), source="help", role="planner")
    H.ai.decide(pid, who, True, role="planner")
    short = [x["item_code"] for x in pv.get("mrp") or [] if float(x.get("net") or 0) > 0]
    return {"text": "{} 下急单 {} × {}，交期 {}（提议 {}，已确认，正在写进 ERPNext）。{}".format(
        sc["customer"].split(" ")[0], sc["item"], qty, due, pid, "要补的料：" + "、".join(short[:4]) if short else "库存够用"),
        "proposal_id": pid}


def _overdue_pm(H, u, who):
    from sim import reliability as REL
    from hub import maint as MT
    rp = REL.params(GRINDER)
    if rp is None:
        raise ValueError("GRD-01 没有保养计划")
    return MT.inject_overdue(H, MODE, GRINDER, round(rp["pm_h"] * 1.4), who)


def _overdue_invoice(H, u, who):
    from hub import finance as FN
    x = H.db.one("select id from invoice where mode=%s and kind='ar' and status not in ('paid','held','failed') order by id desc limit 1",
                 (MODE,))
    if x is None:
        raise ValueError("现在没有未收的应收发票（订单做完开票后再试）")
    FN.set_sim(H.db, MODE, True)
    return FN.make_overdue(H, MODE, x["id"], 15, who)


# 动作 → 名字、允许的学生岗位（老师都能做）、做完去哪看、实现
def _roles():
    from hub.maint_api import MANAGE                      # 设备维护：维修工、厂长
    from hub.ont.actions import FINANCE_INITIATORS, INITIATORS
    return {
        "stop-grinder": MANAGE + ("operator", "lead"),     # 设备在谁手上：操作工、班组长、维修工
        "rush-order": INITIATORS,                          # 接单算料：计划员（与厂情中枢发起动作同一张表）
        "overdue-pm": MANAGE,
        "overdue-invoice": FINANCE_INITIATORS,
    }


ACTIONS = {
    "stop-grinder": {"label": "让磨床停机 2 小时", "look": "/3d", "fn": _stop_grinder},
    "rush-order": {"label": "下一张急单", "look": "/work/planner", "fn": _rush_order},
    "overdue-pm": {"label": "让磨床保养逾期", "look": "/maint", "fn": _overdue_pm},
    "overdue-invoice": {"label": "让一张发票逾期 15 天", "look": "/finance", "fn": _overdue_invoice},
}
ROLE_NAME = {"planner": "计划员", "engineer": "工艺员", "operator": "操作工", "quality": "质检员", "manager": "厂长", "sales": "销售",
             "service": "售后", "safety": "安全员", "maintenance": "维修工", "lead": "班组长", "approver": "审批人"}

_last = {}          # 用户 → 上次动手的时刻（time.monotonic）


def _uid(u):
    return str(u.get("uid") or u.get("name") or "")


def roles_of(name):
    return _roles()[name]


def check(u, name, now=None):
    """能不能做：返回 None，或 (HTTP 状态, 原因)。不改任何东西。"""
    if name not in ACTIONS:
        return 404, "没有这个动作：{}".format(name)
    if u.get("mode") != MODE:
        return 403, "当场动手只在教学模式下的演示工厂里能用"
    if not u.get("teacher") and u.get("role") not in roles_of(name):
        return 403, "这一步要{}来做（你现在是{}）".format("、".join(ROLE_NAME.get(r, r) for r in roles_of(name)),
                                                  ROLE_NAME.get(u.get("role"), u.get("role")))
    left = wait_s(u, now)
    if left:
        return 429, "刚动过手，{} 秒后再试".format(left)
    return None


def rate_s(u):
    return RATE_TEACHER_S if u.get("teacher") else RATE_S


def wait_s(u, now=None):
    t = _last.get(_uid(u))
    now = time.monotonic() if now is None else now
    gap = rate_s(u)
    return 0 if t is None or now - t >= gap else int(gap - (now - t)) + 1


def run(H, u, name, who, now=None):
    bad = check(u, name, now)
    if bad:
        raise HTTPException(*bad)
    try:
        res = ACTIONS[name]["fn"](H, u, who) or {}
    except KeyError as e:
        raise HTTPException(404, "没有：{}".format(e))
    except PermissionError as e:
        raise HTTPException(403, str(e))
    except ValueError as e:
        raise HTTPException(409, str(e))
    _last[_uid(u)] = time.monotonic() if now is None else now
    return dict(res, action=name, look=ACTIONS[name]["look"], wait_s=rate_s(u))


def listing(u, now=None):
    """帮助页用：每个动作此刻能不能按、为什么不能"""
    out = {}
    for n, a in ACTIONS.items():
        bad = check(u, n, now)
        out[n] = {"label": a["label"], "look": a["look"], "ok": bad is None, "why": bad[1] if bad else "",
                  "roles": list(roles_of(n)), "wait_s": wait_s(u, now)}
    return {"enabled": u.get("mode") == MODE, "teacher": bool(u.get("teacher")), "actions": out}


def mount(app, H, user_of, who):
    @app.get("/api/help/try")
    def try_list(u=Depends(user_of)):
        return listing(u)

    @app.post("/api/help/try/{name}")
    def try_run(name: str, body: dict = Body(default={}), u=Depends(user_of)):
        return run(H, u, name, who(u))
