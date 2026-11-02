"""图 23.3.1：由关节编码器的位置读数（噪声 0.1 mrad，采样 4 ms）求速度。(a) 直接求解（逐点差分）的速度抖动很大；
吉洪诺夫正则化（惩罚加速度，λ 由偏差原理确定）得到平滑、准确的速度；(b) L 曲线（惩罚加速度）：横轴为残差 ‖Av − b‖，纵轴为 ‖Lv‖，
标出 L 曲线拐角、偏差原理和误差最小（事先不知道）三种 λ。"""
import numpy as np

from _fig import BLUE, GREEN, INK, MUTED, RED, T, figure, plt

rng = np.random.default_rng(23031)
n, h = 500, 0.004
t = h * np.arange(1, n + 1)
v_true = 1.2 * (np.tanh((t - 0.4) / 0.12) - np.tanh((t - 1.5) / 0.15)) / 2
A = h * np.tril(np.ones((n, n)))
sigma = 1e-4
b = A @ v_true + rng.normal(0, sigma, n)
D = (np.eye(n) - np.eye(n, k=-1))[1:] / h
AtA, Atb, DtD = A.T @ A, A.T @ b, D.T @ D
lams = np.logspace(-6, 0, 121)
V = [np.linalg.solve(AtA + l ** 2 * DtD, Atb) for l in lams]
rn = np.array([np.linalg.norm(A @ v - b) for v in V])
sn = np.array([np.linalg.norm(D @ v) for v in V])
es = np.array([np.sqrt(np.mean((v - v_true) ** 2)) for v in V])
x, y = np.log(rn), np.log(sn)
dx, dy = np.gradient(x), np.gradient(y)
kap = (dx * np.gradient(dy) - dy * np.gradient(dx)) / (dx ** 2 + dy ** 2) ** 1.5
i_l = int(np.argmax(kap[5:-5])) + 5
i_dp = int(np.argmin(np.abs(rn - sigma * np.sqrt(n))))
i_b = int(np.argmin(es))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.5), gridspec_kw={"width_ratios": [1.4, 1]})
a1.plot(t, np.linalg.solve(A, b), color=MUTED, lw=0.6, label=T("直接求解（逐点差分）", "direct solve (differencing)"))
a1.plot(t, V[i_dp], color=RED, lw=1.8, label=T("吉洪诺夫正则化（偏差原理）", "Tikhonov (discrepancy principle)"))
a1.plot(t, v_true, color=INK, lw=1, ls="--", label=T("真实速度", "true velocity"))
a1.set_xlabel(T("时间 / s", "time / s"))
a1.set_ylabel(T("关节速度 / (rad/s)", "joint velocity / (rad/s)"))
a1.legend(frameon=False, fontsize=8.5, loc="upper right")
a1.set_title(T("(a) 由位置读数求速度", "(a) Velocity from position readings"), fontsize=10)
a2.loglog(rn, sn, color=BLUE, lw=1.6)
for i, col, lab in ((i_l, GREEN, T("L 曲线拐角", "L-curve corner")), (i_dp, RED, T("偏差原理", "discrepancy principle")), (i_b, INK, T("误差最小", "smallest error"))):
    a2.plot(rn[i], sn[i], "o", color=col, ms=8, label=f"{lab}: λ = {lams[i]:.1e}")
a2.set_xlabel("‖Av − b‖")
a2.set_ylabel("‖Lv‖")
a2.legend(frameon=False, fontsize=8)
a2.set_title(T("(b) L 曲线（惩罚加速度）", "(b) L-curve (penalizing acceleration)"), fontsize=10)
for a in (a1, a2):
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig23_3_1")
