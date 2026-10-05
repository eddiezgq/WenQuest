"""图 11.5.1：三种解法的精度。在 [0, 1] 上以单项式为基拟合 2～14 次多项式（已知精确最小二乘解），横轴为 A 的条件数 κ，纵轴为解的相对误差：
正规方程的误差约为 κ²ε，豪斯霍尔德 QR 与 SVD 约为 κε（ε ≈ 2.2 × 10⁻¹⁶ 为机器精度）。"""
import numpy as np

from _fig import BLUE, GREEN, INK, MUTED, RED, T, figure, plt

t = np.linspace(0.0, 1.0, 40)
rng = np.random.default_rng(115)
K, En, Eq, Es = [], [], [], []
for d in range(2, 15):
    V = np.vander(t, d + 1, increasing=True)
    Qc, _ = np.linalg.qr(V, mode="complete")
    x = rng.normal(size=d + 1)
    b = V @ x + Qc[:, d + 1:] @ rng.normal(size=V.shape[0] - d - 1) * 1e-8
    rel = lambda z: np.linalg.norm(z - x) / np.linalg.norm(x)
    Q, R = np.linalg.qr(V)
    K.append(np.linalg.cond(V)); En.append(rel(np.linalg.solve(V.T @ V, V.T @ b)))
    Eq.append(rel(np.linalg.solve(R, Q.T @ b))); Es.append(rel(np.linalg.lstsq(V, b, rcond=None)[0]))
K = np.array(K)
eps = np.finfo(float).eps
fig, ax = plt.subplots(figsize=(6.6, 4.4))
ax.loglog(K, np.minimum(En, 10), "o-", color=RED, label=T("正规方程", "normal equations"))
ax.loglog(K, Eq, "s-", color=BLUE, label=T("豪斯霍尔德 QR", "Householder QR"))
ax.loglog(K, Es, "^--", color=GREEN, label="SVD（lstsq）")
ax.loglog(K, K * eps, color=MUTED, lw=1, ls=":")
ax.loglog(K, np.minimum(K ** 2 * eps, 10), color=MUTED, lw=1, ls="-.")
ax.text(K[-1] * 0.5, K[-1] * eps * 2.5, "κε", color=MUTED, fontsize=11)
ax.text(K[4], min(K[4] ** 2 * eps, 10) * 4, "κ²ε", color=MUTED, fontsize=11)
ax.set_xlabel(T("条件数 κ(A)", "condition number κ(A)")); ax.set_ylabel(T("解的相对误差", "relative error of the solution"))
ax.legend(frameon=False, fontsize=10)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_title(T("病态问题上三种解法的精度", "accuracy of three solvers on ill-conditioned problems"), fontsize=11)
figure(fig, "fig11_5_1")
