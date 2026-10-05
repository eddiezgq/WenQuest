"""《数字集成电路设计》全书的手算模型：长沟道平方律 MOSFET 与 CMOS 反相器（参数按 SKY130 tt、27 °C 校准）。

书中程序 `from mos import *` 使用；与浏览器实验的 JS 模型（labs/micro/kit/models/mos.js）共用同一份参数
labs/micro/kit/models/params.json，算法一一对应，构建时比对（第 17 轮 RM2）。
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # 仓库根目录（textbook/dic/conventions/ 向上三级）
P = json.loads((ROOT / "labs/micro/kit/models/params.json").read_text(encoding="utf-8"))
VDD, VTn, VTp, kn, kp = P["VDD"], P["VTn"], P["VTp"], P["kn"], P["kp"]
L, Wmin, Cg, Cd = P["L"], P["Wmin"], P["Cg"], P["Cd"]


def idn(vgs, vds, W, L=L, vdd=None):
    """NMOS 漏极电流（A），长沟道平方律，忽略沟道长度调制。"""
    vov = vgs - VTn
    if vov <= 0 or vds <= 0:
        return 0.0
    k = kn * W / L
    return k * (vov * vds - vds * vds / 2) if vds < vov else k / 2 * vov * vov


def idp(vsg, vsd, W, L=L):
    vov = vsg - VTp
    if vov <= 0 or vsd <= 0:
        return 0.0
    k = kp * W / L
    return k * (vov * vsd - vsd * vsd / 2) if vsd < vov else k / 2 * vov * vov


def vout(vin, Wn, Wp, vdd=VDD):
    """反相器输出电压：二分法解 In = Ip，固定 60 次，与 JS 一致。"""
    lo, hi = 0.0, vdd
    for _ in range(60):
        mid = (lo + hi) / 2
        f = idn(vin, mid, Wn) - idp(vdd - vin, vdd - mid, Wp)
        if f > 0:      # 下拉更强，输出应更低
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def vm(Wn, Wp, vdd=VDD):
    r = math.sqrt(kp * Wp / (kn * Wn))
    return (VTn + r * (vdd - VTp)) / (1 + r)


def noise_margins(Wn, Wp, vdd=VDD, step=0.0005):
    """在 0..VDD 网格上找斜率 = -1 的两点（中心差分），与 JS 一致。"""
    n = int(round(vdd / step))
    vs = [i * step for i in range(n + 1)]
    vo = [vout(v, Wn, Wp, vdd) for v in vs]
    g = [(vo[i + 1] - vo[i - 1]) / (2 * step) for i in range(1, n)]
    idx = [i + 1 for i, s in enumerate(g) if s < -1]
    vil, vih = vs[idx[0]], vs[idx[-1]]
    voh, vol = vout(vil, Wn, Wp, vdd), vout(vih, Wn, Wp, vdd)
    return dict(VIL=vil, VIH=vih, VOH=voh, VOL=vol, NML=vil - vol, NMH=voh - vih)


def idsat_n(W, vdd=VDD):
    return kn / 2 * W / L * (vdd - VTn) ** 2


def idsat_p(W, vdd=VDD):
    return kp / 2 * W / L * (vdd - VTp) ** 2


def req_n(W, vdd=VDD):
    return 0.75 * vdd / idsat_n(W, vdd)


def req_p(W, vdd=VDD):
    return 0.75 * vdd / idsat_p(W, vdd)


def delays(Wn, Wp, CL, vdd=VDD):
    """tPHL、tPLH（s）：0.69·Req·(自载 + CL)。"""
    Cself = (Wn + Wp) * Cd
    return 0.69 * req_n(Wn, vdd) * (Cself + CL), 0.69 * req_p(Wp, vdd) * (Cself + CL)


def cin(Wn, Wp):
    return (Wn + Wp) * Cg


def fo4(Wn, Wp, vdd=VDD):
    return delays(Wn, Wp, 4 * cin(Wn, Wp), vdd)


def chain_delay(N, CL, ratio, vdd=VDD):
    """N 级等比反相器链，第一级为最小对称反相器，返回总延时（s）。"""
    Wn, Wp = Wmin, ratio * Wmin
    C1 = cin(Wn, Wp)
    F = CL / C1
    f = F ** (1 / N)
    R = (req_n(Wn, vdd) + req_p(Wp, vdd)) / 2
    gamma = Cd / Cg
    return N * 0.69 * R * C1 * (gamma + f)


def wn_for_vol(I, VOLmax, vdd=VDD):
    """线性区：吸收电流 I 时输出低电平不超过 VOLmax 所需的 Wn（μm）。"""
    return I / (kn / L * ((vdd - VTn) * VOLmax - VOLmax ** 2 / 2))


def dyn_power(N, alpha, C, V, f):
    return alpha * C * V * V * f * N


def fopt(gamma):
    """Optimum fan-out per stage: f (ln f − 1) = γ, by bisection on [e, 10]."""
    lo, hi = math.e, 10.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if mid * (math.log(mid) - 1) < gamma:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def fo4_tp(ratio, vdd=VDD):
    a, b = fo4(Wmin, ratio * Wmin, vdd)
    return (a + b) / 2


def vdd_for_fo4(limit, ratio, lo=0.9, hi=VDD):
    """Lowest supply whose FO4 delay (average of the two edges) is at most `limit`."""
    for _ in range(80):
        mid = (lo + hi) / 2
        if fo4_tp(ratio, mid) > limit:
            lo = mid
        else:
            hi = mid
    return hi


# ======================================================================= 第 2 章：门与逻辑努力
# 参考反相器：Wn = Wmin、Wp = r·Wmin（两管等强）。门按“等效反相器”定尺寸，最坏情况下的上拉、下拉与参考反相器一样强。

def r_ratio():
    return kn / kp


def tau():
    """逻辑努力的时间单位 τ = 0.69·R·Cinv（s）：R 为参考反相器的等效电阻（两管相等），Cinv 为它的输入电容。
    第 1 章反相器链每级延时 0.69RC1(γ + f) = τ(γ + f)，所以以 τ 为单位，反相器的寄生延时 p_inv = γ。"""
    r = r_ratio()
    R = (req_n(Wmin) + req_p(r * Wmin)) / 2
    return 0.69 * R * cin(Wmin, r * Wmin)


def gamma_self():
    return Cd / Cg


def le_g(kind, n):
    """手算模型的逻辑努力：n 输入与非门 (n + r)/(1 + r)，或非门 (1 + n·r)/(1 + r)，反相器 1。"""
    r = r_ratio()
    if kind == "inv":
        return 1.0
    if kind == "nand":
        return (n + r) / (1 + r)
    if kind == "nor":
        return (1 + n * r) / (1 + r)
    raise ValueError(kind)


def le_p(kind, n):
    """手算模型的寄生延时（以 τ 为单位）：输出节点上的漏极宽度是参考反相器的 n 倍，p = n·γ（反相器 γ）。"""
    return (1 if kind == "inv" else n) * gamma_self()


def gate_widths(kind, n):
    """等效反相器尺寸（μm）：返回 (每个 NMOS 宽, 每个 PMOS 宽)。"""
    r = r_ratio()
    if kind == "inv":
        return Wmin, r * Wmin
    if kind == "nand":
        return n * Wmin, r * Wmin
    if kind == "nor":
        return Wmin, n * r * Wmin
    raise ValueError(kind)


def path_delay(gs, ps, B, H, N=None):
    """路径的最小延时（以 τ 为单位）：D = N·F^(1/N) + ΣP，F = G·B·H。gs、ps 为各级的 g、p 列表。"""
    G = 1.0
    for g in gs:
        G *= g
    N = N or len(gs)
    F = G * B * H
    return N * F ** (1 / N) + sum(ps), F


def stage_sizes(gs, bs, Cin, Cout):
    """按每级努力相等，从输出往回求各级输入电容：Cin_i = g_i·b_i·Cout_i / f。返回 [Cin_1, …, Cin_N]，Cin_1 = Cin。"""
    G, B = 1.0, 1.0
    for g, b in zip(gs, bs):
        G *= g
        B *= b
    N = len(gs)
    f = (G * B * Cout / Cin) ** (1 / N)
    caps, c = [], Cout
    for g, b in reversed(list(zip(gs, bs))):
        c = g * b * c / f
        caps.append(c)
    return list(reversed(caps)), f


# ======================================================================= 第 4 章：导线
WIRES = P["wires"]["layers"]


def wire_r(layer, w):
    """每微米电阻（Ω/μm）：方块电阻 / 线宽。"""
    return WIRES[layer]["Rsq"] / w


def wire_c(layer, w, s=None):
    """每微米电容（F/μm）：对衬底的面积电容 + 两条边的边缘电容；给出间距 s 时再加两侧同层导线的耦合电容（邻线视为交流地）。"""
    q = WIRES[layer]
    c = q["Carea"] * w + 2 * q["Cfringe"]
    if s is not None:
        c += 2 * q["Kside"] / (s + q["s0"])
    return c * 1e-18


def wire_cc(layer, s):
    """同层相邻两条导线之间每微米的耦合电容（F/μm）。"""
    q = WIRES[layer]
    return q["Kside"] / (s + q["s0"]) * 1e-18


def wire_delay(Rd, Cself, Rw, Cw, CL):
    """驱动器（电阻 Rd、自身漏极电容 Cself）经分布式 RC 线（总电阻 Rw、总电容 Cw）驱动 CL 的 50 % 延时（s）：
    0.69·Rd·(Cself + Cw + CL) + 0.38·Rw·Cw + 0.69·Rw·CL。"""
    return 0.69 * Rd * (Cself + Cw + CL) + 0.38 * Rw * Cw + 0.69 * Rw * CL


def repeater_delay(Lw, layer, w, k, size, CL=None, s=None):
    """长度 Lw（μm）的导线分成 k 段，每段前放一个 size 倍参考反相器的中继器，最后驱动 CL（默认一个同样的中继器的输入）。返回总延时（s）。"""
    r = r_ratio()
    R0 = (req_n(Wmin) + req_p(r * Wmin)) / 2
    C0 = cin(Wmin, r * Wmin)
    Rd, Cself, Cin_rep = R0 / size, gamma_self() * C0 * size, C0 * size
    seg = Lw / k
    Rw, Cw = wire_r(layer, w) * seg, wire_c(layer, w, s) * seg
    CL = Cin_rep if CL is None else CL
    t = 0.0
    for i in range(k):
        load = Cin_rep if i < k - 1 else CL
        t += wire_delay(Rd, Cself, Rw, Cw, load)
    return t


def repeater_opt(Lw, layer, w, s=None):
    """中继器的最优段数与尺寸（闭式解，连续变量）：k = Lw·√(0.38·r·c / (0.69·R0·C0·(1 + γ)))，size = √(R0·c / (r·C0))。"""
    rr = r_ratio()
    R0 = (req_n(Wmin) + req_p(rr * Wmin)) / 2
    C0 = cin(Wmin, rr * Wmin)
    rw, cw = wire_r(layer, w), wire_c(layer, w, s)
    k = Lw * math.sqrt(0.38 * rw * cw / (0.69 * R0 * C0 * (1 + gamma_self())))
    size = math.sqrt(R0 * cw / (rw * C0))
    return k, size


def reference():
    r = kn / kp
    pr = P["problems"]
    out = {"r": r,
           "idsat_n_per_um": idsat_n(1.0), "idsat_p_per_um": idsat_p(1.0)}
    # 1.1
    p = pr["p11"]
    w = wn_for_vol(p["Iload"], p["VOLmax"])
    out["p11"] = {"Wn": w, "WnL": w / L, "Ron": p["VOLmax"] / p["Iload"]}
    # 1.2
    out["p12"] = {}
    for key, ratio in (("ratio1", 1.0), ("ratio_r", r)):
        nm = noise_margins(Wmin, ratio * Wmin)
        nm["VM"] = vm(Wmin, ratio * Wmin)
        out["p12"][key] = nm
    # 1.3
    out["p13"] = {}
    for key, ratio in (("ratio1", 1.0), ("ratio_sqrt", math.sqrt(r)), ("ratio_r", r)):
        a, b = fo4(Wmin, ratio * Wmin)
        out["p13"][key] = {"ratio": ratio, "tphl": a, "tplh": b, "tp": (a + b) / 2,
                           "mismatch": (b - a) / ((a + b) / 2)}
    # 1.4
    CL = pr["p14"]["CL"]
    C1 = cin(Wmin, r * Wmin)
    t = {str(N): chain_delay(N, CL, r) for N in range(1, 11)}
    nbest = min(range(1, 11), key=lambda N: t[str(N)])
    nfew = next((N for N in range(1, 11) if t[str(N)] < pr["p14"]["tmax"]), 0)
    gamma = Cd / Cg
    out["p14"] = {"Cin": C1, "F": CL / C1, "Nopt4": math.log(CL / C1) / math.log(4), "t": t,
                  "gamma": gamma, "fopt": fopt(gamma), "Nbest": nbest, "Nfew": nfew}
    # 1.5
    q = pr["p15"]
    out["p15"] = {"P_VDD": dyn_power(q["N"], q["alpha"], q["Cgate"], VDD, q["f"]),
                  "P_low": dyn_power(q["N"], q["alpha"], q["Cgate"], q["Vlow"], q["f"]),
                  "Vlim": vdd_for_fo4(q["fo4max"], r), "fo4_low": fo4_tp(r, q["Vlow"])}
    out["r_lab"] = round(r * 20) / 20          # the symmetric ratio on the lab's 0.05-step slider
    # 第 2 章
    q23 = pr["p23"]
    gn = le_g("nand", q23["n_addr"])
    H23 = q23["Cout_units"] / q23["Cin_units"]
    out["ch2"] = {"tau": tau(), "g": {}, "p": {}, "dec": {}}
    for k, n in (("nand", 2), ("nand", 3), ("nor", 2), ("nor", 3)):
        out["ch2"]["g"][f"{k}{n}"] = le_g(k, n)
        out["ch2"]["p"][f"{k}{n}"] = le_p(k, n)
    for N in (2, 3, 4):
        gs = [gn] + [1.0] * (N - 1)
        ps = [le_p("nand", q23["n_addr"])] + [le_p("inv", 1)] * (N - 1)
        out["ch2"]["dec"][str(N)] = path_delay(gs, ps, q23["branch"], H23)[0]
    # 第 4 章
    out["ch4"] = {"r": {}, "c": {}, "cn": {}, "rep": {}}
    for l, q in WIRES.items():
        out["ch4"]["r"][l] = wire_r(l, q["wmin"])
        out["ch4"]["c"][l] = wire_c(l, q["wmin"])
        out["ch4"]["cn"][l] = wire_c(l, q["wmin"], q["smin"])
    q43 = pr["p43"]
    CL43 = q43["load_units"] * cin(Wmin, r * Wmin)
    for k in range(1, 6):
        out["ch4"]["rep"][str(k)] = repeater_delay(q43["L_um"], q43["layer"], q43["w_um"], k, 20, CL43)
    k_opt, s_opt = repeater_opt(q43["L_um"], q43["layer"], q43["w_um"])
    out["ch4"]["opt"] = {"k": k_opt, "size": s_opt}
    return out
