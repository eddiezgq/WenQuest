"""7.1 受力图与平衡方程：UR5e 的上臂、小臂、腕部在一条直线上，末端持 5 kg 负载。取“肩关节以外的整条手臂”为隔离体，
由平衡方程求肩关节（shoulder_lift）的约束反力和反力矩；取“肘关节以外”为隔离体求肘关节的力矩。随肩关节角 θ（手臂与水平面的夹角）变化，
与模型给出的关节力矩限值比较（算例 7.1.1、7.1.2，图 7.1.1）。
连杆的长度、质量、质心取零件库 UR5e 的 MuJoCo 模型；腕部三个连杆的质量按集中在小臂末端算，负载在小臂末端外 L_w 处（本书的简化）。"""
import numpy as np

import _ch7 as H
from bookout import T, figure, out, style

G = 9.81
P = 5.0                                   # 负载 kg（UR5e 的额定负载）
U = H.ur5e()
L1, L2, LW = U["L_ua"], U["L_fa"], U["L_w"]
items = [(T("上臂", "upper arm"), U["m_ua"], U["c_ua"]), (T("小臂", "forearm"), U["m_fa"], L1 + U["c_fa"]),
         (T("腕部", "wrist"), U["m_w"], L1 + L2), (T("负载", "payload"), P, L1 + L2 + LW)]
W = sum(m for _, m, _ in items) * G                         # 隔离体的总重力 N
M_sh = sum(m * G * x for _, m, x in items)                  # θ = 0（水平）时对肩关节的重力矩
M_el = sum(m * G * (x - L1) for _, m, x in items[1:])       # 肘关节以外
x_c = M_sh / W                                              # 合重力的作用线到肩关节的距离
share = {n: 100 * m * G * x / M_sh for n, m, x in items}
th = np.linspace(-90, 90, 181)          # 手臂伸直、绕肩关节整体转动
tau_sh = M_sh * np.cos(np.radians(th))
P_max = (U["tau_big"] - sum(m * G * x for _, m, x in items[:3])) / (G * (L1 + L2 + LW))   # 水平时肩关节允许的最大负载

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.6, 3.1), gridspec_kw={"width_ratios": [1.35, 1.0]})
# (a) 受力图
a0.plot([0, L1 + L2 + LW], [0, 0], color=H.INK, lw=4, solid_capstyle="round")
for x in (0, L1, L1 + L2):
    a0.plot(x, 0, "o", ms=7, mfc="white", mec=H.INK, mew=1.2)
for n, m, x in items:
    f = m * G
    a0.annotate("", xy=(x, -0.03 - 0.04 - f / 1200), xytext=(x, -0.03), arrowprops=dict(arrowstyle="-|>", color="#d62728", lw=1.1))
    a0.text(x, -0.08 - f / 1200, f"{n}\n{f:.0f} N", ha="center", va="top", fontsize=6.2, color="#d62728")
a0.annotate("", xy=(0, 0.03 + 0.04 + W / 1200), xytext=(0, 0.03), arrowprops=dict(arrowstyle="-|>", color="#1f77b4", lw=1.2))
a0.text(0.02, 0.08 + W / 1200, T(f"F = {W:.0f} N", f"F = {W:.0f} N"), fontsize=6.6, color="#1f77b4", va="top")
a0.add_patch(__import__("matplotlib.patches", fromlist=["Arc"]).Arc((0, 0), 0.16, 0.16, theta1=200, theta2=340, color="#1f77b4", lw=1.1))
a0.text(-0.02, -0.1, T(f"M = {M_sh:.0f} N·m", f"M = {M_sh:.0f} N·m"), ha="right", va="top", fontsize=6.6, color="#1f77b4")
a0.text(-0.03, 0.03, T("肩", "shoulder"), ha="right", fontsize=6.4)
a0.text(L1, 0.03, T("肘", "elbow"), ha="center", fontsize=6.4)
a0.set_xlim(-0.15, 1.05)
a0.set_ylim(-0.36, 0.3)
a0.set_aspect("equal")
a0.axis("off")
a0.set_title(T("(a) 肩关节以外的手臂（水平）的受力图", "(a) Free-body diagram of the arm outboard of the shoulder (horizontal)"), fontsize=7.6)
# (b) 肩关节力矩随角度
a1.plot(th, tau_sh, color="#1f77b4", lw=1.3, label=T("肩关节的重力矩", "gravity torque at shoulder"))
a1.axhline(U["tau_big"], color="#d62728", lw=0.8, ls="--", label=T("模型的关节力矩限值", "joint torque limit (model)"))
a1.plot(th, M_el * np.cos(np.radians(th)), color="#2ca02c", lw=1.3, label=T("肘关节的重力矩", "gravity torque at elbow"))
a1.set_ylim(0, U["tau_big"] * 1.15)
a1.set_xlabel(T("手臂与水平面的夹角 θ / (°)", "Arm angle above horizontal θ / °"), fontsize=7.4)
a1.set_ylabel(T("力矩 / N·m", "Torque / N·m"), fontsize=7.4)
a1.legend(fontsize=6.2, frameon=False, loc="upper right")
a1.tick_params(labelsize=6.5)
a1.set_title(T("(b) 关节的重力矩 M(θ) = M₀ cos θ（手臂伸直）", "(b) Gravity torques M(θ) = M₀ cos θ (arm straight)"), fontsize=7.6)
fig.tight_layout()
figure(fig, "fig7_1_1")

out(L1=L1 * 1000, L2=L2 * 1000, LW=LW * 1000, m_ua=U["m_ua"], m_fa=U["m_fa"], m_w=U["m_w"], c_ua=U["c_ua"] * 1000, c_fa=U["c_fa"] * 1000,
    P=P, W=W, M_sh=M_sh, M_el=M_el, x_c=x_c * 1000, tau_big=U["tau_big"], tau_small=U["tau_small"], P_max=P_max, S_sh=U["tau_big"] / M_sh,
    share_ua=share[items[0][0]], share_fa=share[items[1][0]], share_w=share[items[2][0]], share_p=share[items[3][0]], reach=(L1 + L2 + LW) * 1000)
