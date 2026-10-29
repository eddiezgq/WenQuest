# -*- coding: utf-8 -*-
"""电脑横机设计计算（第 54 轮）。

模型出自教材《缝纫机设计与制造》第 17 章：17.2 选针器响应，17.3 按针位选针（t_n = p/v、提前量补偿、v_max = 段数·p/T_c、换向余量 v²/2a），
17.4 摇床与制动，17.7 线圈长度闭环（Δd = −k·Δl / (∂l/∂d)），17.7.2 全成型（隔针编织），17.8 设计实例（一趟行程 D = w + L_k + 2c、
一趟用时 t = D/v + v/a + 停顿，一片 = 趟数 × t）。默认参数就是 17.8 节的算例：E12、前片 275 针、单系统、1.2 m/s、10 m/s²、760 横列。

教材没给的（机头运动质量、传动、电机、摇床伺服、全成型的趟数倍数和套口工时）补成“示例值”，界面上标明，同第 42 轮刺绣机的做法。
"""
import math

from .common import Checks, line_chart, make_params, result

MACHINE = "flatknit"
NAME = ("电脑横机", "Computerized Flat Knitting")
VERSION = "1.0"
LECTURES = ("第 17 章", "chapter 17")
ERR_MAX = 0.25                # 选针位置误差 ≤ 0.25 个针距（17.3 节、虚拟实验 17-1 标红的线）

GROUPS = [
    ("basic", "基本参数", "Basic", [
        ("E", "机号 E（针 / 英寸）", "Gauge E (needles / inch)", "", 12, 3, 18, 1),
        ("B", "针床有效宽度", "Needle-bed working width", "mm", 1270, 500, 2600, 10),
        ("sys", "系统数", "Systems", "", 1, 1, 4, 1),
        ("Lk", "每个系统的三角座跨度", "Cam-box span per system", "mm", 150, 60, 300, 5),
    ]),
    ("motion", "机头运动（17.3、17.8 节）", "Carriage motion (17.3, 17.8)", [
        ("v", "机头最高速度", "Carriage top speed", "m/s", 1.2, 0.2, 2.0, 0.05),
        ("a", "机头加速度", "Carriage acceleration", "m/s²", 10, 2, 30, 0.5),
        ("dwell", "每次换向停顿（摇床、换纱嘴）", "Dwell at each reversal (racking, yarn carriers)", "s", 0.05, 0, 0.5, 0.01),
        ("c_min", "换向余量下限（三角座离开、纱嘴停放）", "Minimum reversal margin (cam box clear, carrier parking)", "mm", 20, 5, 100, 1),
    ]),
    ("select", "选针（17.2–17.3 节）", "Needle selection (17.2–17.3)", [
        ("comp", "提前量补偿", "Lead compensation", "", "fixed", None, None, None),
        ("Td", "选针器延迟 T_d", "Selector delay T_d", "ms", 0.6, 0.1, 3.0, 0.05),
        ("dTd", "延迟的不确定量（温度、电压）", "Delay uncertainty (temperature, voltage)", "ms", 0.1, 0, 1.0, 0.01),
        ("Tc", "吸合—释放周期 T_c", "Pick-up–release cycle T_c", "ms", 1.2, 0.2, 5.0, 0.05),
        ("seg", "选针器段数", "Selector segments", "", 1, 1, 8, 1),
    ]),
    ("stitch", "度目与线圈长度（17.4、17.7 节）", "Stitch cam and loop length (17.4, 17.7)", [
        ("lstar", "目标线圈长度 l*", "Target loop length l*", "mm", 5.0, 2.0, 12.0, 0.1),
        ("dldd", "∂l / ∂d（弯纱深度每毫米对应的线圈长度）", "∂l / ∂d (loop length per mm of stitch depth)", "", 2.0, 1.0, 3.0, 0.1),
        ("step", "度目步进每步", "Stitch-cam motor step", "mm", 0.01, 0.001, 0.1, 0.001),
        ("meas", "测长轮精度", "Yarn-length sensor accuracy", "%", 0.3, 0.05, 3, 0.05),
        ("kcl", "闭环增益 k", "Closed-loop gain k", "", 0.5, 0.1, 1.0, 0.05),
    ]),
    ("rack", "摇床与制动（17.4 节）", "Racking and braking (17.4)", [
        ("rack", "每次摇床量（针距）", "Racking per move (pitches)", "", 1, 0.5, 4, 0.5),
        ("ar", "摇床伺服加速度", "Racking servo acceleration", "m/s²", 5, 0.5, 30, 0.5),
        ("vr", "摇床伺服最高速度", "Racking servo top speed", "m/s", 0.15, 0.02, 1, 0.01),
        ("tset", "摇床停稳时间", "Racking settling time", "ms", 5, 0, 50, 1),
        ("ab", "急停制动加速度", "Emergency braking deceleration", "m/s²", 20, 5, 60, 1),
        ("e_end", "换向点外的制动余量", "Braking room beyond the reversal point", "mm", 50, 10, 200, 5),
    ]),
    ("piece", "衣片（17.6、17.8 节）", "Garment piece (17.6, 17.8)", [
        ("N", "衣片针数", "Needles in the piece", "", 275, 20, 1200, 1),
        ("pcs", "并排织几片", "Pieces side by side", "", 1, 1, 6, 1),
        ("gap", "并排时片间空针", "Empty needles between pieces", "", 10, 0, 50, 1),
        ("rib", "罗纹横列", "Rib courses", "", 120, 0, 2000, 1),
        ("jac", "提花意匠行", "Jacquard design rows", "", 300, 0, 3000, 1),
        ("col", "提花颜色数", "Jacquard colours", "", 2, 1, 6, 1),
        ("xfer", "收针、翻针横列", "Narrowing / transfer courses", "", 40, 0, 1000, 1),
    ]),
    ("whole", "全成型对比（17.7.2 节，示例值）", "Whole-garment comparison (17.7.2, example values)", [
        ("fashion", "编织方式", "Knitting method", "", "pieces", None, None, None),
        ("kpc", "一件衣服折合几片前片的机时", "Machine time per garment in front-piece equivalents", "", 3.2, 1, 6, 0.1),
        ("kwhole", "全成型的趟数倍数（翻针多）", "Pass multiplier for whole-garment knitting (more transfers)", "", 1.6, 1, 3, 0.05),
        ("tlink", "套口、缝合工时（每件）", "Linking and seaming per garment", "min", 25, 0, 120, 1),
    ]),
    ("drive", "机头驱动（选电机用，示例值）", "Carriage drive (for motor sizing, example values)", [
        ("m0", "机头基础质量", "Carriage base mass", "kg", 25, 5, 150, 0.5),
        ("msys", "每个系统增加的质量", "Mass added per system", "kg", 15, 2, 60, 0.5),
        ("Ff", "导轨摩擦与拖链阻力", "Rail friction and cable-chain drag", "N", 40, 0, 500, 5),
        ("r", "同步带轮节圆半径", "Belt pulley pitch radius", "mm", 30, 10, 80, 0.5),
        ("ig", "减速比", "Reduction ratio", "", 3, 1, 10, 0.5),
        ("eta", "传动效率", "Drive efficiency", "", 0.9, 0.5, 1, 0.01),
        ("TmR", "电机额定转矩", "Motor rated torque", "N·m", 3.18, 0.1, 50, 0.01),
        ("TmP", "电机峰值转矩", "Motor peak torque", "N·m", 9.55, 0.1, 150, 0.01),
        ("Jm", "电机转子惯量", "Motor rotor inertia", "×10⁻⁴ kg·m²", 2.6, 0.01, 100, 0.01),
        ("Nm", "电机最高转速", "Motor top speed", "r/min", 3000, 500, 6000, 100),
    ]),
    ("prod", "产能", "Output", [
        ("hours", "每天开机", "Running hours per day", "h", 20, 1, 24, 0.5),
        ("eff", "开机效率（断纱、换纱、落片）", "Running efficiency (yarn breaks, changes, doffing)", "", 0.85, 0.3, 1, 0.01),
    ]),
]
CHOICES = {
    "comp": [("none", "不补偿", "None"), ("fixed", "固定提前量（按最高速度整定）", "Fixed lead (tuned at top speed)"),
             ("realtime", "按实时速度", "Real-time speed")],
    "fashion": [("pieces", "织衣片 + 套口", "Pieces + linking"), ("whole", "全成型（隔针编织）", "Whole garment (alternate needles)")],
}
PARAMS, DEFAULTS, clean = make_params(GROUPS, CHOICES)


def pitch(E):
    return 25.4 / E


def margin(p):
    """换向余量 c（mm）：固定提前量要在经过第一枚针前达到全速，c ≥ v²/(2a)；不补偿或按实时速度补偿只要三角座离开、纱嘴停放"""
    need = p["v"] ** 2 / (2 * p["a"]) * 1000
    return max(p["c_min"], need) if p["comp"] == "fixed" else p["c_min"]


def width(p):
    """织物宽度（mm）：几片并排时连同片间空针；全成型隔针编织，同样针数的织物要占两倍的针"""
    n = p["N"] * p["pcs"] + p["gap"] * (p["pcs"] - 1)
    return n * pitch(p["E"]) * (2 if p["fashion"] == "whole" else 1)


def passes(p):
    """一片（并排时一组）要走几趟：罗纹一趟一横列；提花每个意匠行按颜色分趟，几个系统就能在一趟里织几色；收针翻针一趟一横列（17.8 节方案 B）"""
    rows = max(1, p["rib"] + p["jac"] * math.ceil(p["col"] / p["sys"]) + p["xfer"])     # 至少一趟（三项都填 0 也不出错）
    return rows * (p["kwhole"] if p["fashion"] == "whole" else 1)


def profile(D_mm, v, a):
    """一趟的速度规律：梯形（到得了最高速度）或三角形（行程太短，到不了）。返回 峰值速度、加速时间、匀速时间、走完的时间（不含停顿）"""
    D = D_mm / 1000
    vp = min(v, math.sqrt(a * D))
    ta = vp / a
    tc = max(0.0, (D - vp * vp / a) / vp)
    return vp, ta, tc, 2 * ta + tc


def pass_time(p, v=None, c=None):
    """一趟：行程 D = 织物宽 + 三角座跨度 + 2c；用时 = 走完 + 停顿。到得了最高速度时就是 17.8 节的 D/v + v/a"""
    v = p["v"] if v is None else v
    c = margin(dict(p, v=v)) if c is None else c
    D = width(p) + p["Lk"] * p["sys"] + 2 * c
    return D, profile(D, v, p["a"])[3] + p["dwell"]


def sel_error(p, x_mm, comp=None):
    """织物上离第一枚针 x_mm 处的选针位置误差（针距）。机头从换向点静止起步，经过 c + x 才到这里。
    不补偿：滞后 u·T_d；固定提前量：超前 (v − u)·T_d，再加不确定量；按实时速度：只剩不确定量 u·ΔT_d"""
    comp = comp or p["comp"]
    c = margin(dict(p, comp=comp))
    u = min(p["v"], math.sqrt(2 * p["a"] * (c + x_mm) / 1000))
    Td, dT = p["Td"] / 1000, p["dTd"] / 1000
    pm = pitch(p["E"])
    if comp == "none":
        e = u * Td * 1000
    elif comp == "fixed":
        e = (p["v"] - u) * Td * 1000 + u * dT * 1000
    else:
        e = u * dT * 1000
    return e / pm


def loop_correction(p, Lm, N):
    """17.7 节线圈长度闭环：测得这一横列用纱 Lm（mm）、织了 N 针，下一个同类横列弯纱深度改多少（mm，负 = 调浅）和步数"""
    dl = Lm / N - p["lstar"]
    dd = -p["kcl"] * dl / p["dldd"]
    return dict(dl=dl, dd=dd, steps=dd / p["step"])


def rack_time(p):
    """摇床走 rack 个针距：梯形或三角形速度，再加停稳时间（s）"""
    d = p["rack"] * pitch(p["E"]) / 1000
    a, v = p["ar"], p["vr"]
    t = 2 * math.sqrt(d / a) if d < v * v / a else d / v + v / a
    return t + p["tset"] / 1000


def drive(p, Jm=None, TmR=None, TmP=None):
    """机头驱动电机（电机侧）：加速段、匀速段、减速段的转矩，按一趟的时间求均方根（17.8 节的一趟）"""
    Jm = (p["Jm"] if Jm is None else Jm) * 1e-4
    m = p["m0"] + p["msys"] * p["sys"]
    r, i, eta, a, v = p["r"] / 1000, p["ig"], p["eta"], p["a"], p["v"]
    k = r / (i * eta)
    rot = Jm * a * i / r
    Ta = (m * a + p["Ff"]) * k + rot
    Tdc = abs((-m * a + p["Ff"]) * k - rot)
    Tc = p["Ff"] * k
    D, t = pass_time(p)
    vp, ta, tc, _ = profile(D, v, a)
    Trms = math.sqrt((Ta ** 2 * ta + Tdc ** 2 * ta + Tc ** 2 * tc) / t)
    rpm = vp / r * i * 60 / (2 * math.pi)
    return dict(m=m, F=m * a + p["Ff"], Tpk=max(Ta, Tdc), Trms=Trms, rpm=rpm, i_opt=r * math.sqrt(m / Jm) if Jm > 0 else None)


def t_at(x_mm, D_mm, v, a):
    """梯形速度走一趟（行程 D）时，到达位置 x 的时刻（s）"""
    x, D = x_mm / 1000, D_mm / 1000
    sa = min(v * v / (2 * a), D / 2)
    vp = math.sqrt(2 * a * sa)
    if x <= sa:
        return math.sqrt(2 * x / a)
    t_run = (D - 2 * sa) / vp
    if x <= D - sa:
        return vp / a + (x - sa) / vp
    return vp / a + t_run + (vp - math.sqrt(max(0.0, vp * vp - 2 * a * (x - (D - sa))))) / a


def production(p, **over):
    q = dict(p, **over)
    D, t = pass_time(q)
    n = passes(q)
    t_piece = n * t / q["pcs"]
    return dict(D=D, t_pass=t, passes=n, t_piece=t_piece, per_day=q["hours"] * 3600 * q["eff"] / t_piece)


def garment(p):
    """一件衣服：织衣片 + 套口，或全成型（隔针编织，等效机号减半，趟数 × 倍数，不套口）"""
    t_pieces = production(dict(p, fashion="pieces"))["t_piece"] * p["kpc"] / 60
    t_whole = production(dict(p, fashion="whole"))["t_piece"] * p["kpc"] / 60
    return dict(knit_pieces=t_pieces, link=p["tlink"], total_pieces=t_pieces + p["tlink"], knit_whole=t_whole, total_whole=t_whole,
                E_eff=p["E"] / 2)


def variants(p):
    """教材 17.8 节的三个改进方向，按当前参数重算"""
    base = production(p)
    rows = [("当前设计", "Current design", p, base)]
    if p["comp"] != "realtime":
        q = dict(p, comp="realtime")
        rows.append(("按实时速度补偿（换向余量减到下限）", "Real-time compensation (margin down to the minimum)", q, production(q)))
    if p["sys"] < 4:
        q = dict(p, sys=p["sys"] + 1)
        rows.append((f"加一个系统（{p['sys'] + 1:.0f} 系统，几色同一趟织）", f"One more system ({p['sys'] + 1:.0f} systems, colours in one pass)", q, production(q)))
    q = dict(p, v=min(2.0, round(p["v"] * 4 / 3, 2)))
    if q["v"] > p["v"]:
        rows.append((f"机头提速到 {q['v']:g} m/s", f"Carriage up to {q['v']:g} m/s", q, production(q)))
    return rows


def analyze(params=None, trial=True):
    p = clean(params)
    for k in ("E", "sys", "seg", "N", "pcs", "gap", "rib", "jac", "col", "xfer"):
        p[k] = int(round(p[k]))
    pm = pitch(p["E"])
    v, a = p["v"], p["a"]
    tn = pm / v                                   # ms：mm / (m/s)
    vmax_sel = math.floor(p["seg"] * pm / p["Tc"] * 100) / 100     # m/s，往小取（显示 1.17 而不是 1.18）
    c = margin(p)
    w = width(p)
    PR = production(p)
    D, t1 = PR["D"], PR["t_pass"]
    errs = [sel_error(p, x) for x in range(0, int(w) + 1, max(1, int(w // 120)))]
    emax = max(errs)
    tr = rack_time(p)
    s_brake = v * v / (2 * p["ab"]) * 1000
    room = c + p["e_end"]                          # 在最后一枚针处全速急停：可用的是换向余量 + 换向点外的余量
    dl_step = p["step"] * p["dldd"] / p["lstar"] * 100           # 度目走一步，线圈长度变化 %
    cl = -loop_correction(p, 1.01 * p["lstar"], 1)["dd"]          # 17.7 节：Δd = −k·Δl / (∂l/∂d)，偏长 1% 时一次调浅多少（mm）
    DR = drive(p)
    G = garment(p)
    ch = Checks()
    ch.add("sel_time", "select", "每枚针的选针时间够选针器动作", "Time per needle covers the selector cycle",
           (f"t_n = {tn:.2f} ms；周期 {p['Tc']:.2f} ms / {p['seg']} 段", f"t_n = {tn:.2f} ms; cycle {p['Tc']:.2f} ms / {p['seg']} segments"),
           ("t_n ≥ T_c / 段数", "t_n ≥ T_c / segments"), "ok" if tn >= p["Tc"] / p["seg"] - 1e-9 else "bad", 17,
           f"机号越高、机头越快，每枚针的时间越短：机头降到 {vmax_sel:.2f} m/s 以下，或换响应更快的选针器，或用多段选针器把相邻的针分开选。",
           f"Higher gauge and faster carriage leave less time per needle: slow below {vmax_sel:.2f} m/s, use a faster selector, or a multi-segment selector.")
    st = "ok" if emax <= ERR_MAX * 0.8 else ("warn" if emax <= ERR_MAX else "bad")
    ch.add("sel_err", "select", "选针位置误差（织物上最大）", "Selection position error (largest on the fabric)",
           (f"{emax:.2f} 个针距", f"{emax:.2f} pitch"), f"≤ {ERR_MAX:g} p", st, 17,
           "不补偿时全速滞后 v·T_d；固定提前量只在全速时准；按实时速度补偿只剩延迟的不确定量。改用“按实时速度”，或缩短选针器延迟、定期标定。",
           "Without compensation it lags v·T_d at speed; a fixed lead is right only at top speed; real-time compensation leaves only the delay "
           "uncertainty. Use real-time compensation, a shorter selector delay, or regular calibration.")
    ch.add("bed", "basic", "织物放得下针床", "Fabric fits the needle bed", f"{w:.0f} / {p['B']:.0f} mm", "≤ 针床宽 / bed width",
           "ok" if w <= p["B"] else "bad", 17, "并排的片数或针数太多：减片数，或用更宽的机器。", "Too many pieces or needles side by side: fewer pieces or a wider machine.")
    ch.add("rack", "rack", "摇床在换向停顿里走完、停稳", "Racking done and settled within the reversal dwell",
           f"{tr * 1000:.0f} / {p['dwell'] * 1000:.0f} ms", "≤ 停顿 / dwell", "ok" if tr <= p["dwell"] + 1e-9 else "bad", 17,
           "摇床来不及就撞针：加大摇床伺服加速度、缩短停稳时间，或加长换向停顿（一趟会慢一点）。",
           "Unfinished racking means needle crashes: faster racking servo, shorter settling, or a longer dwell (each pass gets slower).")
    ch.add("brake", "rack", "急停距离（在最后一枚针处全速急停）", "Emergency stop distance (full-speed stop at the last needle)",
           f"{s_brake:.0f} / {room:.0f} mm", ("≤ 换向余量 + 换向点外余量", "≤ reversal margin + room beyond it"), "ok" if s_brake <= room else "bad", 17,
           "撞针、开门要立即停，制动距离 v²/(2a)；最坏是在织物边上全速时发生：加大制动、降机头速度，或在两端多留空。",
           "Crashes and open doors need an immediate stop over v²/(2a); the worst case is at full speed at the fabric edge: stronger braking, "
           "lower speed, or more room at the ends.")
    ch.add("cam_res", "stitch", "度目分辨率（走一步线圈长度变化）", "Stitch-cam resolution (loop-length change per step)",
           f"{dl_step:.2f}%", "≤ 0.5%", "ok" if dl_step <= 0.5 + 1e-9 else ("warn" if dl_step <= 1 else "bad"), 17,
           "线圈长度要控制在 ±1% 以内，度目要到百分之一毫米量级：换细分更高的步进电机或更小导程。",
           "To hold loop length within ±1% the stitch cam needs ~0.01 mm steps: finer micro-stepping or a smaller lead.")
    ch.add("meas", "stitch", "测长精度", "Yarn-length sensor accuracy", f"{p['meas']:.2f}%", "≤ 0.5%",
           "ok" if p["meas"] <= 0.5 + 1e-9 else ("warn" if p["meas"] <= 1 else "bad"), 17,
           "测不准就闭不了环：测长轮打滑、编码器分辨率低都会让同批衣片长短不一。", "Inaccurate measurement defeats the loop: a slipping wheel or coarse encoder gives uneven pieces.")
    ch.add("m_peak", "drive", "机头电机峰值转矩", "Carriage motor peak torque", f"{DR['Tpk']:.2f} N·m", f"≤ {p['TmP']:.2f} N·m",
           "ok" if DR["Tpk"] <= p["TmP"] else "bad", 17, "加速度大、机头重（系统多）就要大电机：降加速度、加大减速比，或换电机（CAE 分析 → 伺服电机选型）。",
           "High acceleration and a heavy carriage need a bigger motor: lower acceleration, more reduction, or a bigger motor (CAE → servo sizing).")
    ch.add("m_rms", "drive", "机头电机发热（均方根转矩）", "Carriage motor heating (RMS torque)", f"{DR['Trms']:.2f} N·m", f"≤ {p['TmR']:.2f} N·m",
           "ok" if DR["Trms"] <= p["TmR"] else "bad", 17, "窄织物换向多，加减速占的时间多，发热大：降加速度、几片并排织，或换电机。",
           "Narrow fabric means frequent reversals and more heating: lower acceleration, knit pieces side by side, or a bigger motor.")
    ch.add("m_rpm", "drive", "机头电机转速", "Carriage motor speed", f"{DR['rpm']:.0f} r/min", f"≤ {p['Nm']:.0f} r/min",
           "ok" if DR["rpm"] <= p["Nm"] else "bad", 17, "减速比或带轮太小：加大带轮半径或减小减速比。", "Reduction too high or pulley too small: larger pulley or less reduction.")
    tpiece = PR["t_piece"]
    results = [
        result("针距 / 每枚针的选针时间", "Pitch / time per needle", f"{pm:.2f} mm / {tn:.2f} ms"),
        result("选针器允许的机头最高速度", "Top carriage speed the selector allows", f"{vmax_sel:.2f}", "m/s"),
        result("不补偿时全速的选针滞后", "Lag at full speed without compensation", f"{v * p['Td'] / pm:.2f}", "p"),
        result("换向余量 c（v²/2a = {:.0f} mm）".format(v * v / (2 * a) * 1000), "Reversal margin c (v²/2a = {:.0f} mm)".format(v * v / (2 * a) * 1000), f"{c:.0f}", "mm"),
        result("织物宽度 / 一趟行程", "Fabric width / travel per pass", f"{w:.0f} / {D:.0f}", "mm"),
        result("一趟用时", "Time per pass", f"{t1:.2f}", "s"),
        result("趟数 / 一片用时", "Passes / time per piece", f"{PR['passes']:.0f} / {tpiece / 60:.1f}", "min"),
        result("每天片数（开机 {:g} h、效率 {:.0%}）".format(p["hours"], p["eff"]), "Pieces per day ({:g} h, {:.0%})".format(p["hours"], p["eff"]), f"{PR['per_day']:.0f}"),
        result("摇床用时 / 急停距离", "Racking time / emergency stop distance", f"{tr * 1000:.0f} ms / {s_brake:.0f} mm"),
        result("线圈长度闭环：实测比目标长 1% 时度目调浅", "Loop-length loop: stitch cam shallower when 1% too long",
               "{:.3f} mm（{:.0f} 步）".format(cl, cl / p["step"]), ""),
        result("度目走一步，线圈长度变化", "Loop-length change per stitch-cam step", f"{p['step'] * p['dldd'] * 1000:.0f} µm（{dl_step:.2f}%）"),
        result("机头运动质量 / 驱动力", "Carriage mass / drive force", f"{DR['m']:.0f} kg / {DR['F']:.0f} N"),
        result("机头电机峰值 / 均方根转矩", "Carriage motor peak / RMS torque", f"{DR['Tpk']:.2f} / {DR['Trms']:.2f}", "N·m"),
        result("一件衣服：衣片 + 套口 / 全成型（隔针编织，等效 E{:g}）".format(G["E_eff"]), "One garment: pieces + linking / whole (alternate needles, equivalent E{:g})".format(G["E_eff"]),
               f"{G['total_pieces']:.0f} / {G['total_whole']:.0f}", "min"),
    ]
    # 曲线
    xs = [round(D * i / 120, 1) for i in range(121)]
    va = lambda x: min(v, math.sqrt(2 * a * x / 1000), math.sqrt(2 * a * max(0.0, D - x) / 1000))   # noqa: E731
    xe = list(range(0, int(w) + 1, max(1, int(w // 100))))
    vs = [round(0.4 + 0.05 * i, 2) for i in range(33)]
    pmin = dict(p, comp="realtime")          # 三种补偿放在同一个换向余量（下限）上比：固定提前量的加速区误差就是教材图 17-4
    charts = [
        line_chart("travel", "一趟的机头速度（m/s）与位置", "Carriage speed over one pass (m/s)", xs, [("机头速度", "speed", "#2d6fb3", [va(x) for x in xs])],
                   xr=[0, D], xl=("机头位置 mm（织物在 {:.0f}–{:.0f}）".format(c, c + w), "Carriage position mm (fabric at {:.0f}–{:.0f})".format(c, c + w))),
        line_chart("selerr", "选针位置误差（针距；换向余量都取下限 {:.0f} mm）".format(p["c_min"]),
                   "Selection error (pitch; all at the minimum margin {:.0f} mm)".format(p["c_min"]), xe,
                   [("不补偿", "none", "#c0392b", [sel_error(pmin, x, "none") for x in xe]),
                    ("固定提前量", "fixed lead", "#e0a030", [sel_error(pmin, x, "fixed") for x in xe]),
                    ("按实时速度", "real-time", "#2e9e6a", [sel_error(pmin, x, "realtime") for x in xe])], ref=ERR_MAX, zero=True,
                   xr=[0, max(1, xe[-1])], xl=("离第一枚针 mm", "From the first needle, mm")),
        line_chart("speed", "机头速度与一片用时（min）", "Carriage speed vs time per piece (min)", vs,
                   [("一片用时", "per piece", "#2d6fb3", [production(dict(p, v=x))["t_piece"] / 60 for x in vs])], xr=[0.4, 2.0],
                   xl=("机头最高速度 m/s", "Carriage top speed, m/s")),
    ]
    # 一趟的时间分配（时序条用 0–360 表示一趟的 0–100%）
    vp, ta, tcst, _ = profile(D, v, a)
    k = 360 / t1
    a1, a2, a3 = ta * k, (ta + tcst) * k, (2 * ta + tcst) * k
    x_in, x_out = t_at(c, D, v, a) * k, t_at(c + w, D, v, a) * k
    timing = [dict(key="acc", zh="加速", en="Accelerate", a=0, b=round(a1, 1)),
              dict(key="run", zh="全速", en="Full speed", a=round(a1, 1), b=round(a2, 1)),
              dict(key="dec", zh="减速", en="Decelerate", a=round(a2, 1), b=round(a3, 1)),
              dict(key="knit", zh="经过织物（选针、编织）", en="Over the fabric (selecting, knitting)", a=round(min(x_in, 359), 1), b=round(min(x_out, 360), 1)),
              dict(key="dwell", zh="换向停顿（摇床、纱嘴）", en="Reversal dwell (racking, carriers)", a=round(a3, 1), b=360)]
    timing = [t for t in timing if t["b"] - t["a"] > 0.05]       # 行程太短到不了最高速度时没有“全速”段；没有停顿就不画停顿
    tables = [
        dict(key="variants", zh="改进方案对照（教材 17.8 节，按当前参数重算）", en="Improvement options (textbook 17.8, recomputed)",
             head=[("方案", "Option"), ("一趟 s", "Pass s"), ("趟数", "Passes"), ("一片 min", "Piece min"), ("比当前", "vs now"), ("红灯", "Red")],
             rows=[[(zh, en), f"{r['t_pass']:.2f}", f"{r['passes']:.0f}", f"{r['t_piece'] / 60:.1f}", f"{(r['t_piece'] / tpiece - 1) * 100:+.0f}%",
                    str(_bad(q))] for zh, en, q, r in variants(p)]),
        dict(key="garment", zh="一件衣服：织衣片 + 套口 与 全成型（示例值；同样针数的织物，全成型隔针编织占两倍针床宽）",
             en="One garment: pieces + linking vs whole garment (example values; the same needle count takes twice the bed width with alternate needles)",
             head=[("做法", "Method"), ("上机 min", "Knitting min"), ("套口 min", "Linking min"), ("合计 min", "Total min"), ("机号", "Gauge")],
             rows=[[("织衣片 + 套口", "Pieces + linking"), f"{G['knit_pieces']:.0f}", f"{G['link']:.0f}", f"{G['total_pieces']:.0f}", f"E{p['E']}"],
                   [("全成型（隔针编织）", "Whole garment (alternate needles)"), f"{G['knit_whole']:.0f}", "0", f"{G['total_whole']:.0f}", f"E{G['E_eff']:g}"]]),
    ]
    return dict(version=VERSION, machine=MACHINE, params=p, checks=list(ch), ok=not any(x["state"] == "bad" for x in ch),
                results=results, charts=charts, timing=timing, timing_x="pass", parts=parts(p, DR), card=adjust_card(p), tables=tables,
                production=dict(PR, t_piece_min=tpiece / 60), drive=DR, garment=G, view=dict(page="model-flatknit", sync="", cfg={}))


def _bad(q):
    """改进方案表里每个方案的红灯数（和 analyze 的红灯判据一样，不递归画表）"""
    pm = pitch(q["E"])
    n = 0
    n += pm / q["v"] < q["Tc"] / q["seg"] - 1e-9
    w = width(q)
    n += max(sel_error(q, x) for x in range(0, int(w) + 1, max(1, int(w // 60)))) > ERR_MAX
    n += rack_time(q) > q["dwell"] + 1e-9
    n += q["v"] ** 2 / (2 * q["ab"]) * 1000 > margin(q) + q["e_end"]
    n += w > q["B"]
    n += q["step"] * q["dldd"] / q["lstar"] * 100 > 1
    n += q["meas"] > 1
    DR = drive(q)
    n += DR["Tpk"] > q["TmP"]
    n += DR["Trms"] > q["TmR"]
    n += DR["rpm"] > q["Nm"]
    return int(n)


def parts(p, DR=None):
    DR = DR or drive(p)
    return [dict(key="bed", zh="针床", en="Needle bed", dims=[("机号 / 针距", "Gauge / pitch", f"E{p['E']} / {pitch(p['E']):.2f}", "mm"),
                                                         ("有效宽度", "Working width", p["B"], "mm"), ("总针数（每床）", "Needles per bed", int(p["B"] / pitch(p["E"])), "")]),
            dict(key="carriage", zh="机头", en="Carriage", dims=[("系统数", "Systems", int(p["sys"]), ""), ("三角座跨度", "Cam-box span", p["Lk"] * p["sys"], "mm"),
                                                             ("运动质量", "Moving mass", round(DR["m"], 1), "kg"), ("最高速度 / 加速度", "Top speed / acceleration", f"{p['v']:g} / {p['a']:g}", "m/s · m/s²")]),
            dict(key="selector", zh="选针器", en="Selector", dims=[("延迟 / 周期", "Delay / cycle", f"{p['Td']:g} / {p['Tc']:g}", "ms"), ("段数", "Segments", int(p["seg"]), "")]),
            dict(key="drive", zh="机头驱动", en="Carriage drive", dims=[("带轮节圆半径", "Pulley radius", p["r"], "mm"), ("减速比", "Reduction", p["ig"], ""),
                                                                    ("电机额定 / 峰值", "Motor rated / peak", f"{p['TmR']:g} / {p['TmP']:g}", "N·m"),
                                                                    ("转矩最小的减速比", "Reduction for least torque", round(DR["i_opt"] or 0, 1) if DR.get("i_opt") else "—", "")])]


def adjust_card(params=None):
    p = clean(params)
    pm = pitch(p["E"])
    return [
        dict(zh="选针提前量标定", en="Calibrate the selection lead",
             do_zh=f"E{p['E']:.0f}、{p['v']:g} m/s 时每枚针只有 {pm / p['v']:.2f} ms；按机器的方法标定选针器延迟（约 {p['Td']:g} ms），线圈温度、电源电压变了要重标。",
             do_en=f"At E{p['E']:.0f} and {p['v']:g} m/s each needle has {pm / p['v']:.2f} ms; calibrate the selector delay (about {p['Td']:g} ms) and recalibrate when coil temperature or supply voltage changes."),
        dict(zh="摇床对针", en="Rack alignment", do_zh="翻针前后针床要针对针：先低速翻针检查对准，撞针多发生在翻针横列和换向端。",
             do_en="Beds must be needle-to-needle for transfers: check alignment with slow transfers; crashes happen most on transfer courses and at the ends."),
        dict(zh="度目与线圈长度闭环", en="Stitch cam and loop-length loop",
             do_zh=f"打开线圈长度闭环（目标 {p['lstar']:g} mm、增益 {p['kcl']:g}）；同批衣片长短不一，先查闭环是否开启、各纱筒张力和牵拉值。",
             do_en=f"Turn on the loop-length loop (target {p['lstar']:g} mm, gain {p['kcl']:g}); for uneven pieces check the loop is on, cone tensions and take-down."),
        dict(zh="纱嘴停放与换向点", en="Carrier parking and reversal", do_zh="纱嘴停在织物边外一点；两侧松边、破边查纱嘴停放位置、换向余量和边针度目。",
             do_en="Park carriers just outside the edge; for loose or broken edges check parking, the reversal margin and edge stitch values."),
        dict(zh="新花型低速试织", en="New design at low speed", do_zh="新花型首片 0.3–0.5 m/s 试织，确认无误再提速；竖向漏针多半是某枚舌针针舌不灵或针钩变形，按位置换针。",
             do_en="Knit the first piece of a new design at 0.3–0.5 m/s; a vertical dropped-stitch line usually means one latch needle to replace."),
    ]
