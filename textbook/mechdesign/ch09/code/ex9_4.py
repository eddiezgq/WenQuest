"""9.4 刚度设计：零件、连接、系统刚度。

算例 9.4.1  UR5e 水平伸直，末端负载 0、2.5、5 kg（连杆长度和质量取零件库 MJCF）。末端下垂由六环串联叠加：
            底座关节 J1 轴承的倾斜、肩关节 J2 和肘关节 J3 的谐波减速器扭转（CSF-25-100，零件库 K1–K3，三段折线）、肩关节输出轴 RJ-201 的扭转
            （第 33 章）、上臂管和小臂管
            的弯曲（6061-T6，Ø85×2.5、Ø75×2，本书设定）。求各环的贡献和末端在负载变化时的当量刚度；
算例 9.4.2  改哪一环最有效：J2 换 CSF-32-100、两根管壁厚加倍、J1 轴承刚度加倍，各自能把 5 kg 时的下垂减少多少；
            改管子或减速器时，自重的变化一并计入（_ch9.arm_sag）；谐波减速器的扭转刚度曲线（三段折线）；
图 9.4.1。
"""
import numpy as np

import _ch9 as H
from bookout import T, figure, out, style

loads = [0.0, 2.5, 5.0]
res = {m: H.arm_sag(m) for m in loads}
r0, r5 = res[0.0], res[5.0]
keys = ["j2", "ua", "j3", "tilt", "rj", "fa"]
d_inc = {k: r5["parts"][k] - r0["parts"][k] for k in keys}
inc = r5["total"] - r0["total"]
k_tip = 5.0 * H.G / inc                                     # N/mm：负载从 0 加到 5 kg 时末端的当量刚度
share = {k: r5["parts"][k] / r5["total"] * 100 for k in keys}
share_inc = {k: d_inc[k] / inc * 100 for k in keys}
joints_pct = (r5["parts"]["j2"] + r5["parts"]["j3"] + r5["parts"]["tilt"] + r5["parts"]["rj"]) / r5["total"] * 100
k25 = H.csf("25-100")
# 改进
TU2, TF2 = (H.TUBE_UA[0], 2 * H.TUBE_UA[1]), (H.TUBE_FA[0], 2 * H.TUBE_FA[1])
var = [(T("原设计", "baseline"), r5["total"]),
       (T("J2、J3 换 CSF-32-100", "CSF-32-100 at J2, J3"), H.arm_sag(5.0, size="32-100")["total"]),
       (T("两根管壁厚加倍", "tube walls doubled"), H.arm_sag(5.0, tube_ua=TU2, tube_fa=TF2)["total"]),
       (T("J1 轴承刚度加倍", "J1 bearing stiffness ×2"), H.arm_sag(5.0, k_tilt=2 * H.K_TILT_J1)["total"])]
k32 = H.csf("32-100")
m_tube = (H.A_tube(*TU2) - H.A_tube(*H.TUBE_UA)) * r5["L1"] + (H.A_tube(*TF2) - H.A_tube(*H.TUBE_FA)) * r5["L2"]
m_tube *= 2.7e-6                                             # kg（铝 2.7 g/cm³）
m_red = 2 * (k32["mass"] - k25["mass"])                     # 两个关节的减速器部件质量之差（零件库）

plt = style()
fig, (a0, a1, a2) = plt.subplots(1, 3, figsize=(7.6, 2.9), gridspec_kw={"width_ratios": [1.15, 1.0, 0.9]})
left = np.zeros(len(loads))
for k in keys:
    v = np.array([res[m]["parts"][k] for m in loads])
    a0.barh(range(len(loads)), v, left=left, color=H.PART_COLORS[k], label=H.PART_NAMES[k])
    left += v
for i, m in enumerate(loads):
    a0.text(left[i] + 0.05, i, f"{left[i]:.2f} mm", va="center", fontsize=6.3)
a0.set_yticks(range(len(loads)))
a0.set_yticklabels([T(f"负载 {m:g} kg", f"payload {m:g} kg") for m in loads], fontsize=6.6)
a0.invert_yaxis()
a0.set_xlim(0, left.max() * 1.3)
a0.set_xlabel(T("末端下垂 / mm", "Tip sag / mm"), fontsize=7.0)
a0.legend(fontsize=5.6, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2)
a0.tick_params(labelsize=6.2)
a0.set_title(T("(a) 各环的贡献", "(a) Contribution of each link"), fontsize=7.3)
a1.barh(range(len(var)), [v for _, v in var], color=["#555555", "#d62728", "#1f77b4", "#9467bd"])
for i, (_, v) in enumerate(var):
    a1.text(v + 0.05, i, f"{v:.2f}", va="center", fontsize=6.3)
a1.set_yticks(range(len(var)))
a1.set_yticklabels([n for n, _ in var], fontsize=6.3)
a1.invert_yaxis()
a1.set_xlim(0, var[0][1] * 1.3)
a1.set_xlabel(T("5 kg 时的末端下垂 / mm", "Tip sag at 5 kg / mm"), fontsize=7.0)
a1.tick_params(labelsize=6.2)
a1.set_title(T("(b) 改哪一环", "(b) Which link to improve"), fontsize=7.3)
Tq = np.linspace(0, 110, 300)
for sz, col in (("25-100", "#d62728"), ("32-100", "#1f77b4"), ("17-100", "#2ca02c")):
    k = H.csf(sz)
    tq = Tq[Tq <= k["repeat"]]
    a2.plot(tq, [H.windup(t, k) * 1e3 for t in tq], color=col, lw=1.3, label=f"CSF-{sz}")
a2.axvline(r5["T2"], color=H.MUTED, lw=0.6, ls="--")
a2.text(r5["T2"] - 2, 0.3, T("J2，5 kg", "J2, 5 kg"), fontsize=6.0, color=H.MUTED, ha="right")
a2.set_xlabel(T("转矩 / N·m", "Torque / N·m"), fontsize=7.0)
a2.set_ylabel(T("扭转角 / mrad", "Windup / mrad"), fontsize=7.0)
a2.set_ylim(0, 4)
a2.legend(fontsize=5.8, frameon=False, loc="upper left")
a2.tick_params(labelsize=6.2)
a2.set_title(T("(c) 谐波减速器的扭转刚度", "(c) Harmonic-drive windup"), fontsize=7.3)
fig.tight_layout()
figure(fig, "fig9_4_1")

p5 = r5["parts"]
out(L1=r5["L1"], L2=r5["L2"], LW=r5["LW"], x_tip=r5["x_tip"], T2_0=r0["T2"], T2_5=r5["T2"], T3_5=r5["T3"],
    K1=k25["K1"] / 1e4, K2=k25["K2"] / 1e4, K3=k25["K3"] / 1e4, T1=k25["T1"], T2k=k25["T2"], rated=k25["rated"], avg=k25["avg"], repeat=k25["repeat"],
    th2=r5["th2"] * 1e3, th3=r5["th3"] * 1e3, th1=r5["th1"] * 1e3, k_tilt=H.K_TILT_J1 / 1e5,
    s_j2=p5["j2"], s_j3=p5["j3"], s_tilt=p5["tilt"], s_ua=p5["ua"], s_fa=p5["fa"], total5=r5["total"], total0=r0["total"],
    pct_j2=share["j2"], pct_tube=share["ua"] + share["fa"], joints_pct=joints_pct, inc=inc, k_tip=k_tip,
    inc_j2=d_inc["j2"], inc_pct_j2=share_inc["j2"],
    s_rj=p5["rj"], k_rj=H.k_rj201() / 1e5, th_rj=r5["th_rj"] * 1e3, OD25=k25["OD"], OD32=k32["OD"], g_ratio=(1 - var[1][1] / var[0][1]) / (1 - var[2][1] / var[0][1]),
    v32=var[1][1], v_tube=var[2][1], v_tilt=var[3][1], g32=(1 - var[1][1] / var[0][1]) * 100,
    g_tube=(1 - var[2][1] / var[0][1]) * 100, g_tilt=(1 - var[3][1] / var[0][1]) * 100, m_tube=m_tube, m_red=m_red,
    K1_32=k32["K1"] / 1e4, K3_32=k32["K3"] / 1e4)
