"""17.5 节的计算：

两连杆机械臂（参数同算例 14.1.2）：大臂 m₁ = 8.4 kg，质心离肩 c₁ = 0.21 m，长 L₁ = 0.425 m，绕质心的转动惯量 J₁ = 0.13 kg·m²；
小臂 m₂ = 2.3 kg，质心离肘 c₂ = 0.196 m，J₂ = 0.031 kg·m²。q₁ 是大臂与水平方向的夹角，q₂ 是小臂相对大臂的转角。

算例 17.5.1  逆动力学：机械臂在 1.0 s 内由 q = (−60°, 90°) 平稳地运动到 (30°, −30°)（五次多项式，起止速度、加速度为零）。
            求两个关节的力矩，并把它分成惯性项、速度项（离心力与科里奥利力）和重力项（图 17.5.1）。
            用数值求导的拉格朗日方程核对手推的公式；用“力矩做的功 = 机械能的增加”核对整个过程。
算例 17.5.2  正动力学：断电、抱闸失灵，机械臂从 q = (0°, 90°) 静止释放，两个关节都不出力（就是一个双摆）。
            数值积分 10 s；第二次把 q₁ 的初值改变 0.001°，比较两次的运动（图 17.5.2）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

m1, c1, L1, J1 = 8.4, 0.21, 0.425, 0.13
m2, c2, L2, J2 = 2.3, 0.196, 0.392, 0.031


def lagrangian(q, qd):
    """由两根连杆质心的速度和角速度直接写出的 L = T − V（不用任何化简后的公式）。"""
    q1, q2 = q; d1, d2 = qd
    v1 = np.array([-c1 * math.sin(q1), c1 * math.cos(q1)]) * d1
    v2 = (np.array([-L1 * math.sin(q1), L1 * math.cos(q1)]) * d1
          + np.array([-c2 * math.sin(q1 + q2), c2 * math.cos(q1 + q2)]) * (d1 + d2))
    Tk = 0.5 * m1 * v1 @ v1 + 0.5 * J1 * d1 ** 2 + 0.5 * m2 * v2 @ v2 + 0.5 * J2 * (d1 + d2) ** 2
    V = g * (m1 * c1 * math.sin(q1) + m2 * (L1 * math.sin(q1) + c2 * math.sin(q1 + q2)))
    return Tk - V


def MCG(q, qd):
    """手推的结果：M(q)、速度项 C(q, q̇)q̇、重力项 g(q)。"""
    q1, q2 = q; d1, d2 = qd
    M11 = J1 + J2 + m1 * c1 ** 2 + m2 * (L1 ** 2 + c2 ** 2 + 2 * L1 * c2 * math.cos(q2))
    M12 = J2 + m2 * (c2 ** 2 + L1 * c2 * math.cos(q2))
    M22 = J2 + m2 * c2 ** 2
    h = m2 * L1 * c2 * math.sin(q2)
    Cqd = np.array([-h * (2 * d1 * d2 + d2 ** 2), h * d1 ** 2])
    G = g * np.array([(m1 * c1 + m2 * L1) * math.cos(q1) + m2 * c2 * math.cos(q1 + q2), m2 * c2 * math.cos(q1 + q2)])
    return np.array([[M11, M12], [M12, M22]]), Cqd, G


def energy(q, qd):
    M, _, G = MCG(q, qd)
    V = g * (m1 * c1 * math.sin(q[0]) + m2 * (L1 * math.sin(q[0]) + c2 * math.sin(q[0] + q[1])))
    return 0.5 * qd @ M @ qd + V


# ---- 算例 17.5.1：逆动力学
qa, qb, Tm = np.radians([-60.0, 90.0]), np.radians([30.0, -30.0]), 1.0


def traj(t):
    s = t / Tm
    p, pd, pdd = 10 * s ** 3 - 15 * s ** 4 + 6 * s ** 5, (30 * s ** 2 - 60 * s ** 3 + 30 * s ** 4) / Tm, (60 * s - 180 * s ** 2 + 120 * s ** 3) / Tm ** 2
    return qa + (qb - qa) * p, (qb - qa) * pd, (qb - qa) * pdd


def tau_numeric(t, e=1e-4):
    """τ = d/dt(∂L/∂q̇) − ∂L/∂q，全部用数值求导。"""
    q, qd, _ = traj(t)
    out_ = np.zeros(2)
    for k in range(2):
        ek = np.eye(2)[k] * e
        dLdqd = lambda tt: (lambda q_, qd_: (lagrangian(q_, qd_ + ek) - lagrangian(q_, qd_ - ek)) / (2 * e))(*traj(tt)[:2])
        out_[k] = (dLdqd(t + e) - dLdqd(t - e)) / (2 * e) - (lagrangian(q + ek, qd) - lagrangian(q - ek, qd)) / (2 * e)
    return out_


ts = np.linspace(0, Tm, 401)
parts = []
for t in ts:
    q, qd, qdd = traj(t)
    M, Cqd, G = MCG(q, qd)
    parts.append((M @ qdd, Cqd, G))
parts = np.array(parts)                                          # [时刻, 项, 关节]
tau = parts.sum(axis=1)
for t in (0.2, 0.5, 0.8):
    k = int(round(t / Tm * 400))
    assert np.max(np.abs(tau_numeric(t) - tau[k])) < 1e-3
power = np.array([tau[i] @ traj(t)[1] for i, t in enumerate(ts)])
work = np.trapezoid(power, ts)
dE = energy(qb, np.zeros(2)) - energy(qa, np.zeros(2))
assert abs(work - dE) < 1e-3 * abs(dE)
i_peak = np.argmax(np.abs(tau[:, 0]))
out(tau1_max=np.max(np.abs(tau[:, 0])), tau2_max=np.max(np.abs(tau[:, 1])), t1_peak=ts[i_peak],
    vel2_max=np.max(np.abs(parts[:, 1, 1])), work=work, dE=dE,
    M11_0=MCG(np.radians([0, 0]), np.zeros(2))[0][0, 0], M11_180=MCG(np.radians([0, 180]), np.zeros(2))[0][0, 0])

plt = style()
fig, axs = plt.subplots(1, 2, figsize=(6.4, 3.2), sharex=True)
names = [T(r"惯性项 $M\ddot{\mathbf{q}}$", r"inertia $M\ddot{\mathbf{q}}$"), T(r"速度项 $C\dot{\mathbf{q}}$", r"velocity $C\dot{\mathbf{q}}$"),
         T(r"重力项 $\mathbf{g}(\mathbf{q})$", r"gravity $\mathbf{g}(\mathbf{q})$")]
cols = [d.VA, d.VB, d.MUTED]
for j, ax in enumerate(axs):
    for k in range(3):
        ax.plot(ts, parts[:, k, j], color=cols[k], lw=1.2, ls="--", label=names[k])
    ax.plot(ts, tau[:, j], color=d.VR, lw=2, label=T("总力矩 τ", "total τ"))
    ax.axhline(0, color=d.MUTED, lw=0.5)
    ax.set_title(T("肩关节 τ₁", "shoulder τ₁") if j == 0 else T("肘关节 τ₂", "elbow τ₂"), fontsize=9)
    ax.set_xlabel("t / s")
    d.spines(ax)
axs[0].set_ylabel(T("力矩 / (N·m)", "torque / (N·m)"))
h_, l_ = axs[0].get_legend_handles_labels()
fig.legend(h_, l_, frameon=False, fontsize=8, loc="lower center", ncol=4)
fig.tight_layout(rect=(0, 0.08, 1, 1))
figure(fig, "fig17_5_1")


# ---- 算例 17.5.2：断电下落（τ = 0）
def f(y):
    q, qd = y[:2], y[2:]
    M, Cqd, G = MCG(q, qd)
    return np.concatenate([qd, np.linalg.solve(M, -Cqd - G)])


def rk4(y, h):
    k1 = f(y); k2 = f(y + h / 2 * k1); k3 = f(y + h / 2 * k2); k4 = f(y + h * k3)
    return y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def end(q):
    return np.array([L1 * math.cos(q[0]) + L2 * math.cos(q[0] + q[1]), L1 * math.sin(q[0]) + L2 * math.sin(q[0] + q[1])])


h, tend = 1e-3, 10.0
ya = np.array([0.0, math.radians(90.0), 0, 0])
yb = ya + np.array([math.radians(1e-3), 0, 0, 0])
E0 = energy(ya[:2], ya[2:])
tt, qa_hist, qb_hist, sep, t_sep, drift = [0.0], [ya[:2].copy()], [yb[:2].copy()], [0.0], None, 0.0
n = int(round(tend / h))
for i in range(1, n + 1):
    ya, yb = rk4(ya, h), rk4(yb, h)
    if i % 10 == 0:
        tt.append(i * h); qa_hist.append(ya[:2].copy()); qb_hist.append(yb[:2].copy())
        dist = np.linalg.norm(end(ya[:2]) - end(yb[:2])); sep.append(dist)
        drift = max(drift, abs(energy(ya[:2], ya[2:]) - E0))
        if t_sep is None and dist > 0.10:
            t_sep = i * h
tt, qa_hist, qb_hist = np.array(tt), np.array(qa_hist), np.array(qb_hist)
assert drift < 1e-6 * (abs(E0) + 10)
assert t_sep is not None and 5.0 < t_sep < 7.5
out(t_sep=t_sep, drift=drift, sep1=sep[100], sep3=sep[300])

fig, ax = plt.subplots(figsize=(4.8, 2.9))
ya_end = np.array([end(q)[1] for q in qa_hist]); yb_end = np.array([end(q)[1] for q in qb_hist])
ax.plot(tt, ya_end, color=d.VA, lw=1.5, label=T("第一次", "run 1"))
ax.plot(tt, yb_end, color=d.VR, lw=1.2, ls="--", label=T("q₁ 的初值大 0.001°", "q₁ starts 0.001° higher"))
ax.axvline(t_sep, color=d.MUTED, lw=0.7, ls=":")
ax.set_ylim(-1.05, 0.8)
ax.text(t_sep + 0.1, -1.0, T("末端相差 10 cm", "ends 10 cm apart"), fontsize=8.5, color=d.MUTED)
ax.set_xlabel("t / s"); ax.set_ylabel(T("末端的高度 / m", "end-effector height / m"))
ax.legend(frameon=False, fontsize=8.5, loc="upper right")
d.spines(ax)
figure(fig, "fig17_5_2")
