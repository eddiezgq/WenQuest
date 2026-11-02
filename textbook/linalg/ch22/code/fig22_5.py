"""图 22.5.1：混合精度迭代改进。(a) 单精度 LU 分解 + 双精度残差：κ(A) = 10²～10¹⁰ 时各步的相对误差（100 阶），
κ·u₃₂ < 1 时收敛到双精度的水平，κ 越大越慢，κ = 10¹⁰ 时发散；(b) 半精度 LU（逐步舍入模拟）+ 单精度修正 + 双精度残差（50 阶），κ = 10～10⁴，κ = 10⁴ 时 κ·u₁₆ > 1，不收敛。"""
import numpy as np
from scipy.linalg import lu_factor, lu_solve

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

rng = np.random.default_rng(22051)                    # 与程序 22.5.1 相同的随机数序列
rng.random(10000)
rng.random(10000)


def make(n, kappa):
    U, _ = np.linalg.qr(rng.standard_normal((n, n)))
    V, _ = np.linalg.qr(rng.standard_normal((n, n)))
    return U @ np.diag(np.logspace(0, -np.log10(kappa), n)) @ V.T


fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.4))
for kexp, col in zip((2, 4, 6, 8, 10), (BLUE, GREEN, ACC, RED, INK)):
    A = make(100, 10.0 ** kexp)
    xt = rng.standard_normal(100)
    b = A @ xt
    F = lu_factor(A.astype(np.float32))
    xk = lu_solve(F, b.astype(np.float32)).astype(np.float64)
    e = [np.linalg.norm(xk - xt) / np.linalg.norm(xt)]
    for _ in range(12):
        xk = xk + lu_solve(F, (b - A @ xk).astype(np.float32)).astype(np.float64)
        e.append(np.linalg.norm(xk - xt) / np.linalg.norm(xt))
    a1.semilogy(e, "o-", ms=3, color=col, label=f"κ = 10^{kexp}".replace("^2", "²").replace("^4", "⁴").replace("^6", "⁶").replace("^8", "⁸").replace("^10", "¹⁰"))
a1.set_ylim(1e-17, 1e3)
a1.set_xlabel(T("改进的步数", "refinement steps"))
a1.set_ylabel(T("解的相对误差", "relative error"))
a1.legend(frameon=False, fontsize=8.5, ncol=2)
a1.set_title(T("(a) 单精度分解 + 双精度残差（100 阶）", "(a) Single-precision LU + double-precision residual (n = 100)"), fontsize=10)


def lu16(A):
    A = A.astype(np.float16)
    n = len(A)
    perm = np.arange(n)
    for k in range(n - 1):
        p = k + int(np.argmax(np.abs(A[k:, k].astype(np.float32))))
        A[[k, p]] = A[[p, k]]
        perm[[k, p]] = perm[[p, k]]
        A[k + 1:, k] = (A[k + 1:, k] / A[k, k]).astype(np.float16)
        A[k + 1:, k + 1:] = (A[k + 1:, k + 1:] - np.outer(A[k + 1:, k], A[k, k + 1:]).astype(np.float16)).astype(np.float16)
    return A, perm


def solve16(F, perm, r):
    L = np.tril(F.astype(np.float32), -1) + np.eye(len(F), dtype=np.float32)
    U = np.triu(F.astype(np.float32))
    return np.linalg.solve(U, np.linalg.solve(L, r[perm].astype(np.float32))).astype(np.float64)


for kexp, col in zip((1, 2, 3, 4), (BLUE, GREEN, ACC, RED)):
    A = make(50, 10.0 ** kexp)
    xt = rng.standard_normal(50)
    b = A @ xt
    F, perm = lu16(A)
    xk = solve16(F, perm, b)
    e = [np.linalg.norm(xk - xt) / np.linalg.norm(xt)]
    for _ in range(30):
        xk = xk + solve16(F, perm, b - A @ xk)
        e.append(np.linalg.norm(xk - xt) / np.linalg.norm(xt))
    a2.semilogy(e, "o-", ms=2.5, color=col, label=f"κ = 10^{kexp}".replace("^1", "¹").replace("^2", "²").replace("^3", "³").replace("^4", "⁴"))
a2.set_ylim(1e-17, 1e3)
a2.set_xlabel(T("改进的步数", "refinement steps"))
a2.legend(frameon=False, fontsize=8.5)
a2.set_title(T("(b) 半精度分解 + 单精度修正 + 双精度残差（50 阶）", "(b) Half-precision LU + single correction + double residual (n = 50)"), fontsize=10)
for a in (a1, a2):
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig22_5_1")
