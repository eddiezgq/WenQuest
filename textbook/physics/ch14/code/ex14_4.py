"""14.4 节的计算（材料数据取自数字工厂的材料库 factory/digital/cae/materials.py，每条注明了出处）：

算例 14.4.1  绳驱夹爪的钢丝：304 不锈钢丝直径 1.5 mm、长 0.80 m，拉力 200 N。应力、应变、伸长量多大？离屈服还有多远？
算例 14.4.2  力传感器：6061-T6 铝合金的方柱，截面 10 mm × 10 mm，受 500 N 的压力。应力和应变多大？
算例 14.4.3  同样重的拉杆，钢（Q235）和铝（6061-T6）哪个更“硬”？比较 E/ρ。
图 14.4.1   几种材料在弹性范围内的应力—应变直线（画到屈服强度为止）。
"""
import math
import sys
from pathlib import Path

import numpy as np

from bookout import T, figure, out, style
import _draw as d

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "factory" / "digital"))
from cae import materials as MATS  # noqa: E402

ss, al, q235 = MATS.BY_ID["304"], MATS.BY_ID["6061-T6"], MATS.BY_ID["Q235"]

dw, Lw, Fw = 1.5e-3, 0.80, 200.0
A = math.pi * dw ** 2 / 4
sig = Fw / A / 1e6                                                   # MPa
eps = sig / ss["E_mpa"]
out(E_ss=ss["E_mpa"] / 1000, ys_ss=ss["yield_mpa"], A_mm2=A * 1e6, sig_w=sig, eps_w_e4=eps * 1e4, dL_mm=eps * Lw * 1000, n_w=ss["yield_mpa"] / sig)

Ac, Fc = 10e-3 * 10e-3, 500.0
sc = Fc / Ac / 1e6
ec = sc / al["E_mpa"]
out(E_al=al["E_mpa"] / 1000, sig_c=sc, eps_c_ue=ec * 1e6)

out(E_q=q235["E_mpa"] / 1000, rho_q=q235["density"], rho_al=al["density"], spec_q=q235["E_mpa"] / 1000 / q235["density"],
    spec_al=al["E_mpa"] / 1000 / al["density"], ys_q=q235["yield_mpa"], ys_al=al["yield_mpa"])

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 2.9))
for mid, col, nm in (("Q235", d.VR, T("Q235 钢", "Q235 steel")), ("304", d.VB, T("304 不锈钢", "304 stainless")),
                     ("6061-T6", d.VA, T("6061-T6 铝", "6061-T6 aluminium")), ("PA66", d.MUTED, T("PA66 尼龙", "PA66 nylon"))):
    m_ = MATS.BY_ID[mid]
    e_y = m_["yield_mpa"] / m_["E_mpa"]
    e = np.linspace(0, min(e_y, 0.0045), 50)
    ax.plot(e * 1000, m_["E_mpa"] * e, color=col, lw=2, label=nm)
    if e_y <= 0.0045:
        ax.plot(e_y * 1000, m_["yield_mpa"], "o", color=col, ms=4)
ax.set_xlabel(T("应变 ε / ‰", "strain ε / ‰")); ax.set_ylabel(T("应力 σ / MPa", "stress σ / MPa"))
ax.set_xlim(0, 4.5); ax.set_ylim(0, 300); ax.legend(frameon=False, fontsize=8.5, loc="lower right", bbox_to_anchor=(1.0, 0.1))
ax.text(0.15, 280, T("圆点：屈服强度", "dots: yield strength"), fontsize=8, color=d.MUTED)
d.spines(ax)
figure(fig, "fig14_4_1")
