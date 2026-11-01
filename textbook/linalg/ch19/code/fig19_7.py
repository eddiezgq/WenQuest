"""图 19.7.1：一个录错的数把主成分拉偏。第一主成分的载荷：原始数据、温升 12.6 K 录成 126 K 之后、用 T² 剔除之后。
图 19.7.2：车间顶棚相机的视频（第 15、40、65 帧）。从左到右：原始帧 M、PCP 的低秩部分 L（背景）、稀疏部分 S（AGV）、
截断 SVD（前两个奇异值）得到的“背景”——AGV 留下了一道拖影。"""
import numpy as np
from scipy import stats

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt
from _num import fix_sign
from _qc import N_I, SHORT, SHORT_EN, X_I
from _video import H, W, pcp, video


def pc1(X):
    Xc = X - X.mean(axis=0)
    Z = Xc / Xc.std(axis=0, ddof=1)
    w, V = np.linalg.eigh(Z.T @ Z / (len(X) - 1))
    return fix_sign(V[:, ::-1])[:, 0]


Xb = X_I.copy()
Xb[57, 3] = round(Xb[57, 3], 1) * 10
keep = np.ones(N_I, bool)
while True:
    Xk = Xb[keep]
    n = len(Xk)
    Dd = Xb - Xk.mean(axis=0)
    T2 = np.einsum("ij,jk,ik->i", Dd, np.linalg.inv(np.cov(Xk.T)), Dd)
    lim = (n - 1) ** 2 / n * stats.beta.ppf(1 - 0.0027, 3, (n - 7) / 2)
    new = keep & (T2 > lim)
    if not new.any():
        break
    keep &= ~new
fig, ax = plt.subplots(figsize=(7.5, 3.6))
x = np.arange(6)
for j, (v, col, lab) in enumerate(((pc1(X_I), BLUE, T("原始数据", "clean data")), (pc1(Xb), RED, T("一个数录错之后", "with one typo")),
                                   (pc1(Xb[keep]), GREEN, T("用 T² 剔除之后", "after T² screening")))):
    ax.bar(x + (j - 1) * 0.26, v, width=0.26, color=col, label=lab)
ax.axhline(0, color=INK, lw=0.6)
ax.set_xticks(x)
ax.set_xticklabels(T(SHORT, SHORT_EN))
ax.set_ylabel(T("第一主成分的载荷", "loading of PC 1"))
ax.legend(frameon=False, fontsize=9, ncol=3, loc="upper left")
ax.set_ylim(-0.1, 0.85)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig19_7_1")

M, B, F, mask = video()
L, S, r, it = pcp(M)
U, sg, Vt = np.linalg.svd(M, full_matrices=False)
L2 = (U[:, :2] * sg[:2]) @ Vt[:2]
fig, ax = plt.subplots(3, 4, figsize=(10.0, 5.6))
heads = [T("原始帧 M", "frame M"), T("低秩部分 L（背景）", "low-rank L (background)"), T("稀疏部分 E（前景）", "sparse E (foreground)"),
         T("截断 SVD 的“背景”", "truncated-SVD background")]
for row, k in enumerate((15, 40, 65)):
    imgs = [M[:, k], L[:, k], np.abs(S[:, k]), L2[:, k]]
    for col in range(4):
        a = ax[row, col]
        if col == 2:
            a.imshow(imgs[col].reshape(H, W), cmap="gray_r", vmin=0, vmax=0.6)
        else:
            a.imshow(imgs[col].reshape(H, W), cmap="gray", vmin=0, vmax=1)
        a.set_xticks([])
        a.set_yticks([])
        if row == 0:
            a.set_title(heads[col], fontsize=9.5)
        if col == 0:
            a.set_ylabel(T(f"第 {k + 1} 帧", f"frame {k + 1}"), fontsize=9.5)
fig.tight_layout()
figure(fig, "fig19_7_2")
