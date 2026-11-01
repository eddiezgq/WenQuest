"""19.3 节：主成分分析与 SVD。中心化数据矩阵的 SVD 与协方差矩阵特征分解的对应；
为什么用 SVD：(1) 单精度下“先求平方和再减”的方差公式失效；(2) 形成 XᵀX 后小奇异值只剩 √ε 的精度；
样本数少于维数时的格拉姆矩阵算法；主成分直线（总体最小二乘）与普通最小二乘：AGV 激光雷达扫到的一面墙。"""
import math

import numpy as np

from _num import fix_sign, sci
from _qc import N_I, X_I
from bookout import out, vec

# (1) SVD 与特征分解的对应（六项检测，标准化后）
X = X_I
Xc = X - X.mean(axis=0)
Z = Xc / Xc.std(axis=0, ddof=1)
U, sig, Vt = np.linalg.svd(Z, full_matrices=False)
V = fix_sign(Vt.T)
w, Ve = np.linalg.eigh(Z.T @ Z / (N_I - 1))
w, Ve = w[::-1], fix_sign(Ve[:, ::-1])
out(sig=vec(sig, 2), lam_from_sig=vec(sig ** 2 / (N_I - 1), 3), dV=float(np.max(np.abs(V - Ve))))
T1 = Z @ V
U = U * np.sign(np.sum(U * (Z @ V), axis=0))
assert np.allclose(T1, U * sig)

# (2) 单精度的方差：轴承位直径 35.010 mm 附近，标准差约 4 μm
rng = np.random.default_rng(20261103)
d = 35.010 + 0.004 * rng.standard_normal(N_I)
true_var = float(np.var(d, ddof=1))
d32 = d.astype(np.float32)
n32 = np.float32(N_I)
one_pass = (np.sum(d32 * d32, dtype=np.float32) - np.sum(d32, dtype=np.float32) ** 2 / n32) / np.float32(N_I - 1)
m32 = np.sum(d32, dtype=np.float32) / n32
two_pass = np.sum((d32 - m32) ** 2, dtype=np.float32) / np.float32(N_I - 1)
out(true_sd_um=1000 * math.sqrt(true_var), one_pass=sci(float(one_pass) + 1e-30, 2), one_pass_v=float(one_pass),
    two_pass_sd_um=1000 * math.sqrt(float(two_pass)), one_pass_sd_um=1000 * math.sqrt(abs(float(one_pass))),
    one_pass_ratio=math.sqrt(abs(float(one_pass)) / true_var), true_var=sci(true_var, 2), two_pass=sci(float(two_pass), 2),
    eps32=sci(float(np.finfo(np.float32).eps), 1))

# (3) 小奇异值：第 18.3 节的三个尺寸 a、b、c = a + b（精确线性相关），σ₃ 理论上为 0
rng = np.random.default_rng(1810)
a = 42.0 + 0.05 * rng.standard_normal(50)
b = 31.5 + 0.04 * rng.standard_normal(50)
A3 = np.c_[a, b, a + b]
A3c = A3 - A3.mean(axis=0)
s_svd = np.linalg.svd(A3c, compute_uv=False)
lam = np.linalg.eigvalsh(A3c.T @ A3c)[::-1]
s_eig3 = math.sqrt(abs(lam[2]))
out(s1=float(s_svd[0]), s3_svd=sci(float(s_svd[2]) + 1e-30, 0), lam3=sci(float(lam[2]), 0), s3_eig=sci(s_eig3, 0),
    rel_svd=sci(float(s_svd[2] / s_svd[0]) + 1e-30, 0), rel_eig=sci(s_eig3 / float(s_svd[0]), 0), big=sci(s_eig3 / float(s_svd[2]), 0),
    eps64=sci(float(np.finfo(float).eps), 1), sqrt_eps=sci(math.sqrt(np.finfo(float).eps), 1))

# (4) 样本少、维数高：N = 20 张 32×32 的图（p = 1024），只解 20×20 的格拉姆矩阵
rng = np.random.default_rng(7)
Ng, p = 20, 1024
Y = rng.standard_normal((Ng, 5)) @ rng.standard_normal((5, p)) + 0.1 * rng.standard_normal((Ng, p))
Yc = Y - Y.mean(axis=0)
G = Yc @ Yc.T
wg, Ug = np.linalg.eigh(G)
wg, Ug = wg[::-1], Ug[:, ::-1]
sg = np.sqrt(np.maximum(wg, 0))
Vg = Yc.T @ Ug[:, :5] / sg[:5]                      # (18.2.9)：vᵢ = Aᵀuᵢ/σᵢ
_, sy, Vty = np.linalg.svd(Yc, full_matrices=False)
assert np.allclose(sg[:5], sy[:5]) and np.allclose(np.abs(Vg.T @ Vty[:5].T), np.eye(5), atol=1e-8)
out(Ng=Ng, p=p, rankYc=int(np.sum(sy > 1e-10 * sy[0])), size_cov=p * p, size_gram=Ng * Ng)

# (5) 激光雷达扫到的墙：AGV 沿墙行驶，墙与车体的 y 轴平行（与 x 轴成 90°），测点在两个方向都有 5 mm 的误差
rng = np.random.default_rng(2026)
th = math.radians(90)
dirv = np.array([math.cos(th), math.sin(th)])
tt = np.linspace(-0.6, 0.6, 40)
P = np.array([2.0, 0.5]) + np.outer(tt, dirv) + 0.005 * rng.standard_normal((40, 2))
Pc = P - P.mean(axis=0)
_, sp_, Vtp = np.linalg.svd(Pc)
v1 = Vtp[0]
ang_tls = math.degrees(math.atan2(v1[1], v1[0])) % 180
k_ols = float(np.polyfit(P[:, 0], P[:, 1], 1)[0])
ang_ols = math.degrees(math.atan(k_ols)) % 180
nrm = Vtp[1]
dist_tls = float(np.sqrt(np.mean((Pc @ nrm) ** 2)))
# 在墙的两端（离中点 0.6 m），拟合直线偏离真实墙面多远
end_tls = 1000 * 0.6 * abs(math.sin(math.radians(ang_tls - 90)))
end_ols = 1000 * 0.6 * abs(math.sin(math.radians(ang_ols - 90)))
out(ang_tls=ang_tls, ang_ols=ang_ols, k_ols=k_ols, rms_tls_mm=1000 * dist_tls, end_tls=end_tls, end_ols=end_ols,
    nrm=vec(fix_sign(nrm[:, None])[:, 0], 3), sp=vec(sp_, 3))
