# -*- coding: utf-8 -*-
"""多头刺绣机设计计算（第 42 轮）。

模型出自教材《缝纫机设计与制造》第 16 章：16.3 大惯量绷架的转速上限（摆线规律 a = 2πs/T²，T = W/(6n)），
16.5 DST 记录，16.6 断线停车、回退补绣与全机效率。与虚拟实验 16-1（labs/embroid.html）同一套公式；
Y 轴（较重的一轴）折算质量 m = m0 + mh × 头数。默认参数：8 头机、绣 7 mm 缎纹，设计转速取在上限以内。
"""
import math

from .common import Checks, line_chart, make_params, result

MACHINE = "embroid"
NAME = ("多头刺绣机", "Multi-head Embroidery")
VERSION = "1.0"
LECTURES = ("第 16 章", "chapter 16")
DST_MAX = 12.1              # DST 每条记录每个方向最大 12.1 mm

GROUPS = [
    ("basic", "基本参数", "Basic", [
        ("H", "头数", "Heads", "", 8, 1, 30, 1),
        ("n", "设计转速", "Design speed", "r/min", 650, 200, 1500, 10),
        ("n_head", "机头最高转速", "Head top speed", "r/min", 1100, 500, 1500, 10),
        ("s", "最长针长（缎纹宽）", "Longest stitch (satin width)", "mm", 7.0, 1.0, 12.1, 0.1),
        ("W", "针离布窗口", "Out-of-fabric window", "°", 204, 150, 260, 1),
    ]),
    ("frame", "绷架（16.3 节）", "Frame (16.3)", [
        ("F", "Y 轴驱动力", "Y-axis drive force", "N", 800, 100, 5000, 10),
        ("Ff", "摩擦力", "Friction", "N", 50, 0, 1000, 5),
        ("m0", "绷架基础质量", "Frame base mass", "kg", 10, 1, 200, 0.5),
        ("mh", "每头增加的质量", "Mass added per head", "kg", 4, 0.5, 20, 0.1),
    ]),
    ("servo", "绷架伺服传动（选电机用）", "Frame servo drive (for motor sizing)", [
        ("rf", "同步带轮节圆半径", "Belt pulley pitch radius", "mm", 20, 5, 60, 0.5),
        ("ig", "减速比", "Reduction ratio", "", 5, 1, 20, 0.5),
        ("eta", "传动效率", "Drive efficiency", "", 0.9, 0.5, 1, 0.01),
    ]),
    ("prod", "断线与产能（16.6 节）", "Thread breaks and output (16.6)", [
        ("N", "花样针数", "Stitches in the design", "", 20000, 1000, 500000, 500),
        ("lam", "断线率（每头每万针）", "Break rate (per head per 10 000 stitches)", "", 0.5, 0, 5, 0.05),
        ("t_fix", "每次断线处理（走过去、穿线、确认）", "Handling per break (walk, rethread, confirm)", "s", 40, 5, 300, 1),
        ("t_back", "每次回退补绣", "Back-up and repair per break", "s", 1.6, 0, 60, 0.1),
        ("d", "检测延迟（漏缝针数）", "Detection delay (stitches missed)", "", 10, 1, 40, 1),
        ("b", "回退针数", "Stitches backed up", "", 12, 0, 60, 1),
        ("colors", "换色次数", "Colour changes", "", 6, 0, 60, 1),
        ("t_color", "每次换色", "Time per colour change", "s", 6, 1, 30, 0.5),
        ("t_load", "上下绷架（每批）", "Frame loading per batch", "s", 0, 0, 1800, 10),
    ]),
]
CHOICES = {}
PARAMS, DEFAULTS, clean = make_params(GROUPS, CHOICES)


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
    H, n, s, W = p["H"], p["n"], p["s"], p["W"]
    a = a_req(s, n, W)
    F = force_req(s, n, H, W, p["Ff"], p["m0"], p["mh"])
    r, i = p["rf"] / 1000, p["ig"]
    Tpk = F * r / (i * p["eta"]) + J * a * i / r
    T = W / (6 * n)
    v = 2 * s / 1000 / T
    return dict(F=F, a=a, Tpk=Tpk, Trms=Tpk * math.sqrt(W / 360), rpm=v / r * i * 60 / (2 * math.pi), v=v,
                i_opt=r * math.sqrt(mass(H, p["m0"], p["mh"]) / J) if J > 0 else None)


def production(p, H=None, n=None):
    """一批（每头一件）：纯缝纫、断线停车、换色、上下绷架 → 全机效率、每小时件数"""
    H = p["H"] if H is None else H
    n = p["n"] if n is None else n
    t_sew = p["N"] / n * 60
    breaks = p["lam"] * H * p["N"] / 10000
    t_break = breaks * (p["t_fix"] + p["t_back"])
    t_col = p["colors"] * p["t_color"]
    t_all = t_sew + t_break + t_col + p["t_load"]
    eff = t_sew / t_all if t_all else 0
    return dict(t_sew=t_sew, breaks=breaks, t_break=t_break, t_col=t_col, t_all=t_all, eff=eff, pph=3600 / t_all * H if t_all else 0)


def dst_records(dx, dy):
    """一次移动至少几条 DST 记录"""
    return max(1, math.ceil(abs(dx) / DST_MAX - 1e-9), math.ceil(abs(dy) / DST_MAX - 1e-9))


def analyze(params=None, trial=True):
    p = clean(params)
    H, n, s, W = int(p["H"]), p["n"], p["s"], p["W"]
    am = a_max(H, p["F"], p["Ff"], p["m0"], p["mh"])
    ar = a_req(s, n, W)
    nm = n_max(s, am, W, p["n_head"])
    Fr = force_req(s, n, H, W, p["Ff"], p["m0"], p["mh"])
    PR = production(p, H, min(n, max(nm, 1)))
    SV = servo(p)
    ch = Checks()
    ch.add("accel", "frame", "最长针在窗口里走得完（所需 ≤ 可用加速度）", "Longest stitch fits the window (required ≤ available acceleration)",
           (f"{ar:.1f} / {am:.1f} m/s²", f"{ar:.1f} / {am:.1f} m/s²"), "≤ 1", "ok" if ar <= am + 1e-9 else "bad", 16,
           f"这一针要 {Fr:.0f} N 推力：降设计转速到 {nm:.0f} r/min 以下，或加大驱动力、减轻绷架；制版时把长缎纹拆窄或改填充。",
           f"This stitch needs {Fr:.0f} N: lower the design speed below {nm:.0f} r/min, or raise the drive force / lighten the frame; "
           "split wide satins or change them to fill when digitising.")
    ch.add("head", "basic", "设计转速不超过机头最高转速", "Design speed within the head top speed", f"{n:.0f} r/min", f"≤ {p['n_head']:.0f} r/min",
           "ok" if n <= p["n_head"] else "bad", 16, "机头本身（针杆、挑线机构）转不到这么快。", "The head itself (needle bar, take-up) cannot run this fast.")
    ch.add("dst", "basic", "单方向针长不超过 DST 记录上限", "Stitch per axis within the DST record limit", f"{s:.1f} mm", f"≤ {DST_MAX} mm",
           "ok" if s <= DST_MAX else "bad", 16, "超过的要拆成几条记录。", "Longer moves must be split into several records.")
    st = "ok" if p["b"] >= p["d"] + 2 else ("warn" if p["b"] >= p["d"] else "bad")
    if p["b"] > p["d"] + 8:
        st = "warn"
    ch.add("backup", "prod", "回退针数与检测延迟", "Back-up stitches vs detection delay", f"{p['b']:.0f} / {p['d']:.0f} 针", ("≥ 延迟 + 2，且不多太多", "≥ delay + 2, not far more"),
           st, 16, "回退少于漏缝针数，补绣接不上留下漏针；退太多又费时、重叠处变厚。回退取漏缝针数再多两三针。",
           "Backing up less than the missed stitches leaves a gap; far more wastes time and thickens the overlap. Use the delay plus two or three.")
    ch.add("eff", "prod", "全机效率（纯缝纫时间 / 一批总时间）", "Machine efficiency (pure sewing / batch time)", f"{PR['eff']:.0%}", "≥ 75%",
           "ok" if PR["eff"] >= 0.75 else ("warn" if PR["eff"] >= 0.6 else "bad"), 16,
           "头多断线停车就多：降断线率（线、针、张力）、缩短每次处理时间（自动回退补绣、灵敏的断线检测），或减少换色。",
           "More heads, more stops: lower the break rate (thread, needle, tension), shorten handling (automatic back-up, faster detection), or fewer colour changes.")
    results = [
        result("绷架折算质量", "Frame equivalent mass", f"{mass(H, p['m0'], p['mh']):.0f}", "kg"),
        result("可用加速度 / 最长针所需", "Available / required acceleration", f"{am:.1f} / {ar:.1f}", "m/s²"),
        result("最长针的转速上限", "Speed limit for the longest stitch", f"{nm:.0f}", "r/min"),
        result("设计转速下这一针需要的推力", "Force this stitch needs at design speed", f"{Fr:.0f}", "N"),
        result("绷架伺服峰值 / 有效转矩（电机侧，不含转子）", "Frame servo peak / RMS torque (motor side, rotor excluded)",
               f"{SV['Tpk']:.2f} / {SV['Trms']:.2f}", "N·m"),
        result("3 mm 填充针的转速上限", "Speed limit for a 3 mm fill stitch", f"{n_max(3, am, W, p['n_head']):.0f}", "r/min"),
        result("纯缝纫时间 / 一批总时间", "Pure sewing / batch time", f"{PR['t_sew'] / 60:.1f} / {PR['t_all'] / 60:.1f}", "min"),
        result("每批断线次数", "Thread breaks per batch", f"{PR['breaks']:.1f}"),
        result("全机效率 / 每小时件数", "Efficiency / pieces per hour", f"{PR['eff']:.0%} / {PR['pph']:.1f}"),
    ]
    sl = [x / 2 for x in range(2, 25)]
    heads = list(range(1, 25))
    charts = [
        line_chart("nmax", "转速上限与针长（r/min）", "Speed limit vs stitch length (r/min)", sl,
                   [(f"{H} 头", f"{H} heads", "#2d6fb3", [n_max(x, am, W, p["n_head"]) for x in sl]),
                    ("机头上限", "head limit", "#8a9aa8", [p["n_head"]] * len(sl))], ref=n, xr=[1, 12], xl=("针长 mm", "Stitch length, mm")),
        line_chart("eff", "头数与全机效率（%）", "Heads vs machine efficiency (%)", heads,
                   [("效率", "efficiency", "#2e9e6a", [production(p, h, min(n, max(n_max(s, a_max(h, p["F"], p["Ff"], p["m0"], p["mh"]), W, p["n_head"]), 1)))["eff"] * 100
                                                     for h in heads])], xr=[1, 24], xl=("头数", "Heads")),
    ]
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
             head=[("头数", "Heads"), ("最长针转速上限", "Limit for the longest stitch"), ("全机效率", "Efficiency"), ("每小时件数", "Pieces per hour")],
             rows=[[str(h), f"{n_max(s, a_max(h, p['F'], p['Ff'], p['m0'], p['mh']), W, p['n_head']):.0f}",
                    f"{production(p, h, min(n, max(n_max(s, a_max(h, p['F'], p['Ff'], p['m0'], p['mh']), W, p['n_head']), 1)))['eff']:.0%}",
                    f"{production(p, h, min(n, max(n_max(s, a_max(h, p['F'], p['Ff'], p['m0'], p['mh']), W, p['n_head']), 1)))['pph']:.1f}"]
                   for h in (1, 2, 4, 6, 8, 12, 15, 20)]),
    ]
    return dict(version=VERSION, machine=MACHINE, params=p, checks=list(ch), ok=not any(c["state"] == "bad" for c in ch),
                results=results, charts=charts, timing=timing, parts=parts(p), card=adjust_card(p), tables=tables, production=PR,
                view=dict(page="embroid", sync="A", cfg=dict(H=H, F=p["F"], s=s, n=n)))


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
