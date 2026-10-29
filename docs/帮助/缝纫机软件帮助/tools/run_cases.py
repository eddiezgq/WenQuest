"""第 52 轮：四个典型案例从头跑到尾，结果存 data/cases.json（帮助里案例的数全从这里取）。

用网页版同一套接口（网关 + 数字工厂计算服务真算）：有限元、疲劳、模态、动力学、减重与复核、数控、电机选型、设计优化；
不用联网的校核直接调计算核心（和网页版同一份）。以后改了计算核心，重跑一遍就知道案例还成不成立（--check 只比对不写）。

用法（本地完整环境 tools/local + 数字工厂 cae、hub 都起来）：
  python3 run_cases.py [网关地址] [账号] [密码]
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "services" / "gateway"))
from app.sewcore import cad, cae_setup as CS, machines as MS  # noqa: E402

B = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].startswith("http") else "http://localhost:8090"
U, P = (sys.argv[2], sys.argv[3]) if len(sys.argv) > 3 else ("teacher1", "Test#2026")


def req(m, p, b=None, raw=False, files=None):
    h = {"authorization": "Bearer " + TOKEN} if TOKEN else {}
    data = None
    if files:
        bd = "----wq" + str(time.time())
        parts = []
        for k, v in files.items():
            if isinstance(v, tuple):
                parts.append(f'--{bd}\r\nContent-Disposition: form-data; name="{k}"; filename="{v[0]}"\r\n\r\n'.encode() + v[1] + b"\r\n")
            else:
                parts.append(f'--{bd}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
        data = b"".join(parts) + f"--{bd}--\r\n".encode()
        h["content-type"] = "multipart/form-data; boundary=" + bd
    elif b is not None:
        data = json.dumps(b).encode()
        h["content-type"] = "application/json"
    r = urllib.request.urlopen(urllib.request.Request(B + p, data=data, method=m, headers=h), timeout=600)
    out = r.read()
    return out if raw else json.loads(out)


TOKEN = ""
TOKEN = req("POST", "/api/v1/auth/login", {"username": U, "password": P})["token"]


def wait(jid):
    for _ in range(300):
        j = req("GET", f"/api/v1/sewing/cae/jobs/{jid}")
        if j["status"] in ("done", "failed"):
            if j["status"] != "done":
                raise RuntimeError(f"job {jid} failed: {j.get('error')}")
            return j["result"]
        time.sleep(3)
    raise RuntimeError("timeout " + jid)


def analyze(machine, p):
    M = MS.get(machine)
    R = M.analyze(M.clean(p))
    return R


def checks_brief(R, states=("bad", "warn")):
    return [dict(key=c["key"], name=c["name"]["zh"], value=c["value"]["zh"], limit=c["limit"]["zh"], state=c["state"]) for c in R["checks"] if c["state"] in states]


def counts(R):
    cs = R["checks"]
    return dict(all=len(cs), bad=sum(c["state"] == "bad" for c in cs), warn=sum(c["state"] == "warn" for c in cs))


def vals(R):
    return {c["key"]: c["value"]["zh"] for c in R["checks"]}


def result(R, zh):
    return next(r["value"] for r in R["results"] if r["zh"].startswith(zh))


def fea(machine, params, part):
    j = req("POST", "/api/v1/sewing/cae/fea", {"machine": machine, "params": params, "part": part})
    r = wait(j["id"])
    return dict(vm=round(r["vm_max_mpa"], 1), sf=round(r["safety_factor"], 1), life_y=r.get("life_years"), u=r.get("u_max_mm"),
                elements=r.get("elements"), force=round(abs(r.get("analytic", {}).get("value", 0)), 1) if r.get("analytic") else None,
                checks=[dict(name=c["zh"], value=c["value"], limit=c["limit"], state=c["state"]) for c in r.get("checks") or []])


def topo(machine, params, part, vf):
    j = req("POST", "/api/v1/sewing/cae/topo", {"machine": machine, "params": params, "part": part, "volfrac": vf})
    r = wait(j["id"])
    v = req("POST", f"/api/v1/sewing/cae/topo/{j['id']}/verify")
    rv = wait(v["id"])
    return dict(jid=j["id"], mass_ratio=r.get("mass_ratio"), area=round(r.get("area"), 1), area0=round(r.get("area0"), 1), iterations=r.get("iterations"),
                verify=dict(vm=round(rv["vm_max_mpa"], 1), sf=round(rv["safety_factor"], 2), life_y=rv.get("life_years"),
                            checks=[dict(name=c["zh"], value=c["value"], state=c["state"]) for c in rv.get("checks") or []]))


def cam(machine, params, part, topo_jid="", **kw):
    j = req("POST", "/api/v1/sewing/cae/cam", dict(machine=machine, params=params, part=part, topo=topo_jid, **kw))
    r = req("GET", f"/api/v1/sewing/cae/jobs/{j['id']}")["result"]
    return dict(time_s=r["time_s"], tools=[("钻头" if t.get("kind") == "drill" else "立铣刀") + " Ø" + str(t.get("d")) for t in r["tools"]], programs=r["programs"], issues=r["issues"],
                checks=[dict(name=c["zh"], value=c["value"], state=c["state"]) for c in r["checks"]], template=r.get("template", {}) and
                {k: r["template"][k] for k in ("plate", "slot_w", "bridges", "stitches", "pins") if k in r["template"]})


out = {"date": time.strftime("%Y-%m-%d")}

# ---------- 案例一 平缝机：从零件到整机 ----------
L = {}
p0 = {}
R = analyze("lockstitch", p0)
L["base"] = dict(counts=counts(R), n=R["params"]["n"], lam=result(R, "连杆比"), stroke=result(R, "针杆行程"), F=result(R, "针杆惯性力"),
                 trial=R["trial"]["counts"], chain=R["chain"], card=[s["zh"] for s in R["card"]], parts3d=[(d["name"], d["zh"]) for d in cad.parts3d(R["params"])["parts"]],
                 results={r["zh"]: f'{r["value"]} {r["unit"]}'.strip() for r in R["results"]})
L["crank_fea"] = fea("lockstitch", p0, "NeedleCrank")
L["rod_fea"] = fea("lockstitch", p0, "ConnectingRod")
L["crank_topo"] = topo("lockstitch", p0, "NeedleCrank", 0.5)
L["crank_cam"] = cam("lockstitch", p0, "NeedleCrank")
L["crank_cam_topo"] = cam("lockstitch", p0, "", topo_jid=L["crank_topo"]["jid"])
j = req("POST", "/api/v1/sewing/cae/mbd", {"machine": "lockstitch", "params": p0})
r = wait(j["id"])
L["mbd"] = dict(peak=round(r["torque_peak_mbd"], 2), formula=round(r["torque_peak_formula"], 2), diff=r["diff"])
mo = req("POST", "/api/v1/sewing/cae/motor", {"machine": "lockstitch", "params": p0})
L["motor"] = dict(peak=round(mo["peak_nm"], 2), rms=round(mo["rms_nm"], 2), pick=(mo.get("pick") or {}).get("name"))
# 机壳模态：用一个简化 C 形机壳（底板 + 立柱 + 机臂）
import build123d as bd  # noqa: E402
import tempfile  # noqa: E402
shell = (bd.Box(300, 120, 20, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)) +
         bd.Pos(250, 0, 20) * bd.Box(50, 80, 200, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)) +
         bd.Pos(20, 0, 170) * bd.Box(280, 70, 60, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)))
with tempfile.TemporaryDirectory() as t:
    bd.export_step(shell, t + "/f.step")
    step = Path(t + "/f.step").read_bytes()
(ROOT / "apps/web/src/static/help/media/case-ls-frame.step").write_bytes(step)     # 帮助里给读者下载，照着做能得到同样的频率
fj = req("POST", "/api/v1/sewing/cae/frame", files={"file": ("机壳-简化.step", step), "machine": "lockstitch", "params": json.dumps(p0), "material": "HT200"})
fr = wait(fj["id"])
L["frame"] = dict(f1=fr.get("f1"), freqs=[round(x) for x in (fr.get("freqs_hz") or [])[:4]], checks=[dict(name=c["zh"], value=c["value"], state=c["state"]) for c in fr.get("checks") or []])
# 提速改型
R6 = analyze("lockstitch", {"n": 6000})
L["up6000"] = dict(counts=counts(R6), bad=checks_brief(R6, ("bad",)), warn=checks_brief(R6, ("warn",)))
fix = {"n": 6000, "mr": 0.10, "fn": 240}
R6b = analyze("lockstitch", fix)
L["up6000_fix"] = dict(params=fix, counts=counts(R6b), F=result(R6b, "针杆惯性力"))
mo6 = req("POST", "/api/v1/sewing/cae/motor", {"machine": "lockstitch", "params": fix})
L["up6000_motor"] = dict(peak=round(mo6["peak_nm"], 2), rms=round(mo6["rms_nm"], 2), pick=(mo6.get("pick") or {}).get("name"), safety=mo6["safety"],
                         rows=[dict(name=x["name"], rated=x["rated_nm"], peak=x["peak_nm"], max_rpm=x["max_rpm"], ok=x["ok"]) for x in mo6["rows"]])
# 表里没有够用的电机 → 本单位零件库录一台高速主轴伺服（示例，不对应任何厂家），重新选型，用完删掉
M6 = dict(power_w=3000, rated_nm=4.8, peak_nm=14.4, rated_rpm=6000, max_rpm=7000, inertia=3.0)
pid = req("POST", "/api/v1/sewing/parts", {"cat": "motor", "code": "SV-3000H", "name": "高速主轴伺服 3 kW（示例）", "fields": M6, "confirm": True})["id"]
try:
    mo6b = req("POST", "/api/v1/sewing/cae/motor", {"machine": "lockstitch", "params": fix})
    L["up6000_motor_lib"] = dict(motor=M6, code="SV-3000H", pick=(mo6b.get("pick") or {}).get("name"),
                                 peak_use=round((mo6b.get("pick") or {}).get("peak_use", 0), 2), rms_use=round((mo6b.get("pick") or {}).get("rms_use", 0), 2))
finally:
    req("DELETE", f"/api/v1/sewing/parts/{pid}")
L["up6000_fea"] = fea("lockstitch", fix, "NeedleCrank")
out["lockstitch"] = L

# ---------- 案例二 包缝机：空间四杆的弯针 ----------
O = {}
R = analyze("overlock", {})
O["base"] = dict(counts=counts(R), warn=checks_brief(R, ("warn",)), vals=vals(R), results={r["zh"]: f'{r["value"]} {r["unit"]}'.strip() for r in R["results"]})
for rr in (6.0, 8.0):
    Rx = analyze("overlock", {"ll_r": rr})
    O[f"ll_r_{int(rr)}"] = dict(counts=counts(Rx), warn=checks_brief(Rx), vals=vals(Rx))
opt = req("POST", "/api/v1/sewing/optimize", {"machine": "overlock", "params": {}, "goal": "upper"})
O["opt_upper"] = dict(candidates=[dict(params=c["params"], value=c["value"], bad=c["bad"], warn=c["warn"]) for c in opt["candidates"][:3]], unit=opt.get("unit"))
if opt["candidates"]:
    Ru = analyze("overlock", opt["candidates"][0]["params"])
    O["opt_upper_after"] = dict(counts=counts(Ru), warn=checks_brief(Ru))
O["rocker_fea"] = fea("overlock", {}, "LL_Rocker")
O["rocker_topo50"] = topo("overlock", {}, "LL_Rocker", 0.5)
O["rocker_topo40"] = topo("overlock", {}, "LL_Rocker", 0.4)
O["rocker_cam"] = cam("overlock", {}, "LL_Rocker")
O["rocker_cam_topo50"] = cam("overlock", {}, "", topo_jid=O["rocker_topo50"]["jid"])
out["overlock"] = O

# ---------- 案例三 绷缝机：五种线迹与用线计划 ----------
C = {"stitches": []}
from app.sewcore import cover as CV  # noqa: E402
for key, zh, _en in CV.CHOICES["stitch"]:
    Rs = analyze("cover", {"stitch": key})
    t = Rs["tables"][0]
    C["stitches"].append(dict(key=key, zh=zh, counts=counts(Rs), per_cm=result(Rs, "每厘米线迹总耗线"), total=result(Rs, "订单总用线"),
                              rows=[[r[0][0] if isinstance(r[0], (list, tuple)) else r[0], r[1], r[2], r[3]] for r in t["rows"]]))
Rc = analyze("cover", {})
C["order"] = {k: Rc["params"][k] for k in ("Lcm", "Q", "W", "cone")}
C["window"] = result(Rc, "弯针定时窗口")
C["window_ms"] = result(Rc, "窗口时间")
C["n"] = Rc["params"]["n"]
for d in (-6, 6):
    Rd = analyze("cover", {"dphi": d})
    C[f"dphi_{'m' if d < 0 else 'p'}6"] = dict(bad=checks_brief(Rd, ("bad",)))
opt = req("POST", "/api/v1/sewing/optimize", {"machine": "cover", "params": {"dphi": -6}, "goal": "timing"})
C["opt_timing"] = [dict(params=c["params"], bad=c["bad"], warn=c["warn"]) for c in opt["candidates"][:3]]
out["cover"] = C

# ---------- 案例四 电子花样机：一个口袋盖花样 ----------
PT = {}
steps = [("base", {}), ("n2000", {"n": 2000}), ("ay50", {"n": 2000, "ay": 50}), ("ry8", {"n": 2000, "ay": 50, "ry": 8})]
for k, p in steps:
    Rp = analyze("pattern", p)
    PT[k] = dict(params=p, counts=counts(Rp), vals=vals(Rp), bad=checks_brief(Rp, ("bad",)), warn=checks_brief(Rp, ("warn",)),
                 limits=result(Rp, "标准针距转速上限"), y=result(Rp, "Y 轴峰值"), avg=result(Rp, "缝制用时"), per_h=result(Rp, "每小时件数"),
                 cycle=result(Rp, "一个周期"))
mp = req("POST", "/api/v1/sewing/cae/motor", {"machine": "pattern", "params": {"n": 2000, "ay": 50}})
PT["motor_ay50"] = [dict(axis=a["zh"], pick=(a.get("pick") or {}).get("name"), r_opt=a.get("r_opt"), current=a.get("current")) for a in mp["axes"]]
mp = req("POST", "/api/v1/sewing/cae/motor", {"machine": "pattern", "params": {"n": 2000, "ay": 50, "ry": 8}})
PT["motor_ry8"] = [dict(axis=a["zh"], pick=(a.get("pick") or {}).get("name"), r_mm=a.get("r_mm"), current=a.get("current")) for a in mp["axes"]]
PT["template_cam"] = cam("pattern", {"n": 2000, "ay": 50, "ry": 8}, "template", slot_w=5.0, plate_t=3.0)
out["pattern"] = PT

# ---------- 案例五 电脑横机：一片前片要织多久（第 54 轮，教材 17.8 节） ----------
from app.sewcore import flatknit as FK  # noqa: E402
K = {}


def fk_brief(params):
    R = analyze("flatknit", params)
    return dict(params=params, counts=counts(R), vals=vals(R), bad=checks_brief(R, ("bad",)), warn=checks_brief(R, ("warn",)),
                t_piece=round(R["production"]["t_piece_min"], 2), t_pass=round(R["production"]["t_pass"], 3), D=round(R["production"]["D"], 1),
                passes=R["production"]["passes"], per_day=round(R["production"]["per_day"]), timing={t["key"]: [t["a"], t["b"]] for t in R["timing"]},
                results={r["zh"]: f'{r["value"]} {r["unit"]}'.strip() for r in R["results"]})


K["base"] = fk_brief({})
K["base"]["variants"] = next(t for t in analyze("flatknit", {})["tables"] if t["key"] == "variants")["rows"]
K["base"]["garment"] = analyze("flatknit", {})["garment"]
K["E18"] = fk_brief({"E": 18})
K["E18_seg2"] = fk_brief({"E": 18, "seg": 2})
K["none"] = fk_brief({"comp": "none"})
K["v16"] = fk_brief({"v": 1.6})
K["sys2"] = fk_brief({"sys": 2, "comp": "realtime"})
K["sys3"] = fk_brief({"sys": 3, "comp": "realtime"})
opt = req("POST", "/api/v1/sewing/optimize", {"machine": "flatknit", "params": {}, "goal": "time"})
K["opt"] = [dict(params=c["params"], value=c["value"], bad=c["bad"], warn=c["warn"]) for c in opt["candidates"]]
best = opt["candidates"][0]["params"]
K["best"] = fk_brief(best)
mo = req("POST", "/api/v1/sewing/cae/motor", {"machine": "flatknit", "params": best})
ax = mo["axes"][0]
K["best_motor"] = dict(mass=ax["mass"], force=round(ax["force"]), pick=(ax.get("pick") or {}).get("name"), current=ax["current"])
K["cuff1"] = fk_brief({"N": 100})
K["cuff3"] = fk_brief({"N": 100, "pcs": 3, "gap": 0})
# 针床模态：简化的针床梁架在两根立柱上（梁 1500 × 200 × 80，立柱 100 × 200 × 700，铸铁；立柱底面固定）
leg = lambda x: bd.Pos(x, 0, 0) * bd.Box(100, 200, 700, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN))   # noqa: E731
bed = leg(0) + leg(1400) + bd.Pos(0, 0, 700) * bd.Box(1500, 200, 80, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN))
with tempfile.TemporaryDirectory() as t:
    bd.export_step(bed, t + "/b.step")
    stepb = Path(t + "/b.step").read_bytes()
(ROOT / "apps/web/src/static/help/media/case-fk-bed.step").write_bytes(stepb)
fj = req("POST", "/api/v1/sewing/cae/frame", files={"file": ("针床-简化.step", stepb), "machine": "flatknit", "params": json.dumps(best), "material": "HT200"})
fr = wait(fj["id"])
K["bed"] = dict(f1=fr.get("f1"), freqs=[round(x) for x in (fr.get("freqs_hz") or [])[:4]], t_move=fr.get("t_move"),
                checks=[dict(name=c["zh"], value=c["value"], state=c["state"]) for c in fr.get("checks") or []])
out["flatknit"] = K

dest = HERE.parent / "data" / "cases.json"
if "--check" in sys.argv:
    print("check only")
else:
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(json.dumps({k: (list(v.keys()) if isinstance(v, dict) else v) for k, v in out.items()}, ensure_ascii=False))
