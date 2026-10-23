# -*- coding: utf-8 -*-
"""电子花样机（模板机）设计计算（第 42 轮）。

模型出自教材《缝纫机设计与制造》第 15 章：15.3 离布窗口与转速上限，15.4 运动规律与前瞻调速，15.1.1 同步带的弹性与共振，
15.6 周期时间，15.8 X、Y 轴伺服选型。与虚拟实验 15-1（labs/pattern.html）同一套公式和花样：
每轴移动时间 t = max(√(C·s/a), 2s/v)；窗口两端各扣余量；起针 3 针、剪线前 2 针限慢速；前瞻先反向后正向。
默认参数是教材算例改出的一台“全绿”的设计：X 轴带轮按 15.8 节第二条路取 10 mm，Y 轴更重、加速度取得低一些。
"""
import math

from .common import Checks, line_chart, make_params, result

MACHINE = "pattern"
NAME = ("电子花样机", "Pattern Sewing")
VERSION = "1.0"
LECTURES = ("第 15 章", "chapter 15")
D = math.pi / 180
R, L = 15.5, 55.0           # 针杆曲柄滑块（第 3 章算例，同平缝机）
LAM = R / L
TIP = 18.0                  # 上止点时针尖在针板上方的高度（mm）
G = 9.8
NSLOW_N = (3, 2)            # 起针后、剪线前限慢速的针数（同虚拟实验 15-1）
MAX_PTS = 3000

LAWS = {"c4": 4.0, "mtrap": 4.89, "cyc": 6.28}

GROUPS = [
    ("basic", "基本参数", "Basic", [
        ("n", "设计缝纫转速", "Design sewing speed", "r/min", 1800, 300, 4000, 50),
        ("n_head", "机头最高转速", "Head top speed", "r/min", 2800, 1000, 4000, 50),
        ("pat", "花样", "Pattern", "", "flap", None, None, None),
        ("s", "针距", "Stitch length", "mm", 3.0, 0.5, 12.7, 0.1),
        ("t", "布加下模板总厚", "Fabric + lower template thickness", "mm", 1.5, 0.5, 8.0, 0.1),
    ]),
    ("motion", "运动规划（15.3–15.4 节）", "Motion planning (15.3–15.4)", [
        ("law", "运动规律", "Motion law", "", "c4", None, None, None),
        ("mg", "窗口每端余量（伺服整定）", "Window margin at each end (servo settling)", "°", 5, 0, 30, 0.5),
        ("dn", "每针允许转速变化", "Speed change allowed per stitch", "r/min", 300, 50, 1000, 10),
        ("nslow", "起针、剪线前慢速", "Slow speed at start and before trimming", "r/min", 400, 100, 1500, 10),
    ]),
    ("xaxis", "X 轴（15.8 节）", "X axis (15.8)", [
        ("mx", "运动质量（压框、模板、滑座）", "Moving mass (clamp, template, carriage)", "kg", 3.0, 0.5, 30, 0.1),
        ("ax", "加速度", "Acceleration", "m/s²", 50, 5, 200, 1),
        ("rx", "同步带轮节圆半径", "Pulley pitch radius", "mm", 10, 5, 40, 0.5),
        ("TxR", "电机额定转矩", "Motor rated torque", "N·m", 1.27, 0.1, 20, 0.01),
        ("TxP", "电机峰值转矩", "Motor peak torque", "N·m", 3.8, 0.3, 60, 0.01),
        ("Jx", "电机转子惯量", "Motor rotor inertia", "×10⁻⁴ kg·m²", 0.3, 0.02, 20, 0.01),
    ]),
    ("yaxis", "Y 轴（带着 X 轴走，更重）", "Y axis (carries the X axis, heavier)", [
        ("my", "运动质量（横梁连同 X 轴）", "Moving mass (beam with the X axis)", "kg", 6.0, 1, 60, 0.1),
        ("ay", "加速度", "Acceleration", "m/s²", 40, 5, 200, 1),
        ("ry", "同步带轮节圆半径", "Pulley pitch radius", "mm", 10, 5, 40, 0.5),
        ("TyR", "电机额定转矩", "Motor rated torque", "N·m", 2.39, 0.1, 20, 0.01),
        ("TyP", "电机峰值转矩", "Motor peak torque", "N·m", 7.16, 0.3, 60, 0.01),
        ("Jy", "电机转子惯量", "Motor rotor inertia", "×10⁻⁴ kg·m²", 1.0, 0.02, 20, 0.01),
    ]),
    ("drive", "传动与工作台", "Drive and table", [
        ("v", "每轴最高速度", "Top speed of each axis", "m/s", 1.0, 0.2, 5, 0.1),
        ("Nmot", "电机额定转速", "Motor rated speed", "r/min", 3000, 1000, 6000, 100),
        ("mu", "导轨摩擦系数", "Guide friction coefficient", "", 0.05, 0, 0.3, 0.01),
        ("EA", "同步带拉伸刚度 EA（15 mm 宽约 150，25 mm 宽约 250）", "Belt axial stiffness EA (15 mm wide ≈ 150, 25 mm ≈ 250)", "kN", 250, 50, 1000, 10),
        ("L1", "滑座一侧带长", "Belt length on one side", "m", 0.3, 0.05, 2, 0.01),
        ("L2", "滑座另一侧带长", "Belt length on the other side", "m", 0.5, 0.05, 2, 0.01),
        ("nyb", "Y 轴同步带根数（两端驱动 = 2）", "Y-axis belts (driven at both ends = 2)", "", 2, 1, 4, 1),
        ("stx", "工作台 X 行程", "Table travel X", "mm", 250, 50, 1500, 10),
        ("sty", "工作台 Y 行程", "Table travel Y", "mm", 160, 50, 1500, 10),
    ]),
    ("cycle", "周期与产能（15.6 节）", "Cycle and output (15.6)", [
        ("t_extra", "剪线、空走、起停另需时间", "Trimming, jumps, start and stop", "s", 1.5, 0, 30, 0.1),
        ("t_load", "取放模板、放布", "Load and unload", "s", 9, 0, 120, 0.5),
    ]),
]
CHOICES = {
    "pat": [("flap", "口袋盖（60 × 40 mm）", "Pocket flap (60 × 40 mm)"), ("circle", "圆（直径 50 mm）", "Circle (50 mm dia.)"),
            ("star", "五角星", "Star"), ("rect", "矩形框（80 × 50 mm）", "Rectangle (80 × 50 mm)"),
            ("bartack", "套结（10 × 2 mm）", "Bartack (10 × 2 mm)"), ("zig", "大之字（宽 12 mm）", "Large zigzag (12 mm wide)"),
            ("csv", "上传的针位表", "Uploaded stitch list")],
    "law": [("c4", "等加速等减速（C = 4）", "Constant acceleration (C = 4)"), ("mtrap", "修正梯形（C = 4.89）", "Modified trapezoid (C = 4.89)"),
            ("cyc", "摆线（C = 6.28）", "Cycloidal (C = 6.28)")],
}
PARAMS, DEFAULTS, _clean = make_params(GROUPS, CHOICES)


def clean(p):
    """参数整理；上传的针位表（pts：[[x, y], …]，mm）照原样留着，项目里一起存"""
    out = _clean(p)
    pts = parse_pts((p or {}).get("pts"))
    if pts:
        out["pts"] = pts
    elif out["pat"] == "csv":
        out["pat"] = "flap"
    return out


def parse_pts(raw):
    """针位表：列表 [[x, y], …] 或 CSV 文字（每行 x, y；可有表头；单位 mm）"""
    if not raw:
        return None
    rows = []
    if isinstance(raw, str):
        for line in raw.splitlines():
            parts = [q for q in line.replace("\t", ",").replace(";", ",").split(",") if q.strip()]
            if len(parts) < 2:
                continue
            try:
                rows.append([float(parts[0]), float(parts[1])])
            except ValueError:
                continue
    elif isinstance(raw, (list, tuple)):
        for q in raw:
            try:
                rows.append([float(q[0]), float(q[1])])
            except (TypeError, ValueError, IndexError):
                continue
    rows = [[round(x, 3), round(y, 3)] for x, y in rows if math.isfinite(x) and math.isfinite(y) and abs(x) < 2000 and abs(y) < 2000]
    return rows[:MAX_PTS] if len(rows) >= 2 else None


# ---------- 针杆与离布窗口（15.3 节） ----------
def xN(f):
    a = f * D
    return R * (1 - math.cos(a)) - L * (1 - math.sqrt(1 - (LAM * math.sin(a)) ** 2))


def _bis(g, a, b):
    ga = g(a)
    for _ in range(60):
        m = (a + b) / 2
        gm = g(m)
        if (gm > 0) == (ga > 0):
            a, ga = m, gm
        else:
            b = m
    return (a + b) / 2


def window(t):
    """布加下模板总厚 t：入布角、出布角、几何窗口 W（度）"""
    f1 = _bis(lambda f: TIP - xN(f) - t, 0.0, 180.0)
    f2 = _bis(lambda f: TIP - xN(f) - t, 180.0, 360.0)
    return f1, f2, 360 - (f2 - f1)


def t_axis(s, a, v, C=4.0):
    """一轴走 s（mm）的时间（s）：加速度限制 √(C·s/a)，速度限制 2s/v（三种规律的峰值速度都约为 2s/Δt）"""
    if s <= 0:
        return 0.0
    return max(math.sqrt(C * s / 1000 / a), 2 * s / 1000 / v)


def n_max(W, tm, n_head=1e9):
    return n_head if tm <= 0 else min(n_head, W / (6 * tm))


def lookahead(caps, dn, n_set=1e9, nslow=None, n0=None):
    """15.4.3 节：反向扫描为后面的慢针提前减速，正向扫描限制加速。nslow 给出时起针 3 针、剪线前 2 针限慢速；
    n0：第 1 针的转速（不给 = 起针慢速，没有慢速时取第 1 针自身上限）"""
    N = len(caps)
    c = [min(x, n_set) for x in caps]
    if nslow is not None:
        for i in range(N):
            if i < NSLOW_N[0] or i >= N - NSLOW_N[1]:
                c[i] = min(c[i], nslow)
    for i in range(N - 2, -1, -1):
        c[i] = min(c[i], c[i + 1] + dn)
    out = []
    for i in range(N):
        if i == 0:
            out.append(min(c[0], n0 if n0 is not None else (nslow if nslow is not None else c[0])))
        else:
            out.append(min(c[i], out[-1] + dn))
    return out


# ---------- 花样（与虚拟实验 15-1 相同，mm，原点在中心） ----------
def _arc(cx, cy, r, a0, a1):
    return ("A", cx, cy, r, a0, a1)


def _sample(segs, s):
    out = []
    for gi, g in enumerate(segs):
        if g[0] == "L":
            (ax, ay), (bx, by) = g[1], g[2]
            dx, dy = bx - ax, by - ay
            n = max(1, math.ceil(math.hypot(dx, dy) / s - 1e-9))
            for j in range(0 if gi == 0 else 1, n + 1):
                out.append([ax + dx * j / n, ay + dy * j / n])
        else:
            _, cx, cy, r, a0, a1 = g
            n = max(2, math.ceil(abs(a1 - a0) * D * r / s - 1e-9))
            for j in range(0 if gi == 0 else 1, n + 1):
                a = (a0 + (a1 - a0) * j / n) * D
                out.append([cx + r * math.cos(a), cy + r * math.sin(a)])
    return out


def stitches(p):
    s = p["s"]
    k = p["pat"]
    if k == "csv" and p.get("pts"):
        return [list(q) for q in p["pts"]]
    if k == "bartack":
        Lb, Wd = 10.0, 2.0
        pts = [[-Lb / 2 + j * Lb / 6, (1 if j % 2 else -1) * 0.3 * Wd] for j in range(7)]
        pts += [[Lb / 2 - q * Lb / 28, (1 if q % 2 else -1) * Wd / 2] for q in range(1, 29)]
        return pts
    if k == "zig":
        return [[-25 + i * 5, 6 if i % 2 else -6] for i in range(11)]
    if k == "circle":
        out = _sample([_arc(0, 0, 25, 90, 450)], s)
    elif k == "star":
        P = [[(12 if i % 2 else 30) * math.cos(math.pi / 2 + i * math.pi / 5), (12 if i % 2 else 30) * math.sin(math.pi / 2 + i * math.pi / 5)] for i in range(10)]
        out = _sample([("L", P[i], P[(i + 1) % 10]) for i in range(10)], s)
    elif k == "rect":
        c = [[-40, -25], [40, -25], [40, 25], [-40, 25]]
        out = _sample([("L", c[i], c[(i + 1) % 4]) for i in range(4)], s)
    else:   # flap
        out = _sample([("L", [-30, 20], [-30, -10]), _arc(-20, -10, 10, 180, 270), ("L", [-20, -20], [20, -20]),
                       _arc(20, -10, 10, 270, 360), ("L", [30, -10], [30, 20])], s)
    if len(out) > 2:                       # 起针回针：沿第一段来回两针（同虚拟实验 15-1）
        out = [out[0], out[1], out[0]] + out[1:]
    return out


# ---------- 电机（15.8 节） ----------
def axis_motor(m, a, r_mm, J4, TR, TP, mu, v, Nmot, duty):
    r = r_mm / 1000
    J = J4 * 1e-4
    F = m * a + mu * m * G
    Tpk = F * r + J * a / r
    Trms = Tpk * math.sqrt(max(0.0, min(1.0, duty)))
    rpm = v / r * 60 / (2 * math.pi)
    return dict(F=F, Tpk=Tpk, Trms=Trms, rpm=rpm, ok_pk=Tpk <= TP, ok_rms=Trms <= TR, ok_rpm=rpm <= Nmot, use_pk=Tpk / TP, use_rms=Trms / TR,
                r_opt=math.sqrt(J / m) * 1000)


def belt(EA_kN, L1, L2, m, nb=1):
    k = nb * EA_kN * 1000 * (1 / L1 + 1 / L2)
    return k, math.sqrt(k / m) / (2 * math.pi)


def plan(p):
    """整个花样：每针自身上限、前瞻后的转速、用时"""
    C = LAWS[p["law"]]
    f1, f2, Wg = window(p["t"])
    W = max(10.0, Wg - 2 * p["mg"])
    pts = stitches(p)
    caps, steps = [], []
    for i, q in enumerate(pts):
        if i == 0:
            caps.append(p["n_head"])
            steps.append((0.0, 0.0))
            continue
        sx, sy = abs(q[0] - pts[i - 1][0]), abs(q[1] - pts[i - 1][1])
        tm = max(t_axis(sx, p["ax"], p["v"], C), t_axis(sy, p["ay"], p["v"], C))
        caps.append(n_max(W, tm, p["n_head"]))
        steps.append((sx, sy))
    sp = lookahead(caps, p["dn"], min(p["n"], p["n_head"]), p["nslow"])
    t_sew = sum(60 / n for n in sp[1:]) if len(sp) > 1 else 0.0
    return dict(pts=pts, caps=caps, speeds=sp, steps=steps, W=W, Wg=Wg, f1=f1, f2=f2, C=C, t_sew=t_sew)


def analyze(params=None, trial=True):
    p = clean(params)
    PL = plan(p)
    C, W, f1, f2 = PL["C"], PL["W"], PL["f1"], PL["f2"]
    s = p["s"]
    nmx = n_max(W, t_axis(s, p["ax"], p["v"], C))
    nmy = n_max(W, t_axis(s, p["ay"], p["v"], C))
    nm45 = n_max(W, max(t_axis(s / math.sqrt(2), p["ax"], p["v"], C), t_axis(s / math.sqrt(2), p["ay"], p["v"], C)))
    duty = W / 360                          # 最坏情况：每针都用满窗口（15.8 节第 3 步）
    MX = axis_motor(p["mx"], p["ax"], p["rx"], p["Jx"], p["TxR"], p["TxP"], p["mu"], p["v"], p["Nmot"], duty)
    MY = axis_motor(p["my"], p["ay"], p["ry"], p["Jy"], p["TyR"], p["TyP"], p["mu"], p["v"], p["Nmot"], duty)
    kx, fx = belt(p["EA"], p["L1"], p["L2"], p["mx"])
    ky, fy = belt(p["EA"], p["L1"], p["L2"], p["my"], p["nyb"])
    tmx, tmy = t_axis(s, p["ax"], p["v"], C), t_axis(s, p["ay"], p["v"], C)
    dx_mm = MX["F"] / kx * 1000
    pts, sp, caps = PL["pts"], PL["speeds"], PL["caps"]
    N = len(pts)
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    bw, bh = (max(xs) - min(xs), max(ys) - min(ys)) if pts else (0, 0)
    avg = (N - 1) * 60 / PL["t_sew"] if PL["t_sew"] > 0 else 0
    t_cycle = PL["t_sew"] + p["t_extra"]
    pph = 3600 / (t_cycle + p["t_load"]) if t_cycle + p["t_load"] > 0 else 0
    slow_n = sum(1 for i in range(1, N) if caps[i] < min(p["n"], p["n_head"]) - 0.5)

    ch = Checks()
    worst = min(nmx, nmy)
    ch.add("speed", "motion", "设计转速下标准针距走得完（两轴中较慢的一轴）", "Standard stitch fits the window at design speed (slower axis)",
           (f"{p['n']:.0f} r/min；上限 X {nmx:.0f}、Y {nmy:.0f}", f"{p['n']:.0f} r/min; limits X {nmx:.0f}, Y {nmy:.0f}"),
           (f"≤ {worst:.0f} r/min", f"≤ {worst:.0f} r/min"), "ok" if p["n"] <= worst + 0.5 else "bad", 15,
           "降设计转速，或提高较慢那一轴的加速度（换电机、减轻运动质量），或用较“硬”的运动规律。",
           "Lower the design speed, or raise the acceleration of the slower axis (motor, lighter moving parts), or use a stiffer motion law.")
    ch.add("head", "motion", "设计转速不超过机头最高转速", "Design speed within the head top speed", f"{p['n']:.0f} r/min",
           f"≤ {p['n_head']:.0f} r/min", "ok" if p["n"] <= p["n_head"] else "bad", 15,
           "超过机头本身的能力（刺布、钩线惯性和线的强度）。", "Beyond what the head itself can do (needle and hook inertia, thread strength).")
    ch.add("margin", "motion", "窗口两端留给伺服整定的余量", "Servo settling margin at the window ends", f"{2 * p['mg']:.1f}°", "≥ 10°",
           "ok" if 2 * p["mg"] >= 10 - 1e-9 else "warn", 15,
           "15.3 节：实际设计要扣跟随误差和整定时间，一般共留 10°–20°；余量太小，模板可能在机针入布后还没停稳。",
           "Section 15.3: allow 10–20° in total for following error and settling, or the template may still be moving when the needle enters.")
    for ax_, M, key in (("X", MX, "x"), ("Y", MY, "y")):
        TP, TR = (p["TxP"], p["TxR"]) if key == "x" else (p["TyP"], p["TyR"])
        ch.add(f"{key}_peak", f"{key}axis", f"{ax_} 轴电机峰值转矩", f"{ax_}-axis motor peak torque", f"{M['Tpk']:.2f} N·m", f"≤ {TP:.2f} N·m",
               "ok" if M["ok_pk"] else "bad", 15, "换更大的电机，或减轻运动质量、减小带轮半径。",
               "Use a bigger motor, or lighten the moving parts, or a smaller pulley.")
        ch.add(f"{key}_rms", f"{key}axis", f"{ax_} 轴电机发热（均方根转矩）", f"{ax_}-axis motor heating (RMS torque)", f"{M['Trms']:.2f} N·m",
               f"≤ {TR:.2f} N·m", "ok" if M["ok_rms"] else "bad", 15,
               "连续以极限速度缝纫时电机会过热：15.8 节三条路——换大电机、减小带轮半径（转速余量换转矩余量）、减轻运动质量。",
               "The motor overheats when sewing continuously at the limit. Section 15.8: bigger motor, smaller pulley (trade speed margin for torque), lighter moving parts.")
        ch.add(f"{key}_rpm", f"{key}axis", f"{ax_} 轴电机转速", f"{ax_}-axis motor speed", f"{M['rpm']:.0f} r/min", f"≤ {p['Nmot']:.0f} r/min",
               "ok" if M["ok_rpm"] else "bad", 15, "带轮太小，最高速度时电机超速：加大带轮或降低每轴最高速度。",
               "Pulley too small, the motor overspeeds at top axis speed: larger pulley or lower axis speed.")
    for ax_, fn, tm, key in (("X", fx, tmx, "x"), ("Y", fy, tmy, "y")):
        r_ = fn * tm
        ch.add(f"belt_{key}", "drive", f"{ax_} 轴同步带共振（固有频率 × 一针移动时间）", f"{ax_}-axis belt resonance (natural frequency × move time)",
               (f"{fn:.0f} Hz × {tm * 1000:.1f} ms = {r_:.2f}", f"{fn:.0f} Hz × {tm * 1000:.1f} ms = {r_:.2f}"), "≥ 1.5",
               "ok" if r_ >= 1.5 else ("warn" if r_ >= 1.0 else "bad"), 15,
               "带的振动周期和一针的移动时间同一量级，移动一停模板会晃：加宽带子、Y 轴两端驱动、减轻压框，或用摆线规律。",
               "The belt's vibration period is close to the move time, so the template rings after each move: wider belt, Y driven at both ends, lighter clamp, or a cycloidal law.")
    rel = dx_mm / s
    ch.add("belt_dx", "drive", "X 轴同步带弹性变形 / 针距", "X-axis belt stretch / stitch length", f"{dx_mm:.3f} mm（{rel:.0%}）", "≤ 10%",
           "ok" if rel <= 0.10 else ("warn" if rel <= 0.20 else "bad"), 15, "带太软：加宽带子或缩短带长。", "Belt too soft: wider belt or shorter belt runs.")
    fits = bw <= p["stx"] and bh <= p["sty"]
    ch.add("travel", "basic", "花样在工作台行程内", "Pattern within the table travel", f"{bw:.0f} × {bh:.0f} mm", f"≤ {p['stx']:.0f} × {p['sty']:.0f} mm",
           "ok" if fits else "bad", 15, "花样超出行程：换大工作台或拆成两段、两次装夹。", "The pattern exceeds the travel: larger table or split it.")
    eff = avg / min(p["n"], p["n_head"]) if p["n"] else 0
    ch.add("avg", "motion", "前瞻后平均转速 / 设计转速", "Average speed after look-ahead / design speed", (f"{avg:.0f} r/min（{eff:.0%}）", f"{avg:.0f} r/min ({eff:.0%})"),
           "≥ 60%", "ok" if eff >= 0.6 else "warn", 15,
           "花样里长针、急转多，或起停慢针占比大：针距改小，或把花样合成一段。", "Many long stitches or start/stop stitches: shorter stitches, or join the pattern into one segment.")

    results = [
        result("入布角 / 出布角", "Needle enters / leaves", f"{f1:.1f} / {f2:.1f}", "°"),
        result("离布窗口（几何 / 实用）", "Out-of-fabric window (geometric / usable)", f"{PL['Wg']:.1f} / {W:.1f}", "°"),
        result("标准针距转速上限 X / Y / 45°", "Speed limit for the standard stitch X / Y / 45°", f"{nmx:.0f} / {nmy:.0f} / {nm45:.0f}", "r/min"),
        result("X 轴峰值 / 均方根转矩", "X-axis peak / RMS torque", f"{MX['Tpk']:.2f} / {MX['Trms']:.2f}", "N·m"),
        result("Y 轴峰值 / 均方根转矩", "Y-axis peak / RMS torque", f"{MY['Tpk']:.2f} / {MY['Trms']:.2f}", "N·m"),
        result("同步带固有频率 X / Y", "Belt natural frequency X / Y", f"{fx:.0f} / {fy:.0f}", "Hz"),
        result("花样针数 / 大小", "Stitches / size", f"{N} / {bw:.0f} × {bh:.0f}", "mm"),
        result("缝制用时 / 平均转速", "Sewing time / average speed", f"{PL['t_sew']:.2f} s / {avg:.0f}", "r/min"),
        result("一个周期（含剪线、空走、上下料）", "One cycle (with trimming, jumps, loading)", f"{t_cycle + p['t_load']:.1f}", "s"),
        result("每小时件数", "Pieces per hour", f"{pph:.0f}"),
    ]
    phi = list(range(0, 360, 2))
    idx = list(range(1, N + 1))
    charts = [
        line_chart("speed", "每针转速与上限（r/min）", "Speed per stitch and its limit (r/min)", idx,
                   [("上限", "limit", "#c0392b", caps), ("前瞻后转速", "planned speed", "#2d6fb3", sp)], xr=[1, max(2, N)],
                   xl=("针号", "Stitch no.")),
        line_chart("needle", "针尖离针板高度（mm）与布厚", "Needle point above the plate (mm) and thickness", phi,
                   [("针尖", "point", "#2d6fb3", [TIP - xN(f) for f in phi])], ref=p["t"]),
        dict(key="pattern", kind="xy", open=p["pat"] not in ("circle", "star", "rect"), zh="花样针迹（mm）", en="Stitch path (mm)",
             x=[round(q[0], 3) for q in pts], series=[dict(zh="", en="", color="#2e9e6a", y=[round(q[1], 3) for q in pts])], ref_zh="", ref_en=""),
    ]
    a0, b0 = (f2 + p["mg"]) % 360, (f1 - p["mg"]) % 360
    timing = [dict(key="in", zh="机针在布中（模板不能动）", en="Needle in the fabric (template must stand still)", a=round(f1, 1), b=round(f2, 1)),
              dict(key="move", zh="模板可以移动（扣去余量）", en="Template may move (less margins)", a=round(a0, 1), b=round(b0, 1))]
    rows = []
    t_acc = 0.0
    for i in range(1, min(N, 41)):
        t_acc += 60 / sp[i]
        rows.append([str(i), f"{math.hypot(*PL['steps'][i]):.2f}", f"{caps[i]:.0f}", f"{sp[i]:.0f}", f"{60 / sp[i] * 1000:.1f}", f"{t_acc:.2f}"])
    tables = [
        dict(key="speed_table", zh="每针转速与用时（前 40 针）", en="Speed and time per stitch (first 40)",
             head=[("针号", "No."), ("针距 mm", "Length mm"), ("上限 r/min", "Limit r/min"), ("转速 r/min", "Speed r/min"),
                   ("这一针 ms", "This stitch ms"), ("累计 s", "Total s")], rows=rows),
        dict(key="motor_table", zh="X、Y 轴电机选型", en="X and Y axis motors",
             head=[("轴", "Axis"), ("驱动力 N", "Force N"), ("峰值 / 电机峰值 N·m", "Peak / motor peak N·m"),
                   ("均方根 / 额定 N·m", "RMS / rated N·m"), ("电机转速 r/min", "Motor speed r/min"), ("最优带轮半径 mm", "Optimal pulley mm")],
             rows=[["X", f"{MX['F']:.1f}", f"{MX['Tpk']:.2f} / {p['TxP']:.2f}", f"{MX['Trms']:.2f} / {p['TxR']:.2f}", f"{MX['rpm']:.0f}", f"{MX['r_opt']:.1f}"],
                   ["Y", f"{MY['F']:.1f}", f"{MY['Tpk']:.2f} / {p['TyP']:.2f}", f"{MY['Trms']:.2f} / {p['TyR']:.2f}", f"{MY['rpm']:.0f}", f"{MY['r_opt']:.1f}"]]),
    ]
    return dict(version=VERSION, machine=MACHINE, params=p, checks=list(ch), ok=not any(c["state"] == "bad" for c in ch),
                results=results, charts=charts, timing=timing, parts=parts(p, MX, MY, kx, ky), card=adjust_card(p), tables=tables,
                plan=dict(n=N, t_sew=PL["t_sew"], avg=avg, slow=slow_n, t_cycle=t_cycle, pph=pph),
                motors=dict(x=MX, y=MY), view=dict(page="model-pattern", sync="", cfg={}))


def parts(p, MX=None, MY=None, kx=None, ky=None):
    return [dict(key="x", zh="X 轴", en="X axis", dims=[("运动质量", "Moving mass", p["mx"], "kg"), ("带轮节圆半径", "Pulley radius", p["rx"], "mm"),
                                                    ("加速度", "Acceleration", p["ax"], "m/s²")]),
            dict(key="y", zh="Y 轴", en="Y axis", dims=[("运动质量", "Moving mass", p["my"], "kg"), ("带轮节圆半径", "Pulley radius", p["ry"], "mm"),
                                                    ("加速度", "Acceleration", p["ay"], "m/s²"), ("同步带根数", "Belts", int(p["nyb"]), "")]),
            dict(key="template", zh="模板", en="Template", dims=[("下片厚度计入布厚", "Lower plate counted in the thickness", p["t"], "mm"),
                                                              ("槽宽 = 中压脚外径 + 1–2 mm", "Slot width = presser-foot diameter + 1–2 mm", "—", "")])]


def adjust_card(params=None):
    p = clean(params)
    f1, f2, Wg = window(p["t"])
    return [
        dict(zh="回原点、核对花样", en="Home and check the pattern", do_zh="开机 X、Y 先回原点；扫模板条码或核对花样号，用错花样机针会打在模板上。",
             do_en="Home X and Y at power-up; scan the template code or check the pattern number — a wrong pattern drives the needle into the template."),
        dict(zh="离布窗口", en="Out-of-fabric window", do_zh=f"布加下模板 {p['t']:.1f} mm 时机针 {f1:.1f}° 入布、{f2:.1f}° 出布；模板只在其余 {Wg:.1f}° 里移动，两端各留 {p['mg']:.1f}°。",
             do_en=f"With {p['t']:.1f} mm the needle enters at {f1:.1f}° and leaves at {f2:.1f}°; the template moves only in the remaining {Wg:.1f}°, less {p['mg']:.1f}° at each end."),
        dict(zh="首件低速试缝", en="First piece at low speed", do_zh="新模板先用 300–500 r/min 试缝，用“单步”检查每个转角的落针点是否在槽中心。",
             do_en="Sew a new template at 300–500 r/min first and single-step the corners to check the needle lands in the middle of the slot."),
        dict(zh="同步带与气压", en="Belts and air", do_zh="检查 X、Y 同步带张紧力；气压不低于 0.5 MPa，压框力不足时布会在模板里滑。",
             do_en="Check the belt tension on X and Y; keep the air at 0.5 MPa or more, or the fabric slips inside the template."),
        dict(zh="升到设计转速", en="Up to design speed", do_zh=f"开前瞻，设计转速 {p['n']:.0f} r/min；断针先查模板槽是否碰中压脚、针距–转速是否超限、原点是否丢失。",
             do_en=f"Turn on look-ahead at {p['n']:.0f} r/min; for broken needles check slot vs presser foot, stitch length vs speed, and lost home."),
    ]
