"""14.5 节：主轴定理。
二次曲线 5x² + 4xy + 8y² = 36：矩阵 [[5, 2], [2, 8]] 的特征值 4、9，主轴 (2, −1)/√5、(1, 2)/√5，在主轴坐标下 4u² + 9v² = 36，半轴 3 和 2。
机器人：AGV 定位误差的协方差 Σ = [[4, 2], [2, 3]] cm²：误差椭圆 xᵀΣ⁻¹x = c 的主轴是 Σ 的特征向量，半轴 √(cλᵢ)；
95% 置信椭圆 c = 5.991（自由度 2 的卡方分布）。随机抽取 10⁵ 个误差样本，落在椭圆内的比例接近 95%；
最不确定的方向与标准差。"""
import numpy as np

from _num import fix_sign
from bookout import out, vec

A = np.array([[5.0, 2], [2, 8]])
w, Q = np.linalg.eigh(A); Q = fix_sign(Q)
out(lamA=", ".join(f"{x:.0f}" for x in w), qa=vec(Q[:, 0] * np.sqrt(5), 0), qb=vec(Q[:, 1] * np.sqrt(5), 0), semi=", ".join(f"{np.sqrt(36 / x):.0f}" for x in w[::-1]),
    tilt=float(np.degrees(np.arctan2(Q[1, 1], Q[0, 1]))))
S = np.array([[4.0, 2], [2, 3]])
ws, Qs = np.linalg.eigh(S); Qs = fix_sign(Qs)
c95 = -2 * np.log(0.05)                        # 自由度 2 的卡方分布 95% 分位数
from scipy.stats import chi2
out(c3=float(chi2.ppf(0.95, 3)))
rng = np.random.default_rng(145)
X = rng.multivariate_normal([0, 0], S, size=100000)
inside = np.mean(np.einsum("ij,jk,ik->i", X, np.linalg.inv(S), X) <= c95)
out(lamS=vec(ws, 3), qs_max=vec(Qs[:, 1], 4), ang_max=float(np.degrees(np.arctan2(Qs[1, 1], Qs[0, 1]))), sd_max=float(np.sqrt(ws[1])), sd_min=float(np.sqrt(ws[0])),
    c95=float(c95), a95=float(np.sqrt(c95 * ws[1])), b95=float(np.sqrt(c95 * ws[0])), inside=float(100 * inside), sdx=float(np.sqrt(S[0, 0])), sdy=float(np.sqrt(S[1, 1])))
