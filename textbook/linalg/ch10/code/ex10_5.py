"""10.5 节：直线拟合、多项式拟合与多元回归。(a) 夹爪手指的力–变形数据拟合直线 F = k δ + F0；(b) 力传感器零点的温度漂移，
多项式次数从 1 到 11：训练误差一直下降，检验误差先降后升（过拟合）；(c) 关节摩擦辨识 τ = Iα + bω + c sign(ω)，三个参数一次求出。"""
import numpy as np

from _data10 import T_test, T_train, alpha, delta, drift_true, force, omega, tau, y_test, y_train
from _num import sci
from bookout import out, vec

# (a)
A = np.column_stack([np.ones_like(delta), delta])
F0, k = np.linalg.solve(A.T @ A, A.T @ force)
r = force - A @ np.array([F0, k])
out(k=k, F0=F0, rms_a=float(np.sqrt(r @ r / r.size)), n_a=delta.size,
    sums=f"\\sum\\delta_i = {delta.sum():.1f},\\ \\sum\\delta_i^2 = {delta @ delta:.2f},\\ \\sum F_i = {force.sum():.2f},\\ \\sum\\delta_iF_i = {delta @ force:.2f}")
# (b) 多项式次数与误差（自变量先标准化到 [-1, 1]，避免范德蒙德矩阵病态）
xs = lambda T: (T - 40.0) / 20.0
rows = []
for d in range(1, 12):
    V = np.vander(xs(T_train), d + 1, increasing=True)
    c = np.linalg.lstsq(V, y_train, rcond=None)[0]
    tr = np.sqrt(np.mean((V @ c - y_train) ** 2))
    te = np.sqrt(np.mean((np.vander(xs(T_test), d + 1, increasing=True) @ c - y_test) ** 2))
    rows.append((d, tr, te))
best = min(rows, key=lambda r: r[2])
out(table=" ".join(f"{d}:{tr*1000:.1f}/{te*1000:.1f}" for d, tr, te in rows), best=best[0],
    tr3=rows[2][1] * 1000, te3=rows[2][2] * 1000, tr8=rows[7][1] * 1000, te8=rows[7][2] * 1000, tr11=rows[10][1] * 1000, te11=rows[10][2] * 1000, tr1=rows[0][1] * 1000, te1=rows[0][2] * 1000)
out(rows=[[d, round(float(tr) * 1000, 1), round(float(te) * 1000, 1)] for d, tr, te in rows])
# 原始温度（不标准化）作自变量时 AᵀA 的条件数
V8 = np.vander(T_train, 9, increasing=True)
V8s = np.vander(xs(T_train), 9, increasing=True)
out(cond_raw=sci(float(np.linalg.cond(V8.T @ V8)), 0), cond_std=sci(float(np.linalg.cond(V8s.T @ V8s)), 0))
# (c) 多元回归
X = np.column_stack([alpha, omega, np.sign(omega)])
th = np.linalg.solve(X.T @ X, X.T @ tau)
res = tau - X @ th
R2 = 1 - (res @ res) / np.sum((tau - tau.mean()) ** 2)
out(I=th[0], b=th[1], c=th[2], R2=float(R2), rms_c=float(np.sqrt(res @ res / res.size)), n_c=tau.size)
