"""9.5 节的示意图。

图 9.5.1：卡尔曼滤波的一个周期：上一步的后验 → 预测（平移并变宽）→ 测量的似然 → 更新（变窄）。
图 9.5.2：算例 9.5.2：只用里程计、只用测量、卡尔曼滤波三者的误差，以及滤波器给出的 ±2√P 范围。
图 9.5.3：算例 9.5.3：P_k 与 K_k 收敛到稳态值；2000 次蒙特卡洛的误差方差与 P_k 一致。
"""
import math

import numpy as np

from _prob import gauss_pdf
from bookout import COLORS as C, T, figure, style

plt = style()


def clean(ax):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


dt, u, sw, sv = 0.1, 0.5, 0.01, 0.05
q, r = sw ** 2, sv ** 2
x0_true, xhat0, P0, N = 0.15, 0.0, 0.04, 100


def kalman(z):
    xh, P, xs, Ps, Ks = xhat0, P0, [], [], []
    for zk in z:
        xm, Pm = xh + u * dt, P + q
        K = Pm / (Pm + r)
        xh, P = xm + K * (zk - xm), (1 - K) * Pm
        xs.append(xh); Ps.append(P); Ks.append(K)
    return np.array(xs), np.array(Ps), np.array(Ks)


def simulate(rng):
    x = np.empty(N + 1)
    x[0] = x0_true
    w = sw * rng.standard_normal(N)
    v = sv * rng.standard_normal(N)
    for k in range(N):
        x[k + 1] = x[k] + u * dt + w[k]
    return x, x[1:] + v


# ---------------------------------------------------------------- 图 9.5.1 一个周期（示意，数值取得便于看清）
m0, s0 = 1.0, 0.10
du, sq = 0.5, 0.12
mp, sp = m0 + du, math.sqrt(s0 ** 2 + sq ** 2)
zm, sz = 1.62, 0.10
K = sp ** 2 / (sp ** 2 + sz ** 2)
m1, s1 = mp + K * (zm - mp), math.sqrt((1 - K) * sp ** 2)
x = np.linspace(0.5, 2.1, 600)
fig, ax = plt.subplots(figsize=(8.0, 3.6))
ax.plot(x, gauss_pdf(x, m0, s0), color=C["muted"], lw=1.8)
ax.plot(x, gauss_pdf(x, mp, sp), color=C["muted"], lw=1.6, ls="--")
ax.plot(x, gauss_pdf(x, zm, sz), color=C["accent"], lw=1.6, ls=":")
ax.plot(x, gauss_pdf(x, m1, s1), color=C["z"], lw=2.2)
ax.annotate("", xy=(mp, 2.25), xytext=(m0, 4.1), arrowprops=dict(arrowstyle="-|>", color=C["ink"], lw=1.2, connectionstyle="arc3,rad=-0.25"))
ax.text(0.62, 3.75, T("① 上一步的估计\n" + r"$\mathcal{N}(\hat x_{k-1}, P_{k-1})$", "① previous estimate\n" + r"$\mathcal{N}(\hat x_{k-1}, P_{k-1})$"), fontsize=9, color=C["muted"])
ax.text(1.05, 4.75, T("② 预测：按里程计平移 " + r"$u\Delta t$" + "，\n方差加上 " + r"$\sigma_w^2$" + "，曲线变宽", "② predict: shift by " + r"$u\Delta t$" + ",\nadd " + r"$\sigma_w^2$" + ", the curve widens"), fontsize=9, color=C["ink"])
ax.text(1.80, 3.6, T("③ 测量 " + r"$z_k$" + " 的似然", "③ likelihood of " + r"$z_k$"), fontsize=9, color=C["accent"])
ax.text(1.77, 4.55, T("④ 更新：二者相乘，\n曲线变窄", "④ update: multiply,\nthe curve narrows"), fontsize=9, color=C["z"])
ax.set_xlim(0.5, 2.15)
ax.set_ylim(0, 5.6)
ax.set_xlabel(T("AGV 的位置 x", "AGV position x"))
ax.set_yticks([])
clean(ax)
ax.spines["left"].set_visible(False)
figure(fig, "fig9_5_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 9.5.2（数据与算例 9.5.2 相同）
rng = np.random.default_rng(905)
xt, z = simulate(rng)
xs, Ps, Ks = kalman(z)
t = dt * np.arange(1, N + 1)
odo = xhat0 + u * t
fig, ax = plt.subplots(figsize=(8.0, 3.6))
ax.fill_between(t, -2000 * np.sqrt(Ps), 2000 * np.sqrt(Ps), color=C["z"], alpha=0.15, lw=0)
ax.plot(t, 1000 * (z - xt[1:]), ".", color=C["accent"], ms=4, label=T("只用测量 " + r"$z_k$", "measurement " + r"$z_k$" + " only"))
ax.plot(t, 1000 * (odo - xt[1:]), color=C["muted"], lw=1.4, ls="--", label=T("只用里程计（航位推算）", "odometry only (dead reckoning)"))
ax.plot(t, 1000 * (xs - xt[1:]), color=C["z"], lw=1.8, label=T("卡尔曼滤波", "Kalman filter"))
ax.axhline(0, color=C["ink"], lw=0.6)
ax.text(0.3, 112, T("蓝带：滤波器给出的 " + r"$\pm 2\sqrt{P_k}$", "blue band: the filter's " + r"$\pm 2\sqrt{P_k}$"), fontsize=9, color=C["z"],
        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
ax.set_ylim(-170, 130)
ax.set_xlabel(T("时间 t / s", "time t / s"))
ax.set_ylabel(T("估计值 − 真实位置 / mm", "estimate − true position / mm"))
ax.legend(fontsize=9, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.12), ncol=3)
clean(ax)
figure(fig, "fig9_5_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 9.5.3 收敛与一致性
Pm_inf = (q + math.sqrt(q * q + 4 * q * r)) / 2
K_inf = Pm_inf / (Pm_inf + r)
P_inf = (1 - K_inf) * Pm_inf
rng2 = np.random.default_rng(9051)
E = np.empty((2000, N))
for i in range(2000):
    xi, zi = simulate(rng2)
    E[i] = kalman(zi)[0] - xi[1:]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.4))
k = np.arange(1, N + 1)
ax1.plot(k, 1000 * np.sqrt(Ps), color=C["z"], lw=1.8, label=T("滤波器的 " + r"$\sqrt{P_k}$", "filter's " + r"$\sqrt{P_k}$"))
ax1.plot(k[::4], 1000 * E.std(axis=0, ddof=1)[::4], "o", color=C["x"], ms=3.5, label=T("2000 次仿真的误差标准差", "error std over 2000 runs"))
ax1.axhline(1000 * math.sqrt(P_inf), color=C["muted"], lw=0.8, ls="--")
ax1.text(60, 1000 * math.sqrt(P_inf) - 5, T("稳态值", "steady state"), fontsize=9, color=C["muted"])
ax1.set_ylim(0, 55)
ax1.set_xlabel(T("步数 k", "step k"))
ax1.set_ylabel("mm")
ax1.legend(fontsize=9, frameon=False)
clean(ax1)
ax2.plot(k, Ks, color=C["z"], lw=1.8)
ax2.axhline(K_inf, color=C["muted"], lw=0.8, ls="--")
ax2.text(55, K_inf + 0.04, T("稳态增益 " + r"$K_\infty$" + f" = {K_inf:.3f}", "steady-state gain " + r"$K_\infty$" + f" = {K_inf:.3f}"), fontsize=9, color=C["muted"])
ax2.set_xlabel(T("步数 k", "step k"))
ax2.set_ylabel(T("卡尔曼增益 " + r"$K_k$", "Kalman gain " + r"$K_k$"))
ax2.set_ylim(0, 1)
clean(ax2)
fig.tight_layout()
figure(fig, "fig9_5_3")
plt.close(fig)
