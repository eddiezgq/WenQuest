"""29.3 节的示意图。

图 29.3.1：(a) 弹簧-阻尼器 ẍ = −ω²x − cẋ 的稳定步长 hω 随阻尼比 ζ 的变化：半隐式欧拉（阻尼显式 / 隐式）、显式欧拉、RK4（无阻尼时 2√2）；
          (b) MuJoCo 中 WQ-CR5（出厂位置环）最后 1 s 关节速度的幅值随时间步长的变化，竖线为线性化算出的 Euler、RK4 步长上限；
          (c) 两连杆臂（连杆 1 水平、连杆 2 下垂 0.5 rad）放开后的能量误差，h = 1 ms：Euler、implicit、RK4。
"""
import math

import mujoco
import numpy as np

from _ch29 import CR_NAMES, Q_CR, arm2_xml, cr_linear, cr_model, cr_servo_xml, h_limit, ur_h_limit, wqcr5
from bookout import COLORS as C, T, figure, style

plt = style()
fig, axs = plt.subplots(1, 3, figsize=(13.2, 3.9))
# (a)
ax = axs[0]
zs = np.linspace(0.01, 4, 200)
for meth, col, lab in (("euler", C["x"], T("半隐式欧拉，阻尼显式", "semi-implicit Euler, explicit damping")),
                       ("implicit", C["z"], T("半隐式欧拉，阻尼隐式", "semi-implicit Euler, implicit damping")),
                       ("explicit", C["accent"], T("显式欧拉", "explicit Euler"))):
    ax.plot(zs, [h_limit(1.0, 2 * z, meth, hmax=50.0) for z in zs], color=col, lw=1.8, label=lab)
ax.axhline(2 * math.sqrt(2), color=C["muted"], lw=1, ls="--")
ax.text(2.4, 2 * math.sqrt(2) + 0.15, T("RK4（无阻尼）", "RK4 (undamped)"), fontsize=8.5, color=C["muted"])
ax.set_ylim(0, 8)
ax.set_xlabel(T("阻尼比 ζ", "damping ratio ζ"))
ax.set_ylabel(T("稳定的最大 hω", "largest stable hω"))
ax.set_title(T("(a) 弹簧-阻尼器的稳定步长", "(a) stable step of a spring-damper"), fontsize=11)
ax.legend(fontsize=8, frameon=False, loc="upper right")
ax.grid(alpha=0.25)

# (b)
W = wqcr5()
M, K, D = cr_linear(Q_CR)
h_eu = ur_h_limit(M, K, np.diag(W.SERVO_KV), "euler")
h_rk = ur_h_limit(M, K, D, "rk4")


def run(h, integ, T_=2.0):
    _, m, d = cr_model(timestep=h, integrator=integ, flags='contact="disable" frictionloss="disable"', actuator=cr_servo_xml())
    act = [mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "pos_" + n) for n in CR_NAMES]
    d.qpos[:] = Q_CR
    d.ctrl[act] = Q_CR + 0.05
    v = 0.0
    n = int(round(T_ / h))
    for k in range(n):
        mujoco.mj_step(m, d)
        if k >= n // 2:
            v = max(v, float(np.abs(d.qvel).max()))
    return v


HS = [0.001, 0.0015, 0.0018, 0.002, 0.0022, 0.0025, 0.003, 0.004, 0.005, 0.008]
ax = axs[1]
for integ, col, mk in (("Euler", C["x"], "o"), ("RK4", C["accent"], "s"), ("implicitfast", C["z"], "^")):
    ax.semilogy([h * 1000 for h in HS], [max(run(h, integ), 1e-4) for h in HS], mk + "-", color=col, ms=4, lw=1.4, label=integ)
for hv, col in ((h_eu, C["x"]), (h_rk, C["accent"])):
    ax.axvline(hv * 1000, color=col, lw=0.8, ls=":")
ax.set_xlabel(T("时间步长 h / ms", "time step h / ms"))
ax.set_ylabel(T("最后 1 s 关节速度的幅值 / (rad/s)", "joint-speed amplitude in the last 1 s / (rad/s)"))
ax.set_title(T("(b) WQ-CR5 出厂位置环", "(b) WQ-CR5, stock position loop"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="center right")
ax.grid(alpha=0.25, which="both")

# (c)
ax = axs[2]
for integ, col in (("Euler", C["x"]), ("implicit", C["z"]), ("RK4", C["accent"])):
    m = mujoco.MjModel.from_xml_string(arm2_xml(timestep=0.001, integrator=integ, flags='energy="enable" limit="disable"'))
    d = mujoco.MjData(m)
    d.qpos[:] = (0.0, 0.5)
    mujoco.mj_forward(m, d)
    E0 = float(d.energy.sum())
    ts, es = [], []
    k = 0
    while d.time < 20 - 1e-12:
        mujoco.mj_step(m, d)
        k += 1
        if k % 20 == 0:
            ts.append(d.time)
            es.append(float(d.energy.sum()) - E0)
    ax.plot(ts, es, color=col, lw=1.4, label=integ)
ax.axhline(0, color=C["ink"], lw=0.6)
ax.set_xlabel("t / s")
ax.set_ylabel(T("能量误差 / J", "energy error / J"))
ax.set_title(T("(c) 两连杆臂的能量漂移（h = 1 ms）", "(c) energy drift of the two-link arm (h = 1 ms)"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="upper left")
ax.grid(alpha=0.25)
fig.tight_layout()
figure(fig, "fig29_3_1")
