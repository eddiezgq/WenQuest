# -*- coding: utf-8 -*-
"""数字工厂界面截图（第 13 轮 8.8，R5）：在本机起一套教学用数字工厂，灌测试数据，用 Playwright 以教师、学生两种账号截图。

    python3 textbook/tools/factory_shots.py mfgtech            # 全部
    python3 textbook/tools/factory_shots.py mfgtech --only 51   # 只截第 51 章的

要本机有 PostgreSQL（默认 postgresql://postgres:wq@localhost:5432，可用 --dsn 或环境变量 WQ_SHOTS_DSN 改），程序新建一个临时库
wq_shots（每次重建）；不接 ERPNext、MQTT。输出 textbook/<书>/shots/<名称>.png 和 shots/清单.yaml（页面、账号、数据来源、日期），
书中由各章的插图程序把截图包成插图。测试数据全部来自仓库：参照工艺规程 std/SH-301_process.yaml，以及按任务单 TS-51-1～53-1 要求
“故意改坏”的三个变体（改法见 VARIANTS）；任务单内容取自 textbook/<书>/ch*/task/*.yaml。账号用“教师”“学生甲”，不出现真实人名。
"""
from __future__ import annotations

import argparse
import base64
import copy
import datetime as dt
import hashlib
import hmac
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
DIGITAL = REPO / "factory" / "digital"
SECRET = "shots-secret"
TASK_KEY = "shots-key"
PORT = 8137
BASE = f"http://127.0.0.1:{PORT}"
STUDENT = {"name": "学生甲", "uid": "S001", "teacher": False, "role": "engineer", "mode": "teach"}


# ---------------------------------------------------------------- 故意改坏的工艺规程（与任务单的要求一致）
def _op(plan, seq):
    return next(o for o in plan["operations"] if o["seq"] == seq)


def v_locate(plan):
    """TS-51-1：把定位外圆的公差 Td 改为 0.3 mm（相当于在不控制公差的粗车外圆上定位）"""
    _op(plan, 50)["locate_check"]["Td"] = 0.3
    return "工序 50 的 locate_check 中 Td 由 0.039 改为 0.3（TS-51-1 的“故意改坏”）"


def v_fixture(plan):
    """TS-52-1：工序 50 写入自己的夹具数据，拧紧扭矩改为 1 N·m（hand_force 10、wrench 100）"""
    fx = yaml.safe_load((DIGITAL / "std" / "JJ-301-50_fixture.yaml").read_text(encoding="utf-8"))
    fx["clamping"]["hand_force"] = 10
    _op(plan, 50)["fixture"] = fx
    return "工序 50 写入夹具数据（同 JJ-301-50），hand_force 由 50 改为 10，即拧紧扭矩 1 N·m（TS-52-1 的“故意改坏”）"


def v_chart(plan):
    """TS-53-1：跟踪图第 40.3 刀（工序 40 总长）的公差改为 ±0.3"""
    c = next(c for c in plan["tolerance_chart"]["cuts"] if abs(c["seq"] - 40.3) < 1e-9)
    c["es"], c["ei"] = 0.3, -0.3
    return "tolerance_chart 第 40.3 刀（工序 40 总长）的公差由 ±0.2 改为 ±0.3（TS-53-1 的“故意改坏”）"


def v_grind(plan):
    """第 55 章：工序 60 的粗磨切深 0.01 → 0.04 mm、精磨 0.005 → 0.02 mm，取消精磨后的光磨（图 55.7.7）"""
    ps = _op(plan, 60)["grinding"]["passes"]
    ps[0]["ap"], ps[1]["ap"], ps[1]["sparkout"] = 0.04, 0.02, 0
    return "工序 60 粗磨切深 0.01 → 0.04 mm、精磨 0.005 → 0.02 mm，取消光磨（第 55 章的“故意改坏”）"


VARIANTS = {"locate": v_locate, "fixture": v_fixture, "chart": v_chart, "grind": v_grind}


# ---------------------------------------------------------------- 数字工厂
def _sign(payload):          # 与 hub/app.py 的 _sign 相同（同一个 WQ_SECRET）
    raw = base64.urlsafe_b64encode(json.dumps(payload, ensure_ascii=False).encode()).decode()
    return raw + "." + hmac.new(SECRET.encode(), raw.encode(), hashlib.sha256).hexdigest()[:32]


def call(method, path, body=None, token=None, key=None):
    h = {"content-type": "application/json"}
    if token:
        h["x-wq-token"] = token
    if key:
        h["authorization"] = "Bearer " + key
    req = urllib.request.Request(BASE + path, method=method, headers=h,
                                 data=None if body is None else json.dumps(body, ensure_ascii=False).encode())
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            t = r.read().decode()
            return json.loads(t) if t and r.headers.get_content_type() == "application/json" else t
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{method} {path} → {e.code}: {e.read().decode()[:300]}") from None


def upload(path, token, filename, data):
    """multipart 上传一个文件（任务单的“上传文件”交付物）"""
    bnd = "----wqshots" + hashlib.md5(data).hexdigest()
    body = (f"--{bnd}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\n"
            "Content-Type: application/octet-stream\r\n\r\n").encode() + data + f"\r\n--{bnd}--\r\n".encode()
    req = urllib.request.Request(BASE + path, method="POST", data=body,
                                 headers={"x-wq-token": token, "content-type": f"multipart/form-data; boundary={bnd}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def sample_docx(title, paras):
    """测试用的交付物（Word）：标题加几段说明，注明是截图用的示例"""
    import io
    import docx
    d = docx.Document()
    d.add_heading(title, 1)
    for t in paras:
        d.add_paragraph(t)
    d.add_paragraph("（数字工厂界面截图用的示例文件，不是答案。）")
    b = io.BytesIO()
    d.save(b)
    return b.getvalue()


def fresh_db(dsn):
    import psycopg
    with psycopg.connect(dsn.rsplit("/", 1)[0] + "/postgres", autocommit=True) as c:
        c.execute("drop database if exists wq_shots with (force)")
        c.execute("create database wq_shots")
    return dsn.rsplit("/", 1)[0] + "/wq_shots"


def start_hub(db):
    env = dict(os.environ, WQ_DB=db, WQ_SECRET=SECRET, WQ_FACTORY_TASK_KEY=TASK_KEY, WQ_AUTO_SCENARIO="0", WQ_MQTT_TIMEOUT="1",
               WQ_AUTH="local", WQ_MODE="teach")
    log = open(REPO / "textbook" / "build" / "factory_shots_hub.log", "w")
    p = subprocess.Popen([sys.executable, "-m", "uvicorn", "hub.app:app", "--host", "127.0.0.1", "--port", str(PORT)],
                         cwd=DIGITAL, env=env, stdout=log, stderr=subprocess.STDOUT)
    for _ in range(90):
        time.sleep(1)
        if p.poll() is not None:
            raise RuntimeError("数字工厂没有起来，见 textbook/build/factory_shots_hub.log")
        try:
            call("POST", "/api/login", {"name": "教师", "role": "engineer", "mode": "teach"})
            return p
        except Exception:  # noqa: BLE001
            continue
    p.terminate()
    raise RuntimeError("数字工厂 90 秒内没有响应")


def seed(book, only=None):
    """灌测试数据：学生提交参照工艺规程和三个变体，下达任务单 TS-50-1～53-1，学生在任务单里选自己的工艺规程。"""
    teacher = call("POST", "/api/login", {"name": "教师", "role": "engineer", "mode": "teach"})["token"]
    student = _sign(STUDENT)
    ref = call("GET", "/api/process/reference/SH-301", token=student)["yaml"]
    subs, notes = {}, {}
    s = call("POST", "/api/process/check", {"yaml": ref, "submit": True, "note": "按参照工艺规程提交"}, token=student)
    subs["ref"] = s["id"]
    for k, fn in VARIANTS.items():
        plan = yaml.safe_load(ref)
        notes[k] = fn(plan)
        s = call("POST", "/api/process/check", {"yaml": yaml.safe_dump(plan, allow_unicode=True, sort_keys=False), "submit": True,
                                                "note": notes[k]}, token=student)
        subs[k] = s["id"]
    tasks = {}
    root = REPO / "textbook" / book
    for ch, code, link in ((50, "TS-50-1", None), (51, "TS-51-1", "ref"), (52, "TS-52-1", "ref"), (53, "TS-53-1", "ref")):
        spec = yaml.safe_load((root / f"ch{ch}" / "task" / f"ts{ch}_1.yaml").read_text(encoding="utf-8"))
        spec.update(book=book, no=f"{ch}.1")
        due = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=10)).isoformat()
        tid = call("POST", "/api/tasks/course/issue", {"spec": spec, "course_id": 101, "course_name": "机械制造技术（示例班）",
                                                       "due": due, "issued_by": "教师"}, key=TASK_KEY)["id"]
        tasks[ch] = tid
        if link:
            i = next(n for n, x in enumerate(spec["交付物"]) if x.get("类型") == "工艺规程")
            call("POST", f"/api/tasks/{tid}/deliverables/{i}/link", {"process": subs[link]}, token=student)
    # 第 52 章截老师审阅页：学生把其余交付物也交上（示例 Word 文件），再提交审批
    spec52 = yaml.safe_load((root / "ch52" / "task" / "ts52_1.yaml").read_text(encoding="utf-8"))
    for i, x in enumerate(spec52["交付物"]):
        if x.get("类型", "文件") == "文件":
            upload(f"/api/tasks/{tasks[52]}/deliverables/{i}/file", student, f"TS-52-1_{i + 1}.docx",
                   sample_docx(x["名称"][0], [x["验收"][0]]))
    call("POST", f"/api/tasks/{tasks[52]}/submit", {}, token=student)
    rev = call("GET", f"/api/tasks/{tasks[52]}/submissions", token=teacher)["submissions"][0]["id"]
    d = {"teacher": teacher, "student": student, "subs": subs, "notes": notes, "tasks": tasks, "review52": rev}
    if not only or "54" in only:
        d.update(seed54(teacher, student))
    if not only or "55" in only:      # 第 55 章另起一批（只截第 55 章时不灌第 54 章的数据，两章的控制图互不干扰）
        d.update(seed55(teacher, student))
    if not only or "56" in only:
        d.update(seed56(book, teacher, student))
    return d


# ---------------------------------------------------------------- 第 54 章：车间数据（第 13 轮 9.4（3））
# 用仿真车间的误差模型（sim/errors.py simulate，与第 54 章的算例同一套）“磨”一个班次的 SH-301：前 30 件正常（每 10 件修整砂轮），
# 老师注入“磨床尾座偏移”后再磨 22 件，学生在质量页发现右轴承位偏大、开 8D；老师批准“校正尾座”后再磨 20 件，学生用 D6 验证。
# 测量消息按真实的历史库入库（hub/historian.py：超差件自动开不合格品单），时间从 7 小时前起排。
SHIFT = {"normal": 30, "problem": 22, "after": 20}     # 控制图显示最近 30 件：正常 8 件 + 注入后 22 件，台阶看得见
_DB = {}


def _db():
    if "db" not in _DB:
        sys.path.insert(0, str(DIGITAL))
        from hub.db import DB
        from hub.historian import Historian
        _DB["db"] = DB(_DB["dsn"])
        _DB["hist"] = Historian(_DB["db"])
        _DB["hist"].load()
    return _DB["db"], _DB["hist"]


def _grind(problem, n, t0, step_min, start_no, seed, batch="B54", wo="WO-54-01"):
    """磨 n 件并入库；返回各特性的测得值"""
    sys.path.insert(0, str(DIGITAL))
    import wqbus
    from sim import errors as ERR
    _, hist = _db()
    r = ERR.simulate(n, problem, seed=seed, dress_every=10)
    for i in range(n):
        ts = (t0 + dt.timedelta(minutes=step_min * i)).isoformat().replace("+00:00", "Z")
        serial = "SH301-{}-{:03d}".format(batch, start_no + i)
        for code, name, nom, lo, hi in ERR.CHARS:
            v = round(r["values"][code][i], 4)
            m = wqbus.make("quality.measurement", "sim/qc-01", {
                "part_serial": serial, "item": "SH-301", "characteristic": code, "name": name, "nominal_mm": nom,
                "lower_tol_mm": lo, "upper_tol_mm": hi, "value_mm": v, "result": "pass" if lo <= v <= hi else "fail",
                "work_order": wo}, mode="teach", ts=ts)
            hist.handle("wq/gearbox/quality/qc-01/measurement", m)
    return r["values"]


def seed54(teacher, student):
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    t0 = now - dt.timedelta(hours=7)
    a = _grind(None, SHIFT["normal"], t0, 6, 1, 541)
    n2 = SHIFT["problem"]
    call("POST", "/api/quality/problems", {"problem": "tailstock_offset"}, token=teacher)
    b = _grind("tailstock_offset", n2, t0 + dt.timedelta(hours=3, minutes=10), 6, 31, 540)
    mean = lambda v: sum(v) / len(v)          # noqa: E731
    dl, dr = mean(b["bearing_seat_d35"]) - mean(a["bearing_seat_d35"]), mean(b["bearing_seat_d35_r"]) - mean(a["bearing_seat_d35_r"])
    fails = sum(1 for v in b["bearing_seat_d35_r"] if v > 35.018)
    assert fails, "注入问题后应有超差件（换一个种子）"
    title = "右轴承位 Ø35 k6 偏大、超差"
    q = call("POST", "/api/quality/8d", {"item": "SH-301", "characteristic": "bearing_seat_d35_r", "title": title}, token=student)
    sec = {
        "d1": "工艺员学生甲（组长）、质检员、磨工、设备员；老师审批",
        "d2": ("第 31 件起，右轴承位均值比前 30 件大 {:.4f} mm，左轴承位大 {:.4f} mm，离头架越远变得越多；右减左从这一件起跳变，"
               "圆跳动不变；之后 {} 件里右轴承位超差 {} 件，全在上限一侧。都在磨床 GRD-01 工序 60 上。").format(dr, dl, n2, fails),
        "d3": "工序 60 之后对右轴承位 100% 检验；已磨的 " + str(n2) + " 件隔离，超差件开不合格品单返修评审。",
        "d4": ("两处都变大，但变化与到头架的距离成正比（右减左跳变），是锥度（尾座端大），不是逐件漂移，也不是分散变大：砂轮磨损、未预热"
               "会让两处一样变；中心孔不好会让跳动变大。锥度来自两顶尖连线与工作台运动方向不平行——尾座偏移。估算偏移 e ≈ 直径差 × L ÷ (2 × 两轴承位距离)。"),
        "d5": "选“校正磨床尾座”：用标准检验棒和千分表把两顶尖连线调到与工作台运动方向平行，能消除锥度的根本原因。",
        "d7": "工序 60 的首件检验加测左右两个轴承位的直径差（≤ 0.004 mm）；设备点检表加“检验棒校尾座”，每班开机检一次。",
        "d8": "数据的形态（哪处变、怎么变）指向原因：只看超差件会以为是砂轮磨损。",
    }
    call("POST", f"/api/quality/8d/{q['id']}", {"action": "save", "d": sec, "fix": "align_tailstock"}, token=student)
    call("POST", f"/api/quality/8d/{q['id']}", {"action": "submit"}, token=student)
    return {"q8d": q["id"], "now": now.isoformat()}


def approve54(d):
    """老师批准措施；措施的实施时刻定在 1 小时 15 分钟前，之后按校正后的磨床再磨 20 件，学生点 D6 验证"""
    sid, now = d["q8d"], dt.datetime.fromisoformat(d["now"])
    call("POST", f"/api/quality/8d/{sid}", {"action": "approve", "note": "同意，按检验棒法校正"}, token=d["teacher"])
    call("POST", "/api/quality/problems", {"clear": True}, token=d["teacher"])
    db, _ = _db()
    fix_at = now - dt.timedelta(hours=1, minutes=15)
    db.x("update quality_8d set fix_at=%s where id=%s", (fix_at, sid))
    _grind(None, SHIFT["after"], fix_at + dt.timedelta(minutes=2), 3, 31 + SHIFT["problem"], 543)
    call("POST", f"/api/quality/8d/{sid}", {"action": "verify"}, token=d["student"])


# ---------------------------------------------------------------- 第 55 章：表面质量（第 13 轮 11.4（5））
# 正常磨 30 件（每 10 件修整）：质量页的轴承位 Ra 单值图（图 55.2.9）；截图时老师注入“砂轮修整不锋利”再磨 30 件，
# 修整周期后几件的酸洗烧伤检验不合格，historian 自动开不合格品单（图 55.5.10）。工艺规程的“故意改坏”见 v_grind（图 55.7.7）。
def seed55(teacher, student):
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    _grind(None, 30, now - dt.timedelta(hours=7), 6, 1, 551, batch="B55", wo="WO-55-01")
    return {"now55": now.isoformat()}


def inject55(d):
    call("POST", "/api/quality/problems", {"problem": "wheel_dull"}, token=d["teacher"])
    now = dt.datetime.fromisoformat(d["now55"])
    v = _grind("wheel_dull", 30, now - dt.timedelta(hours=3, minutes=50), 6, 31, 552, batch="B55", wo="WO-55-01")
    assert sum(v["burn_bearing"]) > 0, "注入“修整不锋利”以后应有烧伤件（换一个种子）"
    assert max(v["ra_bearing"]) <= 0.8, "烧伤件的 Ra 应合格（第 55.5 节的要点）"


# ---------------------------------------------------------------- 第 56 章：SH-101 的工艺路线（第 13 轮十二）
# 学生提交两份 SH-101 的路线：本章的参照路线（std/SH-101_route.yaml）和把铣键槽挪到渗碳淬火之后的一份（图 56.9.6）；
# 下达任务单 TS-56-1，学生把参照路线那份选为“工艺规程”交付物（图 56.10.5）；工艺规程页选零件 SH-101（图 56.10.4）。
def seed56(book, teacher, student):
    ref = (DIGITAL / "std" / "SH-101_route.yaml").read_text(encoding="utf-8")
    ok = call("POST", "/api/process/check", {"yaml": ref, "submit": True, "note": "SH-101 工艺路线（按教材第 56 章拟定）"}, token=student)
    plan = yaml.safe_load(ref)
    ops = plan["operations"]
    key = next(o for o in ops if o["seq"] == 50)
    ops.remove(key)
    ops.insert(next(i for i, o in enumerate(ops) if o["seq"] == 80), key)
    key["seq"] = 75                                   # 重新编号，只看“顺序”和“路线”的意见
    note = "SH-101：铣键槽（原工序 50）挪到渗碳淬火、磨削之后，改为工序 75（第 56 章的“故意排错”）"
    bad = call("POST", "/api/process/check", {"yaml": yaml.safe_dump(plan, allow_unicode=True, sort_keys=False), "submit": True, "note": note},
               token=student)
    spec = yaml.safe_load((REPO / "textbook" / book / "ch56" / "task" / "ts56_1.yaml").read_text(encoding="utf-8"))
    spec.update(book=book, no="56.1")
    due = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=14)).isoformat()
    tid = call("POST", "/api/tasks/course/issue", {"spec": spec, "course_id": 101, "course_name": "机械制造技术（示例班）",
                                                   "due": due, "issued_by": "教师"}, key=TASK_KEY)["id"]
    i = next(n for n, x in enumerate(spec["交付物"]) if x.get("类型") == "工艺规程")
    call("POST", f"/api/tasks/{tid}/deliverables/{i}/link", {"process": ok["id"]}, token=student)
    return {"s56_ok": ok["id"], "s56_bad": bad["id"], "t56": tid, "n56": note}


# ---------------------------------------------------------------- 截图
def shots_list(d):
    s, t = d["subs"], d["tasks"]
    return [  # (名称, 章, 账号, 页面, 操作, 说明)
        ("shot50_1", 50, "student", "/process", "precheck_ref", "“工艺规程与 AI 评审”页：下载参照工艺规程、上传 AI 预检、提交记录"),
        ("shot50_2", 50, "student", f"/process/{s['ref']}", None, "按参照工艺规程提交后，AI 工艺评审员的意见与建议分"),
        ("shot50_3", 50, "student", f"/tasks/{t[50]}", None, "工程任务单 TS-50-1 在数字工厂的学生页：交付物、验收标准、进度"),
        ("shot51_1", 51, "student", f"/process/{s['locate']}", None, d["notes"]["locate"]),
        ("shot51_2", 51, "student", f"/tasks/{t[51]}", "precheck_task", "任务单 TS-51-1 的学生页：选定自己的工艺规程提交，点“AI 预检”"),
        ("shot52_1", 52, "student", f"/process/{s['fixture']}", None, d["notes"]["fixture"]),
        ("shot52_2", 52, "teacher", f"/tasks/review/{d['review52']}", None, "任务单 TS-52-1 的老师审阅页：交付物、AI 评审员的意见、评分"),
        ("shot53_1", 53, "student", f"/process/{s['chart']}", None, d["notes"]["chart"]),
        ("shot53_2", 53, "student", f"/tasks/{t[53]}", "precheck_task", "任务单 TS-53-1 的学生页：选定工艺规程提交，AI 预检"),
        ("shot54_0", 54, "student", "/work/quality", "clip",
         "质量页：左轴承位的单值控制图（砂轮每 10 件修整一次的锯齿），右栏是不合格品单和质量异常单"),
        ("shot54_1", 54, "student", "/work/quality", "select_r",
         "质量页：右轴承位的单值控制图（老师注入“尾座偏移”以后偏大），右栏自动开的不合格品单和学生开的 8D"),
        ("shot54_2", 54, "teacher", f"/quality/8d/{d.get('q8d')}", None, "学生填好 D1–D5、提交纠正措施，老师审批前的 8D 页"),
        ("shot54_3", 54, "student", f"/quality/8d/{d.get('q8d')}", "approve54", "老师批准“校正尾座”、车间再磨 20 件以后，学生做 D6 验证：措施前后对比"),
        ("shot55_1", 55, "student", "/work/quality", "select_ra", "质量页：工序 60 后轴承位 Ra 的单值图（每 10 件修整砂轮）"),
        ("shot55_2", 55, "student", "/work/quality", "inject55", "质量页：老师注入“砂轮修整不锋利”以后，酸洗烧伤检验不合格的件自动开出不合格品单"),
        ("shot55_3", 55, "student", f"/process/{s['grind']}", None, d["notes"]["grind"]),
        ("shot56_1", 56, "student", f"/process/{d.get('s56_bad')}", None, d.get("n56", "")),
        ("shot56_2", 56, "student", "/process", "select101", "“工艺规程与 AI 评审”页选零件 SH-101：零件图要求、下载模板、上传 AI 预检"),
        ("shot56_3", 56, "student", f"/tasks/{d.get('t56')}", "precheck_task", "任务单 TS-56-1 的学生页：交付物“工艺规程”指定零件 SH-101，选定提交的工艺规程后 AI 预检"),
    ]


def take(book, d, only=None):
    from playwright.sync_api import sync_playwright
    out = REPO / "textbook" / book / "shots"
    out.mkdir(exist_ok=True)
    users = {"teacher": {"token": d["teacher"], "user": {"name": "教师", "role": "engineer", "mode": "teach", "teacher": True}},
             "student": {"token": d["student"], "user": STUDENT}}
    ref = call("GET", "/api/process/reference/SH-301", token=d["student"])["yaml"]
    done = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for name, ch, who, path, act, note in shots_list(d):
            if only and str(ch) not in only:
                continue
            ctx = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2, locale="zh-CN")
            ctx.add_init_script(f"localStorage.setItem('wq-df-session', {json.dumps(json.dumps(users[who], ensure_ascii=False))})")
            if act == "approve54":
                approve54(d)
            if act == "inject55":
                inject55(d)
            pg = ctx.new_page()
            pg.goto(BASE + path, wait_until="networkidle")
            pg.wait_for_timeout(800)
            if act == "precheck_ref":       # 上传参照工艺规程，点“AI 预检（不提交）”
                pg.set_input_files("input[type=file]", files=[{"name": "SH-301_process.yaml", "mimeType": "text/yaml", "buffer": ref.encode()}])
                pg.wait_for_timeout(300)
                pg.get_by_role("button", name="AI 预检（不提交）").click()
                pg.wait_for_timeout(1500)
            elif act == "select_r":       # 选右轴承位
                pg.locator(".card-head select").first.select_option("SH-301|bearing_seat_d35_r")
                pg.wait_for_timeout(1200)
            elif act == "select_ra":
                pg.locator(".card-head select").first.select_option("SH-301|ra_bearing")
                pg.wait_for_timeout(1200)
            elif act == "inject55":
                pg.locator(".card-head select").first.select_option("SH-301|burn_bearing")
                pg.wait_for_timeout(1200)
            elif act == "select101":
                pg.locator("label:has-text(\"零件\") select").first.select_option("SH-101")
                pg.wait_for_timeout(1200)
            elif act == "precheck_task":
                pg.get_by_role("button", name="AI 预检").click()
                pg.wait_for_timeout(1500)
            cards = pg.locator(".page section.card")
            n = min(cards.count(), 2 if path.startswith("/tasks") else 9)     # 任务单页只截前两块（任务、交付物），后面是步骤和量规
            boxes = [cards.nth(i).bounding_box() for i in range(n)]
            top = pg.locator(".page .page-title").first.bounding_box() or boxes[0]
            x0 = min(b["x"] for b in boxes) - 8
            clip = {"x": x0, "y": top["y"] - 8, "width": max(b["x"] + b["width"] for b in boxes) + 8 - x0,
                    "height": max(b["y"] + b["height"] for b in boxes) + 8 - top["y"] + 8}
            if act in ("select_r", "clip", "select_ra", "inject55"):   # 质量页只截控制图、前几行测量值和右栏的不合格品、8D
                clip["height"] = min(clip["height"], 760)
            pg.screenshot(path=str(out / f"{name}.png"), clip=clip, full_page=True)
            done.append({"名称": name, "章": ch, "账号": "教师" if who == "teacher" else "学生甲", "页面": path,
                         "说明": note, "数据": "测试数据（factory_shots.py 灌入，见程序说明）"})
            ctx.close()
        b.close()
    man = out / "清单.yaml"
    old = yaml.safe_load(man.read_text(encoding="utf-8")) if man.exists() else {}
    items = {x["名称"]: x for x in (old or {}).get("截图", [])}
    items.update({x["名称"]: x for x in done})
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    man.write_text("# 数字工厂界面截图清单（由 textbook/tools/factory_shots.py 生成，不要手改）\n" + yaml.safe_dump(
        {"日期": dt.date.today().isoformat(), "数字工厂版本": commit, "截图": sorted(items.values(), key=lambda x: x["名称"])},
        allow_unicode=True, sort_keys=False, width=200), encoding="utf-8")
    return done


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("book")
    ap.add_argument("--only", nargs="*", help="只截这几章（如 51 52）")
    ap.add_argument("--dsn", default=os.environ.get("WQ_SHOTS_DSN", "postgresql://postgres:wq@localhost:5432/postgres"))
    a = ap.parse_args(argv)
    (REPO / "textbook" / "build").mkdir(exist_ok=True)
    _DB["dsn"] = fresh_db(a.dsn)
    hub = start_hub(_DB["dsn"])
    try:
        d = seed(a.book, a.only)
        for x in take(a.book, d, a.only):
            print("截图", x["名称"], x["页面"])
    finally:
        hub.terminate()
        hub.wait(20)


if __name__ == "__main__":
    main()
