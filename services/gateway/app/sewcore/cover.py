# -*- coding: utf-8 -*-
"""绷缝机 / 链缝机（401、406、407、602、605）设计计算（第 40 轮）。

模型出自教材《缝纫机设计与制造》第 10 讲：10.3–10.4 弯针运动与定时（虚拟实验 10-1 looper.html，即教材 model10.py），
10.6 耗线量（虚拟实验 10-2 coverstitch.html）。与教材程序 course/calc/ch10.py 同一套公式；默认参数就是教材算例。
"""
import math

from .common import Checks, line_chart, make_params, mod360, result

MACHINE = "cover"
NAME = ("绷缝机", "Coverstitch")
VERSION = "1.0"
LECTURES = ("第 10 讲", "lecture 10")
D = math.pi / 180
R, L = 15.5, 55.0           # 针杆曲柄滑块（同平缝机算例）
LAM = R / L
T = 1.5                     # 布厚（弯针模型）
RN = 0.45                   # 机针半径
S = 30                      # 弯针左右行程
H0 = 2.2                    # 线环最大时的回升量
PHR0 = 176                  # 弯针最右点的标准主轴角
A_LOOP, A_COV = 0.5, 0.3    # 耗线模型：线环、覆盖线的附加量
TY = {"401": (1, False), "406": (2, False), "407": (3, False), "602": (2, True), "605": (3, True)}

GROUPS = [
    ("basic", "基本参数", "Basic", [
        ("n", "最高转速", "Top speed", "r/min", 6500, 3000, 8000, 100),
        ("stitch", "线迹", "Stitch type", "", "406", None, None, None),
        ("spc", "针密（每厘米针数）", "Stitches per cm", "/cm", 7, 3, 12, 0.5),
        ("g", "针距（两针间距）", "Needle gauge", "mm", 4.0, 2.0, 7.0, 0.1),
        ("t", "布厚（耗线用）", "Fabric thickness (for consumption)", "mm", 0.5, 0.2, 3.0, 0.1),
        ("nr", "401 的行数（双线链缝）", "Rows of 401", "", 1, 1, 4, 1),
    ]),
    ("looper", "弯针（第 10 讲）", "Looper (lecture 10)", [
        ("dphi", "弯针定时（相对标准）", "Looper timing (vs standard)", "°", 0, -15, 15, 0.5),
        ("dz", "弯针高低（相对标准）", "Looper height (vs standard)", "mm", 0, -1.5, 1.5, 0.05),
        ("e", "让针幅度", "Needle-avoid amplitude", "mm", 1.0, 0, 2, 0.02),
        ("gap", "弯针尖与针的间隙", "Point-to-needle clearance", "mm", 0.03, -0.05, 0.2, 0.01),
        ("rr", "弯针回退量（越过针右边）", "Looper retraction (right of needle)", "mm", 3.2, 1, 7, 0.05),
    ]),
    ("order", "订单与线团（耗线量计划）", "Order and cones (thread plan)", [
        ("Lcm", "每件缝长", "Seam length per piece", "cm", 172, 10, 1000, 1),
        ("Q", "件数", "Pieces", "", 1000, 1, 1000000, 1),
        ("W", "损耗（剪线头、试缝、断线）", "Waste allowance", "", 0.12, 0, 0.5, 0.01),
        ("cone", "每个线团长度", "Length per cone", "m", 5000, 500, 30000, 100),
    ]),
]
CHOICES = {"stitch": [("401", "401 双线链缝", "401 two-thread chainstitch"), ("406", "406 两针绷缝", "406 two-needle coverstitch"),
                      ("407", "407 三针绷缝", "407 three-needle coverstitch"), ("602", "602 两针带覆盖线", "602 two-needle with top cover"),
                      ("605", "605 三针带覆盖线", "605 three-needle with top cover")]}
PARAMS, DEFAULTS, clean = make_params(GROUPS, CHOICES)


def X(f):
    return R * (1 - math.cos(f * D)) - L * (1 - math.sqrt(1 - (LAM * math.sin(f * D)) ** 2))


HT = T + X(101.7)
DEYE = X(114.18) - X(101.7) - T


def ztip(f):
    return HT - X(f)


def rise(f):
    return X(180) - X(f)


def floop(h):
    h = max(h, 0)
    return (h / H0) ** 2 * math.exp(2 * (1 - h / H0))


def bis(g, a, b):
    ga = g(a)
    for _ in range(80):
        m = (a + b) / 2
        gm = g(m)
        if (gm > 0) == (ga > 0):
            a, ga = m, gm
        else:
            b = m
    return (a + b) / 2


RW = [bis(lambda h: floop(h) - 0.6, 0.3, H0), bis(lambda h: floop(h) - 0.6, H0, 8)]   # 线环够大的回升量范围


def dcOf(rr):
    return math.acos(max(-1, min(1, 1 - 2 * rr / S))) / D


ZB0 = ztip(PHR0 + dcOf(3.2)) + DEYE + 1.5


def evaluate(st):
    """弯针一圈的判定（与 ch10.py 的 evaluate() 相同）"""
    phR = PHR0 + st["dphi"]
    dc = dcOf(st["rr"])
    y0 = -(RN + st["gap"]) + st["e"] * math.sin(dc * D)
    zb = ZB0 + st["dz"]

    def looper(f):
        return st["rr"] - S / 2 * (1 - math.cos((f - phR) * D)), y0 - st["e"] * math.sin((f - phR) * D)
    fc = mod360(phR + dc)
    h = rise(fc)
    eye = ztip(fc) + DEYE
    ds = zb - eye
    ytop = 0.5 + 0.9 * max(h, 0)
    gap = -looper(fc)[1] - RN
    fd = bis(lambda f: ztip(f) - zb, 60, 179.9)
    fu = bis(lambda f: ztip(f) - zb, 180.1, 300)
    xd, yd = looper(fd)
    wb = wf = 9.0
    f = 0.0
    while f < 360:
        if ztip(f) <= zb:
            x, y = looper(f)
            if x <= 0:
                if 180 <= f <= fu:
                    wb = min(wb, -y - RN)
                else:
                    wf = min(wf, y - RN)
        f += 0.25
    ok = [RW[0] <= h <= RW[1], 0.2 <= ds <= ytop - 0.3, 0 <= gap <= 0.10, (-xd - RN) >= 0.3 and (yd - RN) >= 0.2, wb >= -0.001 and wf >= 0.05]
    return dict(fc=fc, h=h, ds=ds, ytop=ytop, gap=gap, fd=fd, fu=fu, xd=xd, yd=yd, wb=wb, wf=wf, ok=ok, fr=mod360(phR - dc), zb=zb, looper=looper)


def cons(tp, spc=7, t=0.5, g=4.0, nr=1):
    """每厘米线迹每根线用多少厘米线（虚拟实验 10-2）"""
    s = 10 / spc
    n, cov = TY[tp]
    o = []
    for _ in range(int(nr) if tp == "401" else 1):
        o += [("needle", (s + 2 * t + 2 * A_LOOP) / s)] * n
        o.append(("looper", (n * (2 * s + 2 * A_LOOP) + s + 2 * (0 if tp == "401" else g)) / s))
    if cov:
        o.append(("cover", (2 * g + n * 2 * A_COV) / s))
    return o


TNAME = {"needle": ("针线", "Needle thread"), "looper": ("弯针线", "Looper thread"), "cover": ("覆盖线", "Top-cover thread")}


def plan(p):
    rows, cnt = [], {}
    items = cons(p["stitch"], p["spc"], p["t"], p["g"], p["nr"])
    for nm, v in items:
        cnt[nm] = cnt.get(nm, 0) + 1
        m = v * p["Lcm"] / 100 * p["Q"] * (1 + p["W"])
        many = sum(1 for k, _ in items if k == nm) > 1
        rows.append(dict(i=cnt[nm] if many else "", kind=nm, zh=TNAME[nm][0], en=TNAME[nm][1], ratio=v, meters=m, cones=math.ceil(m / p["cone"] - 1e-9)))
    return rows


def analyze(params=None, trial=True):
    p = clean(params)
    st = {k: p[k] for k in ("dphi", "dz", "e", "gap", "rr")}
    E = evaluate(st)
    win = [d / 2 for d in range(-30, 31) if all(evaluate(dict(st, dphi=d / 2))["ok"])]
    lo, hi = (win[0], win[-1]) if win else (None, None)
    width = (hi - lo) if win else 0
    ms = width / (p["n"] / 60 * 360) * 1000
    ch = Checks()
    names = [("loop_rise", "钩线时机针回升量（线环够大）", "Needle rise at the catch (loop big enough)", f"{E['h']:.2f} mm（{E['fc']:.1f}°）",
              f"{RW[0]:.2f}–{RW[1]:.2f} mm", "调弯针定时：回升太少线环还没张开，太多线环已收缩。", "Adjust the looper timing: too little rise and the loop is not open, too much and it is shrinking."),
             ("point_h", "弯针尖在线环高度内", "Looper point within the loop height", f"{E['ds']:.2f} mm", f"0.20–{E['ytop'] - 0.3:.2f} mm",
              "调弯针高低。", "Adjust the looper height."),
             ("gap", "弯针尖与针的间隙", "Point-to-needle clearance", f"{E['gap']:.3f} mm", "0–0.10 mm",
              "间隙为负碰针，太大从线环外滑过。", "Negative hits the needle; too large slides outside the loop."),
             ("descend", "针下行时让开弯针", "Needle clears the looper on its way down", f"x {-E['xd'] - RN:.2f}，y {E['yd'] - RN:.2f} mm",
              ("x ≥ 0.30，y ≥ 0.20 mm", "x ≥ 0.30, y ≥ 0.20 mm"), "回退量或让针幅度不够：针下来时扎到弯针或弯针线。",
              "Not enough retraction or avoid amplitude: the needle comes down onto the looper or its thread."),
             ("avoid", "针在弯针平面下方时不相碰", "No contact while the needle is below the looper plane", f"后 {E['wb']:.2f}，前 {E['wf']:.2f} mm",
              ("后 ≥ 0，前 ≥ 0.05 mm", "back ≥ 0, front ≥ 0.05 mm"), "加大让针幅度。", "Increase the needle-avoid amplitude.")]
    for (key, zh, en, val, lim, azh, aen), ok in zip(names, E["ok"]):
        if key == "descend":
            val = (f"x {-E['xd'] - RN:.2f}，y {E['yd'] - RN:.2f} mm", f"x {-E['xd'] - RN:.2f}, y {E['yd'] - RN:.2f} mm")
        if key == "avoid":
            val = (f"后 {E['wb']:.2f}，前 {E['wf']:.2f} mm", f"back {E['wb']:.2f}, front {E['wf']:.2f} mm")
        if key == "loop_rise":
            val = (f"{E['h']:.2f} mm（{E['fc']:.1f}°）", f"{E['h']:.2f} mm ({E['fc']:.1f}°)")
        ch.add(key, "looper", zh, en, val, lim, "ok" if ok else "bad", 10, "" if ok else azh, "" if ok else aen)
    if win:
        m = min(p["dphi"] - lo, hi - p["dphi"])
        ch.add("timing_margin", "looper", "弯针定时离窗口边缘", "Looper timing margin to the window edges",
               (f"{p['dphi']:+.1f}°，窗口 {lo:+.1f}° 到 {hi:+.1f}°", f"{p['dphi']:+.1f}°, window {lo:+.1f}° to {hi:+.1f}°"), "≥ 1.5°",
               "ok" if m >= 1.5 else ("warn" if m >= 0 else "bad"), 10,
               "" if m >= 1.5 else "定时太靠窗口边缘，零件误差和高速变形一吃掉余量就跳针：调到窗口中间。",
               "" if m >= 1.5 else "Too near the edge of the window: tolerances and deflection at speed will cause skips; move to the middle.")
    else:
        ch.add("timing_margin", "looper", "弯针定时窗口", "Looper timing window", ("没有可行的定时", "no workable timing"), ("有窗口", "a window exists"), "bad", 10,
               "其他参数（高低、间隙、回退、让针）不对，任何定时都会出毛病。", "Other settings are wrong, so no timing works.")
    ch.add("window_ms", "looper", "定时窗口对应的时间", "Time span of the timing window", f"{ms:.3f} ms", "≥ 0.15 ms",
           "ok" if ms >= 0.15 else "warn", 10, "" if ms >= 0.15 else "转速太高，窗口只剩零点一几毫秒：降速或加宽窗口。",
           "" if ms >= 0.15 else "At this speed the window lasts only a fraction of a millisecond: lower the speed or widen the window.")
    PL = plan(p)
    total = sum(r["ratio"] for r in PL)
    results = [
        result("钩线角 / 机针回升", "Catch angle / needle rise", f"{E['fc']:.1f} / {E['h']:.2f}", "° / mm"),
        result("线环够大的回升范围", "Rise range with a big enough loop", f"{RW[0]:.2f}–{RW[1]:.2f}", "mm"),
        result("弯针定时窗口", "Looper timing window", f"{lo:+.1f} … {hi:+.1f}" if win else "—", "°"),
        result("窗口时间（最高转速）", "Window time at top speed", f"{ms:.3f}", "ms"),
        result("针下到弯针平面的转角", "Needle reaches the looper plane", f"{E['fd']:.1f}", "°"),
        result("弯针回到最右（回退）", "Looper back at the right", f"{E['fr']:.1f}", "°"),
        result("每厘米线迹总耗线", "Thread per cm of seam (all threads)", f"{total:.2f}", "cm/cm"),
        result("订单总用线 / 线团", "Order total / cones", f"{sum(r['meters'] for r in PL):,.0f} m / {sum(r['cones'] for r in PL)}"),
    ]
    phi = list(range(0, 360, 2))
    charts = [
        line_chart("needle", "针尖高出弯针平面（mm）", "Needle point above the looper plane (mm)", phi,
                   [("针尖", "point", "#2d6fb3", [ztip(f) - E["zb"] for f in phi])], zero=True),
        line_chart("looper", "弯针尖左右位置（mm，0 = 针中心，负为针左）", "Looper point across (mm, 0 = needle centre, negative = left)", phi,
                   [("弯针尖", "looper point", "#c0392b", [E["looper"](f)[0] for f in phi])], zero=True),
    ]
    timing = [dict(key="below", zh="针在弯针平面下方", en="Needle below the looper plane", a=round(E["fd"], 1), b=round(E["fu"], 1)),
              dict(key="left", zh="弯针尖在针左边", en="Looper point left of the needle", a=round(E["fc"], 1), b=round(E["fr"], 1), mark=round(E["fc"], 1))]
    tables = [dict(key="plan", zh="耗线量与线团计划", en="Thread consumption and cones",
                   head=[("线", "Thread"), ("每厘米线迹用线（cm）", "per cm of seam (cm)"), ("总长（m）", "Total (m)"), ("线团（个）", "Cones")],
                   rows=[[(f"{r['zh']} {r['i']}".strip(), f"{r['en']} {r['i']}".strip()), f"{r['ratio']:.2f}", f"{r['meters']:,.0f}", str(r["cones"])] for r in PL] +
                   [[("合计", "Total"), f"{total:.2f}", f"{sum(r['meters'] for r in PL):,.0f}", str(sum(r["cones"] for r in PL))]])]
    return dict(version=VERSION, machine=MACHINE, params=p, checks=list(ch), ok=not any(c["state"] == "bad" for c in ch),
                results=results, charts=charts, timing=timing, parts=parts(p), card=adjust_card(p), tables=tables, plan=PL,
                view=dict(page="looper", sync="ST", cfg=st))


def parts(p):
    n, cov = TY[p["stitch"]]
    return [dict(key="looper", zh="弯针", en="Looper", dims=[("左右行程", "Stroke across", S, "mm"), ("回退量", "Retraction", p["rr"], "mm"),
                                                             ("让针幅度", "Needle-avoid amplitude", p["e"], "mm"), ("与针间隙", "Clearance", p["gap"], "mm")]),
            dict(key="needles", zh="机针", en="Needles", dims=[("针数", "Needles", n, ""), ("针距", "Gauge", p["g"], "mm"),
                                                               ("覆盖线（上装饰线）", "Top cover thread", "有" if cov else "无", "")])]


def adjust_card(params=None):
    p = clean(params)
    E = evaluate({k: p[k] for k in ("dphi", "dz", "e", "gap", "rr")})
    return [
        dict(zh="弯针定时", en="Looper timing", do_zh=f"转到 {E['fc']:.1f}°（针从最低点回升 {E['h']:.2f} mm），弯针尖正好到针的中心线。",
             do_en=f"At {E['fc']:.1f}° (needle risen {E['h']:.2f} mm) the looper point reaches the needle centre line."),
        dict(zh="弯针高低", en="Looper height", do_zh=f"这时弯针尖在针眼上沿上方 {E['ds']:.2f} mm。", do_en=f"The point is then {E['ds']:.2f} mm above the top of the eye."),
        dict(zh="弯针与针的间隙", en="Looper clearance", do_zh=f"弯针尖擦过针，间隙 {E['gap']:.2f} mm（0–0.10 mm）。", do_en=f"Clearance {E['gap']:.2f} mm (0–0.10 mm)."),
        dict(zh="回退量与让针", en="Retraction and avoid", do_zh=f"弯针最右时尖在针右边 {p['rr']:.2f} mm；让针幅度 {p['e']:.2f} mm。",
             do_en=f"At its rightmost the point is {p['rr']:.2f} mm right of the needle; avoid amplitude {p['e']:.2f} mm."),
        dict(zh="线量", en="Thread", do_zh="按“耗线量与线团计划”表备线；试缝检查跳针、线环大小、覆盖线是否盖满。",
             do_en="Stock thread as in the consumption table; sew a test seam and check skips, loop size and top-cover coverage."),
    ]
