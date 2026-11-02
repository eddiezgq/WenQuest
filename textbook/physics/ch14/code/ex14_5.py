"""14.5 节的计算（材料数据取自数字工厂的材料库 factory/digital/cae/materials.py）：

算例 14.5.1  剪切：由 E 和泊松比 ν 求钢（Q235）和铝（6061-T6）的剪切模量 G = E/(2(1 + ν))。
            一个 M8 螺栓（光杆直径 8 mm）单剪受 5.0 kN 的横向力，切应力多大？8.8 级螺栓屈服强度 640 MPa，
            按切应力屈服约为 σs/√3 估算，安全系数多少？
算例 14.5.2  体积形变：液压油的体积模量取 1.5 GPa，油缸和管路里 2.0 L 的油从 0 加压到 20 MPa，体积缩小多少？
            钢的体积模量 K = E/(3(1 − 2ν)) 是多少？
图 14.5.1    拉伸试验的应力—应变曲线（教学模型，弹性模量、屈服强度、抗拉强度取材料库的值，曲线形状为典型形状）：
            Q235 有明显的屈服平台；6061-T6 没有，用 0.2% 规定塑性延伸强度（Ramberg–Osgood 模型）。
            核对：由模型曲线用 0.2% 偏移法求出的屈服强度等于材料库的值（图 14.5.1）。
            实验 14.5 和动画 14.5.1 用同样的曲线。
"""
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

from bookout import T, figure, out, style
import _draw as d

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "factory" / "digital"))
from cae import materials as MATS  # noqa: E402

q, al = MATS.BY_ID["Q235"], MATS.BY_ID["6061-T6"]
G = lambda m_: m_["E_mpa"] / (2 * (1 + m_["nu"])) / 1000
K = lambda m_: m_["E_mpa"] / (3 * (1 - 2 * m_["nu"])) / 1000
out(G_q=G(q), G_al=G(al), nu_q=q["nu"], nu_al=al["nu"], K_q=K(q))

F, db, sb = 5000.0, 8e-3, 640.0
tau = F / (math.pi * db ** 2 / 4) / 1e6
tau_y = sb / math.sqrt(3)
out(tau=tau, tau_y=tau_y, n_b=tau_y / tau)

Ko, V, p = 1.5e9, 2.0e-3, 20e6
dV = V * p / Ko
out(Ko=Ko / 1e9, dV_cm3=dV * 1e6, dV_pct=p / Ko * 100)


# ---- 应力—应变曲线（工程应力、工程应变）
def curve_q235(e):
    E, sy, su = q["E_mpa"], q["yield_mpa"], q["ultimate_mpa"]
    e_y, e_l, e_u, e_f = 1.04 * sy / E, 0.018, 0.20, 0.30
    if e <= e_y: return E * e
    if e <= e_y + 0.001: return 1.04 * sy - 0.04 * sy * (e - e_y) / 0.001                  # 上屈服点后跌到下屈服点
    if e <= e_l: return sy
    if e <= e_u: u = (e - e_l) / (e_u - e_l); return sy + (su - sy) * (1 - (1 - u) ** 2)
    if e <= e_f: return su - 0.20 * su * ((e - e_u) / (e_f - e_u)) ** 2                      # 颈缩：工程应力下降
    return float("nan")


def ro(m_, e_u):
    """Ramberg–Osgood：ε = σ/E + 0.002(σ/σs)ⁿ，n 由“抗拉强度时的应变 e_u”定。"""
    E, sy, su = m_["E_mpa"], m_["yield_mpa"], m_["ultimate_mpa"]
    n = math.log((e_u - su / E) / 0.002) / math.log(su / sy)
    return n, (lambda s: s / E + 0.002 * (s / sy) ** n)


n_al, eps_al = ro(al, 0.080)


def curve_al(e):
    su, e_u, e_f = al["ultimate_mpa"], 0.080, 0.12
    if e <= e_u: return brentq(lambda s: eps_al(s) - e, 0, su * 1.0000001)
    if e <= e_f: return su - 0.15 * su * ((e - e_u) / (e_f - e_u)) ** 2
    return float("nan")


# 0.2% 偏移法：σ = E(ε − 0.002) 与曲线的交点
def offset_yield(curve, E):
    e = brentq(lambda x: curve(x) - E * (x - 0.002), 0.0021, 0.05)
    return curve(e)


oy_al = offset_yield(curve_al, al["E_mpa"])
assert abs(oy_al - al["yield_mpa"]) < 0.5
out(n_al=n_al, oy_al=oy_al, ys_al=al["yield_mpa"], us_al=al["ultimate_mpa"], ys_q=q["yield_mpa"], us_q=q["ultimate_mpa"],
    E_q=q["E_mpa"] / 1000, E_al=al["E_mpa"] / 1000)

plt = style()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 2.9))
eq = np.linspace(0, 0.30, 1201); ea = np.linspace(0, 0.12, 1201)
a1.plot(eq * 100, [curve_q235(x) for x in eq], color=d.VR, lw=2, label=T("Q235 钢", "Q235 steel"))
a1.plot(ea * 100, [curve_al(x) for x in ea], color=d.VA, lw=2, label=T("6061-T6 铝", "6061-T6 aluminium"))
a1.plot(0.30 * 100, curve_q235(0.30), "x", color=d.VR, ms=7, mew=2); a1.plot(12, curve_al(0.12), "x", color=d.VA, ms=7, mew=2)
a1.set_xlabel(T("应变 ε / %", "strain ε / %")); a1.set_ylabel(T("应力 σ / MPa", "stress σ / MPa")); a1.set_ylim(0, 480)
a1.set_title(T("(a) 拉到断裂（× 为断裂点）", "(a) to fracture (× = break)"), fontsize=9.5); a1.legend(frameon=False, fontsize=8, loc="lower right"); d.spines(a1)
ez = np.linspace(0, 0.008, 400)
a2.plot(ez * 100, [curve_q235(x) for x in ez], color=d.VR, lw=2)
a2.plot(ez * 100, [curve_al(x) for x in ez], color=d.VA, lw=2)
eo = np.linspace(0.002, 0.0065, 50)
a2.plot(eo * 100, al["E_mpa"] * (eo - 0.002), color=d.MUTED, lw=1, ls="--")
a2.plot(brentq(lambda x: curve_al(x) - al["E_mpa"] * (x - 0.002), 0.0021, 0.05) * 100, oy_al, "o", color=d.VA, ms=5)
a2.text(0.47, 60, T("0.2% 偏移线", "0.2% offset line"), fontsize=8, color=d.MUTED)
a2.text(0.45, 245, T("屈服平台", "yield plateau"), fontsize=8, color=d.VR)
a2.set_xlabel(T("应变 ε / %", "strain ε / %")); a2.set_xlim(0, 0.8); a2.set_ylim(0, 320)
a2.set_title(T("(b) 开头放大：屈服", "(b) close-up: yielding"), fontsize=9.5); d.spines(a2)
fig.tight_layout()
figure(fig, "fig14_5_1")
