# -*- coding: utf-8 -*-
"""电控箱的热与流体（第 62 轮）：功率级损耗 → 热阻网络 → 间歇缝纫负载下的散热器温度和结温峰值 → 母线电容寿命；开关时间在结温和共模电流之间的折中。

模型出自教材《缝纫机设计与制造》第 18 章（18.3 功率级与热设计、18.4 电磁兼容、18.7 案例“电控箱夏天频繁报过热”），
公式和常数与虚拟实验 18-1（labs/ebox.html）逐项一致，默认参数就是教材算例（单相 220 V、550 W 平缝机伺服电控箱，示意值）：
  损耗（每只开关管，正弦电流有效值 I、峰值 I_p = √2·I、调制 m·cosφ = 0.6）：
    IGBT 导通 P_c = V_ce0·I_p·(1/2π + m·cosφ/8) + R_ce·I_p²·(1/8 + m·cosφ/3π)
    开关     P_s = ½·V_dc·(I_p/π)·t_sw·f_sw
    二极管   P_d = V_f0·I_p·(1/2π − m·cosφ/8) + R_f·I_p²·(1/8 − m·cosφ/3π) + 0.3·P_s（反向恢复）
    逆变桥 6 只 + 整流桥 2·0.9·0.6·I
  间歇负载：每分钟起停 N 次，一个周期 t_c = 60/N；加速、减速各 t_acc 用峰值电流，其余缝纫时间用运行电流；
    平均损耗 P = f_acc·P(I_pk) + f_run·P(I_run)
  热阻网络（飞絮堵塞 c：散热器热阻 × (1 + 1.5c)、箱内温升 × (1 + c)，示意）：
    箱内空气 T_in = T_a + R_box·(1 + c)·(P + P_其他)；散热器 T_hs = T_in + R_hs·(1 + 1.5c)·P
    结温峰值 T_j = T_hs + (P_c + P_s)(I_pk)·R_jc·(1 − e^{−t_acc/τ})
  电容：芯部 = 箱内空气 + ΔT_c；寿命 L = L_0·2^{(T_r − T)/10}（十度法则）
  共模电流 i_cm = C_p·dv/dt = C_p·V_dc/(t_sw/2)

第 62 轮加的（教材没有的，界面标“示例值”）：
  - 电流从这台机的设计来：主轴（平缝、包缝）按一转的转矩均方根 ÷ 转矩常数 K_t；花样机 X / Y、刺绣机绷架、横机机头按各自伺服的
    有效 / 峰值转矩 ÷ K_t（这些轴一直在加减速，按“连续运行”算平均损耗）。默认 K_t = 1 N·m/A，平缝机教材算例正好是 3 A；
  - 箱体到车间的热阻可以按外壳尺寸算：每个外表面的自然对流（竖板 1.42·(ΔT/H)^¼、热面朝上 1.32·(ΔT/L)^¼、朝下 0.59·(ΔT/L)^¼，
    常用简化式；顶面、顶面翅片泡在侧面升上来的热空气里，按自然对流 CFD 标定打 0.5、0.4 的折扣）或风扇吹（平板强制对流 h ≈ 3.9·√(v/L)）
    + 辐射 εσ(T_s² + T_a²)(T_s + T_a)；翅片按效率 0.85 计面积，不计辐射（翅片之间互相辐射）。
    默认外壳 260 × 160 × 90 mm 算出约 0.6 K/W，和教材给的 0.6 K/W 相近。CAE 复核（流体 + 温度场）替换的就是这一段。
"""
import math

from .common import Checks, line_chart, make_params, result

VERSION = "1.0"
LECTURES = ("第 18 章", "chapter 18")
MCOS, RRF = 0.6, 0.3
SIGMA = 5.670e-8
TOP_PLUME, FIN_PLUME = 0.5, 0.4      # 自然对流：顶面、顶面翅片相对经验式的折扣（第 62 轮 CFD 标定，见 box_resistance）

GROUPS = [
    ("load", "工况（默认取本机的设计）", "Duty (taken from this machine's design by default)", [
        ("src", "电流从哪里来", "Where the currents come from", "", "design", None, None, None),
        ("Irun", "主轴缝纫时相电流（有效值；绷缝、花样、刺绣机的主轴和手填时用）", "Spindle phase current while sewing (rms; cover, pattern, embroidery spindles and when entered by hand)", "A", 3.0, 0.2, 40, 0.1),
        ("Ipk", "起停时相电流（驱动器限流值）", "Phase current at start and stop (drive current limit)", "A", 9.0, 0.5, 80, 0.1),
        ("Kt", "电机转矩常数 K_t（示例值）", "Motor torque constant K_t (example value)", "N·m/A", 1.0, 0.1, 5.0, 0.05),
        ("tacc", "每次加速 / 减速时间", "Each acceleration / deceleration", "s", 0.15, 0.02, 1.0, 0.01),
        ("starts", "每分钟起停次数", "Starts and stops per minute", "/min", 30, 1, 120, 1),
        ("duty", "缝纫时间占比", "Share of time sewing", "", 0.5, 0.05, 1.0, 0.05),
        ("Ta", "车间温度", "Workshop temperature", "°C", 40, 0, 60, 1),
    ]),
    ("power", "功率级（18.3、18.4 节）", "Power stage (18.3, 18.4)", [
        ("Vdc", "直流母线电压", "DC bus voltage", "V", 310, 100, 800, 5),
        ("Vce0", "开关管导通压降", "Switch on-state voltage", "V", 1.0, 0.3, 3.0, 0.05),
        ("Rce", "开关管导通电阻", "Switch on-state resistance", "Ω", 0.10, 0.005, 1.0, 0.005),
        ("Vf0", "续流二极管压降", "Diode forward voltage", "V", 0.9, 0.3, 3.0, 0.05),
        ("Rf", "续流二极管电阻", "Diode resistance", "Ω", 0.08, 0.005, 1.0, 0.005),
        ("tsw", "开关时间 t_sw（开通 + 关断）", "Switching time t_sw (on + off)", "ns", 300, 50, 1500, 10),
        ("fsw", "开关频率", "Switching frequency", "kHz", 12, 2, 40, 0.5),
        ("Paux", "其他电路发热（开关电源、主控、电磁铁驱动）", "Other heat (power supply, controller, solenoid drivers)", "W", 8, 0, 100, 0.5),
    ]),
    ("cool", "散热（18.3、18.7 节）", "Cooling (18.3, 18.7)", [
        ("Rjc", "单管结到散热器热阻", "Junction-to-heatsink resistance per switch", "K/W", 3.5, 0.3, 10, 0.1),
        ("tau", "芯片热时间常数", "Chip thermal time constant", "s", 0.05, 0.005, 1.0, 0.005),
        ("Rhs", "散热器到箱内空气热阻", "Heatsink-to-inside-air resistance", "K/W", 1.5, 0.1, 10, 0.05),
        ("rbox_src", "箱内空气到车间的热阻", "Inside-air-to-workshop resistance", "", "given", None, None, None),
        ("Rbox", "箱内空气到车间热阻（给定时）", "Inside-air-to-workshop resistance (when given)", "K/W", 0.6, 0.05, 5, 0.05),
        ("clog", "飞絮堵塞程度（0 干净，1 严重）", "Lint clogging (0 clean, 1 severe)", "", 0.0, 0.0, 1.0, 0.05),
    ]),
    ("box", "外壳（按尺寸算热阻、CAE 复核用）", "Enclosure (for the size-based resistance and the CAE check)", [
        ("L", "外形长", "Length", "mm", 260, 120, 600, 5),
        ("W", "外形宽", "Width", "mm", 160, 80, 400, 5),
        ("H", "外形高", "Height", "mm", 90, 40, 300, 5),
        ("wall", "壁厚（铝）", "Wall thickness (aluminium)", "mm", 3, 1.5, 10, 0.5),
        ("fins", "顶面散热翅片数", "Fins on the top face", "", 0, 0, 30, 1),
        ("fin_h", "翅片高", "Fin height", "mm", 20, 5, 60, 1),
        ("fin_t", "翅片厚", "Fin thickness", "mm", 2, 1, 6, 0.5),
        ("eps", "外表面发射率（喷涂约 0.85，本色铝约 0.1）", "Surface emissivity (painted ~0.85, bare aluminium ~0.1)", "", 0.85, 0.05, 0.95, 0.05),
        ("air", "外面的空气", "Air outside", "", "natural", None, None, None),
        ("vfan", "风扇吹过外壳的风速", "Fan air speed over the enclosure", "m/s", 2.0, 0.3, 10, 0.1),
    ]),
    ("cap", "母线电容（18.7 节）", "Bus capacitor (18.7)", [
        ("Tr", "额定温度", "Rated temperature", "°C", 105, 85, 125, 5),
        ("L0", "额定温度下的寿命", "Life at rated temperature", "h", 2000, 500, 20000, 100),
        ("dTc", "电容芯部比箱内空气高", "Capacitor core above inside air", "K", 5, 0, 30, 1),
        ("hours", "每年通电小时", "Powered hours per year", "h", 4800, 500, 8760, 100),
    ]),
    ("limits", "判据（示意值，可改）", "Criteria (illustrative, editable)", [
        ("Tjmax", "结温设计上限", "Junction design limit", "°C", 125, 80, 175, 1),
        ("Thsmax", "散热器过热报警值", "Heatsink over-temperature alarm", "°C", 100, 60, 150, 1),
        ("lifemin", "电容寿命至少", "Minimum capacitor life", "年", 5, 1, 20, 0.5),
        ("Cp", "电机对地寄生电容", "Motor-to-earth parasitic capacitance", "pF", 300, 10, 5000, 10),
        ("Icmmax", "共模电流峰值上限", "Common-mode current peak limit", "A", 0.8, 0.1, 5, 0.05),
        ("fswmin", "开关频率至少（电机啸叫）", "Minimum switching frequency (motor whine)", "kHz", 8, 2, 20, 0.5),
        ("Thot", "最热的车间（说明书写的上限）", "Hottest workshop (the manual's limit)", "°C", 45, 25, 60, 1),
        ("clog_m", "要扛得住的飞絮堵塞", "Lint clogging the design must survive", "", 0.3, 0.0, 1.0, 0.05),
    ]),
]
CHOICES = {
    "src": [("design", "按本机设计算（主轴转矩 ÷ K_t）", "From this machine's design (torque ÷ K_t)"),
            ("manual", "主轴电流手填", "Spindle current by hand")],
    "rbox_src": [("given", "给定（教材 0.6 K/W）", "Given (textbook 0.6 K/W)"),
                 ("geometry", "按外壳尺寸算", "From the enclosure size")],
    "air": [("natural", "自然对流（没有风扇）", "Natural convection (no fan)"),
            ("fan", "风扇吹", "Fan")],
}
PARAMS, DEFAULTS, _clean = make_params(GROUPS, CHOICES)
# 花样机、刺绣机一只箱子里有主轴和两根伺服轴，箱子和散热器都大一号（示例值）；其余机型就是教材那只 550 W 电控箱
MACHINE_DEFAULTS = {
    "pattern": dict(Rhs=0.6, Rbox=0.3, Paux=15, L=360, W=240, H=120),
    "embroid": dict(Rhs=0.6, Rbox=0.3, Paux=15, L=360, W=240, H=120),
}


def defaults_for(machine):
    return dict(DEFAULTS, **MACHINE_DEFAULTS.get(machine, {}))


def clean(p, machine=None):
    """整理参数；机型不同，没填的项按这台机型的默认"""
    return _clean(dict(MACHINE_DEFAULTS.get(machine, {}), **(p or {})))


# ---------------------------------------------------------------- 损耗
def switch_losses(p, I):
    """一只开关管的导通 P_c、开关 P_s，一只二极管 P_d（W）"""
    Ip = math.sqrt(2) * I
    pc = p["Vce0"] * Ip * (1 / (2 * math.pi) + MCOS / 8) + p["Rce"] * Ip * Ip * (1 / 8 + MCOS / (3 * math.pi))
    ps = 0.5 * p["Vdc"] * (Ip / math.pi) * p["tsw"] * 1e-9 * p["fsw"] * 1e3
    pd = p["Vf0"] * Ip * (1 / (2 * math.pi) - MCOS / 8) + p["Rf"] * Ip * Ip * (1 / 8 - MCOS / (3 * math.pi)) + RRF * ps
    return pc, ps, pd


def stage_loss(p, I):
    """一台驱动的功率级损耗（W）：逆变桥 6 只管 + 整流桥"""
    if I <= 0:
        return 0.0
    pc, ps, pd = switch_losses(p, I)
    return 6 * (pc + ps + pd) + 2 * 0.9 * 0.6 * I


# ---------------------------------------------------------------- 电流从设计来
def drives_of(machine, design_params, p):
    """这台机的电控箱里有几台驱动、各自的运行 / 峰值电流（A）和负载方式。
    startstop：主轴，起停时用峰值；continuous：一直在加减速的伺服轴，平均损耗按有效值电流"""
    from .machines import get
    Kt = p["Kt"]
    manual = p["src"] == "manual"
    out = []
    spindle = dict(key="spindle", zh="主轴伺服", en="Spindle servo", Irun=p["Irun"], Ipk=p["Ipk"], mode="startstop", src="manual")
    if machine in ("lockstitch", "overlock") and not manual:
        from .cae_setup import spindle_torque
        T = spindle_torque(machine, design_params)
        Trms = math.sqrt(sum(x * x for x in T) / len(T))
        spindle.update(Irun=min(Trms / Kt, p["Ipk"]), src="design", Trms=Trms)
    if machine != "flatknit" or manual:            # 横机没有主轴；手填时就是一台手填电流的驱动
        out.append(spindle if machine != "flatknit" else dict(spindle, key="main", zh="主驱动（手填）", en="Main drive (by hand)"))
    if machine == "flatknit" and manual:
        return out
    M = get(machine)
    d = M.clean(design_params or {})
    if machine == "pattern":
        from . import pattern as P
        W = max(10.0, P.window(d["t"])[2] - 2 * d["mg"])
        for ax, zh, en in (("x", "X 轴伺服", "X-axis servo"), ("y", "Y 轴伺服", "Y-axis servo")):
            q = P.axis_motor(d["m" + ax], d["a" + ax], d["r" + ax], d["J" + ax], d["T" + ax + "R"], d["T" + ax + "P"], d["mu"], d["v"],
                             d["Nmot"], W / 360)
            out.append(dict(key=ax, zh=zh, en=en, Irun=q["Trms"] / Kt, Ipk=q["Tpk"] / Kt, mode="continuous", src="design",
                            Trms=q["Trms"], Tpk=q["Tpk"]))
    elif machine == "embroid":
        from . import embroid as E
        q = E.servo(d)
        for ax, zh, en in (("x", "绷架 X 轴伺服", "Frame X servo"), ("y", "绷架 Y 轴伺服", "Frame Y servo")):
            out.append(dict(key=ax, zh=zh, en=en, Irun=q["Trms"] / Kt, Ipk=q["Tpk"] / Kt, mode="continuous", src="design",
                            Trms=q["Trms"], Tpk=q["Tpk"]))
    elif machine == "flatknit":
        from . import flatknit as K
        q = K.drive(d)
        out.append(dict(key="carriage", zh="机头伺服", en="Carriage servo", Irun=q["Trms"] / Kt, Ipk=q["Tpk"] / Kt, mode="continuous",
                        src="design", Trms=q["Trms"], Tpk=q["Tpk"]))
    return out


# ---------------------------------------------------------------- 外壳到车间的热阻（按尺寸）
def box_resistance(p, P_total, clog=None):
    """外壳各面的对流 + 辐射，算箱子（外壳温度 ≈ 箱内空气）到车间的热阻 K/W；ΔT 和 h 互相依赖，迭代几次"""
    L, W, H = p["L"] / 1000, p["W"] / 1000, p["H"] / 1000
    n, fh, ft = int(p["fins"]), p["fin_h"] / 1000, p["fin_t"] / 1000
    Ta = p["Ta"] + 273.15
    top, side_LH, side_WH = L * W, L * H, W * H
    A_env = 2 * top + 2 * side_LH + 2 * side_WH
    A_fin = n * (2 * fh * W + ft * W) * 0.85               # 翅片沿宽度方向，效率 0.85
    Lc = top / (2 * (L + W))
    dT = 15.0
    faces = {}
    for _ in range(30):
        Ts = Ta + dT
        hr = p["eps"] * SIGMA * (Ts * Ts + Ta * Ta) * (Ts + Ta)
        if p["air"] == "fan":
            hc = 3.9 * math.sqrt(p["vfan"] / max(L, 0.05))
            h_up = h_dn = h_v = h_fin = hc
        else:
            h_v = 1.42 * (dT / H) ** 0.25
            # 盒子顶面和顶面翅片泡在从四个侧面升上来的热空气里，比孤立平板的经验式差得多：
            # 第 62 轮自然对流 CFD（教材那只 260 × 160 × 90 mm 电控箱）顶面约一半、翅片约 0.4 倍，按这个折扣
            h_up = 1.32 * (dT / Lc) ** 0.25 * TOP_PLUME
            h_dn = 0.59 * (dT / Lc) ** 0.25
            h_fin = 1.42 * (dT / max(fh, 0.005)) ** 0.25 * FIN_PLUME
        faces = {"top": ((h_up + hr) * top, top), "bottom": ((h_dn + hr) * top, top),
                 "sides": ((h_v + hr) * (2 * side_LH + 2 * side_WH), 2 * side_LH + 2 * side_WH),
                 "fins": (h_fin * A_fin, A_fin)}
        G = sum(v[0] for v in faces.values())
        R = 1 / G
        new = P_total * R * (1 + (p["clog"] if clog is None else clog))
        if abs(new - dT) < 0.01:
            break
        dT = max(0.5, new)
    return dict(R=R, dT=dT, h_rad=hr, A_env=A_env, A_fin=A_fin, faces={k: dict(G=v[0], A=v[1]) for k, v in faces.items()})


# ---------------------------------------------------------------- 热
def thermal(p, drives, Ta=None, clog=None, tsw=None, Rbox=None):
    """一组工况下的温度和寿命。Rbox 给定时用它（CAE 复核算出来的），否则按 rbox_src"""
    q = dict(p)
    if Ta is not None:
        q["Ta"] = Ta
    if clog is not None:
        q["clog"] = clog
    if tsw is not None:
        q["tsw"] = tsw
    c = q["clog"]
    tc = 60 / q["starts"]
    facc = min(q["tacc"] * 2 / tc, q["duty"])
    frun = max(q["duty"] - facc, 0)
    rows, Pavg = [], 0.0
    for d in drives:
        Pk, Pr = stage_loss(q, d["Ipk"]), stage_loss(q, d["Irun"])
        if d["mode"] == "startstop":
            Pa = facc * Pk + frun * Pr
        else:
            Pa = q["duty"] * Pr
        rows.append(dict(d, Pk=Pk, Pr=Pr, Pavg=Pa))
        Pavg += Pa
    Ptot = Pavg + q["Paux"]
    if Rbox is None:
        Rbox = q["Rbox"] if q["rbox_src"] == "given" else box_resistance(q, Ptot, c)["R"]
    rhs = q["Rhs"] * (1 + 1.5 * c)
    Tin = q["Ta"] + Rbox * (1 + c) * Ptot
    Ths = Tin + rhs * Pavg
    Tj, worst = -1e9, None
    for r in rows:
        pc, ps, _ = switch_losses(q, r["Ipk"])
        tpk = q["tacc"] if r["mode"] == "startstop" else min(q["tacc"], 0.05)
        peak = Ths + (pc + ps) * q["Rjc"] * (1 - math.exp(-tpk / q["tau"]))
        pc, ps, _ = switch_losses(q, r["Irun"])
        r["Tjrun"] = Ths + (pc + ps) * q["Rjc"]
        r["Tjpk"] = max(peak, r["Tjrun"])             # 加速时间很短、或一直在动的伺服轴：稳态运行的结温可能更高
        if r["Tjpk"] > Tj:
            Tj, worst = r["Tjpk"], r
    Tcap = Tin + q["dTc"]
    life_h = q["L0"] * 2 ** ((q["Tr"] - Tcap) / 10)
    icm = q["Cp"] * 1e-12 * q["Vdc"] / (q["tsw"] * 1e-9 / 2)
    return dict(Pavg=Pavg, Ptot=Ptot, facc=facc, frun=frun, Rbox=Rbox, rhs=rhs, Tin=Tin, Ths=Ths, Tjpk=Tj, worst=worst,
                Tcap=Tcap, life_h=life_h, life_y=life_h / q["hours"], icm=icm, drives=rows,
                acc_share=(sum(facc * r["Pk"] for r in rows if r["mode"] == "startstop") / Pavg) if Pavg > 0 else 0.0)


def tsw_window(p, drives, Ta=None, Rbox=None):
    """开关时间 t_sw 能选的范围（ns）：下限由共模电流定，上限由结温定（在最热的车间里）。下限超过参数表上限 1500 ns 就没有窗口"""
    lo = 2 * p["Cp"] * 1e-12 * p["Vdc"] / p["Icmmax"] * 1e9
    Ta = max(p["Ta"], p["Thot"]) if Ta is None else Ta

    def ok(t):
        r = thermal(p, drives, Ta=Ta, tsw=t, Rbox=Rbox)
        return r["Tjpk"] <= p["Tjmax"] and r["Ths"] <= p["Thsmax"]
    if lo > 1500 or not ok(max(lo, 50)):
        return lo, None
    a, b = max(lo, 50), 1500.0                  # 参数表上限；到这里还合格，上限就只受参数表限制
    if ok(b):
        return lo, b
    for _ in range(60):
        m = (a + b) / 2
        a, b = (m, b) if ok(m) else (a, m)
    return lo, a


def cycle(p, drives, r, n=480):
    """两个起停周期里的电流、结温（一阶响应，跑三遍到周期稳态）和散热器温度——教材图 18-3"""
    d = r["worst"] or (drives[0] if drives else None)
    tc = 60 / p["starts"]
    T = 2 * tc
    ta = min(p["tacc"], p["duty"] * tc / 2)
    tr = max(p["duty"] * tc - 2 * ta, 0)
    cont = d and d["mode"] == "continuous"

    def I_of(u):
        k = u % tc
        if cont:
            return d["Irun"] if k < p["duty"] * tc else 0.0
        if k < ta:
            return d["Ipk"]
        if k < ta + tr:
            return d["Irun"]
        if k < 2 * ta + tr:
            return d["Ipk"]
        return 0.0

    def p_of(I):
        if I <= 0:
            return 0.0
        pc, ps, _ = switch_losses(p, I)
        return pc + ps
    dt = T / n
    z, ts, tj, ii = 0.0, [], [], []
    for _ in range(3):
        ts, tj, ii = [], [], []
        for i in range(n + 1):
            u = i * dt
            I = I_of(u)
            z += (p_of(I) * p["Rjc"] - z) * (1 - math.exp(-dt / p["tau"]))
            ts.append(round(u, 4))
            tj.append(r["Ths"] + z)
            ii.append(I)
    return ts, tj, ii, [r["Ths"]] * len(ts)


# ---------------------------------------------------------------- 校核与结果
def analyze(p, machine="lockstitch", design_params=None, Rbox=None):
    p = clean(p, machine)
    design_params = design_params or {}
    drives = drives_of(machine, design_params, p)
    r = thermal(p, drives, Rbox=Rbox)
    hot = thermal(p, drives, Ta=max(p["Ta"], p["Thot"]), Rbox=Rbox)
    dirty = thermal(p, drives, clog=max(p["clog"], p["clog_m"]), Rbox=Rbox)
    lo, hi = tsw_window(p, drives, Rbox=Rbox)
    geo = box_resistance(p, r["Ptot"])
    C = Checks()
    st = lambda ok, warn=False: "ok" if ok else ("warn" if warn else "bad")  # noqa: E731
    C.add("ths", "heat", "散热器温度不超过过热报警值", "Heatsink below the over-temperature alarm",
          f"{r['Ths']:.1f} °C", f"≤ {p['Thsmax']:g} °C", st(r["Ths"] <= p["Thsmax"]), 18,
          "散热器温度传感器会报过热，机器停下：加散热面积或风扇、降低起停电流、清理飞絮",
          "The heatsink sensor trips and the machine stops: add cooling area or a fan, lower the start current, clean out lint")
    C.add("tj", "heat", "起停时结温峰值不超过设计上限", "Peak junction temperature at start and stop within the design limit",
          f"{r['Tjpk']:.1f} °C", f"≤ {p['Tjmax']:g} °C", st(r["Tjpk"] <= p["Tjmax"]), 18,
          "降额余量不够，开关管寿命和可靠性下降：缩短开关时间（在窗口内）、降低峰值电流或缩短加速时间",
          "Not enough derating margin: shorten the switching time (within the window), lower the peak current or the acceleration time")
    C.add("life", "heat", "母线电容寿命", "Bus capacitor life",
          (f"{r['life_y']:.1f} 年（芯部 {r['Tcap']:.1f} °C）", f"{r['life_y']:.1f} years (core {r['Tcap']:.1f} °C)"),
          (f"≥ {p['lifemin']:g} 年", f"≥ {p['lifemin']:g} years"), st(r["life_y"] >= p["lifemin"]), 18,
          "电容会提前干涸、鼓包：降低箱内温度，或选 105 °C、更长寿命的电容，离散热器远一点",
          "The capacitor will dry out and bulge early: cool the inside air, or use a longer-life 105 °C part away from the heatsink")
    C.add("icm", "emc", "共模电流峰值", "Common-mode current peak",
          f"{r['icm']:.2f} A", f"≤ {p['Icmmax']:g} A", st(r["icm"] <= p["Icmmax"]), 18,
          "dv/dt 太大，滤波器压不住，传导和辐射发射可能超标：放慢开关（在窗口内）、加强入口滤波",
          "dv/dt too high for the filter; conducted and radiated emissions may fail: switch slower (within the window), strengthen the input filter")
    C.add("fsw", "emc", "开关频率", "Switching frequency", f"{p['fsw']:g} kHz", f"≥ {p['fswmin']:g} kHz", st(p["fsw"] >= p["fswmin"]), 18,
          "频率太低，电机啸叫、电流纹波大（示意判据）", "Too low: motor whine and current ripple (illustrative criterion)")
    win_ok = hi is not None and lo <= p["tsw"] <= hi
    C.add("window", "emc", "开关时间在可选窗口内（最热车间）", "Switching time inside the allowed window (hottest workshop)",
          f"{p['tsw']:g} ns", (f"{lo:.0f}–{hi:.0f} ns" if hi else f"无窗口（下限 {lo:.0f} ns 时结温已超）",
                               f"{lo:.0f}–{hi:.0f} ns" if hi else f"no window (junction too hot already at {lo:.0f} ns)"),
          st(win_ok, hi is not None), 18,
          "开关慢了结温高、快了共模电流大：取窗口中间；窗口不存在说明散热或电流要先改",
          "Slower switching heats the junction, faster raises common-mode current: pick the middle; no window means fix cooling or current first")
    C.add("hot", "margin", "最热车间仍合格", "Still within limits in the hottest workshop",
          (f"{max(p['Ta'], p['Thot']):g} °C 车间：散热器 {hot['Ths']:.1f}、结温 {hot['Tjpk']:.1f} °C",
           f"{max(p['Ta'], p['Thot']):g} °C workshop: heatsink {hot['Ths']:.1f}, junction {hot['Tjpk']:.1f} °C"),
          (f"≤ {p['Thsmax']:g} / {p['Tjmax']:g} °C", f"≤ {p['Thsmax']:g} / {p['Tjmax']:g} °C"),
          st(hot["Ths"] <= p["Thsmax"] and hot["Tjpk"] <= p["Tjmax"], True), 18,
          "说明书写的最高环境温度下会报过热：留出余量，或在散热器过热时自动限加速度（18.3 节）",
          "It would trip at the manual's maximum ambient: add margin, or limit acceleration automatically when the heatsink is hot (18.3)")
    C.add("lint", "margin", "飞絮堵塞后仍合格（18.7 节）", "Still within limits with lint clogging (18.7)",
          (f"堵塞 {max(p['clog'], p['clog_m']):g}：散热器 {dirty['Ths']:.1f}、结温 {dirty['Tjpk']:.1f} °C",
           f"clogging {max(p['clog'], p['clog_m']):g}: heatsink {dirty['Ths']:.1f}, junction {dirty['Tjpk']:.1f} °C"),
          (f"≤ {p['Thsmax']:g} / {p['Tjmax']:g} °C", f"≤ {p['Thsmax']:g} / {p['Tjmax']:g} °C"),
          st(dirty["Ths"] <= p["Thsmax"] and dirty["Tjpk"] <= p["Tjmax"], True), 18,
          "飞絮糊住散热面会报过热（18.7 节）：保养规程写明清理周期、加防尘网，或散热留余量",
          "Lint on the cooling surfaces will trip it (18.7): set a cleaning interval, add a dust filter, or leave thermal margin")
    ok = all(c["state"] != "bad" for c in C)
    res = [result("功率级平均损耗", "Average power-stage loss", f"{r['Pavg']:.1f}", "W"),
           result("其中起停贡献", "Share from starts and stops", f"{r['acc_share'] * 100:.0f}", "%"),
           result("箱内空气", "Inside air", f"{r['Tin']:.1f}", "°C"),
           result("散热器", "Heatsink", f"{r['Ths']:.1f}", "°C"),
           result("结温峰值", "Peak junction", f"{r['Tjpk']:.1f}", "°C"),
           result("电容寿命", "Capacitor life", f"{r['life_y']:.1f}", "年 / years"),
           result("共模电流峰值", "Common-mode current peak", f"{r['icm']:.2f}", "A"),
           result("箱子到车间热阻（用的）", "Enclosure-to-workshop resistance (used)", f"{r['Rbox']:.2f}", "K/W"),
           result("按外壳尺寸算的热阻", "Size-based resistance", f"{geo['R']:.2f}", "K/W")]
    ts, tj, ii, th = cycle(p, drives, r)
    charts = [
        line_chart("cycle", "间歇缝纫：结温和散热器温度（两个起停周期，图 18-3）", "Intermittent sewing: junction and heatsink (two cycles, Fig. 18-3)",
                   ts, [("结温", "Junction", "#c0392b", tj), ("散热器", "Heatsink", "#2d6fb3", th)], ref=p["Tjmax"],
                   xr=[0, ts[-1]], xl=("时间 s", "time s")),
        line_chart("current", "相电流（最热的那台驱动）", "Phase current (the hottest drive)", ts, [("电流 A", "Current A", "#7d5ba6", ii)],
                   zero=True, xr=[0, ts[-1]], xl=("时间 s", "time s")),
    ]
    tsws = list(range(50, 1210, 20))
    tr = [thermal(p, drives, Ta=max(p["Ta"], p["Thot"]), tsw=t, Rbox=Rbox) for t in tsws]
    charts.append(line_chart("trade", f"开关时间的折中（{max(p['Ta'], p['Thot']):g} °C 车间，图 18-4 右）",
                             f"Switching-time trade-off ({max(p['Ta'], p['Thot']):g} °C workshop, Fig. 18-4 right)", tsws,
                             [("结温峰值 °C", "Peak junction °C", "#c0392b", [x["Tjpk"] for x in tr]),
                              ("共模电流 ×100 A", "Common-mode current ×100 A", "#2d6fb3", [x["icm"] * 100 for x in tr])],
                             ref=p["Tjmax"], xr=[50, 1190], xl=("开关时间 t_sw ns", "switching time t_sw ns")))
    cl = [i / 20 for i in range(21)]
    cr = [thermal(p, drives, clog=c, Rbox=Rbox) for c in cl]
    charts.append(line_chart("lint", "飞絮堵塞以后（图 18-7 左）", "With lint clogging (Fig. 18-7 left)", cl,
                             [("散热器 °C", "Heatsink °C", "#2d6fb3", [x["Ths"] for x in cr]),
                              ("结温峰值 °C", "Peak junction °C", "#c0392b", [x["Tjpk"] for x in cr])],
                             ref=p["Thsmax"], xr=[0, 1], xl=("堵塞程度", "clogging")))
    tas = list(range(20, 51))
    lr = [thermal(p, drives, Ta=t, Rbox=Rbox) for t in tas]
    charts.append(line_chart("capacitor", "电容寿命随车间温度（十度法则，图 18-7 右）", "Capacitor life vs workshop temperature (10-degree rule, Fig. 18-7 right)",
                             tas, [("寿命 年", "Life years", "#2e9e6a", [min(x["life_y"], 30) for x in lr])], ref=p["lifemin"],
                             xr=[20, 50], xl=("车间温度 °C", "workshop °C")))
    return dict(params=p, machine=machine, ok=ok, checks=list(C), results=res, charts=charts, drives=[
        dict(key=d["key"], zh=d["zh"], en=d["en"], Irun=round(d["Irun"], 2), Ipk=round(d["Ipk"], 2), mode=d["mode"], src=d["src"],
             Pavg=round(d["Pavg"], 2), Pk=round(d["Pk"], 1), Pr=round(d["Pr"], 1), Tjpk=round(d["Tjpk"], 1),
             **({"Trms": round(d["Trms"], 3)} if "Trms" in d else {})) for d in r["drives"]],
        thermal={k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if k not in ("drives", "worst")},
        window=dict(lo=round(lo, 1), hi=round(hi, 1) if hi else None), geometry=geo, variants=variants(p, machine, design_params, Rbox),
        box=box_spec(p, r), lectures=LECTURES)


def analyze_light(p, machine, design_params, Rbox=None):
    """改进方案表用：不画曲线、不递归"""
    drives = drives_of(machine, design_params, p)
    r = thermal(p, drives, Rbox=Rbox)
    hot = thermal(p, drives, Ta=max(p["Ta"], p["Thot"]), Rbox=Rbox)
    dirty = thermal(p, drives, clog=max(p["clog"], p["clog_m"]), Rbox=Rbox)
    lo, hi = tsw_window(p, drives, Rbox=Rbox)
    bad = sum([r["Ths"] > p["Thsmax"], r["Tjpk"] > p["Tjmax"], r["life_y"] < p["lifemin"], r["icm"] > p["Icmmax"], p["fsw"] < p["fswmin"],
               hi is None])
    warn = sum([hot["Ths"] > p["Thsmax"] or hot["Tjpk"] > p["Tjmax"], dirty["Ths"] > p["Thsmax"] or dirty["Tjpk"] > p["Tjmax"],
                hi is not None and not lo <= p["tsw"] <= hi])
    return dict(r=r, bad=bad, warn=warn)


def variants(p, machine, design_params, Rbox=None):
    """改进方案对照（同第 54 轮横机的做法）：每行一种改法，给关键数和还剩几盏红 / 黄灯"""
    drives = drives_of(machine, design_params, p)
    lo, hi = tsw_window(p, drives, Rbox=Rbox)
    rows = []
    base = thermal(p, drives, Rbox=Rbox)
    # 改成“按外壳尺寸算”的那几行（加翅片、加风扇）：按现在用的热阻和按尺寸公式的比例缩放，只比改法本身带来的变化，不混进换模型的差别
    scale = base["Rbox"] / max(box_resistance(p, base["Ptot"])["R"], 1e-9)

    def add(zh, en, q, rb=Rbox):
        if rb is None and q.get("rbox_src") == "geometry" and (p["rbox_src"] != "geometry" or Rbox is not None):
            rq = thermal(q, drives_of(machine, design_params, q))
            rb = box_resistance(q, rq["Ptot"])["R"] * scale
        a = analyze_light(q, machine, design_params, rb)
        r = a["r"]
        rows.append([zh, en, f"{r['Ths']:.1f}", f"{r['Tjpk']:.1f}", f"{r['life_y']:.1f}", f"{r['icm']:.2f}", str(a["bad"]), str(a["warn"])])
    add("现在的设计", "Current design", p)
    if p["rbox_src"] == "geometry" or p["fins"] > 0 or Rbox is not None:
        q = dict(p, rbox_src="geometry", fins=max(p["fins"], 0) + 10)
        add(f"顶面加 10 片散热翅片（共 {int(q['fins'])} 片）", f"Add 10 fins on top ({int(q['fins'])} in all)", q, None)
    else:
        add("加大散热面积（箱子热阻 −25%）", "More cooling area (enclosure resistance −25%)", dict(p, Rbox=p["Rbox"] * 0.75))
    if p["air"] != "fan":
        q = dict(p, rbox_src="geometry", air="fan", vfan=2.0)
        add("加风扇，2 m/s 吹过外壳", "Add a fan, 2 m/s over the enclosure", q, None)
    if hi is not None and not lo <= p["tsw"] <= hi:
        mid = round((lo + min(hi, 3 * lo)) / 2 / 10) * 10
        add(f"开关时间改到窗口中间 {mid:g} ns", f"Switching time to the middle of the window, {mid:g} ns", dict(p, tsw=mid))
    if any(d["mode"] == "startstop" for d in drives):
        add("起停限流降 20%、加速时间 +25%", "Start current −20%, acceleration time +25%", dict(p, Ipk=p["Ipk"] * 0.8, tacc=min(1.0, p["tacc"] * 1.25)))
    if p["clog"] > 0.1:
        add("定期清理飞絮（堵塞降到 0.1）", "Clean out lint regularly (clogging down to 0.1)", dict(p, clog=0.1))
    if int(rows[0][6]) + int(rows[0][7]) > 0:          # 有红黄灯：再给一行“上面几条一起用”
        q = dict(p, clog=min(p["clog"], 0.1), rbox_src="geometry", air="fan", vfan=max(p["vfan"], 2.0), fins=p["fins"] + 10)
        zh, en = ["加风扇", "加 10 片翅片"], ["fan", "10 more fins"]
        if p["clog"] > 0.1:
            zh.insert(0, "定期清理")
            en.insert(0, "regular cleaning")
        if any(d["mode"] == "startstop" for d in drives):
            q.update(Ipk=p["Ipk"] * 0.8, tacc=min(1.0, p["tacc"] * 1.25))
            zh.append("起停限流降 20%")
            en.append("start current −20%")
        add("几条一起：" + " + ".join(zh), "All together: " + " + ".join(en), q, None)
    return dict(key="variants", zh="改进方案对照", en="Improvement options",
                cols=[["改法", "Change"], ["", ""], ["散热器 °C", "Heatsink °C"], ["结温峰值 °C", "Peak junction °C"], ["电容寿命 年", "Cap life yrs"],
                      ["共模电流 A", "CM current A"], ["红灯", "Red"], ["黄灯", "Yellow"]], rows=rows)


def box_spec(p, r):
    """参数化电控箱（给计算服务建 STEP 和热载荷用）：外壳、顶面翅片、功率模块贴在顶板里面（铝外壳兼作散热器）"""
    return dict(L=p["L"], W=p["W"], H=p["H"], wall=p["wall"], fins=int(p["fins"]), fin_h=p["fin_h"], fin_t=p["fin_t"],
                p_ipm=round(r["Pavg"], 2), p_aux=round(p["Paux"], 2), t_air_c=p["Ta"], eps=p["eps"],
                air=p["air"], vfan=p["vfan"])
