# -*- coding: utf-8 -*-
"""数字工厂枢纽服务（hub）：历史库写入 + 看板指标 + AI 工厂助手 + MES + 教学评分 + 工作台网页。

运行：uvicorn hub.app:app --port 8100
环境变量：WQ_DB、WQ_MQTT_HOST/PORT/USER/PASSWORD、WQ_MQTT_WS（浏览器连总线的地址）、WQ_ERPNEXT_URL、
WQ_NODERED_URL、WQ_TZ、WQ_SECRET、WQ_CLAUDE_KEY / WQ_DEEPSEEK_KEY（可选）；
线上另有 WQ_AUTH=wenquest、WQ_SSO_URL、WQ_LOGIN_URL、WQ_AI_PER_HOUR、WQ_HISTORY_DAYS（见第 3 轮细则）。
"""
import base64
import datetime as dt
import hashlib
import hmac
import json
import logging
import os
import secrets
import sys
import threading
import time
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.dirname(HERE), os.path.dirname(os.path.dirname(HERE))]

from fastapi import Body, Depends, FastAPI, File, Header, HTTPException, Request, UploadFile  # noqa: E402
from fastapi.responses import FileResponse, JSONResponse, Response  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

import wqbus  # noqa: E402
from wqbus import layout as L  # noqa: E402
from wqbus.client import Bus  # noqa: E402
from wqbus.topics import topic, unit_topic  # noqa: E402
from factory import data as F  # noqa: E402
from hub import kpi, mrp  # noqa: E402
from hub import select as lib_select  # noqa: E402
from hub import design as design_web  # noqa: E402
from hub import erp_sso  # noqa: E402
from hub.ai import Assistant, ROLE_NAMES  # noqa: E402
from hub.db import DB  # noqa: E402
from hub.historian import Historian  # noqa: E402
from hub.privacy import actor  # noqa: E402
from hub.mes import MES  # noqa: E402
from hub.teach import Teach  # noqa: E402

log = logging.getLogger("hub")
logging.basicConfig(level=os.environ.get("WQ_LOG", "INFO"), format="%(asctime)s hub %(levelname)s %(message)s")

SECRET = (os.environ.get("WQ_SECRET") or secrets.token_hex(16)).encode()
ROLES = ("planner", "engineer", "operator", "quality", "manager")
STUDENT_ROLES = ("planner", "engineer", "operator", "quality")
# 登录方式（第 3 轮 D2）：local = 填名字进入（自己电脑上用）；wenquest = 问渠账号（线上）
AUTH = os.environ.get("WQ_AUTH", "local")
SSO_URL = os.environ.get("WQ_SSO_URL", "")          # 学习平台核对登录的接口，如 https://learn.<域名>/api/v1/auth/sso
LOGIN_URL = os.environ.get("WQ_LOGIN_URL", "")      # 学习平台登录页，如 https://learn.<域名>/pages/login/login
SSO_COOKIE = "wq_sso"                               # 全站登录凭证（学习平台设置，整个域名共用）
TOKEN_DAYS = float(os.environ.get("WQ_TOKEN_DAYS", "7"))
# AI 工厂助手每人每小时提问上限（D7）；0 = 不限。线上默认 30，自己电脑上默认不限
AI_PER_HOUR = int(os.environ.get("WQ_AI_PER_HOUR", "30" if AUTH == "wenquest" else "0"))
DEFAULT_MODE = os.environ.get("WQ_MODE", "teach")
WEB_DIST = os.environ.get("WQ_WEB_DIST", os.path.join(os.path.dirname(HERE), "web", "dist"))
PUBLISH_ALLOW = ("wq/gearbox/design/",)       # HTTP → 总线网关只放行这些主题（FreeCAD 宏用）


class Hub:
    def __init__(self):
        self.db = DB()
        self.bus = None
        self.ai = None
        self.hist = None
        self.mes = None
        self.teach = None
        self.stop = threading.Event()
        self.last_brief = {}
        self._ncr_sent = set()

    def publish(self, tp, type_, source, data, corr=None, mode=None):
        msg = wqbus.make(type_, source, data, mode=mode or DEFAULT_MODE, corr=corr)
        self.bus.publish_msg(tp, msg)
        # 立即入库，页面马上能读到（总线回来的同一条会按 id 去重）
        self.hist.handle(tp, msg)
        return msg

    def start(self):
        self.db.init()
        self.bus = Bus("wq-hub-" + secrets.token_hex(3))
        self.ai = Assistant(self.db, self.publish)
        self.hist = Historian(self.db, self.on_message)
        self.hist.load()
        self.mes = MES(self.db, self.publish)
        self.teach = Teach(self.db)
        self.bus.subscribe("wq/#", self.hist.handle_raw, raw=True)
        try:
            self.bus.start(timeout=float(os.environ.get("WQ_MQTT_TIMEOUT", "20")))
        except ConnectionError:
            log.exception("总线未就绪，后台继续重连")
        threading.Thread(target=self._loop, daemon=True, name="ai-loop").start()

    def on_message(self, tp, msg):
        t = msg["type"]
        if t == "erp.doc":
            self.ai.on_erp_result(msg)
        elif t == "design.release":
            self.ai.on_design_release(dict(msg, _topic=tp))
        elif t == "quality.measurement" and msg["data"]["result"] == "fail":
            r = self.db.one("select * from ncr where part_serial=%s", (msg["data"]["part_serial"],))
            if r and r["ncr_id"] not in self._ncr_sent:
                self._ncr_sent.add(r["ncr_id"])
                self.publish(topic("quality", "qc-01", "ncr"), "quality.ncr", "hub",
                             {"ncr_id": r["ncr_id"], "part_serial": r["part_serial"], "status": "open",
                              "item": r["item"], "work_order": r["work_order"], "detail": r["detail"]},
                             r["work_order"], msg["mode"])

    def _first_run(self):
        """第一次启动（教学模式、历史库还是空的）：让仿真器载入实验 7 情景，首页一打开就有内容。"""
        if DEFAULT_MODE != "teach" or os.environ.get("WQ_AUTO_SCENARIO", "1") != "1":
            return
        for _ in range(6):
            if self.db.one("select 1 as x from bus_message where mode='teach' and type='erp.doc' limit 1"):
                return
            if self.bus and self.bus._connected.is_set():
                log.info("历史库为空，请仿真器载入实验 7 情景")
                self.mes.command("sim", "load_scenario", "teach", "system", speed=1)
            if self.stop.wait(15):
                return

    def _loop(self):
        """每 20 秒按规则检查一次提醒；每 10 分钟或状况明显变化时重写今日简报。"""
        try:
            self._first_run()
        except Exception:  # noqa: BLE001
            log.exception("载入情景失败")
        while not self.stop.wait(float(os.environ.get("WQ_AI_EVERY_S", "20"))):
            self._prune()
            for mode in self.active_modes():
                try:
                    new = self.ai.evaluate(mode)
                    last = self.last_brief.get(mode, 0)
                    if new or time.time() - last > 600:
                        self.ai.briefing(mode)
                        self.last_brief[mode] = time.time()
                except Exception:  # noqa: BLE001
                    log.exception("AI 巡检出错（%s）", mode)

    _pruned_day = None

    def _prune(self):
        """D9：历史库只保留最近 WQ_HISTORY_DAYS 天（0 = 全部保留），每天清理一次。"""
        days = float(os.environ.get("WQ_HISTORY_DAYS", "0"))
        today = dt.date.today()
        if days <= 0 or self._pruned_day == today:
            return
        self._pruned_day = today
        try:
            for table in ("bus_message", "machine_state_log"):
                self.db.x("delete from {} where ts < now() - make_interval(days => %s)".format(table), (int(days),))
            log.info("历史库已清理 %s 天以前的记录", int(days))
        except Exception:  # noqa: BLE001
            log.exception("清理历史库失败")

    def active_modes(self):
        rows = self.db.q("select distinct mode from bus_message where ts > now() - interval '1 day' and mode is not null")
        return [r["mode"] for r in rows] or [DEFAULT_MODE]


H = Hub()
app = FastAPI(title="问渠数字工厂枢纽 WenQuest Digital Factory Hub", version="1.0.0")


@app.on_event("startup")
def _startup():
    if os.environ.get("WQ_HUB_NO_START") != "1":
        H.start()


@app.on_event("shutdown")
def _shutdown():
    H.stop.set()
    if H.bus:
        H.bus.stop()


# ---------------------------------------------------------------- 登录（统一入口）
def _sign(payload):
    raw = base64.urlsafe_b64encode(json.dumps(payload, ensure_ascii=False).encode()).decode()
    sig = hmac.new(SECRET, raw.encode(), hashlib.sha256).hexdigest()[:32]
    return raw + "." + sig


def user_of(x_wq_token: str = Header(default="")):
    try:
        raw, sig = x_wq_token.split(".")
        if hmac.compare_digest(sig, hmac.new(SECRET, raw.encode(), hashlib.sha256).hexdigest()[:32]):
            u = json.loads(base64.urlsafe_b64decode(raw.encode()))
            if u.get("exp", float("inf")) > time.time():
                u.setdefault("teacher", True)      # 本地版的旧凭证：人人可用全部角色
                return u
    except Exception:  # noqa: BLE001
        pass
    raise HTTPException(401, "请先登录")


def check_allowed(teacher, role, mode):
    """D3：学生只能用教学模式和四个岗位角色；厂长角色、生产模式、教师控制台只给老师。"""
    if role not in ROLES or mode not in ("teach", "prod"):
        raise HTTPException(400, "角色或模式不对")
    if not teacher and (role not in STUDENT_ROLES or mode != "teach"):
        raise HTTPException(403, "厂长角色和生产模式只对老师开放")


def who(u):
    """总线上代表这个人的写法：线上版“角色·匿名编号”，本地版姓名（第 4 轮 C5）。"""
    return actor(u["name"], u.get("role"))


def require_teacher(u):
    if not u.get("teacher"):
        raise HTTPException(403, "只有老师可以做这个操作")


def wenquest_user(cookie):
    """拿浏览器带来的全站登录凭证向学习平台核对身份。返回 {id, fullname, username, teacher} 或 None。"""
    if not cookie or not SSO_URL:
        return None
    import httpx
    try:
        r = httpx.get(SSO_URL, cookies={SSO_COOKIE: cookie}, timeout=10)
    except httpx.HTTPError:
        log.exception("学习平台登录核对失败")
        raise HTTPException(503, "暂时连不上学习平台，请稍后再试")
    if r.status_code != 200:
        return None
    x = r.json().get("user") or {}
    if not x.get("id"):
        return None
    return {"id": x["id"], "fullname": (x.get("fullname") or x.get("username") or "").strip(),
            "username": x.get("username", ""), "teacher": bool(x.get("can_create_courses"))}


def _display_name(w):
    # 实验评分、提议记录按这个名字区分人；加上账号编号，重名的同学也不会混在一起
    return "{}（{}）".format(w["fullname"] or w["username"], w["id"])[:60]


@app.get("/api/login/info")
def login_info(request: Request):
    """登录页用：登录方式、学习平台登录页地址，以及（线上）此人是否已在学习平台登录。"""
    out = {"auth": AUTH, "login_url": LOGIN_URL, "student_roles": STUDENT_ROLES}
    if AUTH == "wenquest":
        w = wenquest_user(request.cookies.get(SSO_COOKIE, ""))
        out["account"] = {"fullname": w["fullname"], "teacher": w["teacher"]} if w else None
    return out


@app.post("/api/login")
def login(request: Request, body: dict = Body(...)):
    mode = body.get("mode", DEFAULT_MODE)
    if AUTH == "wenquest":
        w = wenquest_user(request.cookies.get(SSO_COOKIE, ""))
        if not w:
            raise HTTPException(401, "请先用问渠账号登录")
        teacher = w["teacher"]
        role = body.get("role") or ("manager" if teacher else "planner")
        if not teacher:
            mode = "teach"
        check_allowed(teacher, role, mode)
        u = {"name": _display_name(w), "uid": w["id"], "teacher": teacher, "role": role, "mode": mode,
             "exp": int(time.time() + TOKEN_DAYS * 86400)}
    else:
        name = str(body.get("name", "")).strip()[:40]
        role = body.get("role", "manager")
        if not name:
            raise HTTPException(400, "请填写姓名")
        check_allowed(True, role, mode)
        u = {"name": name, "role": role, "mode": mode, "teacher": True}
    if u["mode"] == "teach":
        H.teach.start(u["name"])
    return {"token": _sign(u), "user": u}


@app.post("/api/me/switch")
def switch(body: dict = Body(...), u=Depends(user_of)):
    role = body.get("role", u["role"])
    mode = body.get("mode", u["mode"])
    check_allowed(u["teacher"], role, mode)
    nu = dict(u, role=role, mode=mode)
    return {"token": _sign(nu), "user": nu}


_ai_calls = {}
_ai_lock = threading.Lock()


def ai_quota(u):
    """D7：AI 工厂助手每人每小时最多 AI_PER_HOUR 次。"""
    if AI_PER_HOUR <= 0:
        return
    now, key = time.time(), u.get("uid") or u["name"]
    with _ai_lock:
        recent = [t for t in _ai_calls.get(key, []) if now - t < 3600]
        if len(recent) >= AI_PER_HOUR:
            wait = int((3600 - (now - recent[0])) // 60) + 1
            raise HTTPException(429, "本小时已问了 {} 次，请 {} 分钟后再问".format(AI_PER_HOUR, wait))
        recent.append(now)
        _ai_calls[key] = recent


@app.get("/api/config")
def config():
    return {
        "mqtt_ws": os.environ.get("WQ_MQTT_WS", "ws://localhost:9001"),
        "erpnext_url": ((os.environ.get("WQ_PUBLIC_URL", "").rstrip("/") + "/api/erp/sso") if AUTH == "wenquest" and erp_sso.enabled()
                        else os.environ.get("WQ_ERPNEXT_URL", "http://localhost:8090")),   # 线上：经单点登录入口（第 7 轮）
        "nodered_url": os.environ.get("WQ_NODERED_URL", "http://localhost:1880"),   # 线上设为空：不对外（D8）
        "auth": AUTH, "login_url": LOGIN_URL,
        "default_mode": DEFAULT_MODE, "roles": ROLE_NAMES, "ai_engine": H.ai.llm.name if H.ai else "rules",
        "tz": str(kpi.TZ), "customers": F.CUSTOMERS, "fg": [{"item_code": "WQR-105", "name": F.ITEMS["WQR-105"][0],
                                                               "price": F.FG_SELLING_PRICE}],
    }


@app.get("/api/routing/{item}")
def routing(item: str):
    from sim.engine import OP_UNITS, routing_for
    if item not in F.BOMS:
        raise HTTPException(404, "没有这个自制件")
    ops = routing_for(item)
    return {"item": item, "name": F.ITEMS[item][0], "routing": F.BOMS[item][0],
            "bom": [{"item_code": c, "qty": q, "name": F.ITEMS[c][0]} for c, q in F.BOMS[item][1]],
            "operations": [{"operation": op, "minutes": m, "units": OP_UNITS[op],
                            "rate_per_hour": kpi.rate_per_hour(OP_UNITS[op][0])} for op, m in ops],
            "std_cost": dict(zip(("material", "operations"), mrp.std_unit_cost(item)))}


@app.get("/api/health")
def health():
    ok_db = bool(H.db.one("select 1 as x"))
    return {"ok": ok_db, "bus": bool(H.bus and H.bus._connected.is_set()),
            "messages": H.db.one("select count(*) as n from bus_message")["n"]}


@app.get("/api/layout")
def get_layout():
    return {"floor": L.FLOOR, "units": {u: {"x": v[0], "y": v[1], "w": v[2], "d": v[3],
                                           "name": wqbus.UNITS[u][1], "en": wqbus.UNITS[u][2]}
                                       for u, v in L.LAYOUT.items()},
            "agv_home": L.AGV_HOME, "aisles": L.AISLES, "cross_x": L.CROSS_X}


# ---------------------------------------------------------------- 看板
@app.get("/api/overview")
def get_overview(u=Depends(user_of)):
    ov = kpi.overview(H.db, None, u["mode"])
    b = H.db.one("select payload from bus_message where type='ai.briefing' and mode=%s order by ts desc limit 1",
                 (u["mode"],))
    ov["briefing"] = b["payload"] if b else None
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=24)
    alerts = H.db.messages(["ai.alert"], since=since, mode=u["mode"], order="desc", limit=40)
    seen, al = set(), []
    for a in alerts:
        k = a["data"].get("key") or a["data"]["title"]
        if k not in seen:
            seen.add(k)
            al.append({"id": a["id"], "ts": a["ts"], **a["data"]})
    ov["alerts"] = al
    ov["proposals"] = [_prop(p) for p in H.db.q(
        "select * from ai_proposal where mode=%s and (status='pending' or decided_at > now() - interval '1 day') "
        "order by created_at desc limit 20", (u["mode"],))]
    ov["todos"] = todos_for(u, ov)
    if u["mode"] == "teach":
        ov["teach"] = H.teach.check(u["name"])
    return ov


def _prop(p):
    return {k: (v.isoformat() if isinstance(v, dt.datetime) else v) for k, v in p.items()}


def todos_for(u, ov):
    """提醒与待办：按角色取不同的东西。"""
    role = u["role"]
    out = []
    if u["mode"] == "teach":
        t = ov.get("teach") or H.teach.status(u["name"])
        for task in t["tasks"]:
            if task["done"]:
                out.append({"kind": "已完成", "tone": "good", "text": task["title"], "src": "任务 · 得 {} 分".format(task["score"]),
                            "act": "查看", "link": "/teach"})
            elif len([x for x in out if x["kind"] == "任务"]) < 2:
                out.append({"kind": "任务", "tone": "task", "text": task["desc"], "src": "实验 7 · " + task["title"],
                            "act": "去做", "link": "/work/" + task["role"]})
        return out[:6]
    for p in ov["proposals"]:
        if p["status"] == "pending" and role in ("planner", "manager"):
            out.append({"kind": "AI 提议", "tone": "info", "text": p["title"], "src": "ai/proposal " + p["proposal_id"],
                        "act": "预览并确认", "proposal_id": p["proposal_id"]})
    for n in ov["quality"]["ncr"]:
        if role in ("quality", "manager"):
            out.append({"kind": "质量", "tone": "bad", "text": "不合格品 {}：{} {} 超差".format(
                n["ncr_id"], n["part_serial"], n["detail"].get("name")), "src": "quality/qc-01 · " + n["ncr_id"],
                "act": "评审", "link": "/work/quality"})
    for a in ov["alerts"][:8]:
        k = a.get("key", "")
        if role == "operator" and not k.startswith(("down:", "tool:")):
            continue
        if role == "quality" and not k.startswith(("trend:", "ncr:")):
            continue
        if role == "planner" and not k.startswith(("late:", "stock:", "down:")):
            continue
        if role == "engineer" and not k.startswith(("release:", "tool:", "trend:")):
            continue
        if k.startswith("ncr:"):
            continue
        out.append({"kind": {"critical": "紧急", "warn": "提醒", "info": "提示"}[a["level"]],
                    "tone": {"critical": "bad", "warn": "warn", "info": "info"}[a["level"]],
                    "text": a["title"] + "：" + (a.get("detail") or ""), "src": (a.get("evidence") or [{}])[0].get("topic", "ai/alert").replace("wq/gearbox/", ""),
                    "act": "查看", "hint": a.get("action_hint")})
    return out[:8]


@app.get("/api/history")
def history(type: str = None, topic_like: str = None, corr: str = None, hours: float = 24, limit: int = 100,
            u=Depends(user_of)):
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=min(hours, 24 * 60))
    rows = H.db.messages([type] if type else None, since=since, mode=u["mode"], topic_like=topic_like, corr=corr,
                         limit=min(limit, 500), order="desc")
    return [{"id": r["id"], "ts": r["ts"], "topic": r["_topic"], "type": r["type"], "source": r["source"],
             "corr": r.get("corr"), "data": r["data"]} for r in rows]


@app.get("/api/message/{mid}")
def message(mid: str, u=Depends(user_of)):
    r = H.db.one("select topic, payload from bus_message where id::text=%s", (mid,))
    if not r:
        raise HTTPException(404, "没有这条消息")
    return dict(r["payload"], topic=r["topic"])


@app.get("/api/machine/{unit}")
def machine_detail(unit: str, u=Depends(user_of)):
    if unit not in wqbus.UNITS:
        raise HTTPException(404, "没有这台设备")
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=24)
    evs = H.db.messages(["machine.event"], since=since, mode=u["mode"], topic_like=unit_topic(unit, "event"),
                        limit=60, order="desc")
    st = H.db.latest_per_topic(["machine.status"], mode=u["mode"], topic_like=unit_topic(unit, "status"))
    ov = kpi.Overview(H.db, None, u["mode"])
    return {"unit": unit, "name": wqbus.UNITS[unit][1], "status": next(iter(st.values()), None),
            "events": evs, "oee": ov.oee()["machines"].get(unit), "rate_per_hour": kpi.rate_per_hour(unit)}


@app.get("/api/work_orders")
def work_orders(u=Depends(user_of)):
    ov = kpi.Overview(H.db, None, u["mode"])
    out = []
    for w in sorted(ov.wos, key=lambda w: w["data"]["name"], reverse=True):
        d = w["data"]
        released = bool(H.db.one("select 1 as x from bus_message where type='machine.cmd' and corr=%s and "
                                 "payload->'data'->>'command'='dispatch' limit 1", (d["name"],)))
        out.append(dict(d, produced=ov.produced(d), released=released, started=d["name"] in ov.started_wos,
                        demo=bool(d.get("demo"))))
    return out


@app.get("/api/work_orders/{name}/cost")
def wo_cost(name: str, u=Depends(user_of)):
    c = mrp.wo_cost(H.db, name, u["mode"])
    if not c:
        raise HTTPException(404, "该工单还没有加工记录")
    mat, ops = mrp.std_unit_cost(c["item"])
    c["std_unit"] = {"material": mat, "operations": ops}
    return c


@app.get("/api/sales_orders")
def sales_orders(u=Depends(user_of)):
    return [s["data"] for s in H.db.erp_docs("Sales Order", u["mode"])]


# ---------------------------------------------------------------- 计划：算料与提议
@app.post("/api/plan/order")
def plan(body: dict = Body(...), u=Depends(user_of)):
    try:
        return mrp.plan_order(H.db, body.get("customer"), body.get("item", "WQR-105"), int(body["qty"]),
                              body["delivery_date"], u["mode"])
    except (KeyError, ValueError) as e:
        raise HTTPException(400, "订单信息不完整：{}".format(e))


@app.post("/api/proposals")
def create_proposal(body: dict = Body(...), u=Depends(user_of)):
    """计划员表单提交：与 AI 起草的提议走同一流程（预览 → 确认 → 桥接写入 ERPNext）。"""
    action = body.get("action", "create_order_and_plan")
    if action == "create_order_and_plan":
        pv = mrp.plan_order(H.db, body.get("customer"), body.get("item", "WQR-105"), int(body["qty"]),
                            body["delivery_date"], u["mode"])
        from hub.ai import _order_title
        title = _order_title(pv)
    elif action == "purchase_request":
        pv = {"material_requests": body["material_requests"]}
        title = "请购：" + "、".join("{} {}".format(x["item_code"], x["qty"]) for x in body["material_requests"])
    elif action == "release_work_order":
        pv = {"work_order": body["work_order"]}
        title = "下达工单 " + body["work_order"]
    else:
        raise HTTPException(400, "不支持的提议 " + action)
    pid = H.ai.propose(action, pv, u["mode"], u["name"], title, source="workbench/" + who(u), role=u["role"])
    return {"proposal_id": pid, "preview": pv, "title": title}


@app.get("/api/proposals")
def list_proposals(u=Depends(user_of)):
    return [_prop(p) for p in H.db.q("select * from ai_proposal where mode=%s order by created_at desc limit 50",
                                     (u["mode"],))]


@app.get("/api/proposals/{pid}")
def get_proposal(pid: str, u=Depends(user_of)):
    p = H.db.one("select * from ai_proposal where proposal_id=%s", (pid,))
    if not p:
        raise HTTPException(404, "没有这个提议")
    out = _prop(p)
    out["results"] = [m["data"] for m in H.db.messages(["erp.doc"], corr=pid)]
    return out


@app.post("/api/proposals/{pid}/{decision}")
def decide(pid: str, decision: str, u=Depends(user_of)):
    if decision not in ("confirm", "reject"):
        raise HTTPException(404)
    executors = {"release_work_order": lambda p: {"dispatched": H.mes.release(p["preview"]["work_order"], p["mode"], who(u))}}
    try:
        st = H.ai.decide(pid, u["name"], decision == "confirm", executors, role=u["role"])
    except KeyError:
        raise HTTPException(404, "没有这个提议")
    except ValueError as e:
        raise HTTPException(409, str(e))
    return {"status": st}


# ---------------------------------------------------------------- AI 助手
@app.post("/api/ai/chat")
def ai_chat(body: dict = Body(...), u=Depends(user_of)):
    msgs = [m for m in body.get("messages", []) if m.get("role") in ("user", "assistant") and m.get("content")]
    if not msgs:
        raise HTTPException(400, "请输入问题")
    ai_quota(u)
    return H.ai.chat(msgs, u["mode"], u["role"], u["name"])


_catalog = lib_select.Catalog()


@app.post("/api/library/select")
def library_select(body: dict = Body(...), u=Depends(user_of)):
    """AI 选型（零件库第 5 轮 P10③）：只从零件库里挑，答案里的编号逐个核对"""
    q = (body.get("question") or "").strip()
    if not q:
        raise HTTPException(400, "请用一句话说需求，例如：35 mm 轴、1450 r/min、径向载荷为主用什么轴承")
    if len(q) > 500:
        raise HTTPException(400, "需求请写短一些（500 字以内）")
    ai_quota(u)
    llm = H.ai.llm if getattr(H, "ai", None) else None
    try:
        return lib_select.answer(_catalog, llm, q)
    except Exception as ex:  # noqa: BLE001 —— 模型出错时退回规则回答
        log.warning("AI 选型出错，改用规则：%s", ex)
        return lib_select.answer(_catalog, None, q)


@app.post("/api/ai/briefing/refresh")
def refresh_briefing(u=Depends(user_of)):
    ai_quota(u)
    H.ai.evaluate(u["mode"])
    return H.ai.briefing(u["mode"])


# ---------------------------------------------------------------- 车间执行
@app.post("/api/mes/release")
def release(body: dict = Body(...), u=Depends(user_of)):
    try:
        return {"dispatched": H.mes.release(body["work_order"], u["mode"], who(u), body.get("units"))}
    except KeyError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(409, str(e))


@app.post("/api/mes/cmd")
def mes_cmd(body: dict = Body(...), u=Depends(user_of)):
    unit, cmd = body.get("unit"), body.get("command")
    allowed = {"start", "pause", "reset"} | ({"inject_fault", "set_speed", "load_scenario"} if u["mode"] == "teach" else set())
    if cmd not in allowed:
        raise HTTPException(403, "不允许的指令 {}".format(cmd))
    if cmd in ("inject_fault", "set_speed", "load_scenario"):
        require_teacher(u)                 # 教师控制台（D3）
    extra = {k: v for k, v in body.items() if k in ("minutes", "reason", "kind", "speed")}
    try:
        H.mes.command(unit, cmd, u["mode"], who(u), body.get("work_order"), body.get("operation"), **extra)
    except KeyError as e:
        raise HTTPException(404, str(e))
    return {"sent": True}


@app.post("/api/ncr/{ncr_id}")
def ncr_decide(ncr_id: str, body: dict = Body(...), u=Depends(user_of)):
    disp = body.get("disposition")
    if disp not in ("rework", "scrap", "use_as_is"):
        raise HTTPException(400, "处置只能是返修、报废或让步接收")
    r = H.db.one("select * from ncr where ncr_id=%s", (ncr_id,))
    if not r:
        raise HTTPException(404, "没有这张不合格品单")
    H.db.x("update ncr set status=%s, decided_by=%s, decided_at=now() where ncr_id=%s", (disp, u["name"], ncr_id))
    H.publish(topic("quality", "qc-01", "ncr"), "quality.ncr", "workbench/" + who(u),
              {"ncr_id": ncr_id, "part_serial": r["part_serial"], "status": disp, "decided_by": who(u),
               "note": body.get("note", ""), "item": r["item"], "work_order": r["work_order"]}, r["work_order"], u["mode"])
    return {"status": disp}


@app.get("/api/ncr")
def ncr_list(u=Depends(user_of)):
    return [_prop(r) for r in H.db.q("select * from ncr where mode=%s or mode is null order by created_at desc limit 100",
                                     (u["mode"],))]


@app.get("/api/quality/measurements")
def measurements(characteristic: str = "bearing_seat_d35", limit: int = 50, u=Depends(user_of)):
    rows = H.db.messages(["quality.measurement"], mode=u["mode"], order="desc", limit=500)
    rows = [r for r in rows if r["data"]["characteristic"] == characteristic][:limit]
    return list(reversed([{"id": r["id"], "ts": r["ts"], **r["data"]} for r in rows]))


# ---------------------------------------------------------------- 设计与文件
@app.post("/api/files")
async def upload(file: UploadFile = File(...), u=Depends(user_of)):
    data = await file.read()
    if len(data) > 50 * 1024 * 1024:
        raise HTTPException(413, "文件超过 50 MB")
    sha = hashlib.sha256(data).hexdigest()
    H.db.x("insert into stored_file (sha256, name, mime, size, content) values (%s,%s,%s,%s,%s) "
           "on conflict (sha256) do nothing", (sha, file.filename, file.content_type, len(data), data))
    return {"sha256": sha, "name": file.filename, "size": len(data), "url": "/api/files/" + sha}


@app.get("/api/files/{sha}")
def download(sha: str):
    r = H.db.one("select name, mime, content from stored_file where sha256=%s", (sha,))
    if not r:
        raise HTTPException(404, "没有这个文件")
    return Response(bytes(r["content"]), media_type=r["mime"] or "application/octet-stream",
                    headers={"Content-Disposition": "inline; filename*=UTF-8''" + _quote(r["name"])})


def _quote(s):
    import urllib.parse
    return urllib.parse.quote(s)


@app.post("/api/bus/publish")
def http_publish(body: dict = Body(...), u=Depends(user_of)):
    """给没有 MQTT 客户端的工具（FreeCAD 宏）用：校验后原样发到总线。只放行设计类主题。"""
    tp, msg = body.get("topic", ""), body.get("message")
    if not tp.startswith(PUBLISH_ALLOW):
        raise HTTPException(403, "这个接口只能发布设计类主题")
    if isinstance(msg, dict) and isinstance(msg.get("data"), dict) and "author" in msg["data"]:
        msg = dict(msg, data=dict(msg["data"], author=who(u)))       # 作者也不以姓名上总线（C5）
    try:
        msg = wqbus.validate(dict(msg, mode=u["mode"]))
    except (wqbus.ValidationError, TypeError) as e:
        raise HTTPException(422, "消息不合规范：{}".format(e))
    H.bus.publish_msg(tp, msg)
    H.hist.handle(tp, msg)
    return {"id": msg["id"]}


@app.get("/api/design/{item}")
def design(item: str, u=Depends(user_of)):
    rel = H.db.messages(["design.release"], mode=u["mode"], order="desc", limit=20)
    gc = H.db.messages(["design.gcode"], mode=u["mode"], order="desc", limit=20)
    return {"releases": [dict(r["data"], id=r["id"], ts=r["ts"]) for r in rel if r["data"]["item"] == item],
            "gcode": [dict(r["data"], id=r["id"], ts=r["ts"]) for r in gc if r["data"]["item"] == item]}


# 网页设计台（第 6 轮 W2、W3）：不装 FreeCAD 也能改参数、校核、发布
def _design_item(item):
    if item != design_web.ITEM:
        raise HTTPException(404, "网页设计台目前只支持 {}".format(design_web.ITEM))


@app.get("/api/design/{item}/params")
def design_params(item: str, u=Depends(user_of)):
    """现行参数：本模式最新发布版的参数；没发布过用工厂数据里的第 1 版"""
    _design_item(item)
    rel = [r for r in H.db.messages(["design.release"], mode=u["mode"], order="desc", limit=50) if r["data"]["item"] == item]
    params = rel[0]["data"].get("params") if rel else None
    params = design_web.normalize(params) if params else design_web.normalize(design_web.defaults())
    return {"item": item, "revision": rel[0]["data"]["revision"] if rel else 1, "params": params,
            "check": design_web.check(params), "limits": design_web.LIMITS}


@app.post("/api/design/{item}/check")
def design_check(item: str, body: dict = Body(...), u=Depends(user_of)):
    _design_item(item)
    try:
        return design_web.check(design_web.normalize(body.get("params") or {}))
    except ValueError as e:
        raise HTTPException(422, str(e))


@app.post("/api/design/{item}/publish")
def design_publish(item: str, body: dict = Body(...), u=Depends(user_of)):
    _design_item(item)

    def emit(tp, type_, data):
        msg = wqbus.make(type_, "web-cad", data, mode=u["mode"])
        H.bus.publish_msg(tp, msg)
        H.hist.handle(tp, msg)
    try:
        params = design_web.normalize(body.get("params") or {})
        return design_web.publish(H.db, emit, params, who(u), u["mode"], (body.get("change_note") or "").strip()[:200])
    except ValueError as e:
        raise HTTPException(422, str(e))


# ---------------------------------------------------------------- ERPNext 单点登录（第 7 轮）
_codes = erp_sso.Codes()


def _sso_person(request, wq_token):
    """当前是谁：线上看学习平台登录（没登录返回跳转），本地版看工作台凭证。返回 (person, redirect)"""
    from fastapi.responses import RedirectResponse
    if AUTH == "wenquest":
        w = wenquest_user(request.cookies.get(SSO_COOKIE, ""))
        if not w:                                    # 还没登录学习平台：先去登录，登录后回到这里
            proto = request.headers.get("x-forwarded-proto") or request.url.scheme
            here = "{}://{}{}?{}".format(proto, request.headers.get("host") or request.url.netloc,
                                         request.url.path, request.url.query)
            return None, RedirectResponse((LOGIN_URL or "/") + "?back=" + urllib.parse.quote(here, safe=""), 302)
        return {"uid": w["id"], "name": w["fullname"] or w["username"], "teacher": w["teacher"]}, None
    try:                                             # 本地版（和 CI 演练）：用工作台凭证代表身份
        u = user_of(wq_token)
    except HTTPException:
        raise HTTPException(401, "本地版请带工作台登录凭证 wq_token")
    return {"uid": erp_sso.local_uid(u["name"]), "name": u["name"], "teacher": u.get("teacher", True)}, None


def _sso_finish(person, redirect_uri, state):
    """在 ERPNext 建好账号，带一次性授权码回到 ERPNext"""
    from fastapi.responses import RedirectResponse
    ident = erp_sso.erp_identity(person, erp_sso.config()["user_domain"])
    try:
        erp_sso.provision(ident)
    except Exception as e:  # noqa: BLE001
        log.exception("ERPNext 建账号失败")
        raise HTTPException(502, "ERPNext 暂时不能登录：{}".format(e))
    code = _codes.issue(ident, redirect_uri)
    return RedirectResponse("{}?{}".format(redirect_uri, urllib.parse.urlencode({"code": code, "state": state})), 302)


@app.get("/api/oauth/authorize")
def oauth_authorize(request: Request, client_id: str = "", redirect_uri: str = "", state: str = "",
                    response_type: str = "code", wq_token: str = ""):
    """ERPNext 登录页跳过来：核对问渠账号 → 在 ERPNext 建好账号 → 带一次性授权码回去"""
    if client_id != erp_sso.CLIENT_ID or response_type != "code" or not erp_sso.valid_redirect(redirect_uri):
        raise HTTPException(400, "登录请求不合规范")
    if not erp_sso.enabled():
        raise HTTPException(503, "ERPNext 单点登录还没有配置")
    person, go = _sso_person(request, wq_token)
    return go or _sso_finish(person, redirect_uri, state)


@app.get("/api/erp/sso")
def erp_sso_start(request: Request, next: str = "", wq_token: str = "", go: int = 0):
    """工作台“ERPNext”入口（第 7 轮补）：不靠 ERPNext 登录页上的脚本（浏览器可能缓存了旧脚本），
    由枢纽向 ERPNext 要一个登录请求编号（state），直接走完授权，浏览器一步进到 ERPNext。
    先回一个“正在进入”的等待页（建账号、登录、打开 ERPNext 要几秒），再自动接着走（go=1）"""
    if not go:
        from fastapi.responses import HTMLResponse
        q = dict(request.query_params, go="1")
        return HTMLResponse(ERP_WAIT_PAGE.replace("__URL__", json.dumps(request.url.path + "?" + urllib.parse.urlencode(q))))
    if not erp_sso.enabled():
        raise HTTPException(503, "ERPNext 单点登录还没有配置")
    person, go = _sso_person(request, wq_token)
    if go:
        return go
    try:
        auth = erp_sso.login_request(next if next.startswith("/") else "")
    except Exception as e:  # noqa: BLE001
        log.exception("向 ERPNext 要登录请求失败")
        raise HTTPException(502, "ERPNext 暂时不能登录：{}".format(e))
    return _sso_finish(person, auth["redirect_uri"], auth["state"])


ERP_WAIT_PAGE = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>正在进入 ERPNext…</title>
<style>
body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#F4F6F8;
 font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;color:#1F2A33}
.box{width:min(420px,90vw);text-align:center}
h1{font-size:18px;font-weight:600;margin:0 0 6px}
p{font-size:13px;color:#5B6B78;margin:0 0 18px;min-height:1.4em}
.bar{height:6px;border-radius:3px;background:#DDE3E8;overflow:hidden}
.bar i{display:block;height:100%;width:0;background:#1E6A7A;border-radius:3px;transition:width .6s ease}
</style></head><body><div class="box">
<h1>正在进入 ERPNext</h1><p id="t">核对问渠账号…</p><div class="bar"><i id="b"></i></div>
</div><script>
var steps=[[8,"核对问渠账号…"],[30,"准备你的 ERPNext 账号…"],[55,"登录 ERPNext…"],[75,"打开 ERPNext 工作台（第一次会慢一些）…"],[90,"快好了…"]];
var k=0,b=document.getElementById("b"),t=document.getElementById("t");
function tick(){if(k<steps.length){b.style.width=steps[k][0]+"%";t.textContent=steps[k][1];k++;setTimeout(tick,k<3?900:2500);}}
tick();setTimeout(function(){location.replace(__URL__);},150);
</script></body></html>"""


@app.post("/api/oauth/token")
async def oauth_token(request: Request):
    """ERPNext 服务器用授权码和密钥换令牌（表单提交）"""
    f = await request.form()
    if not erp_sso.check_client(f.get("client_id"), f.get("client_secret")):
        return JSONResponse({"error": "invalid_client"}, 401)
    if f.get("grant_type") != "authorization_code":
        return JSONResponse({"error": "unsupported_grant_type"}, 400)
    ident = _codes.take(f.get("code", ""), f.get("redirect_uri", ""))
    if not ident:
        return JSONResponse({"error": "invalid_grant"}, 400)
    key = erp_sso.config()["secret"].encode()
    return {"access_token": erp_sso.sign_token(ident, key), "token_type": "Bearer", "expires_in": erp_sso.TOKEN_TTL}


@app.get("/api/oauth/userinfo")
def oauth_userinfo(authorization: str = Header(default="")):
    key = erp_sso.config()["secret"].encode()
    body = erp_sso.read_token(authorization.replace("Bearer ", "", 1).strip(), key) if key else None
    if not body:
        return JSONResponse({"error": "invalid_token"}, 401)
    return {k: body[k] for k in ("sub", "email", "email_verified", "name", "given_name")}


@app.get("/api/freecad/pack.zip")
def freecad_pack(request: Request, x_wq_token: str = Header(default=""), u=Depends(user_of)):
    """进阶：桌面 FreeCAD 宏包（第 6 轮 W5）。工作台地址、本人凭证、模式已填进 wq_publish.py，解压即用"""
    import io
    import zipfile
    proto = request.headers.get("x-forwarded-proto") or request.url.scheme
    base = "{}://{}".format(proto, request.headers.get("host") or request.url.netloc)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name in ("wq_shaft.py", "wq_publish.py", "wq_drawing.py", "wq_cam_keyway.py", "wq_library.py"):
            text = open(os.path.join(design_web.FREECAD_DIR, name), encoding="utf-8").read()
            if name == "wq_publish.py":
                text = (text.replace('os.environ.get("WQ_HUB_URL", "http://localhost:8100")', 'os.environ.get("WQ_HUB_URL", {!r})'.format(base))
                        .replace('os.environ.get("WQ_USER", "工艺员")', 'os.environ.get("WQ_USER", {!r})'.format(who(u)))
                        .replace('os.environ.get("WQ_MODE", "teach")', 'os.environ.get("WQ_MODE", {!r})'.format(u["mode"]))
                        .replace('os.environ.get("WQ_TOKEN", "")', 'os.environ.get("WQ_TOKEN", {!r})'.format(x_wq_token)))
            if name == "wq_library.py":
                text = text.replace('"https://factory.wenquestrobotics.com"', repr(base))
            z.writestr("wenquest-freecad/" + name, text)
        z.writestr("wenquest-freecad/使用说明.txt", FREECAD_README.format(base=base, mode="教学" if u["mode"] == "teach" else "生产"))
    return Response(buf.getvalue(), media_type="application/zip",
                    headers={"Content-Disposition": "attachment; filename=wenquest-freecad.zip"})


FREECAD_README = """问渠数字工厂 · 桌面 FreeCAD 宏包（进阶，选做）

不想装软件的话，直接用“设计与工艺”页上的“在线设计”即可，效果相同。

1. 安装 FreeCAD 1.1（https://www.freecad.org/downloads.php），装好后打开。
2. 把本压缩包解压到任意文件夹，例如“文档\\wenquest-freecad”。
3. FreeCAD 菜单：宏 → 宏…，在“用户宏的位置”里选这个文件夹。
4. 改设计：在宏列表里选 wq_shaft.py → 编辑，修改 PARAMS（例如键槽长 45 → 42），保存。
5. 发布：选 wq_publish.py → 执行。成功后回到 {base}/work/engineer 刷新，能看到新版本、零件图和 G 代码。
6. 插入零件库标准件：执行 wq_library.py，搜索 6207 等编号。

说明：wq_publish.py 里已经填好了工作台地址和你的登录凭证（{mode}模式，7 天内有效）。
发布时提示“请先登录”，说明凭证过期了：回到“设计与工艺”页重新下载宏包即可。
不要把这个宏包转给别人——别人用它发布会记在你名下。
"""


# ---------------------------------------------------------------- 教学
@app.get("/api/teach")
def teach_status(u=Depends(user_of)):
    if u["mode"] != "teach":
        raise HTTPException(409, "生产模式没有实验任务")
    return H.teach.check(u["name"])


@app.post("/api/teach/{tid}")
def teach_answer(tid: str, body: dict = Body(...), u=Depends(user_of)):
    if u["mode"] != "teach":
        raise HTTPException(409, "生产模式没有实验任务")
    try:
        return H.teach.answer(u["name"], tid, body)
    except KeyError:
        raise HTTPException(404, "这个任务不用提交答案，系统会自动检查")


@app.post("/api/scenario/reset")
def teach_reset(body: dict = Body(default={}), u=Depends(user_of)):
    """重置教学情景：清空教学模式的历史，让仿真器重新载入实验 7 情景。只有“厂长”角色（教师）能做。"""
    require_teacher(u)
    if u["role"] != "manager":
        raise HTTPException(403, "请用厂长（教师）角色重置")
    H.db.x("delete from bus_message where mode='teach'")
    H.db.x("delete from machine_state_log where mode='teach'")
    H.db.x("delete from ncr where mode='teach' or mode is null")
    H.db.x("delete from ai_proposal where mode='teach'")
    if body.get("scores"):
        H.db.x("delete from task_result")
    H.hist._last_state = {k: v for k, v in H.hist._last_state.items() if k[1] != "teach"}
    H.hist._failed_parts.clear()
    H.ai._sent = {k: v for k, v in H.ai._sent.items() if k[0] != "teach"}
    H.mes.command("sim", "load_scenario", "teach", who(u), speed=float(body.get("speed", 1)))
    return {"reset": True}


# ---------------------------------------------------------------- 零件库文件（第 2 轮 L14）
from hub import library as _library  # noqa: E402
_library.mount(app)

# ---------------------------------------------------------------- 课程接口（第 4 轮）
from hub import course as _course  # noqa: E402
_course.mount(app, H)


# ---------------------------------------------------------------- 网页
if os.path.isdir(WEB_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(WEB_DIST, "assets")), name="assets")

    @app.get("/{path:path}")
    def spa(path: str):
        if path.startswith("api/") or path.startswith("library/"):
            return JSONResponse({"detail": "Not Found"}, 404)
        f = os.path.join(WEB_DIST, path)
        if path and os.path.isfile(f):
            return FileResponse(f)
        if path.startswith("embed/"):            # 嵌入式 3D 车间（第 4 轮 C8）：只许学习平台和本站嵌入
            anc = " ".join(["'self'"] + [o for o in os.environ.get("WQ_EMBED_ORIGINS", os.environ.get(
                "WQ_LIBRARY_ORIGINS", "")).split(",") if o.strip()] + ["http://localhost:*", "http://127.0.0.1:*"])
            return FileResponse(os.path.join(WEB_DIST, "index.html"),
                                headers={"Content-Security-Policy": "frame-ancestors " + anc, "Cache-Control": "no-cache"})
        return FileResponse(os.path.join(WEB_DIST, "index.html"))

