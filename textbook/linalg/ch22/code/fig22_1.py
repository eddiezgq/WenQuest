"""图 22.1.1：(a) 两点边值问题的多重打靶矩阵：区间数 N 增加时，条件数始终约为 8，部分选主元的增长因子指数增长、解的误差随之增大，
完全选主元与 QR 分解的误差始终在机器精度；(b) 50 个 100 阶随机矩阵的增长因子：部分、车式、完全三种选主元。"""
import numpy as np

from _fig import BLUE, GREEN, INK, MUTED, RED, T, figure, plt
from _ge import lu, shooting, solve

rng = np.random.default_rng(22012)
Ns = [5, 10, 15, 20, 30, 40, 50, 60, 70, 80]
gp, ep, ec, eq, kk = [], [], [], [], []
for N in Ns:
    A = shooting(N)
    x = rng.standard_normal(A.shape[0])
    b = A @ x
    xp, g = solve(A, b, "partial")
    xc, _ = solve(A, b, "complete")
    Q, R = np.linalg.qr(A)
    xq = np.linalg.solve(R, Q.T @ b)
    e = lambda y: np.linalg.norm(y - x) / np.linalg.norm(x)
    gp.append(g); ep.append(e(xp)); ec.append(e(xc)); eq.append(e(xq)); kk.append(np.linalg.cond(A))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.5), gridspec_kw={"width_ratios": [1.4, 1]})
a1.semilogy(Ns, gp, "o-", color=RED, lw=1.6, label=T("部分选主元的增长因子", "growth factor, partial pivoting"))
a1.semilogy(Ns, ep, "s--", color=RED, lw=1, label=T("部分选主元：解的相对误差", "partial pivoting: relative error"))
a1.semilogy(Ns, ec, "^-", color=GREEN, lw=1, label=T("完全选主元：解的相对误差", "complete pivoting: relative error"))
a1.semilogy(Ns, eq, "v-", color=BLUE, lw=1, label=T("QR 分解：解的相对误差", "QR: relative error"))
a1.semilogy(Ns, kk, "-", color=INK, lw=1.2, label=T("条件数 κ₂(A)", "condition number κ₂(A)"))
a1.set_xlabel(T("小区间数 N（矩阵阶数 2N + 2）", "number of subintervals N (order 2N + 2)"))
a1.legend(frameon=False, fontsize=8.5, loc="upper left")
a1.set_title(T("(a) 多重打靶矩阵：良态，部分选主元却不稳定", "(a) Multiple-shooting matrix: well conditioned, yet partial pivoting is unstable"), fontsize=10)
g = {p: [] for p in ("partial", "rook", "complete")}
rng = np.random.default_rng(22011)                    # 与程序 22.1.1 相同的 50 个随机矩阵
for _ in range(50):
    M = rng.standard_normal((100, 100))
    for p in g:
        g[p].append(lu(M, p)[4])
a2.boxplot([g["partial"], g["rook"], g["complete"]], widths=0.5)
a2.set_xticks([1, 2, 3])
a2.set_xticklabels([T("部分", "partial"), T("车式", "rook"), T("完全", "complete")])
a2.set_ylabel(T("增长因子 ρ", "growth factor ρ"))
a2.set_title(T("(b) 50 个 100 阶随机矩阵", "(b) Fifty random matrices of order 100"), fontsize=10)
for a in (a1, a2):
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig22_1_1")
