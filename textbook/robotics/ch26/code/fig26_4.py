"""26.4 节的示意图。

图 26.4.1：(a) 算例 26.4.1：关节 1 的恒速试验，各速度下稳定后的平均力矩（点）与拟合的 τ = f_c sign θ̇ + f_v θ̇（实线）；
              虚线为斯特里贝克模型（式 (26.4.2)，参数为示意值：f_s = 3、f_c = 2 N·m，v_s = 0.1 rad/s，f_v = 1.5 N·m·s/rad）在低速处的样子；
          (b) 算例 26.4.2：辨识实验中关节 1 的“摩擦力矩”（滤波后的实测力矩减去不含摩擦的真模型）对滤波后速度的散点：
              速度换向附近（|θ̇| < 0.05 rad/s，橙色）的点落在库仑模型的两条直线之间。
"""
import numpy as np

from _ch26 import EXC_Q0, FC_TRUE, FV_TRUE, KD, KP, exc_experiment, friction_mjcf, payload_parts, ur_chain
from bookout import COLORS as C, T, figure, style
import mujoco

plt = style()
ch = ur_chain()
SPEEDS = [0.05, 0.1, 0.2, 0.5, 1.0, 1.5]


def constant_speed(j, w, T_=3.0, dt=0.001):
    m = mujoco.MjModel.from_xml_string(friction_mjcf())
    d = mujoco.MjData(m)
    m.jnt_limited[:] = 0
    d.qpos[:] = EXC_Q0
    d.qvel[j] = w
    taus = []
    for k in range(int(T_ / dt)):
        t = k * dt
        qdes = EXC_Q0.copy()
        qdes[j] += w * t
        qdd = np.zeros(6)
        qdd[j] = w
        tau = ch.rnea(qdes, qdd, np.zeros(6)) + KP * (qdes - d.qpos) + KD * (qdd - d.qvel)
        d.qfrc_applied[:] = tau
        mujoco.mj_step(m, d)
        if t >= 1.5:
            taus.append(tau[j])
    return float(np.mean(taus))


w = np.array(SPEEDS + [-s for s in SPEEDS])
tau = np.array([constant_speed(0, x) for x in w])
fc, fv = np.linalg.lstsq(np.column_stack([np.sign(w), w]), tau, rcond=None)[0]
fig, axs = plt.subplots(1, 2, figsize=(11.2, 4.1))
ax = axs[0]
v = np.linspace(-1.6, 1.6, 801)
v = v[v != 0]
ax.plot(v[v > 0], fc + fv * v[v > 0], color=C["z"], lw=1.6, label=T(r"拟合：$f_c\,\mathrm{sign}\,\dot\theta + f_v\dot\theta$", r"fit: $f_c\,\mathrm{sign}\,\dot\theta + f_v\dot\theta$"))
ax.plot(v[v < 0], -fc + fv * v[v < 0], color=C["z"], lw=1.6)
FS, FCs, VS, FVs = 3.0, 2.0, 0.1, 1.5
st = (FCs + (FS - FCs) * np.exp(-(v / VS) ** 2)) * np.sign(v) + FVs * v
ax.plot(v, st, "--", color=C["accent"], lw=1.3, label=T("斯特里贝克模型（示意）", "Stribeck model (illustrative)"))
ax.plot(w, tau, "o", color=C["x"], ms=6, label=T("恒速试验（MuJoCo）", "constant-speed tests (MuJoCo)"))
ax.axhline(0, color=C["muted"], lw=0.6)
ax.axvline(0, color=C["muted"], lw=0.6)
ax.set_xlabel(T(r"关节 1 的速度 $\dot\theta_1$ / (rad/s)", r"joint 1 rate $\dot\theta_1$ / (rad/s)"))
ax.set_ylabel(T("摩擦力矩 / (N·m)", "friction torque / (N·m)"))
ax.set_title(T("(a) 恒速试验与摩擦模型", "(a) constant-speed tests and friction models"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="upper left")
ax.grid(alpha=0.25)
# (b)
pl = payload_parts()
E = exc_experiment(payload=pl, seed=263)
chp = ur_chain(payload=pl)
Qf, Qd, Qdd, TAUf = E["Qf"], E["Qd"], E["Qdd"], E["TAUf"]
ff = np.array([TAUf[k, 0] - chp.rnea(Qf[k], Qd[k], Qdd[k])[0] for k in range(len(Qf))])
low = np.abs(Qd[:, 0]) < 0.05
ax = axs[1]
ax.plot(Qd[~low, 0], ff[~low], ".", color=C["z"], ms=3, alpha=0.6, label=r"$|\dot\theta_1| \geq 0.05$ rad/s")
ax.plot(Qd[low, 0], ff[low], ".", color=C["accent"], ms=5, label=T(r"$|\dot\theta_1| < 0.05$ rad/s（换向附近）", r"$|\dot\theta_1| < 0.05$ rad/s (near reversal)"))
vv = np.linspace(0.001, 1.4, 50)
ax.plot(vv, FC_TRUE[0] + FV_TRUE[0] * vv, color=C["ink"], lw=1.0)
ax.plot(-vv, -FC_TRUE[0] - FV_TRUE[0] * vv, color=C["ink"], lw=1.0, label=T("模型中设的摩擦", "friction set in the model"))
ax.set_xlabel(T(r"滤波后的速度 $\dot\theta_1$ / (rad/s)", r"filtered rate $\dot\theta_1$ / (rad/s)"))
ax.set_ylabel(T("实测力矩 − 不含摩擦的模型 / (N·m)", "measured torque − friction-free model / (N·m)"))
ax.set_title(T("(b) 辨识实验中的关节 1", "(b) joint 1 in the identification run"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="upper left")
ax.grid(alpha=0.25)
ax.set_xlim(-1.4, 1.4)
fig.tight_layout()
figure(fig, "fig26_4_1")
