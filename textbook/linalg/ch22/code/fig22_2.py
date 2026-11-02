"""图 22.2.1：(a) 带主元的乔列斯基分解每一步取的主元（剩余的最大对角元）：六个传感器的协方差矩阵（秩 3）在第 4 步骤降到噪声水平；
仓库地面 200 个测点的高斯核矩阵（核长度 3 m）主元平滑衰减，数值秩由阈值决定；
(b) 冗余机械臂 KKT 矩阵的 LDLᵀ 主元：3 个正（关节）、2 个负（约束），与特征值的符号一致（西尔维斯特惯性定理）。"""
import math

import numpy as np

from _fig import BLUE, GREEN, INK, MUTED, RED, T, figure, plt

rng = np.random.default_rng(22021)


def pivots(A):
    A = A.copy()
    n = len(A)
    d = []
    for k in range(n):
        j = k + int(np.argmax(np.diag(A)[k:]))
        piv = A[j, j]
        d.append(piv)
        if piv <= 1e-15 * d[0]:
            break
        A[[k, j]] = A[[j, k]]
        A[:, [k, j]] = A[:, [j, k]]
        r = A[k, k + 1:] / math.sqrt(piv)
        A[k + 1:, k + 1:] -= np.outer(r, r)
    return np.array(d)


F = rng.standard_normal((6, 3))
Sig = F @ F.T + 1e-10 * np.eye(6)
pts = rng.random((200, 2)) * [20.0, 10.0]
D2 = ((pts[:, None, :] - pts[None, :, :]) ** 2).sum(-1)
Kg = np.exp(-D2 / (2 * 3.0 ** 2)) + 1e-12 * np.eye(200)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.4))
d1, d2 = pivots(Sig), pivots(Kg)
a1.semilogy(range(1, len(d1) + 1), d1 / d1[0], "o-", color=RED, label=T("6 个传感器的协方差（真实秩 3）", "covariance of 6 sensors (true rank 3)"))
a1.semilogy(range(1, len(d2) + 1), d2 / d2[0], "-", color=BLUE, label=T("200 个测点的高斯核矩阵", "Gaussian kernel matrix, 200 points"))
a1.axhline(1e-8, color=MUTED, ls="--", lw=1)
a1.text(len(d2) * 0.98, 2e-8, T("阈值 10⁻⁸", "threshold 10⁻⁸"), color=MUTED, fontsize=9, ha="right")
a1.set_xlabel(T("步数 k", "step k"))
a1.set_ylabel(T("第 k 个主元 / 第 1 个主元", "k-th pivot / first pivot"))
a1.legend(frameon=False, fontsize=8.5)
a1.set_title(T("(a) 带主元的乔列斯基分解：主元的衰减给出数值秩", "(a) Pivoted Cholesky: decaying pivots reveal numerical rank"), fontsize=10)
Lk = np.array([0.40, 0.35, 0.25])
q = np.radians([30.0, 60.0, -30.0])
c = np.cumsum(q)
J = np.array([[-np.sum(Lk[j:] * np.sin(c[j:])) for j in range(3)], [np.sum(Lk[j:] * np.cos(c[j:])) for j in range(3)]])
W = np.diag([4.0, 2.0, 1.0])
K = np.block([[W, J.T], [J, np.zeros((2, 2))]])
d = []
A = K.copy()
for k in range(5):
    d.append(A[k, k])
    A[k + 1:, k + 1:] -= np.outer(A[k + 1:, k], A[k, k + 1:]) / A[k, k]
ev = np.sort(np.linalg.eigvalsh(K))[::-1]
xs = np.arange(1, 6)
a2.bar(xs - 0.2, d, width=0.38, color=[GREEN if v > 0 else RED for v in d], label=T("LDLᵀ 的主元 dₖ", "LDLᵀ pivots dₖ"))
a2.bar(xs + 0.2, ev, width=0.38, color=MUTED, label=T("特征值（从大到小）", "eigenvalues (descending)"))
a2.axhline(0, color=INK, lw=0.8)
a2.set_xticks(xs)
a2.set_xticklabels(["1", "2", "3", "4", "5"])
a2.set_xlabel(T("序号（主元：前 3 个对应关节速度，后 2 个对应约束）", "index (pivots: first 3 joints, last 2 constraints)"), fontsize=9)
for xv, v in zip(xs, d):
    a2.text(xv - 0.2, v + (0.08 if v > 0 else -0.25), f"{v:.3g}", ha="center", fontsize=8)
a2.legend(frameon=False, fontsize=8.5)
a2.set_title(T("(b) 冗余机械臂的 KKT 矩阵：3 正 2 负", "(b) KKT matrix of the redundant arm: 3 positive, 2 negative"), fontsize=10)
for a in (a1, a2):
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig22_2_1")
