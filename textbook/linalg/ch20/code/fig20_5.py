"""图 20.5.1：(a) 条件数从 1 到 10¹⁵ 的 100 阶方程组，用部分选主元的 LU 分解求解：后向误差始终约为 ε，
前向误差随条件数增长，大致不超过 κ·后向误差；(b) 部分选主元的增长因子：威尔金森矩阵为 2ⁿ⁻¹，随机矩阵很小。"""
import numpy as np
import scipy.linalg as sla

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

rng = np.random.default_rng(2005)
n = 100
K, ETA, FWD = [], [], []
for k in np.linspace(0, 15, 31):
    Q1, _ = np.linalg.qr(rng.standard_normal((n, n)))
    Q2, _ = np.linalg.qr(rng.standard_normal((n, n)))
    A = Q1 @ np.diag(np.logspace(0, -k, n)) @ Q2.T
    x = np.ones(n)
    b = A @ x
    xh = np.linalg.solve(A, b)
    r = b - A @ xh
    ETA.append(np.linalg.norm(r) / (np.linalg.norm(A, 2) * np.linalg.norm(xh) + np.linalg.norm(b)))
    FWD.append(np.linalg.norm(xh - x) / np.linalg.norm(x))
    K.append(np.linalg.cond(A))
K, ETA, FWD = map(np.array, (K, ETA, FWD))
eps = np.finfo(float).eps
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.5))
a1.loglog(K, FWD, "o", color=RED, ms=4, label=T("前向误差 ‖x̂ − x‖/‖x‖", "forward error ‖x̂ − x‖/‖x‖"))
a1.loglog(K, ETA, "s", color=BLUE, ms=4, label=T("后向误差（相对残差）", "backward error (relative residual)"))
a1.loglog(K, K * eps, color=MUTED, lw=1, ls="--", label="κ·ε")
a1.axhline(eps, color=BLUE, lw=0.6, ls=":")
a1.set_xlabel(T("条件数 κ₂(A)", "condition number κ₂(A)"))
a1.set_ylabel(T("相对误差", "relative error"))
a1.legend(frameon=False, fontsize=8.5)
a1.set_title(T("(a) 后向误差小，前向误差 ≈ κ × 后向误差", "(a) Small backward error, forward ≈ κ × backward"), fontsize=11)
ns = np.arange(5, 61, 5)
gw, gr = [], []
for m in ns:
    W = np.eye(m) - np.tril(np.ones((m, m)), -1)
    W[:, -1] = 1.0
    gw.append(np.abs(sla.lu(W)[2]).max())
    G = rng.standard_normal((m, m))
    gr.append(np.abs(sla.lu(G)[2]).max() / np.abs(G).max())
a2.semilogy(ns, gw, "o-", color=RED, label=T("威尔金森矩阵：2ⁿ⁻¹", "Wilkinson's matrix: 2ⁿ⁻¹"))
a2.semilogy(ns, gr, "s-", color=BLUE, label=T("随机矩阵", "random matrices"))
a2.semilogy(ns, 1 / (ns * eps), color=MUTED, lw=1, ls="--", label=T("1/(nε)：增长到这里，结果全错", "1/(nε): growth this large ruins the result"))
a2.set_xlabel("n")
a2.set_ylabel(T("增长因子", "growth factor"))
a2.legend(frameon=False, fontsize=8.5)
a2.set_title(T("(b) 部分选主元的增长因子", "(b) Growth factor of partial pivoting"), fontsize=11)
for a in (a1, a2):
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig20_5_1")
