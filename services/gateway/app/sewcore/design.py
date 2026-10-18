# -*- coding: utf-8 -*-
"""平缝机设计计算（第 39 轮）：一组设计参数 → 各机构尺寸、运动曲线、时序、校核（红绿灯）、试缝结果。

网页版（网关 /api/v1/sewing/*）与 FreeCAD 工作台都只调 analyze()，所以两边同一组参数的结果完全一样。
判据出处：第 3 讲（针杆惯性力、连杆比）、第 4 讲（挑线余量）、第 5 讲（钩线回升窗口、梭尖间隙）、第 6 讲（送布时序）、
第 7 讲（张力）、第 8 讲（整机惯性力、全机时序）、第 23 讲（尺寸链、二阶共振）。
"""
import math

from .kit import FEED_A, FT, LK0, THREAD, FEED_FAB, Mech

VERSION = "1.0"

# ---------- 参数表：网页表单、FreeCAD 面板、计算书都从这里生成 ----------
# (key, 中文, English, 单位, 默认, 最小, 最大, 步长)
GROUPS = [
    ("basic", "基本参数", "Basic", [
        ("n", "最高转速", "Top speed", "r/min", 5000, 2000, 7000, 100),
        ("s", "针距", "Stitch length", "mm", 3.0, 1.0, 5.0, 0.1),
        ("fab", "面料", "Fabric", "", "cotton", None, None, None),
        ("th", "缝线", "Thread", "", "t24", None, None, None),
    ]),
    ("needle", "刺布机构（曲柄滑块）", "Needle bar (slider-crank)", [
        ("r", "曲柄半径", "Crank radius", "mm", 15.5, 10, 25, 0.1),
        ("l", "连杆长", "Connecting-rod length", "mm", 55.0, 35, 90, 0.5),
        ("mr", "针杆组件质量", "Needle-bar assembly mass", "kg", 0.12, 0.05, 0.25, 0.005),
        ("F_lim", "针杆轴套允许载荷", "Needle-bar bushing load limit", "N", 800, 300, 1500, 10),
    ]),
    ("takeup", "挑线机构（连杆式）", "Take-up (linkage)", [
        ("lk_r", "挑线曲柄半径", "Take-up crank radius", "mm", 20.7, 15, 26, 0.1),
        ("lk_a", "挑线杆 P–M", "Lever P–M", "mm", 43.4, 35, 52, 0.1),
        ("lk_b", "摇杆 M–Q", "Rocker M–Q", "mm", 40.9, 32, 50, 0.1),
        ("lk_c", "挑线杆 P–线眼", "Lever P–eye", "mm", 65.7, 55, 80, 0.1),
        ("lk_al", "线眼偏角", "Eye offset angle", "°", 2.8, -10, 15, 0.1),
        ("lk_d", "挑线曲柄相位", "Take-up crank phase", "°", -6.8, -30, 20, 0.1),
        ("u", "过线板位置", "Thread-guide position", "mm", 0, -12, 12, 0.5),
        ("stroke", "挑线簧行程", "Check-spring stroke", "mm", 10, 4, 14, 0.5),
    ]),
    ("hook", "钩线机构（旋梭）", "Hook (rotary hook)", [
        ("psi", "旋梭定时（旋梭转角）", "Hook timing (hook angle)", "°", 0, -25, 25, 0.5),
        ("dz", "针杆高度调整", "Needle-bar height adjustment", "mm", 0, -1.2, 1.2, 0.05),
        ("g", "梭尖间隙（Nm 90 针）", "Hook clearance (Nm 90 needle)", "mm", 0.08, 0.0, 0.2, 0.01),
        ("d", "机针直径", "Needle diameter", "mm", 0.9, 0.6, 1.2, 0.05),
    ]),
    ("feed", "送布机构", "Feed", [
        ("h", "送布牙高出针板", "Feed-dog height", "mm", 0.8, 0.3, 1.6, 0.05),
        ("dT", "送布定时", "Feed timing", "°", 0, -15, 25, 0.5),
        ("dP", "水平送布相位", "Horizontal-feed phase", "°", 0, -30, 30, 0.5),
        ("P", "压脚压力（相对）", "Presser-foot pressure (relative)", "", 1.0, 0.3, 3.0, 0.05),
        ("mode", "送布方式", "Feed type", "", "drop", None, None, None),
    ]),
    ("tension", "线张力", "Thread tension", [
        ("Td", "夹线器张力", "Upper (tension disc)", "cN", 100, 30, 280, 1),
        ("Tb", "底线张力", "Bobbin", "cN", 40, 10, 100, 1),
    ]),
    ("frame", "平衡与机壳", "Balance and frame", [
        ("k", "平衡率", "Balance ratio", "", 0.3, 0.0, 1.0, 0.01),
        ("fn", "机壳一阶固有频率", "Frame first natural frequency", "Hz", 190, 120, 320, 1),
        ("zeta", "机壳阻尼比", "Frame damping ratio", "", 0.03, 0.01, 0.15, 0.005),
    ]),
]
CHOICES = {
    "fab": [("lining", "衬里滑料", "Lining"), ("cotton", "棉布", "Cotton"), ("denim", "牛仔布", "Denim")],
    "th": [("t18", "Tex 18（细）", "Tex 18 (fine)"), ("t24", "Tex 24", "Tex 24"), ("t40", "Tex 40（粗）", "Tex 40 (coarse)")],
    "mode": [("drop", "下送布", "Drop feed"), ("needle", "针送布", "Needle feed"), ("compound", "综合送布", "Compound feed")],
}
PARAMS = {p[0]: p for g in GROUPS for p in g[3]}
DEFAULTS = {k: p[4] for k, p in PARAMS.items()}


def clean(p):
    """把外来参数整理成合法的一组：未知的键丢掉，数值夹到范围里，选项不在表里用默认。"""
    out = dict(DEFAULTS)
    for k, v in (p or {}).items():
        if k not in PARAMS:
            continue
        spec = PARAMS[k]
        if k in CHOICES:
            if v in [c[0] for c in CHOICES[k]]:
                out[k] = v
            continue
        try:
            v = float(v)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(v):
            continue
        out[k] = min(spec[6], max(spec[5], v))
    out["n"] = round(out["n"])
    return out


def mech_of(p):
    lk = dict(r=p["lk_r"], a=p["lk_a"], b=p["lk_b"], c=p["lk_c"], al=p["lk_al"], d=p["lk_d"])
    return Mech(r=p["r"], l=p["l"], mr=p["mr"], lk=lk)


def _yield(sigma, half=0.03):
    return math.erf(half / sigma / math.sqrt(2))


# 梭尖间隙尺寸链（第 23 讲 23.3 节，八个环；公差为示意值，与虚拟实验 23-1 相同）
# (中文, English, 公差 ±mm, 装配调整时吸收, 换针时变)
CHAIN = [("针杆套孔位置", "Needle-bar bushing bore position", 0.03, 1, 0),
         ("针杆与针杆套的游隙", "Needle bar / bushing play", 0.008, 0, 0),
         ("针夹孔偏移", "Needle-clamp bore offset", 0.02, 1, 0),
         ("机针凹口面尺寸", "Needle scarf face", 0.02, 0, 1),
         ("机针安装偏转", "Needle mounting twist", 0.015, 0, 1),
         ("旋梭轴孔位置", "Hook-shaft bore position", 0.03, 1, 0),
         ("梭尖到安装基准", "Hook point to mounting datum", 0.02, 1, 0),
         ("旋梭轴径向游隙", "Hook-shaft radial play", 0.01, 0, 0)]
CHAIN_ADJ = 0.01          # 装配调整误差 ±mm
CHAIN_HALF = 0.03         # 间隙 0.07 ± 0.03 mm 为合格


def chain():
    wc = sum(c[2] for c in CHAIN)
    sg = math.sqrt(sum((c[2] / 3) ** 2 for c in CHAIN))
    rem = [CHAIN_ADJ] + [c[2] for c in CHAIN if not c[3] and not c[4]]
    sa = math.sqrt(sum((t / 3) ** 2 for t in rem))
    ss = math.sqrt(sa ** 2 + 2 * sum((c[2] / 3) ** 2 for c in CHAIN if c[4]))
    return dict(worst=wc, sigma=sg, y_int=_yield(sg), sigma_adj=sa, y_adj=_yield(sa), sigma_swap=ss, y_swap=_yield(ss))


def vib(n, fn=190, z=0.03):
    """机壳振动速度 mm/s（第 23 讲 23.6 节的单自由度模型：一阶 300 N、二阶 120 N 激振，按转速平方缩放）"""
    def amp(r):
        return 1 / math.sqrt((1 - r * r) ** 2 + (2 * z * r) ** 2)
    K = 1e8 * (fn / 190) ** 2
    vs = []
    for order, F0 in ((1, 300), (2, 120)):
        f = order * n / 60
        X = F0 * (n / 5000) ** 2 / K * amp(f / fn)
        vs.append(2 * math.pi * f * X / math.sqrt(2) * 1000)
    return math.hypot(*vs)


VREF = vib(5000)


def _angle_where(fn, a, b, step=0.01):
    """[a, b] 里 fn 第一次为真的角度（找不到返回 None）"""
    x = a
    while x <= b:
        if fn(x):
            return x
        x += step
    return None


def analyze(params=None, trial=True):
    p = clean(params)
    M = mech_of(p)
    n, s, fab = p["n"], p["s"], p["fab"]
    t = FT[fab]
    w = 2 * math.pi * n / 60
    lam = M.LAM

    # ---- 刺布 ----
    aT, aB = M.acc(0, n), M.acc(180, n)
    vmax, fv = max((abs(M.vel(f / 10, n)), f / 10) for f in range(0, 1801))
    F_bdc, F_tdc = p["mr"] * abs(aB), p["mr"] * aT
    n_max_F = n * math.sqrt(p["F_lim"] / F_bdc) if F_bdc > 0 else None
    pin, pout = M.cross(t), 360 - M.cross(t)          # 针尖入布 / 出布
    ein = M.cross(t - M.EYE)                           # 针眼上沿入布

    # ---- 钩线 ----
    G = M.hook_geom(psi=p["psi"], dz=p["dz"], g=p["g"], d=p["d"], fab="woven")
    phc = int(math.floor(G["fc"] + 0.5))
    w16 = _angle_where(lambda f: M.rise(f) >= 1.6, 180, 260)
    w25 = _angle_where(lambda f: M.rise(f) > 2.5, 180, 260)
    hook_speed = 2 * w * 13.5e-3                       # 旋梭转速是主轴两倍，梭尖线速度 m/s

    # ---- 挑线 ----
    TK = M.takeup(u=p["u"], t=t, s=s, phc=phc, rpm=n, lk=M.LK0)

    # ---- 送布 ----
    F = M.feed_model(fab=fab, mode=p["mode"], s=s, dT=p["dT"], dP=p["dP"], h=p["h"], P=p["P"])

    # ---- 张力 ----
    E = M.tension(fab=fab, th=p["th"], Td=p["Td"], Tb=p["Tb"], s=s, n=n)

    # ---- 整机惯性力与振动 ----
    FF = M.forces(n=n, k=p["k"], dT=p["dT"])
    fmag = [math.hypot(x, y) for x, y in FF]
    fmax = max(fmag)
    r2 = 2 * n / 60 / p["fn"]
    v_mm = vib(n, p["fn"], p["zeta"])
    noise = 83.5 + 20 * math.log10(v_mm / VREF)
    n_res = p["fn"] * 30
    CH = chain()

    # ---- 校核：每条 {key, 组, 名称, 数值, 判据, 结论 ok/warn/bad, 讲次, 建议} ----
    checks = []

    def bi(x):
        return dict(zh=x[0], en=x[1]) if isinstance(x, tuple) else dict(zh=x, en=x)

    def chk(key, grp, zh, en, value, limit, state, lec, adv_zh="", adv_en=""):
        """value / limit：纯数字写一个字符串；带文字的写 (中文, English)"""
        checks.append(dict(key=key, group=grp, name=dict(zh=zh, en=en), value=bi(value), limit=bi(limit), state=state, lecture=lec,
                           advice=dict(zh=adv_zh, en=adv_en)))

    chk("needle_force", "needle", "针杆下止点惯性力", "Needle-bar inertia force at BDC", f"{F_bdc:.0f} N", f"≤ {p['F_lim']:.0f} N",
        "ok" if F_bdc <= p["F_lim"] else "bad", 3,
        f"惯性力与转速平方成正比；这组尺寸在 {n_max_F:.0f} r/min 以内不超限。减轻针杆组件或减小曲柄半径。" if F_bdc > p["F_lim"] else "",
        f"The force grows with speed squared; these dimensions stay within the limit up to {n_max_F:.0f} r/min. Lighten the needle bar or shorten the crank." if F_bdc > p["F_lim"] else "")
    chk("lambda", "needle", "连杆比 λ = r/l", "Rod ratio λ = r/l", f"{lam:.3f}", "0.20–0.40",
        "ok" if 0.2 <= lam <= 0.4 else "warn", 3,
        "λ 太大二阶惯性力大、针杆侧向力大；太小机头高度增加。" if not 0.2 <= lam <= 0.4 else "",
        "Too large: strong second-order force and side load; too small: a taller head." if not 0.2 <= lam <= 0.4 else "")
    chk("catch_rise", "hook", "钩线时机针回升量", "Needle rise when the hook catches", (f"{G['h']:.2f} mm（{G['fc']:.1f}°）", f"{G['h']:.2f} mm ({G['fc']:.1f}°)"), "1.6–2.5 mm",
        "ok" if 1.6 <= G["h"] <= 2.5 else "bad", 5,
        "调旋梭定时：回升量太小钩线太早、太大线环已收缩，都会跳针。" if not 1.6 <= G["h"] <= 2.5 else "",
        "Adjust the hook timing: too little rise catches too early, too much catches a shrinking loop; both skip." if not 1.6 <= G["h"] <= 2.5 else "")
    res_txt = {"ok": ("钩住线环", "loop caught"), "skip": ("跳针", "skip"), "hit": ("梭尖碰针", "hook hits needle"), "cut": ("梭尖划线", "hook splits thread")}
    chk("hook", "hook", "钩线（线环余量、间隙、梭尖高度）", "Loop catch (margin, clearance, point height)",
        (f"{res_txt[G['res']][0]}；间隙 {G['g']:.2f} mm，梭尖高于针眼 {G['D']:.2f} mm",
         f"{res_txt[G['res']][1]}; clearance {G['g']:.2f} mm, point {G['D']:.2f} mm above the eye"),
        ("钩住且不碰针、不划线", "caught, no hit, no split"),
        "ok" if G["res"] == "ok" else "bad", 5,
        {"hit": "换粗针后要把旋梭沿轴向移出，恢复间隙。", "cut": "降低针杆或提前钩线。", "skip": "按调机卡重新定旋梭定时、针杆高度、梭尖间隙。"}.get(G["res"], ""),
        {"hit": "After fitting a thicker needle, move the hook axially to restore the clearance.", "cut": "Lower the needle bar or catch earlier.",
         "skip": "Reset hook timing, needle-bar height and clearance as on the adjustment card."}.get(G["res"], ""))
    if TK["ok"]:
        chk("takeup_margin", "takeup", "绕梭时挑线余量（最小）", "Take-up margin round the bobbin (min)", (f"{TK['margin']:.1f} mm（{TK['at']}°）", f"{TK['margin']:.1f} mm ({TK['at']}°)"), "≥ 1 mm",
            "ok" if TK["margin"] >= 1 else "bad", 4,
            "加大挑线曲柄半径或线眼到 P 的距离，或把过线板往放线多的方向调。" if TK["margin"] < 1 else "",
            "Increase the take-up crank radius or the P–eye length, or move the thread guide to give more thread." if TK["margin"] < 1 else "")
        chk("takeup_neg", "takeup", "针眼入布后欠线", "Thread shortfall after the eye enters", f"{TK['neg']:.1f} mm", "≤ 1 mm",
            "ok" if TK["neg"] <= 1 else "bad", 4, "欠线超过线的弹性伸长，线环张不开。" if TK["neg"] > 1 else "",
            "More shortfall than the thread can stretch: the loop cannot open." if TK["neg"] > 1 else "")
        chk("takeup_pre", "takeup", "针眼入布前多放的线", "Thread released before the eye enters", f"{TK['pre']:.1f} mm", (f"≤ 挑线簧行程 {p['stroke']:.1f} mm", f"≤ check-spring stroke {p['stroke']:.1f} mm"),
            "ok" if TK["pre"] <= p["stroke"] else "warn", 4, "多出的线挑线簧收不住，面线松垮。" if TK["pre"] > p["stroke"] else "",
            "The check spring cannot take up the extra thread; the upper thread goes slack." if TK["pre"] > p["stroke"] else "")
        mu0, mu1 = TK["mu"]
        chk("takeup_mu", "takeup", "挑线四杆传动角范围", "Take-up linkage transmission angle", f"{mu0:.0f}°–{mu1:.0f}°", "40°–140°",
            "ok" if mu0 >= 40 and mu1 <= 140 else "warn", 4, "传动角太小，摇杆受力大、磨损快。" if not (mu0 >= 40 and mu1 <= 140) else "",
            "A small transmission angle loads and wears the rocker." if not (mu0 >= 40 and mu1 <= 140) else "")
    else:
        chk("takeup_ok", "takeup", "挑线四杆能否整周转动", "Take-up linkage turns a full revolution", ("不能（装不上）", "no (cannot be assembled)"), ("能整周转动", "full revolution"), "bad", 4,
            "四杆尺寸不满足整周转动，改挑线杆或摇杆长度。", "The four-bar cannot turn a full revolution; change the lever or rocker length.")
    chk("feed_drag", "feed", "机针在布中时送布量", "Feed while the needle is in the fabric", f"{F['drag']:.2f} mm", "≤ 0.05 mm",
        "ok" if F["drag"] <= 0.05 else "bad", 6, "送布太晚：提前送布定时。" if F["drag"] > 0.05 else "",
        "Feed too late: advance the feed timing." if F["drag"] > 0.05 else "")
    chk("feed_slip", "feed", "实际针距 / 设定针距", "Actual / set stitch length", (f"{F['eps'] * 100:.0f}%（不打滑需压力 ≥ {F['Pmin']:.2f}）", f"{F['eps'] * 100:.0f}% (no slip needs pressure ≥ {F['Pmin']:.2f})"), "100%",
        "ok" if F["eps"] >= 0.999 else "warn", 6, "加大压脚压力或牙高。" if F["eps"] < 0.999 else "",
        "Raise the presser-foot pressure or the dog height." if F["eps"] < 0.999 else "")
    chk("feed_back", "feed", "回拖", "Back-drag", f"{F['back']:.2f} mm", "≤ 0.05 mm", "ok" if F["back"] <= 0.05 else "warn", 6,
        "水平与抬牙相位不配，调水平送布相位。" if F["back"] > 0.05 else "", "Horizontal and lift phases mismatch: adjust the horizontal phase." if F["back"] > 0.05 else "")
    chk("feed_ply", "feed", "上下层错位（缝 40 cm）", "Ply shift over 40 cm", f"{F['ply']:.1f} mm", "≤ 3 mm", "ok" if F["ply"] <= 3 else "warn", 6,
        "滑料用针送布或综合送布。" if F["ply"] > 3 else "", "Use needle feed or compound feed for slippery fabric." if F["ply"] > 3 else "")
    chk("feed_marks", "feed", "牙痕与压痕", "Dog and foot marks", ("有", "yes") if F["marks"] else ("无", "none"), ("无", "none"), "warn" if F["marks"] else "ok", 6,
        "降低牙高或压脚压力。" if F["marks"] else "", "Lower the dog or the foot pressure." if F["marks"] else "")
    chk("tension_bal", "tension", "交织点位置（0.5 = 布中间）", "Interlock position (0.5 = mid-fabric)", f"{E['z']:.2f}", "0.40–0.60",
        "ok" if E["bal"] else "warn", 7, "面线、底线张力比例不对。" if not E["bal"] else "", "Upper/bobbin tension ratio is wrong." if not E["bal"] else "")
    chk("tension_sf", "tension", "缝线强度安全系数", "Thread strength safety factor", f"{E['sf']:.2f}", "≥ 1.5", "ok" if not E["brk"] else "bad", 7,
        "峰值张力太大会断线：降夹线器张力或换粗一号线。" if E["brk"] else "", "Peak tension too high: lower the disc tension or use a heavier thread." if E["brk"] else "")
    chk("tension_pucker", "tension", "张力起皱", "Tension pucker", f"{E['pucker']:.2f}%", f"≤ {E['f']['plim']}%", "ok" if not E["pk"] else "bad", 7,
        "两根线张力都偏高，按比例一起降。" if E["pk"] else "", "Both tensions are high; lower them together." if E["pk"] else "")
    chk("tension_loose", "tension", "线迹收紧", "Stitch tightness", (f"较小张力 {min(E['Tn'], p['Tb']):.0f} cN", f"lower tension {min(E['Tn'], p['Tb']):.0f} cN"), f"≥ {E['f']['Tmin']} cN",
        "ok" if not E["loose"] else "warn", 7, "", "")
    chk("tension_jam", "tension", "线与面料匹配", "Thread suits the fabric", THREAD[p["th"]]["name"], ("不粗于面料允许", "not coarser than the fabric allows"), "ok" if not E["jam"] else "bad", 7,
        "换细一号的线和针。" if E["jam"] else "", "Use a finer thread and needle." if E["jam"] else "")
    chk("frame_force", "frame", "整机惯性力（最大合力）", "Machine inertia force (peak)", f"{fmax:.0f} N", "≤ 550 N", "ok" if fmax <= 550 else "warn", 8,
        "调平衡率，或降低最高转速。" if fmax > 550 else "", "Adjust the balance ratio or lower the top speed." if fmax > 550 else "")
    chk("frame_res", "frame", "二阶激振频率 / 机壳固有频率", "2nd-order excitation / frame natural frequency", (f"{r2:.3f}（共振转速 {n_res:.0f} r/min）", f"{r2:.3f} (resonance at {n_res:.0f} r/min)"), "≤ 0.90",
        "ok" if r2 <= 0.9 else "bad", 23, "离共振太近：机壳加筋提高固有频率，或降低最高转速。" if r2 > 0.9 else "",
        "Too close to resonance: stiffen the frame to raise its natural frequency, or lower the top speed." if r2 > 0.9 else "")
    chk("chain", "manuf", "梭尖间隙合格率（装配调整后）", "Hook-clearance yield (after adjustment)", (f"{CH['y_adj'] * 100:.2f}%（互换装配 {CH['y_int'] * 100:.1f}%）", f"{CH['y_adj'] * 100:.2f}% (interchangeable: {CH['y_int'] * 100:.1f}%)"), "≥ 99%",
        "ok" if CH["y_adj"] >= 0.99 else "bad", 23, "", "")

    # ---- 曲线：每 2° 一个点 ----
    ang = list(range(0, 360, 2))
    curves = dict(
        phi=ang,
        needle_x=[round(M.xN(f), 3) for f in ang],
        needle_tip=[round(M.tip(f), 3) for f in ang],
        needle_v=[round(M.vel(f, n), 3) for f in ang],
        needle_a=[round(M.acc(f, n), 1) for f in ang],
        takeup_S=[round(TK["S"][f], 2) for f in ang] if TK["ok"] else [],
        takeup_D=[round(TK["D"][f], 2) for f in ang] if TK["ok"] else [],
        feed_x=[round(F["X"](f), 3) for f in ang],
        feed_y=[round(F["Y"](f), 3) for f in ang],
        force=[round(fmag[f], 1) for f in ang],
    )
    # ---- 时序条（主轴转角区间，度） ----
    timing = [
        dict(key="needle_in", zh="针尖在布中", en="Needle point in fabric", a=round(pin, 1), b=round(pout, 1)),
        dict(key="eye_in", zh="针眼在布中", en="Needle eye in fabric", a=round(ein, 1), b=round(360 - ein, 1)),
        dict(key="catch", zh="钩线窗口（回升 1.6–2.5 mm）", en="Catch window (rise 1.6–2.5 mm)", a=round(w16 or 0, 1), b=round(w25 or 0, 1),
             mark=round(G["fc"], 1)),
        dict(key="dog_up", zh="送布牙在针板上", en="Feed dog above the plate", a=round(F["rise"], 1), b=round(F["drop"], 1)),
        dict(key="takeup_top", zh="挑线杆最高点", en="Take-up lever top", a=TK.get("top", 0), b=TK.get("top", 0)),
    ]
    T = M.trial(_cfg(p), 30, 7) if trial else None
    out = dict(
        version=VERSION, params=p,
        key=dict(lam=lam, stroke=2 * p["r"], omega=w, vmax=vmax, vmax_at=fv, a_tdc=aT, a_bdc=aB, F_bdc=F_bdc, F_tdc=F_tdc, n_max_F=n_max_F,
                 phc0=M.PHC0, fc=G["fc"], rise_fc=G["h"], D=G["D"], g=G["g"], hook_speed=hook_speed, pin=pin, pout=pout, ein=ein,
                 takeup_Smax=TK.get("Smax"), takeup_acc=TK.get("acc"), takeup_margin=TK.get("margin"),
                 feed_S=F["S"], feed_eff=M.EFF0, fe=M.FE, fmax=fmax, r2=r2, vib=v_mm, noise=noise, n_res=n_res,
                 tension_z=E["z"], tension_peak=E["peak"], cw=0.06 + p["k"] * p["mr"]),
        checks=checks,
        ok=not any(c["state"] == "bad" for c in checks),
        curves=curves, timing=timing, chain=CH,
        parts=parts(p, M, F),
    )
    if T:
        out["trial"] = dict(res=T["res"], counts={k: T["res"].count(k) for k in ("ok", "skip", "hit", "cut", "break")},
                            faults=T["ev"]["faults"])
    return out


def _cfg(p):
    """设计参数 → 虚拟样机（教材实验 8-2 / 三维样机）的调机参数"""
    keys = ("psi", "dz", "g", "d", "u", "stroke", "fab", "th", "Td", "Tb", "dT", "dP", "h", "P", "s", "n", "k", "mode")
    return {k: p[k] for k in keys}


def proto_cfg(params):
    return _cfg(clean(params))


def parts(p, M=None, F=None):
    """五个机构的关键零件尺寸（零件参数表；三维模型 cad.py 照此生成）"""
    M = M or mech_of(p)
    F = F or M.feed_model(fab=p["fab"], mode=p["mode"], s=p["s"], dT=p["dT"], dP=p["dP"], h=p["h"], P=p["P"])
    cw_mass = 0.06 + p["k"] * p["mr"]
    return [
        dict(key="crank", zh="针杆曲柄", en="Needle-bar crank", dims=[("曲柄半径 r", "Crank radius r", p["r"], "mm"),
                                                                     ("平衡块质量（在曲柄半径处）", "Counterweight (at crank radius)", round(cw_mass * 1000), "g")]),
        dict(key="rod", zh="针杆连杆", en="Connecting rod", dims=[("中心距 l", "Centre distance l", p["l"], "mm")]),
        dict(key="needlebar", zh="针杆", en="Needle bar", dims=[("行程 2r", "Stroke 2r", round(2 * p["r"], 2), "mm"),
                                                                 ("组件质量", "Assembly mass", round(p["mr"] * 1000), "g")]),
        dict(key="takeup", zh="挑线杆与摇杆", en="Take-up lever and rocker", dims=[
            ("挑线曲柄半径", "Crank radius", p["lk_r"], "mm"), ("挑线杆 P–M", "Lever P–M", p["lk_a"], "mm"),
            ("挑线杆 P–线眼", "Lever P–eye", p["lk_c"], "mm"), ("线眼偏角", "Eye offset angle", p["lk_al"], "°"),
            ("摇杆 M–Q", "Rocker M–Q", p["lk_b"], "mm"), ("摇杆支点 Q（z, y）", "Rocker pivot Q (z, y)", f"{LK0['Qz']}, {LK0['Qy']}", "mm")]),
        dict(key="hook", zh="旋梭与下轴", en="Rotary hook and lower shaft", dims=[
            ("梭尖回转半径", "Hook-point radius", 13.5, "mm"), ("下轴与主轴传动比", "Lower/upper shaft ratio", "2 : 1", ""),
            ("钩线角（主轴）", "Catch angle (main shaft)", round(M.PHC0 + p["psi"] / 2, 2), "°"),
            ("梭尖间隙", "Hook clearance", p["g"], "mm")]),
        dict(key="feed", zh="送布偏心轮与送布牙", en="Feed eccentrics and feed dog", dims=[
            ("抬牙偏心距", "Lift eccentricity", FEED_A, "mm"), ("送布偏心距（针距 {:.1f} mm）".format(p["s"]), "Feed eccentricity (stitch {:.1f} mm)".format(p["s"]),
                                                              round(F["S"] / 2, 3), "mm"),
            ("牙高出针板", "Dog height above plate", p["h"], "mm"), ("送布效率", "Feed efficiency", round(M.EFF0, 3), "")]),
    ]


def adjust_card(params=None):
    """调机卡：装配后按这个顺序调，每步给目标值（第 5、6、7 讲的调机方法）"""
    p = clean(params)
    M = mech_of(p)
    G = M.hook_geom(psi=p["psi"], dz=p["dz"], g=p["g"], d=p["d"])
    F = M.feed_model(fab=p["fab"], mode=p["mode"], s=p["s"], dT=p["dT"], dP=p["dP"], h=p["h"], P=p["P"])
    E = M.tension(fab=p["fab"], th=p["th"], Td=p["Td"], Tb=p["Tb"], s=p["s"], n=p["n"])
    return [
        dict(zh="针杆高度", en="Needle-bar height",
             do_zh=f"转到钩线角 {G['fc']:.1f}°（针杆从下止点回升 {G['h']:.2f} mm），梭尖应在针眼上沿上方 {G['D']:.2f} mm。",
             do_en=f"Turn to the catch angle {G['fc']:.1f}° (needle risen {G['h']:.2f} mm from BDC); the hook point should be {G['D']:.2f} mm above the top of the eye."),
        dict(zh="旋梭定时", en="Hook timing",
             do_zh=f"同一位置梭尖对准机针中心线；主轴 {G['fc']:.1f}° 时钩线。", do_en=f"At the same position the hook point meets the needle centre line; catch at {G['fc']:.1f}°."),
        dict(zh="梭尖间隙", en="Hook clearance",
             do_zh=f"梭尖到机针凹口 {G['g']:.2f} mm（Nm {round(p['d'] * 100)} 针）。换针号后重调。",
             do_en=f"Hook point to needle scarf {G['g']:.2f} mm (Nm {round(p['d'] * 100)} needle). Reset after changing the needle size."),
        dict(zh="送布牙高度", en="Feed-dog height", do_zh=f"牙在最高点时高出针板 {p['h']:.2f} mm。", do_en=f"At its highest the dog stands {p['h']:.2f} mm above the plate."),
        dict(zh="送布定时", en="Feed timing",
             do_zh=f"送布牙在主轴 {F['drop']:.1f}° 落到针板以下；这时针眼上沿距针板 {F['eyeAtDrop']:+.2f} mm（不小于 0：针眼入布时布已停）。",
             do_en=f"The dog drops below the plate at {F['drop']:.1f}°; the top of the eye is then {F['eyeAtDrop']:+.2f} mm from the plate (not below 0: the fabric has stopped when the eye enters)."),
        dict(zh="挑线簧", en="Check spring", do_zh=f"行程 {p['stroke']:.1f} mm。", do_en=f"Stroke {p['stroke']:.1f} mm."),
        dict(zh="张力", en="Tension",
             do_zh=f"底线 {p['Tb']:.0f} cN（提梭壳慢慢下滑），夹线器 {p['Td']:.0f} cN；试缝看交织点在布中间（计算值 {E['z']:.2f}）。",
             do_en=f"Bobbin {p['Tb']:.0f} cN (the case slides down slowly), disc {p['Td']:.0f} cN; sew a test seam and check the interlock sits mid-fabric (computed {E['z']:.2f})."),
    ]
