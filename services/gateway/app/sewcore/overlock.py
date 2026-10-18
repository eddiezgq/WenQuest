# -*- coding: utf-8 -*-
"""包缝机（504 三线 / 514 四线）设计计算（第 40 轮）。

模型与算例出自教材《缝纫机设计与制造》第 9 讲：9.5 斜向引针、9.6 下弯针空间四杆（RSSR）、9.7 上弯针、
9.8 三者配合（送布窗口 292°→68°）、9.9 切边（上刀最低点、重叠量 0.5–1 mm）、9.10 差动送布（虚拟实验 9-1 的面料模型）。
RSSR 与教材程序 course/calc/ch09.py、虚拟实验 9-2（rssr.html）同一套公式；默认参数就是教材算例机。
"""
import math

from .common import Checks, line_chart, make_params, mod360, result

MACHINE = "overlock"
NAME = ("包缝机", "Overlock")
VERSION = "1.0"
LECTURES = ("第 9 讲", "lecture 9")
DEG = math.pi / 180
INCLINE = 20.0                      # 针与下弯针摆轴都斜 20°（教材算例机）
M0 = (22.0, 1.27606, -51.53467)     # 主轴上偏心中心（教材坐标）

GROUPS = [
    ("basic", "基本参数", "Basic", [
        ("n", "最高转速", "Top speed", "r/min", 7000, 3000, 9000, 100),
        ("s", "针距", "Stitch length", "mm", 2.5, 1.0, 4.5, 0.1),
        ("stitch", "线迹", "Stitch type", "", "504", None, None, None),
        ("fab", "面料", "Fabric", "", "jersey", None, None, None),
        ("t", "布厚（两层）", "Fabric thickness (two plies)", "mm", 1.5, 0.4, 4.0, 0.1),
    ]),
    ("needle", "斜向引针机构", "Inclined needle drive", [
        ("r", "曲柄半径", "Crank radius", "mm", 12.25, 8, 16, 0.05),
        ("l", "连杆长", "Connecting-rod length", "mm", 42.0, 30, 60, 0.5),
        ("tip0", "针尖最高时高出针板", "Needle tip above plate at TDC", "mm", 9.5, 6, 14, 0.1),
        ("mr", "针杆组件质量（强度、动力学用）", "Needle-bar assembly mass (for CAE)", "kg", 0.08, 0.03, 0.2, 0.005),
    ]),
    ("lower", "下弯针（空间四杆 RSSR）", "Lower looper (spatial RSSR)", [
        ("ll_r", "偏心半径", "Eccentric radius", "mm", 4.3619, 2, 11, 0.01),
        ("ll_b", "球头连杆长", "Ball-link length", "mm", 22.4789, 16, 32, 0.01),
        ("ll_c", "摆杆长", "Rocker length", "mm", 22.0, 16, 30, 0.1),
        ("ll_R", "弯针尖到摆轴", "Looper point to rocker axis", "mm", 38.0, 30, 46, 0.5),
        ("ll_J", "下弯针组件对摆轴的转动惯量（估计）", "Lower looper assembly inertia about its axis (estimate)", "g·cm²", 200, 20, 2000, 10),
    ]),
    ("upper", "上弯针（空间四杆 RSSR）", "Upper looper (spatial RSSR)", [
        ("ul_r", "偏心半径", "Eccentric radius", "mm", 7.3801, 3, 12, 0.01),
        ("ul_b", "球头连杆长", "Ball-link length", "mm", 29.47, 22, 38, 0.01),
        ("ul_c", "摆杆长", "Rocker length", "mm", 20.0, 15, 26, 0.1),
    ]),
    ("feed", "送布与差动", "Feed and differential", [
        ("f_on", "送布牙露出针板（开始）", "Feed dog rises above plate", "°", 292, 250, 330, 1),
        ("f_off", "送布牙落下（结束）", "Feed dog drops below plate", "°", 68, 30, 110, 1),
        ("D", "差动比 D", "Differential ratio D", "", 1.21, 0.6, 2.2, 0.01),
        ("pf", "压脚压力（相对）", "Presser-foot pressure (relative)", "", 1.0, 0.5, 2.0, 0.05),
        ("lm", "主送布臂长 l_m", "Main feed arm l_m", "mm", 20, 12, 30, 0.5),
    ]),
    ("knife", "切边", "Trimming knife", [
        ("kn_ph", "上刀最低点", "Upper knife at bottom", "°", 180, 0, 359, 1),
        ("kn_ov", "上下刀重叠量", "Knife overlap", "mm", 0.8, 0, 2, 0.05),
        ("w", "线迹宽（切边线到针）", "Stitch width (cut line to needle)", "mm", 4.0, 2, 7, 0.5),
    ]),
    ("drive", "主轴电机（CAE 选型用）", "Spindle motor (for CAE sizing)", [
        ("T_sew", "缝纫阻力矩（估计）", "Sewing resistance torque (estimate)", "N·m", 0.15, 0.0, 2.0, 0.05),
        ("mat", "关键零件材料", "Material of key parts", "", "45-QT", None, None, None),
    ]),
]
from .design import CHOICES as _LC

CHOICES = {
    "mat": _LC["mat"],
    "stitch": [("504", "504 三线包缝", "504 three-thread"), ("514", "514 四线包缝", "514 four-thread")],
    "fab": [("jersey", "汗布（单面针织）", "Single jersey"), ("rib", "罗纹", "Rib knit"), ("fleece", "卫衣布（毛圈）", "Fleece"),
            ("chiffon", "雪纺（薄梭织）", "Chiffon (light woven)"), ("twill", "斜纹布（中厚梭织）", "Twill (medium woven)")],
}
PARAMS, DEFAULTS, clean = make_params(GROUPS, CHOICES)

# 虚拟实验 9-1 的面料参数：e0 = D = 1 时布边被拉长的比例；eta = 差动牙行程传到布上的比例；
# gmax 两牙之间能推挤的最大比例；emax 拉开到送布牙打滑前的最大比例；lam 波浪的波长 mm
DFAB = {"jersey": dict(e0=0.18, eta=0.85, gmax=0.35, emax=0.6, lam=30), "rib": dict(e0=0.30, eta=0.80, gmax=0.30, emax=0.8, lam=26),
        "fleece": dict(e0=0.10, eta=0.90, gmax=0.25, emax=0.4, lam=36), "chiffon": dict(e0=-0.06, eta=0.95, gmax=0.55, emax=0.08, lam=30),
        "twill": dict(e0=0.01, eta=0.90, gmax=0.12, emax=0.02, lam=40)}

# RSSR 预设（教材坐标，rssr.html）；ph0 为弧度
LL = dict(gam=90, bet=20, dl=-7.133, Q0=(0, 16.6497, -67.772), xc=22, ph0=-2.50136)
UL = dict(gam=90, bet=-75.97, dl=0.0, Q0=(35.3839, -18.6172, -72.7627), xc=15.3839, ph0=0.244346)


# ---------- 向量 ----------
def _add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def _sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def _mul(a, s): return (a[0] * s, a[1] * s, a[2] * s)
def _dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def _cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def _norm(a): return math.sqrt(_dot(a, a))
def _unit(a): return _mul(a, 1 / _norm(a))


def _rot(v, ax, th):
    return _add(_add(_mul(v, math.cos(th)), _mul(_cross(ax, v), math.sin(th))), _mul(ax, _dot(ax, v) * (1 - math.cos(th))))


def rssr(r, b, c, pre, n=7000, full=False):
    """空间四杆 RSSR 一整圈（每 1°）：摆角、角速度、传动角；装不上（|M| > √(P²+K²)）的转角记进 fail。
    与教材 ch09.py 的 stats()、rssr.html 的 solve() 同一套公式。"""
    w = 2 * math.pi * n / 60
    ex = (1.0, 0.0, 0.0)
    e = _unit((math.cos(pre["gam"] * DEG), math.sin(pre["gam"] * DEG) * math.sin(pre["bet"] * DEG),
               math.sin(pre["gam"] * DEG) * math.cos(pre["bet"] * DEG)))
    ref = _sub(ex, _mul(e, _dot(ex, e)))
    if _norm(ref) < 1e-6:
        ref = _sub((0, 0, 1.0), _mul(e, e[2]))
    ref = _unit(ref)
    v0 = _rot(ref, e, pre["dl"] * DEG)
    v1 = _cross(e, v0)
    Q = tuple(pre["Q0"])
    C = (pre["xc"], M0[1], M0[2])
    th, thd, gm, fail, pts = [], [], [], [], []
    prev = None
    for k in range(360):
        ang = k * DEG + pre["ph0"]
        A = _add(C, (0, r * math.cos(ang), r * math.sin(ang)))
        K = _sub(A, Q)
        P_, K_ = _dot(K, v0), _dot(K, v1)
        M = (_dot(K, K) + c * c - b * b) / (2 * c)
        rho = math.hypot(P_, K_)
        if abs(M) > rho:
            fail.append(k)
            th.append(None)
            thd.append(None)
            gm.append(None)
            prev = None
            continue
        t = math.atan2(K_, P_) + math.acos(M / rho)
        if prev is not None:
            while t - prev > math.pi:
                t -= 2 * math.pi
            while t - prev < -math.pi:
                t += 2 * math.pi
        prev = t
        rv = _mul(_add(_mul(v0, math.cos(t)), _mul(v1, math.sin(t))), c)
        B = _add(Q, rv)
        d = _sub(A, B)
        tt = _cross(e, rv)
        Ad = _mul(_cross(ex, _sub(A, C)), w)
        den = _dot(d, tt)
        th.append(t)
        thd.append(_dot(d, Ad) / den)
        gm.append(math.degrees(math.asin(min(1, abs(den) / _norm(d) / _norm(tt)))))
        if full:
            pts.append(dict(A=A, B=B, Q=Q, C=C, e=e))
    ok = [x for x in th if x is not None]
    out = dict(fail=fail, th=th, thd=thd, gm=gm, e=e, v0=v0, v1=v1, Q=Q, C=C, pts=pts)
    if ok and not fail:
        mx, mn = max(ok), min(ok)
        imx, imn = th.index(mx), th.index(mn)
        out.update(swing=math.degrees(mx - mn), gmin=min(g for g in gm if g is not None), wmax=max(abs(x) for x in thd if x is not None),
                   back=(imn - imx) % 360, fwd=360 - (imn - imx) % 360, i_max=imx, i_min=imn)
    return out


def rssr_pose(r, b, c, pre, phi):
    """主轴转角 phi（度）时 RSSR 各点位置（画三维零件用）；装不上返回 None"""
    ex = (1.0, 0.0, 0.0)
    e = _unit((math.cos(pre["gam"] * DEG), math.sin(pre["gam"] * DEG) * math.sin(pre["bet"] * DEG),
               math.sin(pre["gam"] * DEG) * math.cos(pre["bet"] * DEG)))
    ref = _sub(ex, _mul(e, _dot(ex, e)))
    if _norm(ref) < 1e-6:
        ref = _sub((0, 0, 1.0), _mul(e, e[2]))
    ref = _unit(ref)
    v0 = _rot(ref, e, pre["dl"] * DEG)
    v1 = _cross(e, v0)
    Q = tuple(pre["Q0"])
    C = (pre["xc"], M0[1], M0[2])
    ang = phi * DEG + pre["ph0"]
    A = _add(C, (0, r * math.cos(ang), r * math.sin(ang)))
    K = _sub(A, Q)
    P_, K_ = _dot(K, v0), _dot(K, v1)
    M = (_dot(K, K) + c * c - b * b) / (2 * c)
    rho = math.hypot(P_, K_)
    if abs(M) > rho:
        return None
    t = math.atan2(K_, P_) + math.acos(M / rho)
    B = _add(Q, _mul(_add(_mul(v0, math.cos(t)), _mul(v1, math.sin(t))), c))
    return dict(A=A, B=B, Q=Q, C=C, e=e, v0=v0, v1=v1, th=t)


def r_critical(b, c, pre, lo, hi=20.0):
    """曲柄能整周转动的最大偏心半径（二分 40 次，同 ch09.py）"""
    for _ in range(40):
        mid = (lo + hi) / 2
        if rssr(mid, b, c, pre)["fail"]:
            hi = mid
        else:
            lo = mid
    return lo


def needle_s(p, f):
    r, l = p["r"], p["l"]
    lam = r / l
    a = f * DEG
    return r * (1 - math.cos(a)) - l * (1 - math.sqrt(1 - (lam * math.sin(a)) ** 2))


def needle_h(p, f):
    """针尖高出针板（mm）；针沿 20° 斜线运动，竖直分量乘 cos20°"""
    return p["tip0"] - needle_s(p, f) * math.cos(INCLINE * DEG)


def crossings(p, level):
    """针尖穿过高度 level 的两个转角（下行入、上行出），0.001° 步长同 ch09.py 的精度，用二分求"""
    def bis(a, b):
        fa = needle_h(p, a) - level
        for _ in range(60):
            m = (a + b) / 2
            fm = needle_h(p, m) - level
            if (fm > 0) == (fa > 0):
                a, fa = m, fm
            else:
                b = m
        return (a + b) / 2
    if needle_h(p, 180) >= level:
        return None
    return bis(0, 180), bis(180, 360)


def diff_feed(fab, D, pf, s):
    """虚拟实验 9-1 的差动送布模型"""
    f = DFAB[fab]
    e0 = f["e0"] * pf
    De = 1 + f["eta"] * (D - 1)
    slip = ""
    Dmax, Dmin = 1 / (1 - f["gmax"]), 1 / (1 + f["emax"])
    if De > Dmax:
        De, slip = Dmax, "push"
    if De < Dmin:
        De, slip = Dmin, "pull"
    eps = (1 + e0) / De - 1
    lamG = 4 + 2 * s
    amp = f["lam"] * math.sqrt(eps) / math.pi if eps >= 0 else lamG * math.sqrt(-eps) / math.pi
    dstar = 1 + e0 / f["eta"]
    return dict(e0=e0, De=De, eps=eps, amp=amp, slip=slip, lamG=lamG, dstar=dstar, lam=f["lam"])


def analyze(params=None, trial=True):
    p = clean(params)
    n = p["n"]
    w = 2 * math.pi * n / 60
    lam = p["r"] / p["l"]
    low = p["tip0"] - 2 * p["r"] * math.cos(INCLINE * DEG)
    cr = crossings(p, p["t"])
    pin, pout = cr if cr else (None, None)
    L = rssr(p["ll_r"], p["ll_b"], p["ll_c"], LL, n)
    U = rssr(p["ul_r"], p["ul_b"], p["ul_c"], UL, n)
    rc = r_critical(p["ll_b"], p["ll_c"], LL, lo=2.0)
    DF = diff_feed(p["fab"], p["D"], p["pf"], p["s"])
    tip_v = L["wmax"] * p["ll_R"] / 1000 if "wmax" in L else None
    ch = Checks()

    # 针与送布（9.5、9.8）
    if cr:
        m1, m2 = p["f_on"] - pout, pin - p["f_off"]
        mm = min(m1, m2)
        ch.add("feed_window", "feed", "送布只在针离布时（两头余量）", "Feed only while the needle is out (margins)",
               (f"出布 {pout:.1f}° → 送布 {p['f_on']:.0f}°：{m1:.1f}°；送布止 {p['f_off']:.0f}° → 入布 {pin:.1f}°：{m2:.1f}°",
                f"leave {pout:.1f}° → feed {p['f_on']:.0f}°: {m1:.1f}°; feed stops {p['f_off']:.0f}° → enter {pin:.1f}°: {m2:.1f}°"),
               ("两头 ≥ 5°（算例约 13°）", "≥ 5° each side (example ≈ 13°)"),
               "ok" if mm >= 5 else ("warn" if mm >= 0 else "bad"), 9,
               "" if mm >= 5 else "针还在布里时送布牙在动：把送布窗口收窄，或减小布厚、提高针尖最高点。",
               "" if mm >= 5 else "The dogs move while the needle is in the fabric: narrow the feed window, or raise the needle's top position.")
    else:
        ch.add("needle_in", "needle", "针能刺穿布", "Needle passes through the fabric", ("刺不穿", "does not pass"), ("针尖最低点低于布面", "lowest tip below fabric top"),
               "bad", 9, "加大曲柄半径或降低针杆。", "Increase the crank radius or lower the needle bar.")
    ch.add("lambda", "needle", "引针连杆比 λ", "Needle rod ratio λ", f"{lam:.3f}", "0.20–0.40", "ok" if 0.2 <= lam <= 0.4 else "warn", 9)
    # 下弯针（9.6）
    if L["fail"]:
        ch.add("ll_turn", "lower", "下弯针机构整周转动", "Lower looper linkage turns fully",
               (f"在 {L['fail'][0]}°–{L['fail'][-1]}° 卡死", f"locks at {L['fail'][0]}°–{L['fail'][-1]}°"), ("能整周转动", "full revolution"), "bad", 9,
               f"偏心半径要小于临界值约 {rc:.2f} mm，或加长球头连杆、摆杆。", f"Keep the eccentric below about {rc:.2f} mm, or lengthen the link or rocker.")
    else:
        arc = L["swing"] * DEG * p["ll_R"]
        ch.add("ll_swing", "lower", "下弯针摆角与弧长", "Lower looper swing and arc",
               (f"{L['swing']:.1f}°，弯针尖走 {arc:.1f} mm", f"{L['swing']:.1f}°, point travels {arc:.1f} mm"),
               ("弧长 15–20 mm（算例 25.7°、约 17 mm）", "arc 15–20 mm (example 25.7°, ≈ 17 mm)"),
               "ok" if 15 <= arc <= 20 else "warn", 9,
               "" if 15 <= arc <= 20 else ("弧长太短，弯针尖赶不到针后钩线环：加大偏心半径（粗估 Δθ ≈ 2r/c，实际还要多一些）。" if arc < 15 else
                                           "弧长太长，弯针尖向右摆得过远，速度和惯性力增大：减小偏心半径。"),
               "" if 15 <= arc <= 20 else ("Arc too short to reach behind the needle: increase the eccentric (rough Δθ ≈ 2r/c, actually a bit more)." if arc < 15 else
                                           "Arc too long: the point swings too far right, raising speed and inertia; reduce the eccentric."))
        ch.add("ll_gamma", "lower", "下弯针最小传动角", "Lower looper minimum transmission angle", f"{L['gmin']:.1f}°", "≥ 40°",
               "ok" if L["gmin"] >= 40 else "warn", 9, "" if L["gmin"] >= 40 else "传动角小，球铰受力大、磨损快：调摆杆长或连杆长。",
               "" if L["gmin"] >= 40 else "A small transmission angle loads the ball joints: change the rocker or link length.")
        ch.add("ll_crit", "lower", "偏心半径离卡死临界值", "Eccentric radius vs. lock-up limit", f"{p['ll_r']:.2f} / {rc:.2f} mm",
               ("不超过临界值的 70%", "≤ 70% of the limit"), "ok" if p["ll_r"] <= 0.7 * rc else "warn", 9,
               "" if p["ll_r"] <= 0.7 * rc else "离卡死太近，制造误差一大就可能装不上。", "" if p["ll_r"] <= 0.7 * rc else "Too close to lock-up; manufacturing errors may stop it assembling.")
        ch.add("ll_speed", "lower", "下弯针尖最高速度", "Lower looper point peak speed", f"{tip_v:.2f} m/s", "≤ 10 m/s",
               "ok" if tip_v <= 10 else "warn", 9, "" if tip_v <= 10 else "弯针尖太快，线环容易被打散，球铰和导套磨损快：降低转速或摆角。",
               "" if tip_v <= 10 else "The point is too fast: loops scatter and joints wear; lower the speed or swing.")
    # 上弯针（9.7）
    if U["fail"]:
        ch.add("ul_turn", "upper", "上弯针机构整周转动", "Upper looper linkage turns fully",
               (f"在 {U['fail'][0]}°–{U['fail'][-1]}° 卡死", f"locks at {U['fail'][0]}°–{U['fail'][-1]}°"), ("能整周转动", "full revolution"), "bad", 9,
               "减小偏心半径或加长连杆。", "Reduce the eccentric or lengthen the link.")
    else:
        ch.add("ul_gamma", "upper", "上弯针最小传动角", "Upper looper minimum transmission angle", f"{U['gmin']:.1f}°", "≥ 40°",
               "ok" if U["gmin"] >= 40 else "warn", 9,
               "" if U["gmin"] >= 40 else "略低于 40° 的经验值（教材算例机即 39°，连杆力只比 40° 时大约 2%，可先保留，样机跑合后看球头温升和磨损再定）；要提高，在摆角不变的前提下移动摇杆轴或改连杆长。",
               "" if U["gmin"] >= 40 else "Slightly under the 40° rule of thumb (the textbook machine has 39°; link force only ~2% higher), acceptable for now — check ball-joint heat and wear after running in; to raise it, move the rocker axis or change the link length at the same swing.")
    # 差动送布（9.10）
    e = DF["eps"]
    st = "ok" if abs(e) <= 0.02 and not DF["slip"] else ("warn" if abs(e) <= 0.05 and not DF["slip"] else "bad")
    look = ("平整", "flat") if abs(e) <= 0.02 else ((f"波浪高约 {DF['amp']:.1f} mm", f"waves ≈ {DF['amp']:.1f} mm high") if e > 0 else
                                                    (f"细褶高约 {DF['amp']:.1f} mm", f"gathers ≈ {DF['amp']:.1f} mm high"))
    ch.add("diff", "feed", "布边平整（差动送布）", "Flat seam edge (differential feed)",
           (f"ε = {e * 100:+.1f}%，{look[0]}" + ("；送布牙打滑" if DF["slip"] else ""), f"ε = {e * 100:+.1f}%, {look[1]}" + ("; dogs slip" if DF["slip"] else "")),
           ("|ε| ≤ 2%（虚拟实验 9-1 的平整带）", "|ε| ≤ 2% (flat band of lab 9-1)"), st, 9,
           "" if st == "ok" else f"把差动比调到约 {DF['dstar']:.2f}（这种面料的平整差动比）。",
           "" if st == "ok" else f"Set the differential ratio to about {DF['dstar']:.2f} (the flat ratio for this fabric).")
    ch.add("diff_range", "feed", "差动比在常见调节范围内", "Ratio within the usual range", f"{p['D']:.2f}", "0.7–2.0",
           "ok" if 0.7 <= p["D"] <= 2.0 else "warn", 9)
    # 切边（9.9）
    kin = cr and pin <= p["kn_ph"] <= pout
    ch.add("knife_time", "knife", "上刀切布时针在布里（布静止）", "Knife cuts while the needle holds the fabric",
           f"{p['kn_ph']:.0f}°", (f"在入布 {pin:.1f}° 与出布 {pout:.1f}° 之间", f"between {pin:.1f}° and {pout:.1f}°") if cr else "—",
           "ok" if kin else "bad", 9, "" if kin else "布在动的时候切，切口不齐：把上刀最低点调到机针在布里的时段。",
           "" if kin else "Cutting while the fabric moves leaves a ragged edge: time the knife bottom while the needle is in.")
    ch.add("knife_ov", "knife", "上下刀重叠量", "Knife overlap", f"{p['kn_ov']:.2f} mm", "0.5–1.0 mm",
           "ok" if 0.5 <= p["kn_ov"] <= 1.0 else ("bad" if p["kn_ov"] < 0.3 else "warn"), 9,
           "" if 0.5 <= p["kn_ov"] <= 1.0 else ("重叠太小切不断。" if p["kn_ov"] < 0.5 else "重叠太大刀口磨损快。"),
           "" if 0.5 <= p["kn_ov"] <= 1.0 else ("Too little overlap does not cut." if p["kn_ov"] < 0.5 else "Too much overlap wears the edges."))

    results = [
        result("引针连杆比 λ", "Needle rod ratio λ", f"{lam:.3f}"),
        result("针杆行程（沿针）", "Needle stroke (along the needle)", f"{2 * p['r']:.2f}", "mm"),
        result("针尖最低点", "Lowest tip position", f"{low:.2f}", "mm"),
        result("入布 / 出布", "Enters / leaves fabric", f"{pin:.1f} / {pout:.1f}" if cr else "—", "°"),
        result("针在布中 / 送布可用", "Needle in fabric / free for feed", f"{pout - pin:.1f} / {360 - (pout - pin):.1f}" if cr else "—", "°"),
        result("下弯针摆角", "Lower looper swing", f"{L['swing']:.2f}" if "swing" in L else "—", "°"),
        result("下弯针来回所用转角", "Lower looper strokes (one way / back)", f"{L['back']} / {L['fwd']}" if "back" in L else "—", "°"),
        result("下弯针最大角速度", "Lower looper peak angular speed", f"{L['wmax']:.1f}" if "wmax" in L else "—", "rad/s"),
        result("下弯针尖最高速度", "Lower looper point peak speed", f"{tip_v:.2f}" if tip_v else "—", "m/s"),
        result("下弯针偏心临界半径", "Lower looper eccentric limit", f"{rc:.2f}", "mm"),
        result("上弯针摆角", "Upper looper swing", f"{U['swing']:.2f}" if "swing" in U else "—", "°"),
        result("平整差动比 D*", "Flat differential ratio D*", f"{DF['dstar']:.3f}"),
        result("布边伸长 ε / 外观", "Edge stretch ε / look", f"{DF['eps'] * 100:+.1f}% / {DF['amp']:.1f}", "% / mm"),
        result("差动臂长 l_d = D·l_m", "Differential arm l_d = D·l_m", f"{p['D'] * p['lm']:.1f}", "mm"),
    ]
    phi = list(range(0, 360, 2))
    charts = [line_chart("needle", "针尖高出针板（mm），虚线为布面", "Needle tip above the plate (mm), dashed: fabric top", phi,
                         [("针尖", "tip", "#2d6fb3", [needle_h(p, f) for f in phi])], ref=p["t"], zero=True)]
    if not L["fail"]:
        charts.append(line_chart("lower", "下弯针摆角（°）", "Lower looper swing (°)", phi,
                                 [("摆角", "swing", "#c0392b", [math.degrees(L["th"][f] - min(x for x in L["th"])) for f in phi])]))
        charts.append(line_chart("lgam", "下弯针传动角（°），虚线 40°", "Lower looper transmission angle (°), dashed 40°", phi,
                                 [("传动角", "γ", "#2e9e6a", [L["gm"][f] for f in phi])], ref=40))
    if not U["fail"]:
        charts.append(line_chart("upper", "上弯针摆角（°）", "Upper looper swing (°)", phi,
                                 [("摆角", "swing", "#7d5ba6", [math.degrees(U["th"][f] - min(x for x in U["th"])) for f in phi])]))
    timing = []
    if cr:
        timing.append(dict(key="needle_in", zh="针在布中", en="Needle in fabric", a=round(pin, 1), b=round(pout, 1)))
    timing.append(dict(key="feed", zh="送布牙在针板上", en="Feed dogs above plate", a=p["f_on"], b=p["f_off"]))
    if "i_max" in L:
        timing.append(dict(key="ll", zh="下弯针一个方向的行程", en="Lower looper stroke one way", a=L["i_max"], b=L["i_min"]))
    if "i_max" in U:
        timing.append(dict(key="ul", zh="上弯针一个方向的行程", en="Upper looper stroke one way", a=U["i_max"], b=U["i_min"]))
    timing.append(dict(key="knife", zh="上刀最低点", en="Upper knife at bottom", a=p["kn_ph"], b=p["kn_ph"], mark=p["kn_ph"]))
    return dict(version=VERSION, machine=MACHINE, params=p, checks=list(ch), ok=not any(c["state"] == "bad" for c in ch),
                results=results, charts=charts, timing=timing, parts=parts(p, rc), card=adjust_card(p),
                view=dict(page="model-overlock", sync=None, cfg={}))


def parts(p, rc=None):
    return [
        dict(key="needle", zh="斜向针杆机构", en="Inclined needle drive", dims=[("曲柄半径 r", "Crank radius r", p["r"], "mm"), ("连杆长 l", "Rod length l", p["l"], "mm"),
                                                                           ("倾角", "Incline", INCLINE, "°")]),
        dict(key="lower", zh="下弯针 RSSR", en="Lower looper RSSR", dims=[("偏心半径", "Eccentric", p["ll_r"], "mm"), ("球头连杆", "Ball link", p["ll_b"], "mm"),
                                                                           ("摆杆", "Rocker", p["ll_c"], "mm"), ("弯针尖到摆轴", "Point to axis", p["ll_R"], "mm"),
                                                                           ("摆轴与针平行（倾角）", "Rocker axis parallel to needle", INCLINE, "°")]),
        dict(key="upper", zh="上弯针 RSSR", en="Upper looper RSSR", dims=[("偏心半径", "Eccentric", p["ul_r"], "mm"), ("球头连杆", "Ball link", p["ul_b"], "mm"),
                                                                           ("摆杆", "Rocker", p["ul_c"], "mm")]),
        dict(key="feed", zh="差动送布", en="Differential feed", dims=[("主送布臂 l_m", "Main arm l_m", p["lm"], "mm"),
                                                                       ("差动臂 l_d", "Differential arm l_d", round(p["D"] * p["lm"], 2), "mm"),
                                                                       ("针距", "Stitch length", p["s"], "mm")]),
        dict(key="knife", zh="切边刀", en="Trimming knives", dims=[("上刀行程", "Upper knife stroke", 6.0, "mm"), ("重叠量", "Overlap", p["kn_ov"], "mm"),
                                                                     ("切边线到针", "Cut line to needle", p["w"], "mm")]),
    ]


def adjust_card(params=None):
    p = clean(params)
    cr = crossings(p, p["t"])
    DF = diff_feed(p["fab"], p["D"], p["pf"], p["s"])
    pin, pout = cr if cr else (0, 0)
    return [
        dict(zh="针杆高度", en="Needle-bar height", do_zh=f"针杆在最高点时针尖高出针板 {p['tip0']:.1f} mm。",
             do_en=f"At the top the needle point is {p['tip0']:.1f} mm above the plate."),
        dict(zh="下弯针", en="Lower looper", do_zh="弯针尖从针后擦过，间隙 0.05 mm；针开始回升时弯针尖到针后（算例 213.6°）。",
             do_en="The point passes behind the needle with 0.05 mm clearance, arriving as the needle starts to rise (example 213.6°)."),
        dict(zh="上弯针", en="Upper looper", do_zh="上弯针穿过下弯针线三角时间隙 0.10 mm；针从上弯针刀身和线之间穿过，间隙 0.10 mm。",
             do_en="0.10 mm clearance where the upper looper crosses the lower looper's thread triangle, and where the needle passes it."),
        dict(zh="送布", en="Feed", do_zh=f"送布牙在 {p['f_on']:.0f}° 露出针板、{p['f_off']:.0f}° 落下；针 {pout:.1f}° 出布、{pin:.1f}° 入布。",
             do_en=f"The dogs rise at {p['f_on']:.0f}° and drop at {p['f_off']:.0f}°; the needle leaves at {pout:.1f}° and enters at {pin:.1f}°."),
        dict(zh="差动比", en="Differential ratio", do_zh=f"差动调节杆放在 D = {p['D']:.2f}（差动臂 {p['D'] * p['lm']:.1f} mm）；这种面料平整约在 D = {DF['dstar']:.2f}，以试缝为准。",
             do_en=f"Set the lever to D = {p['D']:.2f} (arm {p['D'] * p['lm']:.1f} mm); this fabric lies flat near D = {DF['dstar']:.2f} — confirm with a test seam."),
        dict(zh="切刀", en="Knives", do_zh=f"上刀最低点在 {p['kn_ph']:.0f}°，越过下刀 {p['kn_ov']:.2f} mm，弹簧轻压贴紧下刀；切边线离针 {p['w']:.1f} mm。",
             do_en=f"Upper knife bottoms at {p['kn_ph']:.0f}°, {p['kn_ov']:.2f} mm past the lower knife, spring-loaded against it; cut line {p['w']:.1f} mm from the needle."),
    ]
