"""19.6 节：多元统计过程控制。第一阶段 200 件受控产品估计均值与协方差；第二阶段 60 件（第 31 件起用错了润滑油）：
六张单变量控制图与霍特林 T² 图的比较；T² 按主成分分解；变量贡献；基于主成分的 T²ₖ 与 SPE（Q 统计量）。"""
import math

import numpy as np
from scipy import stats

from _num import fix_sign
from _qc import FAULT_OIL, N_I, N_II, SHORT, START_II, X_I, X_II
from bookout import out, vec

p = 6
alpha = 0.0027
m = X_I.mean(axis=0)
S = np.cov(X_I.T)
s = np.sqrt(np.diag(S))
Si = np.linalg.inv(S)

# 控制限：第二阶段（新产品）用 F 分布；样本很多时接近 χ²
ucl = p * (N_I + 1) * (N_I - 1) / (N_I * (N_I - p)) * stats.f.ppf(1 - alpha, p, N_I - p)
ucl_chi = stats.chi2.ppf(1 - alpha, p)
# 第一阶段（回头检查建模数据本身）用贝塔分布
ucl_I = (N_I - 1) ** 2 / N_I * stats.beta.ppf(1 - alpha, p / 2, (N_I - p - 1) / 2)
D1 = X_I - m
T2_I = np.einsum("ij,jk,ik->i", D1, Si, D1)
out(alpha=alpha, ucl=float(ucl), ucl_chi=float(ucl_chi), ucl_I=float(ucl_I), nI_alarm=int(np.sum(T2_I > ucl_I)),
    fa6=float(100 * (1 - (1 - alpha) ** 6)), fa1=float(100 * alpha), F=float(stats.f.ppf(1 - alpha, p, N_I - p)))

# 第二阶段
D = X_II - m
T2 = np.einsum("ij,jk,ik->i", D, Si, D)
Zs = D / s
ind = np.abs(Zs) > 3
a, b = slice(0, START_II), slice(START_II, N_II)
out(n2=N_II, start=START_II + 1, t2_a=int(np.sum(T2[a] > ucl)), t2_b=int(np.sum(T2[b] > ucl)),
    ind_a=int(np.sum(ind[a].any(axis=1))), ind_b=int(np.sum(ind[b].any(axis=1))), nb=N_II - START_II,
    fault=vec(FAULT_OIL, 1))
for j, nm in ((2, "noise"), (3, "temp"), (4, "vib")):
    out(**{f"ind_{nm}": int(np.sum(ind[b, j]))})
# 第一次报警：T² 与单变量图
first_t2 = int(np.argmax(T2[b] > ucl)) + START_II + 1
first_ind = int(np.argmax(ind[b].any(axis=1))) + START_II + 1
out(first_t2=first_t2, first_ind=first_ind)
# 期望检出率（非中心 χ² 近似）
R = S / np.outer(s, s)
ncp = float(FAULT_OIL @ np.linalg.solve(R, FAULT_OIL))
out(ncp=ncp, power=float(100 * (1 - stats.ncx2.cdf(ucl, p, ncp))))

# T² = ∑ tᵢ²/λᵢ：T² 不随单位改变，用标准化数据的主成分（19.2 节的 λᵢ）分解；故障件的 T² 主要来自哪几个主成分
Z1 = D1 / s
w, Vr = np.linalg.eigh(Z1.T @ Z1 / (N_I - 1))
w, Vr = w[::-1], fix_sign(Vr[:, ::-1])
Z2 = D / s
part = (Z2 @ Vr) ** 2 / w
assert np.allclose(part.sum(axis=1), T2)
share = part[b].sum(axis=0) / part[b].sum()
out(share=vec(100 * share, 0), share_last3=float(100 * share[3:].sum()), w=vec(w, 3))
# 一件“单变量图看不出、T² 报警”的产品
quiet = [i for i in range(START_II, N_II) if T2[i] > ucl and np.abs(Zs[i]).max() < 3]
u = quiet[0]
out(n_quiet=len(quiet), u=u + 1, t2_u=float(T2[u]), z_u=vec(Zs[u], 2), zmax_u=float(np.abs(Zs[u]).max()))

# 变量贡献 cⱼ = dⱼ (S⁻¹d)ⱼ，∑cⱼ = T²
c31 = D[u] * (Si @ D[u])
cb = (D[b] * (D[b] @ Si)).mean(axis=0)
order = np.argsort(-cb)
out(cu=vec(c31, 1), cb=vec(cb, 1), top_c="、".join(SHORT[i] for i in order[:3]))

# 基于主成分（标准化后的相关矩阵）的监控：前 k 个主成分的 T²ₖ 与残差的 SPE
k = 3
Tk = Z2 @ Vr[:, :k]
T2k = np.sum(Tk ** 2 / w[:k], axis=1)
E = Z2 - Tk @ Vr[:, :k].T
spe = np.sum(E ** 2, axis=1)
ucl_k = k * (N_I + 1) * (N_I - 1) / (N_I * (N_I - k)) * stats.f.ppf(1 - alpha, k, N_I - k)
th1, th2, th3 = (np.sum(w[k:] ** i) for i in (1, 2, 3))
h0 = 1 - 2 * th1 * th3 / (3 * th2 ** 2)
za = stats.norm.ppf(1 - alpha)
spe_lim = th1 * (za * math.sqrt(2 * th2 * h0 ** 2) / th1 + 1 + th2 * h0 * (h0 - 1) / th1 ** 2) ** (1 / h0)
E1 = Z1 - (Z1 @ Vr[:, :k]) @ Vr[:, :k].T
spe_I = np.sum(E1 ** 2, axis=1)
out(k=k, ucl_k=float(ucl_k), spe_lim=float(spe_lim), t2k_a=int(np.sum(T2k[a] > ucl_k)), t2k_b=int(np.sum(T2k[b] > ucl_k)),
    spe_a=int(np.sum(spe[a] > spe_lim)), spe_b=int(np.sum(spe[b] > spe_lim)), spe_I=int(np.sum(spe_I > spe_lim)),
    th1=float(th1), th2=float(th2), th3=float(th3), h0=float(h0), za=float(za))
