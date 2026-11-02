"""图 23.1.1：三种最小二乘解法的相对误差随条件数 κ 的变化（m = 100、n = 10，每个 κ 取 3 个随机问题的平均）。
(a) 残差几乎为零（tan θ = 10⁻⁸）：QR、SVD 的误差约为 κu，正规方程约为 κ²u；(b) 残差很大（tan θ = 1）：三种方法都受 κ²u·tan θ 一项支配，
QR、SVD 与正规方程相差不大——这时正规方程“丢掉一半有效数字”的缺点已被问题本身的敏感性掩盖。"""
import numpy as np
from scipy.linalg import cho_factor, cho_solve, qr, solve_triangular

from _fig import BLUE, GREEN, INK, MUTED, RED, T, figure, plt

rng = np.random.default_rng(23012)
u = 2.0 ** -53
m, n = 100, 10
kexps = np.arange(1, 11.5, 0.5)
fig, axs = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
for ax, tan, title in ((axs[0], 1e-8, T("(a) 残差几乎为零：tan θ = 10⁻⁸", "(a) Nearly zero residual: tan θ = 10⁻⁸")),
                       (axs[1], 1.0, T("(b) 残差很大：tan θ = 1", "(b) Large residual: tan θ = 1"))):
    E = {"ne": [], "qr": [], "svd": []}
    for ke in kexps:
        acc = {k: [] for k in E}
        for _ in range(3):
            U, _ = np.linalg.qr(rng.standard_normal((m, m)))
            V, _ = np.linalg.qr(rng.standard_normal((n, n)))
            A = U[:, :n] @ np.diag(np.logspace(0, -ke, n)) @ V.T
            x = rng.standard_normal(n)
            y = A @ x
            r = U[:, n:] @ rng.standard_normal(m - n)
            r *= tan * np.linalg.norm(y) / np.linalg.norm(r)
            b = y + r
            try:
                xn = cho_solve(cho_factor(A.T @ A), A.T @ b)
                acc["ne"].append(np.linalg.norm(xn - x) / np.linalg.norm(x))
            except np.linalg.LinAlgError:
                acc["ne"].append(np.nan)
            Q, R = qr(A, mode="economic")
            acc["qr"].append(np.linalg.norm(solve_triangular(R, Q.T @ b) - x) / np.linalg.norm(x))
            Us, s, Vt = np.linalg.svd(A, full_matrices=False)
            acc["svd"].append(np.linalg.norm(Vt.T @ ((Us.T @ b) / s) - x) / np.linalg.norm(x))
        for k in E:
            E[k].append(np.nanmean(acc[k]) if not np.all(np.isnan(acc[k])) else np.nan)
    kap = 10.0 ** kexps
    ax.loglog(kap, E["ne"], "o-", color=RED, ms=4, label=T("正规方程", "normal equations"))
    ax.loglog(kap, E["qr"], "s-", color=BLUE, ms=4, label="QR")
    ax.loglog(kap, E["svd"], "^-", color=GREEN, ms=4, label="SVD")
    ax.loglog(kap, kap * u, color=MUTED, ls="--", lw=1, label="κu")
    ax.loglog(kap, kap ** 2 * u * tan, color=INK, ls=":", lw=1.2, label="κ²u·tan θ")
    ax.loglog(kap, np.minimum(kap ** 2 * u, 1e3), color=RED, ls="--", lw=0.8, alpha=0.6, label="κ²u")
    ax.set_ylim(1e-17, 1e2)
    ax.set_xlabel(T("条件数 κ(A)", "condition number κ(A)"))
    ax.set_title(title, fontsize=10)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
axs[0].set_ylabel(T("解的相对误差", "relative error of x"))
axs[0].legend(frameon=False, fontsize=8.5, loc="upper left")
fig.tight_layout()
figure(fig, "fig23_1_1")
