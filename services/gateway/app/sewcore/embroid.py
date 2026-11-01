# -*- coding: utf-8 -*-
"""多头刺绣机设计计算（第 42 轮）。

模型出自教材《缝纫机设计与制造》第 16 章：16.3 大惯量绷架的转速上限（摆线规律 a = 2πs/T²，T = W/(6n)），
16.5 DST 记录，16.6 断线停车、回退补绣与全机效率。与虚拟实验 16-1（labs/embroid.html）同一套公式；
Y 轴（较重的一轴）折算质量 m = m0 + mh × 头数。默认参数：8 头机、绣 7 mm 缎纹，设计转速取在上限以内。

第 69 轮：可以上传花样文件（DST / CSV，stitchfile.py）。有文件时针数、换色、最长针都从文件来，
每一针（含跳步）按自己的长度取转速上限，再前瞻调速（同第 15 章 15.4.3 节），纯缝纫时间按每针的转速加起来——
这就是 16.3 节说的“控制器按每一针的长度预先算好转速”。X、Y 两轴都按 Y 轴（较重的一轴）的推力算，偏保守。
主轴伺服的转矩（阻力矩 + 起停加速）是示例模型，教材没有给，参数都标“示例值”。
"""
import hashlib
import math

from . import stitchfile as SF
from .common import Checks, line_chart, make_params, result

MACHINE = "embroid"
NAME = ("多头刺绣机", "Multi-head Embroidery")
VERSION = "1.1"
LECTURES = ("第 16 章", "chapter 16")
DST_MAX = 12.1              # DST 每条记录每个方向最大 12.1 mm

GROUPS = [
    ("basic", "基本参数", "Basic", [
        ("H", "头数", "Heads", "", 8, 1, 30, 1),
        ("n", "设计转速", "Design speed", "r/min", 650, 200, 1500, 10),
        ("n_head", "机头最高转速", "Head top speed", "r/min", 1100, 500, 1500, 10),
        ("s", "最长针长（缎纹宽）", "Longest stitch (satin width)", "mm", 7.0, 1.0, 12.1, 0.1),
        ("W", "针离布窗口", "Out-of-fabric window", "°", 204, 150, 260, 1),
        ("dn", "每针允许转速变化（前瞻调速，有花样文件时用；示例值）", "Speed change allowed per stitch (look-ahead, with a design file; example)",
         "r/min", 100, 10, 1000, 10),
    ]),
    ("frame", "绷架（16.3 节）", "Frame (16.3)", [
        ("F", "Y 轴驱动力", "Y-axis drive force", "N", 800, 100, 5000, 10),
        ("Ff", "摩擦力", "Friction", "N", 50, 0, 1000, 5),
        ("m0", "绷架基础质量", "Frame base mass", "kg", 10, 1, 200, 0.5),
        ("mh", "每头增加的质量", "Mass added per head", "kg", 4, 0.5, 20, 0.1),
        ("stx", "绷架每头行程 X（示例值）", "Frame travel per head X (example)", "mm", 400, 50, 2000, 10),
        ("sty", "绷架每头行程 Y（示例值）", "Frame travel per head Y (example)", "mm", 400, 50, 2000, 10),
    ]),
    ("servo", "绷架伺服传动（选电机用）", "Frame servo drive (for motor sizing)", [
        ("rf", "同步带轮节圆半径", "Belt pulley pitch radius", "mm", 20, 5, 60, 0.5),
        ("ig", "减速比", "Reduction ratio", "", 5, 1, 20, 0.5),
        ("eta", "传动效率", "Drive efficiency", "", 0.9, 0.5, 1, 0.01),
    ]),
    ("spindle", "主轴伺服（示例值，教材没有给）", "Main-shaft servo (example values, not in the textbook)", [
        ("T0", "主轴基础阻力矩（电机侧）", "Main-shaft base drag torque (motor side)", "N·m", 0.5, 0, 20, 0.05),
        ("Th", "每个机头的阻力矩（电机侧）", "Drag torque per head (motor side)", "N·m", 0.3, 0, 5, 0.01),
        ("J0", "主轴系统基础惯量（电机侧）", "Main-shaft base inertia (motor side)", "kg·m²", 0.002, 0, 0.5, 0.0005),
        ("Jh", "每个机头的折算惯量（电机侧）", "Inertia per head (motor side)", "kg·m²", 0.0008, 0, 0.1, 0.0001),
        ("ta", "主轴起停加速时间", "Main-shaft start / stop time", "s", 0.3, 0.05, 3, 0.05),
    ]),
    ("prod", "断线与产能（16.6 节）", "Thread breaks and output (16.6)", [
        ("src", "花样从哪里来", "Where the design comes from", "", "manual", None, None, None),
        ("N", "花样针数", "Stitches in the design", "", 20000, 1000, 500000, 500),
        ("lam", "断线率（每头每万针）", "Break rate (per head per 10 000 stitches)", "", 0.5, 0, 5, 0.05),
        ("t_fix", "每次断线处理（走过去、穿线、确认）", "Handling per break (walk, rethread, confirm)", "s", 40, 5, 300, 1),
        ("t_back", "每次回退补绣", "Back-up and repair per break", "s", 1.6, 0, 60, 0.1),
        ("d", "检测延迟（漏缝针数）", "Detection delay (stitches missed)", "", 10, 1, 40, 1),
        ("b", "回退针数", "Stitches backed up", "", 12, 0, 60, 1),
        ("colors", "换色次数", "Colour changes", "", 6, 0, 60, 1),
        ("t_color", "每次换色", "Time per colour change", "s", 6, 1, 30, 0.5),
        ("t_load", "上下绷架（每批）", "Frame loading per batch", "s", 0, 0, 1800, 10),
        ("Q", "订单件数（0 = 不算交期）", "Order quantity (0 = no delivery time)", "件", 0, 0, 10000000, 100),
        ("days", "要求交期（0 = 不校核）", "Required delivery (0 = no check)", "天", 0, 0, 3650, 1),
        ("hday", "每天开机", "Running hours per day", "h", 16, 1, 24, 0.5),
    ]),
]
CHOICES = {"src": [("manual", "手填（针数、最长针、换色次数）", "By hand (stitches, longest stitch, colour changes)"),
                   ("file", "上传花样文件（DST / CSV）", "Upload a design file (DST / CSV)")]}
PARAMS, DEFAULTS, _clean = make_params(GROUPS, CHOICES)


def clean(p):
    """参数整理；“花样从哪里来”选上传文件时，文件原样留着（dst：base64；pts：CSV 原文），项目里一起存。
    没有文件就退回手填；选手填时不存文件（换项目、存项目都不会把上一个花样带走）。文件太大照留一个标记，算的时候亮红灯"""
    out = _clean(p)
    raw = p or {}
    if out["src"] == "file":
        for k in ("dst", "pts"):
            v = raw.get(k)
            if isinstance(v, str) and v:
                if len(v) <= SF.MAX_TEXT:
                    out[k] = v
                else:
                    out["file_big"] = True
                if isinstance(raw.get("fname"), str):
                    out["fname"] = raw["fname"][:120]
                break
        if not (out.get("dst") or out.get("pts") or out.get("file_big")):
            out["src"] = "manual"
    return out


_CACHE = {}                 # 读过的花样：sha1 → (记录表, 统计)；只留最近几个（每个工作进程各一份）
_CACHE_N = 4


def design_file(p):
    """有花样文件时返回 (记录表, 统计)；没有返回 None；读不出来、太大抛 StitchFileError"""
    if p.get("src") != "file":
        return None
    if p.get("file_big"):
        raise SF.StitchFileError("花样文件太大（超过 {} 万条记录），请拆成几个花样。".format(SF.MAX_RECORDS // 10000),
                                 "The design file is too large; split the design.")
    dst, pts = p.get("dst"), p.get("pts")
    key = hashlib.sha1((dst or pts or "").encode()).hexdigest()
    if key not in _CACHE:
        recs = SF.load(dst, pts)
        if len(_CACHE) >= _CACHE_N:
            _CACHE.pop(next(iter(_CACHE)))
        _CACHE[key] = (tuple(recs), SF.stats(recs))
    return _CACHE[key]


def mass(H, m0=10, mh=4):
    return m0 + mh * H


def a_max(H, F=800, Ff=50, m0=10, mh=4):
    """绷架可用加速度：(驱动力 − 摩擦) / 折算质量"""
    return max(0.0, (F - Ff) / mass(H, m0, mh))


def a_req(s, n, W=204):
    """摆线规律走一针 s（mm）在窗口里所需的峰值加速度（m/s²）"""
    T = W / (6 * n)
    return 2 * math.pi * s / 1000 / T ** 2


def n_max(s, a, W=204, n_head=1e9):
    return min(n_head, W / 6 * math.sqrt(a / (2 * math.pi * s / 1000))) if s > 0 and a > 0 else 0.0


def force_req(s, n, H, W=204, Ff=50, m0=10, mh=4):
    return mass(H, m0, mh) * a_req(s, n, W) + Ff


def servo(p, J=0.0):
    """绷架伺服（电机侧）：设计转速下走最长针所需的峰值、有效转矩和最高转速。J 为电机转子惯量（kg·m²）。
    摆线规律峰值速度 v = 2s/T；最坏情况每针都走最长针，绷架在窗口 W 里动，有效值按 √(W/360) 折算（同 15.8 节）"""
    H, W = p["H"], p["W"]
    PL = plan(p)
    s, n = worst(p, PL)
    a = a_req(s, n, W)
    F = force_req(s, n, H, W, p["Ff"], p["m0"], p["mh"])
    r, i = p["rf"] / 1000, p["ig"]
    Tpk = F * r / (i * p["eta"]) + J * a * i / r
    T = W / (6 * n)
    v = 2 * s / 1000 / T
    Trms = Tpk * math.sqrt(W / 360)
    if PL is not None and PL["t_sew"] > 0:
        # 有花样文件：每针的峰值转矩按它自己的长度和转速算，按用时加权求有效值（同样按每针用满窗口折算）
        acc = 0.0
        for x, v_ in zip(PL["s"], PL["sp"]):
            if x <= 0:
                continue
            v_ = max(v_, 1.0)
            ai = a_req(x, v_, W)
            Ti = force_req(x, v_, H, W, p["Ff"], p["m0"], p["mh"]) * r / (i * p["eta"]) + J * ai * i / r
            acc += Ti * Ti * (W / 360) * 60 / v_
        Trms = math.sqrt(acc / PL["t_sew"])
    return dict(F=F, a=a, Tpk=Tpk, Trms=Trms, rpm=v / r * i * 60 / (2 * math.pi), v=v, s=s, n=n,
                i_opt=r * math.sqrt(mass(H, p["m0"], p["mh"]) / J) if J > 0 else None)


def production(p, H=None, n=None, t_sew=None, N=None, colors=None):
    """一批（每头一件）：纯缝纫、断线停车、换色、上下绷架 → 全机效率、每小时件数。
    有花样文件时 t_sew 按每针调速算好传进来，针数、换色次数也取文件的"""
    H = p["H"] if H is None else H
    n = p["n"] if n is None else n
    N = p["N"] if N is None else N
    colors = p["colors"] if colors is None else colors
    if t_sew is None:
        t_sew = N / n * 60
    breaks = p["lam"] * H * N / 10000
    t_break = breaks * (p["t_fix"] + p["t_back"])
    t_col = colors * p["t_color"]
    t_all = t_sew + t_break + t_col + p["t_load"]
    eff = t_sew / t_all if t_all else 0
    pph = 3600 / t_all * H if t_all else 0
    days = p["Q"] / (pph * p["hday"]) if p.get("Q") and pph > 0 else None
    return dict(t_sew=t_sew, breaks=breaks, t_break=t_break, t_col=t_col, t_all=t_all, eff=eff, pph=pph, days=days)


def plan(p, H=None, F=None, n=None):
    """有花样文件：每条记录（针、跳步）按自己的长度取转速上限，前瞻调速，加起来是纯缝纫时间。
    换色记录不转（换色时间另算）。返回每条记录的长度、上限、转速和总时间；没有文件返回 None"""
    df = design_file(p)
    if df is None:
        return None
    from .pattern import lookahead
    recs, st = df
    H = p["H"] if H is None else H
    F = p["F"] if F is None else F
    n = p["n"] if n is None else n
    am = a_max(H, F, p["Ff"], p["m0"], p["mh"])
    W, nh = p["W"], p["n_head"]
    sl, kinds = [], []
    for dx, dy, k in recs:
        if k == "c" and dx == 0 and dy == 0:       # 原地换色不转（换色时间另算）；带位移的换色记录当一次走框
            continue
        sl.append(max(abs(dx), abs(dy)))
        kinds.append(k)
    # 跳步也按同样的窗口限速（教材：跳步不落针、不受窗口限制，但大绷架长跳步同样要降速）——偏保守
    caps = [max(1.0, n_max(x, am, W, nh)) if x > 0 else nh for x in sl]
    sp = lookahead(caps, p["dn"], min(n, nh)) if caps else []
    t_sew = sum(60 / max(v, 1.0) for v in sp)
    return dict(s=sl, kinds=kinds, caps=caps, sp=sp, t_sew=t_sew, stats=st, am=am,
                avg=len(sp) * 60 / t_sew if t_sew > 0 else 0)


def run_production(p, H=None, F=None, n=None):
    """手填：整个花样一个转速（设计转速和最长针上限取小）；有文件：按每针调速。返回 (产能, 调速结果或 None)"""
    H = p["H"] if H is None else H
    F = p["F"] if F is None else F
    n = p["n"] if n is None else n
    PL = plan(p, H, F, n)
    if PL is None:
        nm = n_max(p["s"], a_max(H, F, p["Ff"], p["m0"], p["mh"]), p["W"], p["n_head"])
        return production(p, H, min(n, max(nm, 1))), None
    st = PL["stats"]
    return production(p, H, n, t_sew=PL["t_sew"], N=st["stitches"], colors=st["colors"]), PL


def worst(p, PL=None):
    """伺服按哪一针算：手填 = 设计转速下的最长针；有文件 = 调速以后所需加速度最大的那一针"""
    PL = plan(p) if PL is None else PL
    if PL is None or not PL["s"]:
        return p["s"], p["n"]
    i = max(range(len(PL["s"])), key=lambda j: a_req(PL["s"][j], max(PL["sp"][j], 1.0), p["W"]) if PL["s"][j] > 0 else 0)
    return PL["s"][i], max(PL["sp"][i], 1.0)


def spindle(p, H=None, n=None):
    """主轴伺服（示例模型）：缝纫时转矩 = 基础阻力矩 + 每头阻力矩 × 头数；起停峰值再加 惯量 × 角加速度"""
    H = p["H"] if H is None else H
    n = p["n"] if n is None else n
    J = p["J0"] + p["Jh"] * H
    Trun = p["T0"] + p["Th"] * H
    Tacc = J * n * 2 * math.pi / 60 / p["ta"]
    return dict(Trun=Trun, Tpk=Trun + Tacc, J=J)


def dst_records(dx, dy):
    """一次移动至少几条 DST 记录"""
    return max(1, math.ceil(abs(dx) / DST_MAX - 1e-9), math.ceil(abs(dy) / DST_MAX - 1e-9))


COLORS = ["#2d6fb3", "#2e9e6a", "#c77d1a", "#7b4fb3", "#1a9aa8", "#b34f7b", "#5a6b2e", "#8a5a2e"]


def _down(vals, k, f=min):
    """长曲线按桶取（默认取最小，降速的地方不会被抹掉）"""
    if len(vals) <= k:
        return list(vals)
    step = len(vals) / k
    return [f(vals[int(a * step):max(int(a * step) + 1, int((a + 1) * step))]) for a in range(k)]


def stitch_view(recs, slow_mask=None, limit=8000):
    """花样图：按颜色分段画针迹，跳步不画；降速的针单独一层（红）"""
    x = y = 0.0
    segs, cur, col = [], [[0.0, 0.0]], 0
    longs = []
    j = 0
    for dx, dy, k in recs:
        nx, ny = x + dx, y + dy
        if k == "s":
            cur.append([nx, ny])
            if slow_mask is not None and slow_mask[j]:
                longs.append([round(x, 2), round(y, 2), round(nx, 2), round(ny, 2)])
        else:
            if len(cur) > 1:
                segs.append(dict(color=COLORS[col % len(COLORS)], pts=cur))
            cur = [[nx, ny]]
            if k == "c":
                col += 1
        if k != "c":
            j += 1
        x, y = nx, ny
    if len(cur) > 1:
        segs.append(dict(color=COLORS[col % len(COLORS)], pts=cur))
    tot = sum(len(g["pts"]) for g in segs)
    stp = max(1, math.ceil(tot / limit))
    for g in segs:
        q = g["pts"]
        g["pts"] = [[round(a, 2), round(b, 2)] for a, b in (q[::stp] + ([q[-1]] if (len(q) - 1) % stp else []))]
    return segs, longs[:3000]


def analyze(params=None, trial=True):
    p = clean(params)
    H, n, W = int(p["H"]), p["n"], p["W"]
    am = a_max(H, p["F"], p["Ff"], p["m0"], p["mh"])
    ch = Checks()
    err = None
    try:
        PR, PL = run_production(p)
    except SF.StitchFileError as e:                 # 文件坏了：照手填算，红灯说明
        err = e
        p["src"] = "manual"
        PR, PL = run_production(p)
    st = PL["stats"] if PL else None
    s = st["s_max"] if st else p["s"]
    N = st["stitches"] if st else p["N"]
    colors = st["colors"] if st else p["colors"]
    ar = a_req(s, n, W)
    nm = n_max(s, am, W, p["n_head"])
    Fr = force_req(s, n, H, W, p["Ff"], p["m0"], p["mh"])
    SV = servo(p)
    SP = spindle(p)
    if err is not None:
        ch.add("file", "prod", "花样文件读得出来", "The design file can be read", (err.zh, err.en), ("DST 或 CSV 针位表", "DST or CSV stitch list"), "bad", 16,
               "在制版软件里另存为 DST（工业多头机通用的格式）再上传；CSV 每行 x, y（mm），可加第三列 0 针 / 1 跳步 / 2 换色。",
               "Save as DST in the digitising software and upload again; a CSV has x, y (mm) per row, optional third column 0 stitch / 1 jump / 2 colour change.")
    if PL is None:
        ch.add("accel", "frame", "最长针在窗口里走得完（所需 ≤ 可用加速度）", "Longest stitch fits the window (required ≤ available acceleration)",
               (f"{ar:.1f} / {am:.1f} m/s²", f"{ar:.1f} / {am:.1f} m/s²"), "≤ 1", "ok" if ar <= am + 1e-9 else "bad", 16,
               f"这一针要 {Fr:.0f} N 推力：降设计转速到 {nm:.0f} r/min 以下，或加大驱动力、减轻绷架；制版时把长缎纹拆窄或改填充。",
               f"This stitch needs {Fr:.0f} N: lower the design speed below {nm:.0f} r/min, or raise the drive force / lighten the frame; "
               "split wide satins or change them to fill when digitising.")
    else:
        n_at = min(nm, n)
        ch.add("accel", "frame", "长针按前瞻调速降下来（16.3 节）", "Long stitches slowed down by look-ahead (16.3)",
               (f"最长 {s:.1f} mm 的一针降到 {n_at:.0f} r/min", f"longest {s:.1f} mm stitch at {n_at:.0f} r/min") if am > 0 else
               ("驱动力不大于摩擦力，绷架走不动", "drive force not above friction, the frame cannot move"),
               ("控制器按每一针的长度调速", "the controller sets the speed stitch by stitch"), "ok" if am > 0 else "bad", 16,
               "每一针在窗口里都走得完：长针自动降速，短针升到设计转速。驱动力要大于摩擦力。",
               "Every stitch fits its window: long stitches slow down, short ones run at the design speed. The drive force must exceed friction.")
        ratio = PL["avg"] / max(1, min(n, p["n_head"]))
        ch.add("avg", "frame", "调速以后的平均转速 / 设计转速", "Average speed after look-ahead / design speed",
               (f"{PL['avg']:.0f} r/min（{ratio:.0%}）", f"{PL['avg']:.0f} r/min ({ratio:.0%})"), "≥ 70%",
               "ok" if ratio >= 0.7 else "warn", 16,
               "长针太多，大部分时间都在降速：制版时把宽缎纹改窄、拆成两针或改填充，或者加大绷架推力。",
               "Too many long stitches, the machine is slowed down most of the time: narrow or split wide satins, use fill, or raise the frame force.")
        ch.add("travel", "frame", "花样外框在绷架行程以内", "Design fits the frame travel",
               (f"{st['w']:.0f} × {st['h']:.0f} mm", f"{st['w']:.0f} × {st['h']:.0f} mm"), (f"≤ {p['stx']:.0f} × {p['sty']:.0f} mm", f"≤ {p['stx']:.0f} × {p['sty']:.0f} mm"),
               "ok" if st["w"] <= p["stx"] + 1e-6 and st["h"] <= p["sty"] + 1e-6 else "bad", 16,
               "花样比每个头的绷架行程大：缩小花样，或分成几块绣。", "The design is larger than the frame travel per head: scale it down or split it.")
    ch.add("head", "basic", "设计转速不超过机头最高转速", "Design speed within the head top speed", f"{n:.0f} r/min", f"≤ {p['n_head']:.0f} r/min",
           "ok" if n <= p["n_head"] else "bad", 16, "机头本身（针杆、挑线机构）转不到这么快。", "The head itself (needle bar, take-up) cannot run this fast.")
    if PL is None:
        ch.add("dst", "basic", "单方向针长不超过 DST 记录上限", "Stitch per axis within the DST record limit", f"{s:.1f} mm", f"≤ {SF.DST_MAX} mm",
               "ok" if s <= SF.DST_MAX else "bad", 16, "超过的要拆成几条记录。", "Longer moves must be split into several records.")
    else:
        ch.add("dst", "basic", "单方向针长不超过 DST 记录上限", "Stitch per axis within the DST record limit",
               (f"最长 {s:.1f} mm；超过的 {st['over']} 针", f"longest {s:.1f} mm; {st['over']} over"), f"≤ {SF.DST_MAX} mm",
               "ok" if not st["over"] else "bad", 16, "针位表里有超过 12.1 mm 的针：机器上要拆成几针，制版时改短。",
               "The list has stitches over 12.1 mm: the machine must split them; shorten them when digitising.")
    stb = "ok" if p["b"] >= p["d"] + 2 else ("warn" if p["b"] >= p["d"] else "bad")
    if p["b"] > p["d"] + 8:
        stb = "warn"
    ch.add("backup", "prod", "回退针数与检测延迟", "Back-up stitches vs detection delay", f"{p['b']:.0f} / {p['d']:.0f} 针", ("≥ 延迟 + 2，且不多太多", "≥ delay + 2, not far more"),
           stb, 16, "回退少于漏缝针数，补绣接不上留下漏针；退太多又费时、重叠处变厚。回退取漏缝针数再多两三针。",
           "Backing up less than the missed stitches leaves a gap; far more wastes time and thickens the overlap. Use the delay plus two or three.")
    ch.add("eff", "prod", "全机效率（纯缝纫时间 / 一批总时间）", "Machine efficiency (pure sewing / batch time)", f"{PR['eff']:.0%}", "≥ 75%",
           "ok" if PR["eff"] >= 0.75 else ("warn" if PR["eff"] >= 0.6 else "bad"), 16,
           "头多断线停车就多：降断线率（线、针、张力）、缩短每次处理时间（自动回退补绣、灵敏的断线检测），或减少换色。",
           "More heads, more stops: lower the break rate (thread, needle, tension), shorten handling (automatic back-up, faster detection), or fewer colour changes.")
    if PR["days"] is not None and p["days"] > 0:
        ch.add("order", "prod", "订单交期", "Order delivery", (f"{PR['days']:.1f} 天", f"{PR['days']:.1f} days"), (f"≤ {p['days']:.0f} 天", f"≤ {p['days']:.0f} days"),
               "ok" if PR["days"] <= p["days"] + 1e-9 else "bad", 16,
               "交期不够：“设计优化”里选“达到订单交期”，找头数最少、推力最小的方案；或者多开几台。",
               "Not in time: use the design optimiser goal “meet the order delivery” for the fewest heads and smallest force, or run more machines.")
    results = [result("绷架折算质量", "Frame equivalent mass", f"{mass(H, p['m0'], p['mh']):.0f}", "kg")]
    if PL is None:
        results += [
            result("可用加速度 / 最长针所需", "Available / required acceleration", f"{am:.1f} / {ar:.1f}", "m/s²"),
            result("最长针的转速上限", "Speed limit for the longest stitch", f"{nm:.0f}", "r/min"),
            result("设计转速下这一针需要的推力", "Force this stitch needs at design speed", f"{Fr:.0f}", "N"),
        ]
    else:
        results += [
            result("花样：针数 / 跳步 / 换色", "Design: stitches / jumps / colour changes", f"{N} / {st['jumps']} / {colors}"),
            result("花样外框", "Design size", f"{st['w']:.1f} × {st['h']:.1f}", "mm"),
            result("最长针 / 它的转速上限", "Longest stitch / its speed limit", f"{s:.1f} mm / {nm:.0f}", "r/min"),
            result("按每针调速：平均转速", "Stitch-by-stitch speed: average", f"{PL['avg']:.0f}", "r/min"),
            result("可用加速度", "Available acceleration", f"{am:.1f}", "m/s²"),
        ]
    results += [
        result("绷架伺服峰值 / 有效转矩（电机侧，不含转子）", "Frame servo peak / RMS torque (motor side, rotor excluded)",
               f"{SV['Tpk']:.2f} / {SV['Trms']:.2f}", "N·m"),
        result("主轴伺服：缝纫时 / 起停峰值转矩（电机侧，示例）", "Main-shaft servo: sewing / start-stop peak torque (motor side, example)",
               f"{SP['Trun']:.2f} / {SP['Tpk']:.2f}", "N·m"),
    ]
    if PL is None:
        results.append(result("3 mm 填充针的转速上限", "Speed limit for a 3 mm fill stitch", f"{n_max(3, am, W, p['n_head']):.0f}", "r/min"))
    results += [
        result("纯缝纫时间 / 一批总时间", "Pure sewing / batch time", f"{PR['t_sew'] / 60:.1f} / {PR['t_all'] / 60:.1f}", "min"),
        result("每批断线次数", "Thread breaks per batch", f"{PR['breaks']:.1f}"),
        result("全机效率 / 每小时件数", "Efficiency / pieces per hour", f"{PR['eff']:.0%} / {PR['pph']:.1f}"),
    ]
    if PR["days"] is not None:
        results.append(result(f"这张订单（{p['Q']:.0f} 件，每天 {p['hday']:g} 小时）", f"This order ({p['Q']:.0f} pieces, {p['hday']:g} h a day)",
                              f"{PR['days']:.1f}", "天"))
    sl = [x / 2 for x in range(2, 25)]
    heads = list(range(1, 25)) if PL is None else sorted({1, 2, 4, 6, 8, 10, 12, 15, 20, 24, H})     # 有文件时每个头数都要整份调速，少算几个点
    hrow = {}

    def per_head(h):
        if h not in hrow:
            hrow[h] = run_production(p, h)[0]
        return hrow[h]
    charts = [
        line_chart("nmax", "转速上限与针长（r/min）", "Speed limit vs stitch length (r/min)", sl,
                   [(f"{H} 头", f"{H} heads", "#2d6fb3", [n_max(x, am, W, p["n_head"]) for x in sl]),
                    ("机头上限", "head limit", "#8a9aa8", [p["n_head"]] * len(sl))], ref=n, xr=[1, 12], xl=("针长 mm", "Stitch length, mm")),
        line_chart("eff", "头数与全机效率（%）", "Heads vs machine efficiency (%)", heads,
                   [("效率", "efficiency", "#2e9e6a", [per_head(h)["eff"] * 100 for h in heads])], xr=[1, 24], xl=("头数", "Heads")),
    ]
    if PL is not None:
        K = 1200
        idx = _down(list(range(1, len(PL["sp"]) + 1)), K, lambda v: v[0])
        charts.insert(0, line_chart("speed", "每针转速与上限（r/min，按段取最低）", "Speed per stitch and its limit (r/min, lowest in each bucket)", idx,
                                    [("上限", "limit", "#c0392b", [round(v) for v in _down(PL["caps"], K)]),
                                     ("前瞻后转速", "planned speed", "#2d6fb3", [round(v) for v in _down(PL["sp"], K)])],
                                    xr=[1, max(2, len(PL["sp"]))], xl=("第几针（含跳步）", "Stitch no. (with jumps)")))
        recs, _ = design_file(p)
        slow = [c < min(n, p["n_head"]) - 0.5 for c in PL["caps"]]
        segs, longs = stitch_view(recs, slow)
        charts.insert(1, dict(key="design", kind="stitch", zh="花样（按颜色；红色是要降速的针）", en="Design (by colour; red = stitches that slow down)",
                              segs=segs, longs=longs, w=round(st["w"], 1), h=round(st["h"], 1)))
    f1 = 180 - (360 - W) / 2
    f2 = 180 + (360 - W) / 2
    timing = [dict(key="in", zh="机针在布中（绷架不能动）", en="Needle in the fabric (frame must stand still)", a=round(f1, 1), b=round(f2, 1)),
              dict(key="move", zh="绷架移动一针", en="Frame moves one stitch", a=round(f2, 1), b=round(f1, 1))]
    tables = [
        dict(key="speed_table", zh="针长与转速（本机）", en="Stitch length and speed (this machine)",
             head=[("针长 mm", "Stitch mm"), ("转速上限 r/min", "Limit r/min"), ("设计转速下所需加速度 m/s²", "Accel. needed at design speed m/s²"),
                   ("所需推力 N", "Force needed N")],
             rows=[[f"{x:g}", f"{n_max(x, am, W, p['n_head']):.0f}", f"{a_req(x, n, W):.1f}", f"{force_req(x, n, H, W, p['Ff'], p['m0'], p['mh']):.0f}"]
                   for x in (2, 3, 4, 5, 6, 7, 8, 10, 12)]),
        dict(key="heads_table", zh="头数与效率（同一花样、同样断线率）", en="Heads and efficiency (same design and break rate)",
             head=[("头数", "Heads"), ("最长针转速上限", "Limit for the longest stitch"), ("全机效率", "Efficiency"), ("每小时件数", "Pieces per hour")]
             + ([("这张订单 天", "This order, days")] if PR["days"] is not None else []),
             rows=[[str(h), f"{n_max(s, a_max(h, p['F'], p['Ff'], p['m0'], p['mh']), W, p['n_head']):.0f}", f"{per_head(h)['eff']:.0%}", f"{per_head(h)['pph']:.1f}"]
                   + ([f"{per_head(h)['days']:.1f}"] if PR["days"] is not None else [])
                   for h in (1, 2, 4, 6, 8, 12, 15, 20)]),
    ]
    if PL is not None:
        bins = [(0, 2), (2, 4), (4, 6), (6, 8), (8, 10), (10, math.inf)]
        rows = []
        for lo, hi in bins:
            ids = [k for k, x in enumerate(PL["s"]) if lo < x <= hi or (lo == 0 and x == 0)]
            if not ids:
                continue
            t = sum(60 / max(PL["sp"][k], 1.0) for k in ids)
            rows.append([f"{lo}–{hi}" if hi < math.inf else f"> {lo}", str(len(ids)), f"{len(ids) / len(PL['s']):.0%}",
                         f"{len(ids) * 60 / t:.0f}", f"{t / 60:.1f}", f"{t / PL['t_sew']:.0%}"])
        tables.insert(0, dict(key="bins_table", zh="花样里各种针长的针数和用时（按每针调速）", en="Stitch lengths in the design: count and time (stitch-by-stitch speed)",
                              head=[("针长 mm", "Length mm"), ("针数（含跳步）", "Stitches (with jumps)"), ("占针数", "Share of stitches"),
                                    ("平均转速 r/min", "Average speed r/min"), ("用时 min", "Time min"), ("占用时", "Share of time")], rows=rows))
    out = dict(version=VERSION, machine=MACHINE, params={k: v for k, v in p.items() if k not in ("dst", "pts")}, checks=list(ch), ok=not any(c["state"] == "bad" for c in ch),
               results=results, charts=charts, timing=timing, parts=parts(p), card=adjust_card(dict(p, s=s)), tables=tables, production=PR,
               view=dict(page="embroid", sync="A", cfg=dict(H=H, F=p["F"], s=s, n=n)))
    if PL is not None:
        out["design"] = dict(stitches=N, jumps=st["jumps"], colors=colors, s_max=round(s, 2), w=round(st["w"], 1), h=round(st["h"], 1),
                             avg=round(PL["avg"]), t_sew=round(PL["t_sew"], 1), fname=p.get("fname", ""))
    return out


def parts(p):
    return [dict(key="frame", zh="绷架（Y 轴）", en="Frame (Y axis)", dims=[("折算质量", "Equivalent mass", round(mass(p["H"], p["m0"], p["mh"]), 1), "kg"),
                                                                      ("驱动力", "Drive force", p["F"], "N"), ("摩擦", "Friction", p["Ff"], "N")]),
            dict(key="heads", zh="机头", en="Heads", dims=[("头数", "Heads", int(p["H"]), ""), ("最高转速", "Top speed", p["n_head"], "r/min")])]


def adjust_card(params=None):
    p = clean(params)
    am = a_max(p["H"], p["F"], p["Ff"], p["m0"], p["mh"])
    return [
        dict(zh="绷架与转速", en="Frame and speed", do_zh=f"本机 {p['s']:.1f} mm 的针转速上限 {n_max(p['s'], am, p['W'], p['n_head']):.0f} r/min；控制器按针长前瞻降速，长缎纹段自动降速。",
             do_en=f"Limit for a {p['s']:.1f} mm stitch is {n_max(p['s'], am, p['W'], p['n_head']):.0f} r/min; the controller slows down on long satins by look-ahead."),
        dict(zh="断线检测", en="Break detection", do_zh=f"检测延迟按 {p['d']:.0f} 针设，回退针数设 {p['b']:.0f} 针；补绣后有缺口加回退针数，有凸起减回退针数。",
             do_en=f"Detection delay {p['d']:.0f} stitches, back-up {p['b']:.0f}; a gap after repair means back up more, a bump means less."),
        dict(zh="换色顺序", en="Colour sequence", do_zh="制版时同色块连起来绣，减少换色、剪线和跳步，比提高转速更能缩短时间。",
             do_en="Digitise same-colour blocks together to cut colour changes, trims and jumps — it saves more time than a higher speed."),
        dict(zh="线、针、张力", en="Thread, needle, tension", do_zh="某个头经常断线，先查这个头的线路、张力和针，再查断线检测器。",
             do_en="If one head breaks often, check its thread path, tension and needle first, then the break detector."),
    ]
