"""33.5 节：用有限元求阶梯轴的理论应力集中系数（图 33.5.1）。

阶梯圆轴 D/d = 1.2，改变过渡圆角 r/d，在纯弯和纯扭两种工况下各算一次（Gmsh + CalculiX，二阶四面体，圆角处局部
加密）。结果与 [SHI] 的首轮估计值（尖圆角 r/d = 0.02：2.7、2.2；大圆角 r/d = 0.1：1.7、1.5）对照。
"""
import numpy as np

import _draw as D
import _fea
from bookout import T, figure, out, style
import mdstd

d, D_ = 40.0, 48.0
rd = [0.02, 0.04, 0.06, 0.09]          # r 不能超过台阶高 (D − d)/2 = 4 mm
res = [_fea.stepped_bar_kt(d, D_, x * d, fine=4) for x in rd]
fine2 = _fea.stepped_bar_kt(d, D_, rd[1] * d, fine=6)          # 网格收敛：圆角处单元 r/4 → r/6（r/8 的模型超出 8 GB 内存）
conv_s = abs(fine2["alpha_sigma"] - res[1]["alpha_sigma"]) / res[1]["alpha_sigma"] * 100
conv_t = abs(fine2["alpha_tau"] - res[1]["alpha_tau"]) / res[1]["alpha_tau"] * 100
a_s = [r["alpha_sigma"] for r in res]
a_t = [r["alpha_tau"] for r in res]
sharp, round_ = mdstd.kt_estimate("shoulder_sharp"), mdstd.kt_estimate("shoulder_round")

plt = style()
fig, ax = plt.subplots(figsize=(6.2, 3.6))
ax.plot(rd, a_s, "o-", color=D.MOMENT, lw=1.6, label=T("弯曲 α_σ（有限元）", "bending α_σ (FEA)"))
ax.plot(rd, a_t, "s-", color=D.TORQUE, lw=1.6, label=T("扭转 α_τ（有限元）", "torsion α_τ (FEA)"))
ax.plot([0.02, 0.1], [sharp["Kt"], round_["Kt"]], "o", mfc="none", mec=D.MOMENT, ms=9, mew=1.4,
        label=T("[SHI] 首轮估计：弯曲", "[SHI] first estimate: bending"))
ax.plot([0.02, 0.1], [sharp["Kts"], round_["Kts"]], "s", mfc="none", mec=D.TORQUE, ms=9, mew=1.4,
        label=T("[SHI] 首轮估计：扭转", "[SHI] first estimate: torsion"))
ax.set_xlabel("r / d")
ax.set_ylabel(T("理论应力集中系数", "theoretical stress-concentration factor"))
ax.set_ylim(1.0, 3.0)
ax.legend(fontsize=8.5, frameon=False)
ax.set_title(T("阶梯轴 D/d = 1.2", "stepped shaft D/d = 1.2"), fontsize=10)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig33_5_1")

out(**{f"as_{i}": v for i, v in enumerate(a_s)}, **{f"at_{i}": v for i, v in enumerate(a_t)},
    rd0=rd[0], rd1=rd[1], rd2=rd[2], rd3=rd[3], n_el=max(r["n_elements"] for r in res),
    conv_s=conv_s, conv_t=conv_t, n_el_fine=fine2["n_elements"], kt_sharp=sharp["Kt"], kts_sharp=sharp["Kts"], kt_round=round_["Kt"], kts_round=round_["Kts"])
