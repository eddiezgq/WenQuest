"""15.7 节：半正定矩阵与协方差矩阵。
(1) 格拉姆矩阵 AᵀA 半正定，秩 = A 的秩（5×3、秩 2 的 A：一个零特征值）；
(2) 样本协方差矩阵半正定；样本数不超过维数时必然奇异；
(3) 三个传感器的相关系数分别用不同时间段的数据两两估计：C = [[1, 0.9, 0.1], [0.9, 1, 0.9], [0.1, 0.9, 1]] 不是半正定的，
    组合 v = (1, −1, 1) 的“方差” vᵀCv < 0；把负特征值截成 0 再把对角元缩放回 1，得到最接近的合法相关矩阵（一种常用修复）；
(4) 勒夫纳序与高斯–马尔可夫定理（10.6 节）：直线拟合 y = c₀ + c₁t，t = 0, 1, …, 9，噪声标准差 σ = 1。
    最小二乘的协方差 P_LS = σ²(AᵀA)⁻¹；另一个无偏估计（只用前后各 3 个点的平均值连线）的协方差 P₂；P₂ − P_LS 半正定。"""
import numpy as np

from bookout import out, tex, vec

rng = np.random.default_rng(157)
# (1)
A = rng.normal(size=(5, 2)) @ rng.normal(size=(2, 3))
lg = np.linalg.eigvalsh(A.T @ A)
out(rankA=int(np.linalg.matrix_rank(A)), lamG=vec(lg, 3), lamG0=float(abs(lg[0])))
# (2) 样本协方差
for n in (2, 3, 4, 50):
    X = rng.normal(size=(n, 3))
    out(**{f"rank_n{n}": int(np.linalg.matrix_rank(np.cov(X.T))), f"min_n{n}": float(np.linalg.eigvalsh(np.cov(X.T))[0])})
# (3) 两两估计的相关矩阵
C = np.array([[1.0, 0.9, 0.1], [0.9, 1, 0.9], [0.1, 0.9, 1]])
lc, Vc = np.linalg.eigh(C)
v = np.array([1.0, -1, 1])
out(lamC=vec(lc, 3), vCv=float(v @ C @ v), minors=", ".join(f"{np.linalg.det(C[:j, :j]):.2f}" for j in (1, 2, 3)))
Cp = Vc @ np.diag(np.maximum(lc, 0)) @ Vc.T
dsc = 1 / np.sqrt(np.diag(Cp))
Cf = Cp * np.outer(dsc, dsc)
out(Cf=tex(Cf, 3), c12=float(Cf[0, 1]), c13=float(Cf[0, 2]), lamCf=vec(np.linalg.eigvalsh(Cf), 3), vCfv=float(v @ Cf @ v))
# (4) 勒夫纳序：高斯–马尔可夫
t = np.arange(10.0)
Am = np.column_stack([np.ones(10), t])
P_ls = np.linalg.inv(Am.T @ Am)
# 估计 2：前三个点的平均 (t̄₁, ȳ₁)，后三个点的平均 (t̄₂, ȳ₂)，过这两点的直线。写成 c = W y（W 为 2×10）
w1 = np.r_[np.ones(3), np.zeros(7)] / 3
w2 = np.r_[np.zeros(7), np.ones(3)] / 3
tb1, tb2 = w1 @ t, w2 @ t
slope = (w2 - w1) / (tb2 - tb1)
icpt = w1 - tb1 * slope
W = np.vstack([icpt, slope])
out(unbiased=bool(np.allclose(W @ Am, np.eye(2))))
P2 = W @ W.T
D = P2 - P_ls
out(P_ls=tex(P_ls, 4), P2=tex(P2, 4), lamD=vec(np.linalg.eigvalsh(D), 4),
    sd_ls=float(np.sqrt(P_ls[1, 1])), sd2=float(np.sqrt(P2[1, 1])))
# 任意方向 u：uᵀP₂u ≥ uᵀP_LS u（例如预测 t = 12 处的值，u = (1, 12)）
u = np.array([1.0, 12])
out(var12_ls=float(u @ P_ls @ u), var12_2=float(u @ P2 @ u))
