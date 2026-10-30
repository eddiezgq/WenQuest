"""29.4 节的示意图。

图 29.4.1：(a) WQ-CR5 出厂位置环各关节的临界延迟 T* = φ_m/ω_c（带标准负载，工作姿态）；
          (b) 机器人厂关节测试台的空载摩擦力矩：各关节的名义值与 ±3σ 的范围（域随机化的取值范围）；
          (c) 负载跑合台的标准动作，测量延迟 2.5 ms，三种控制器的 TCP 误差随时间的变化。
"""
import mujoco
import numpy as np

from _ch29 import Q_CR, cr_chain, cr_friction, cr_linear, cr_load, cr_load_xml, cr_model, cr_test_sigma, cr_track, pd_delay_margin, pd_gains, wqcr5
from bookout import COLORS as C, T, figure, style

plt = style()
W = wqcr5()
KP, KV = np.array(W.SERVO_KP), np.array(W.SERVO_KV)
M, _, _ = cr_linear(Q_CR, payload=True)
Md = np.diag(M)
fig, axs = plt.subplots(1, 3, figsize=(13.2, 3.9))
x = np.arange(6)
ax = axs[0]
Ts = [pd_delay_margin(Md[j], KP[j], KV[j])[2] * 1000 for j in range(6)]
ax.bar(x, Ts, 0.55, color=[C["x"] if t < 3 else C["z"] for t in Ts])
for i, v in enumerate(Ts):
    ax.text(i, v + 0.4, f"{v:.1f}", ha="center", fontsize=8.5)
ax.set_xticks(x, [f"J{i + 1}" for i in range(6)])
ax.set_ylabel(T("临界延迟 T* / ms", "critical delay T* / ms"))
ax.set_title(T("(a) 出厂位置环的临界延迟", "(a) critical delays of the stock loop"), fontsize=11)
ax.grid(alpha=0.25, axis="y")

ax = axs[1]
S = cr_test_sigma()
nom = np.array([s["fric"] for s in S])
sig = np.array([s["fric_sigma"] for s in S])
hi = np.array([s["fric_hi"] for s in S])
ax.errorbar(x, nom, yerr=3 * sig, fmt="o", color=C["z"], capsize=5, lw=1.6, label=T("名义值 ±3σ", "nominal ±3σ"))
ax.plot(x, hi, "_", color=C["x"], ms=18, mew=2, label=T("测试台的上限（不合格线）", "test-bench upper limit"))
ax.set_xticks(x, [f"J{i + 1}\n{W.MODULES[s]['code']}" for i, s in enumerate(W.JOINT_MODULE)])
ax.set_ylim(0, 2.3)
ax.set_ylabel(T("空载摩擦力矩 / (N·m)", "no-load friction torque / (N·m)"))
ax.set_title(T("(b) 关节测试台的散布", "(b) spread at the joint test bench"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="upper right")
ax.grid(alpha=0.25, axis="y")

ax = axs[2]
_, m, d = cr_model(tool=cr_load_xml())
d.qpos[:] = Q_CR
mujoco.mj_forward(m, d)
MP = np.zeros((6, 6))
mujoco.mj_fullM(m, d, MP)
nom_ch = cr_chain(payload=cr_load())
FC0, FV0 = cr_friction()
kpB, kdB = pd_gains(np.diag(MP), 25.0)
kpC, kdC = pd_gains(np.diag(MP), 80.0)
CTRL = {"A": dict(kp=KP, kd=KV), "B": dict(kp=kpB, kd=kdB, ff_model=nom_ch, fric_ff=(FC0, FV0)),
        "C": dict(kp=kpC, kd=kdC, ff_model=nom_ch, fric_ff=(FC0, FV0))}
names = {"A": T("A 出厂位置环", "A stock loop"), "B": T("B 前馈 + 低增益", "B feed-forward + low gain"),
         "C": T("C 前馈 + 高增益", "C feed-forward + high gain")}
cols = {"A": C["muted"], "B": C["z"], "C": C["x"]}
for k, v in CTRL.items():
    r = cr_track(**v, delay=0.0025)
    ax.semilogy(r["t"], np.maximum(r["e"] * 1000, 1e-3), color=cols[k], lw=1.4, label=names[k])
ax.set_xlabel("t / s")
ax.set_ylabel(T("TCP 误差 / mm", "TCP error / mm"))
ax.set_title(T("(c) 标准动作，延迟 2.5 ms", "(c) standard motion, 2.5 ms delay"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="lower right")
ax.grid(alpha=0.25, which="both")
fig.tight_layout()
figure(fig, "fig29_4_1")
