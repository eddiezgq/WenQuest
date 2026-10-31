"""7.5 摩擦力与自锁（算例 7.5.1、7.5.2，图 7.5.1）。
1. 螺旋副：把螺纹展开成斜面。升角 λ = arctan(Ph / (π d₂))，当量摩擦角 φ′ = arctan(μ / cos β)（β 为牙侧角，牙型角的一半）；
   拧紧（举升）效率 η = tan λ / tan(λ + φ′)；λ ≤ φ′ 时自锁。比较 M8 粗牙螺钉（螺距取零件库内六角螺钉的规格表）
   和机器人升降轴常用的 Tr16×4 梯形丝杠（本书设定）。
2. 摩擦夹持：两指夹爪靠摩擦夹住 1 kg 的工件竖直加速提起，需要的夹紧力 F = m(g + a)·S / (2μ)，随指面材料的摩擦系数变化。"""
import csv
import math

import numpy as np

import _ch7 as H
from bookout import T, figure, out, style

with (H.ROOT / "library" / "catalog" / "A" / "A-BLT-HEX" / "specs.csv").open(encoding="utf-8") as f:
    m8 = next(r for r in csv.DictReader(f) if r["size"].startswith("M8"))
d_m8, P_m8 = float(m8["d_mm"]), float(m8["P_mm"])
SCREWS = {
    "m8": {"name": T("M8 粗牙螺钉", "M8 coarse screw"), "d2": d_m8 - 0.6495 * P_m8, "Ph": P_m8, "beta": 30.0, "color": "#1f77b4"},    # ISO 724：d₂ = d − 0.6495P
    "tr": {"name": T("Tr16×4 梯形丝杠", "Tr16×4 trapezoidal screw"), "d2": 16 - 0.5 * 4, "Ph": 4.0, "beta": 15.0, "color": "#d62728"},  # ISO 2904：d₂ = d − 0.5P
}
MU0 = 0.15                                     # 钢对钢、有润滑的常用摩擦系数（本书取值）


def screw(s, mu):
    lam = math.atan(s["Ph"] / (math.pi * s["d2"]))
    phi = math.atan(mu / math.cos(math.radians(s["beta"])))
    return lam, phi, math.tan(lam) / math.tan(lam + phi)


res = {k: screw(s, MU0) for k, s in SCREWS.items()}
mu_lock = {k: math.tan(res[k][0]) * math.cos(math.radians(s["beta"])) for k, s in SCREWS.items()}   # 刚好自锁的摩擦系数
# 2. 夹持
M_P, A_UP, S_G = 1.0, 5.0, 2.0                 # 工件 kg、竖直加速度 m/s²、夹持安全系数（本书设定）
PADS = [(T("铝合金指面", "aluminum pad"), 0.25), (T("聚氨酯指面", "polyurethane pad"), 0.5), (T("橡胶指面", "rubber pad"), 0.8)]
grip = {n: M_P * (H.G + A_UP) * S_G / (2 * mu) for n, mu in PADS}

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.6, 3.0))
mus = np.linspace(0.02, 0.3, 120)
for k, s in SCREWS.items():
    a0.plot(mus, [100 * screw(s, m)[2] for m in mus], color=s["color"], lw=1.3, label=s["name"])
    a0.axvline(mu_lock[k], color=s["color"], lw=0.7, ls=":")
a0.axvline(MU0, color=H.MUTED, lw=0.7, ls="--")
a0.text(MU0 + 0.004, 92, f"μ = {MU0}", fontsize=6.4, color=H.MUTED)
a0.axhline(50, color=H.MUTED, lw=0.5)
a0.text(0.29, 52, T("η = 50%", "η = 50%"), fontsize=6.2, color=H.MUTED, ha="right")
a0.set_xlabel(T("摩擦系数 μ", "Friction coefficient μ"), fontsize=7.2)
a0.set_ylabel(T("举升（拧紧）效率 η / %", "Raising (tightening) efficiency η / %"), fontsize=7.2)
a0.set_ylim(0, 100)
a0.legend(fontsize=6.2, frameon=False, loc="upper right", bbox_to_anchor=(1.0, 0.86))
a0.tick_params(labelsize=6.3)
a0.set_title(T("(a) 螺旋副的效率；点线右边自锁", "(a) Screw efficiency; self-locking right of the dotted lines"), fontsize=7.4)
mg = np.linspace(0.15, 1.0, 100)
a1.plot(mg, M_P * (H.G + A_UP) * S_G / (2 * mg), color="#2ca02c", lw=1.3)
for n, mu in PADS:
    a1.plot(mu, grip[n], "o", color=H.INK, ms=3.5)
    a1.text(mu + 0.02, grip[n] + 2, f"{n}\n{grip[n]:.0f} N", fontsize=6.2)
a1.set_xlabel(T("指面与工件的摩擦系数 μ", "Pad–workpiece friction coefficient μ"), fontsize=7.2)
a1.set_ylabel(T("所需夹紧力 / N", "Required grip force / N"), fontsize=7.2)
a1.tick_params(labelsize=6.3)
a1.set_title(T("(b) 夹爪夹 1 kg、向上加速 5 m/s²", "(b) Gripper holding 1 kg, accelerating up at 5 m/s²"), fontsize=7.4)
fig.tight_layout()
figure(fig, "fig7_5_1")

o = {}
for k, s in SCREWS.items():
    lam, phi, eta = res[k]
    o.update({f"{k}_d2": s["d2"], f"{k}_Ph": s["Ph"], f"{k}_lam": math.degrees(lam), f"{k}_phi": math.degrees(phi), f"{k}_eta": 100 * eta,
              f"{k}_mulock": mu_lock[k], f"{k}_lock": T("自锁", "self-locking") if lam <= phi else T("不自锁", "not self-locking")})
out(mu0=MU0, d_m8=d_m8, P_m8=P_m8, m_p=M_P, a_up=A_UP, S_g=S_G, **o,
    grip_al=grip[PADS[0][0]], grip_pu=grip[PADS[1][0]], grip_rub=grip[PADS[2][0]], mu_al=PADS[0][1], mu_pu=PADS[1][1], mu_rub=PADS[2][1])
