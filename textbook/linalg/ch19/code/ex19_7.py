"""19.7 节：鲁棒主成分分析。(1) 200 件检测记录里有一个录错的数（第 58 件的温升 12.6 K 录成 126 K）：主成分和相关系数被拉偏；
用 T² 剔除后重新估计。(2) 车间顶棚相机的视频：主成分追踪（PCP）把它分成低秩的背景和稀疏的 AGV，
与直接取前两个奇异值（截断 SVD）比较。"""
import numpy as np
from scipy import stats

from _num import fix_sign
from _qc import N_I, X_I
from _video import H, NF, W, pcp, video
from bookout import out, vec


def pca(X):
    Xc = X - X.mean(axis=0)
    s = Xc.std(axis=0, ddof=1)
    Z = Xc / s
    w, V = np.linalg.eigh(Z.T @ Z / (len(X) - 1))
    return w[::-1], fix_sign(V[:, ::-1]), np.corrcoef(X.T)


# (1) 一个录错的数
i_bad = 57
Xb = X_I.copy()
true_val = Xb[i_bad, 3]
Xb[i_bad, 3] = round(true_val, 1) * 10
w0, V0, R0 = pca(X_I)
w1, V1, R1 = pca(Xb)
ang = float(np.degrees(np.arccos(min(1.0, abs(V0[:, 0] @ V1[:, 0])))))
out(bad_no=i_bad + 1, true_val=float(round(true_val, 1)), bad_val=float(Xb[i_bad, 3]), ang_pc1=ang,
    r_tv0=float(R0[3, 4]), r_tv1=float(R1[3, 4]), r_nt0=float(R0[2, 3]), r_nt1=float(R1[2, 3]),
    w1_0=float(w0[0]), w1_1=float(w1[0]), v1_1=vec(V1[:, 0], 2), sd_t0=float(X_I[:, 3].std(ddof=1)), sd_t1=float(Xb[:, 3].std(ddof=1)))
# 用 T² 剔除：回头检查第一阶段数据，超出限的剔掉，重新估计，直到没有新的超限点
p, alpha = 6, 0.0027
keep = np.ones(N_I, bool)
rounds = 0
while True:
    rounds += 1
    Xk = Xb[keep]
    n = len(Xk)
    D = Xb - Xk.mean(axis=0)
    T2 = np.einsum("ij,jk,ik->i", D, np.linalg.inv(np.cov(Xk.T)), D)
    lim = (n - 1) ** 2 / n * stats.beta.ppf(1 - alpha, p / 2, (n - p - 1) / 2)
    new = keep & (T2 > lim)
    if rounds == 1:
        out(t2_bad=float(T2[i_bad]), lim1=float(lim))
    if not new.any():
        break
    keep &= ~new
w2, V2, R2 = pca(Xb[keep])
others = [int(i) + 1 for i in np.where(~keep)[0] if i != i_bad]
out(removed=int(N_I - keep.sum()), others="、".join(str(i) for i in others), rounds=rounds, ang_fix=float(np.degrees(np.arccos(min(1.0, abs(V0[:, 0] @ V2[:, 0]))))),
    r_tv2=float(R2[3, 4]))

# (2) 视频：背景与前景
M, B, F, mask = video()
L, S, r, it = pcp(M)
sL = np.linalg.svd(L, compute_uv=False)
fg = np.abs(S) > 0.05
U, sg, Vt = np.linalg.svd(M, full_matrices=False)
L2 = (U[:, :2] * sg[:2]) @ Vt[:2]
fg2 = np.abs(M - L2) > 0.05
out(hv=H, wv=W, nfr=NF, m_rows=H * W, frac_fg=float(100 * mask.mean()), lam_pcp=float(1 / np.sqrt(H * W)), iters=it,
    sL1=float(sL[0]), sL2=float(sL[1]), sL3=float(sL[2]),
    err_pcp=float(100 * np.linalg.norm(L - B) / np.linalg.norm(B)), err_svd=float(100 * np.linalg.norm(L2 - B) / np.linalg.norm(B)),
    ghost_pcp=float(np.abs(L - B).max()), ghost_svd=float(np.abs(L2 - B).max()),
    rec_pcp=float(100 * (fg & mask).sum() / mask.sum()), fp_pcp=float(100 * (fg & ~mask).sum() / (~mask).sum()),
    rec_svd=float(100 * (fg2 & mask).sum() / mask.sum()), fp_svd=float(100 * (fg2 & ~mask).sum() / (~mask).sum()),
    sM=vec(sg[:4], 1))
