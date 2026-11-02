"""图 23.2.1：UR5e 标定的雅可比矩阵（150 × 24）。(a) 24 个奇异值：前 18 个在 0.4～13 之间，后 6 个落到差分误差的水平（10⁻⁹ 以下）；
(b) 截断 SVD：保留前 k 个奇异值时，参数修正量的范数与残差的均方根——k = 18 时残差降到测量噪声，再多保留一个，修正量就大得荒谬。"""
import numpy as np

from _fig import BLUE, INK, MUTED, RED, T, figure, plt
from _ur5e import NOMINAL, fk_all, jac, measure, poses, true_params

Q = poses(50)
y = measure(true_params(), Q)
J = jac(NOMINAL, Q)
U, s, Vt = np.linalg.svd(J, full_matrices=False)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.4))
a1.semilogy(range(1, 25), np.maximum(s, 1e-17), "o", color=BLUE)
a1.axhline(s[0] * 1e-6, color=MUTED, ls="--", lw=1)
a1.text(24, s[0] * 2e-6, T("阈值 10⁻⁶σ₁", "threshold 10⁻⁶σ₁"), color=MUTED, fontsize=9, ha="right")
a1.axvline(18.5, color=RED, lw=1, ls=":")
a1.text(18.2, 1e-3, T("数值秩 18", "numerical rank 18"), color=RED, fontsize=9, ha="right")
a1.set_xlabel(T("序号 i", "index i"))
a1.set_ylabel(T("奇异值 σᵢ", "singular value σᵢ"))
a1.set_title(T("(a) 标定雅可比矩阵的奇异值", "(a) Singular values of the calibration Jacobian"), fontsize=10)
r0 = y - fk_all(NOMINAL, Q)
c = U.T @ r0
ks = np.arange(1, 23)
nrm, res = [], []
for k in ks:
    dp = Vt[:k].T @ (c[:k] / s[:k])
    nrm.append(np.linalg.norm(dp))
    res.append(np.linalg.norm(J @ dp - r0) / np.sqrt(len(r0)) * 1000)
a2.semilogy(ks, nrm, "o-", color=RED, ms=4, label=T("修正量的范数 ‖δp‖", "size of correction ‖δp‖"))
a2.semilogy(ks, res, "s-", color=BLUE, ms=4, label=T("残差的均方根 / mm", "RMS residual / mm"))
a2.axhline(0.05, color=MUTED, ls="--", lw=1)
a2.text(1, 0.06, T("测量噪声 0.05 mm", "measurement noise 0.05 mm"), color=MUTED, fontsize=9)
a2.axvline(18, color=INK, lw=1, ls=":")
a2.set_xlabel(T("保留的奇异值个数 k", "number of singular values kept, k"))
a2.legend(frameon=False, fontsize=9, loc="upper left")
a2.set_title(T("(b) 截断 SVD：k 的选择", "(b) Truncated SVD: choosing k"), fontsize=10)
for a in (a1, a2):
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig23_2_1")
