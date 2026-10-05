"""5.5 复合材料：碳纤维/环氧单向板的性能（混合律与 Halpin–Tsai 式），[0/45/−45/90]s 准各向同性层合板的面内刚度（经典层合理论），
各方向的弹性模量（算例 5.5.1，图 5.5.1）；PA66 的吸湿（材料库）。

纤维与树脂的性能是常见的典型值（T700 级碳纤维、通用环氧树脂，厂商数据表的量级），本书设定，待核对。"""
import numpy as np

import _ch5 as H
from bookout import T, figure, out, style

from _cfrp import (E1, E2, E2_inv, EF1, EF2, EM, G12, NU12, QI, RHO, VF, A_matrix, Ex_at)  # noqa: E402

A_qi = A_matrix(QI)
A_ud = A_matrix([0])
phis = np.linspace(0, 360, 361)
E_qi = np.array([Ex_at(A_qi, p) for p in phis])
E_ud = np.array([Ex_at(A_ud, p) for p in phis])
Eqi = float(E_qi[0])
al = H.lib("6061-T6")
st = H.lib("45-QT")
pa = H.lib("PA66")

plt = style()
fig = plt.figure(figsize=(7.2, 3.2))
a0 = fig.add_subplot(1, 2, 1, projection="polar")
a0.plot(np.radians(phis), E_ud, color="#d62728", lw=1.0, label=T("单向板 [0]", "unidirectional [0]"))
a0.plot(np.radians(phis), E_qi, color="#2ca02c", lw=1.4, label=T("准各向同性 [0/±45/90]s", "quasi-isotropic [0/±45/90]s"))
a0.plot(np.radians(phis), np.full(phis.size, al["E"]), color="#1f77b4", lw=0.8, ls="--", label=T("铝合金 6061-T6", "6061-T6 aluminium"))
a0.set_rlim(0, 150)
a0.set_rticks([50, 100, 150])
a0.set_rlabel_position(112)
a0.tick_params(labelsize=6.2)
a0.legend(fontsize=6.2, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=1)
a0.set_title(T("(a) 各方向的弹性模量 / GPa", "(a) Modulus in each direction / GPa"), fontsize=7.8, pad=12)
a1 = fig.add_subplot(1, 2, 2)
items = [(T("钢", "steel"), st["E"] / st["rho"]), (T("铝合金", "Al alloy"), al["E"] / al["rho"]), (T("碳纤维准各向同性", "CFRP quasi-iso"), Eqi / RHO),
         (T("碳纤维单向（纵向）", "CFRP UD (fibre dir.)"), E1 / RHO), (T("碳纤维单向（横向）", "CFRP UD (transverse)"), E2 / RHO)]
a1.barh(range(len(items)), [v for _, v in items], color=["#1f77b4", "#1f77b4", "#2ca02c", "#d62728", "#d62728"])
a1.set_yticks(range(len(items)))
a1.set_yticklabels([n for n, _ in items], fontsize=6.6)
a1.invert_yaxis()
a1.set_xlabel(T("比刚度 E/ρ / (GPa·cm³/g)", "Specific stiffness E/ρ / (GPa·cm³/g)"), fontsize=7.2)
a1.tick_params(labelsize=6.5)
a1.set_title(T("(b) 比刚度", "(b) Specific stiffness"), fontsize=7.8)
fig.tight_layout()
figure(fig, "fig5_5_1")

out(Ef1=EF1, Ef2=EF2, Em=EM, Vf=VF, E1=E1, E2=E2, E2_inv=E2_inv, G12=G12, nu12=NU12, rho=RHO, Eqi=Eqi,
    Eqi_min=float(E_qi.min()), Eqi_max=float(E_qi.max()), Eud45=float(Ex_at(A_ud, 45)), Eud90=float(Ex_at(A_ud, 90)),
    sr_qi=Eqi / RHO, sr_al=al["E"] / al["rho"], sr_st=st["E"] / st["rho"], sr_ud=E1 / RHO,
    pa_dry=pa["E"], pa_wet=pa["E"] * 0.5, pa_note=pa["note"])
