"""2.2 节的算例：线性变换的矩阵、行列式与面积、相似变换下的不变量。

算例 2.2.1：柔顺手腕在自身坐标系 {b} 中的刚度矩阵 K_b = diag(2000, 500) N/m，{b} 相对基座 {s} 转过 30°。
           求 K_s，沿 x_s 推 1 mm 时的回复力；在 {b} 中再算一遍核对；比较 tr、det。
算例 2.2.2：同一个变换换到一组斜的基下（P 的两列不垂直），相似矩阵的迹、行列式、特征多项式都不变。
另外核对：变换矩阵的各列 = 基向量的像；线性；平行四边形面积 = |det|（拉格朗日恒等式）；四种基本变换的行列式。
"""
import math

import numpy as np

from _la import d, rot2
from bookout import out, tex, vec

# ---------------------------------------------------------------- 基本变换
TR = {"rot": rot2(d(30)), "shear": np.array([[1.0, 0.5], [0.0, 1.0]]), "scale": np.array([[1.5, 0.0], [0.0, 0.5]]),
      "refl": np.array([[1.0, 0.0], [0.0, -1.0]]), "proj": np.array([[1.0, 0.0], [0.0, 0.0]])}
dets = {k: float(np.linalg.det(A)) for k, A in TR.items()}
e1, e2 = np.array([1.0, 0.0]), np.array([0.0, 1.0])
rng = np.random.default_rng(2)
for A in TR.values():
    assert np.allclose(A @ e1, A[:, 0]) and np.allclose(A @ e2, A[:, 1])        # 各列 = 基向量的像
    x, y, al, be = rng.normal(size=2), rng.normal(size=2), 0.7, -1.3
    assert np.allclose(A @ (al * x + be * y), al * (A @ x) + be * (A @ y))      # 线性
    a, b = A[:, 0], A[:, 1]                                                   # 拉格朗日恒等式：|a|²|b|² − (a·b)² = (det)²
    assert abs((a @ a) * (b @ b) - (a @ b) ** 2 - np.linalg.det(A) ** 2) < 1e-12

# ---------------------------------------------------------------- 算例 2.2.1
Kb = np.diag([2000.0, 500.0])                                    # N/m
phi = d(30)
R = rot2(phi)                                                    # R_sb：各列是 {b} 的两根轴在 {s} 中的分量
Ks = R @ Kb @ R.T
delta_s = np.array([0.001, 0.0])                                 # 沿 x_s 推 1 mm
f_s = Ks @ delta_s
delta_b = R.T @ delta_s
f_b = Kb @ delta_b
assert np.allclose(R @ f_b, f_s)                                 # 两条路算出同一个力
f_ang = math.degrees(math.atan2(f_s[1], f_s[0]))
assert abs(np.trace(Ks) - np.trace(Kb)) < 1e-9 and abs(np.linalg.det(Ks) - np.linalg.det(Kb)) < 1e-6
assert np.allclose(Ks, Ks.T)

# ---------------------------------------------------------------- 算例 2.2.2：斜的基
P = np.array([[1.0, 0.5], [0.0, 1.0]])                            # 新基向量 (1, 0)、(0.5, 1)，不垂直
Kp = np.linalg.inv(P) @ Ks @ P
assert abs(np.trace(Kp) - np.trace(Ks)) < 1e-9 and abs(np.linalg.det(Kp) - np.linalg.det(Ks)) < 1e-6
assert np.allclose(np.poly(Kp), np.poly(Ks))                      # 特征多项式相同
assert not np.allclose(Kp, Kp.T)                                  # 斜基下不再对称

out(
    det_rot=dets["rot"], det_shear=dets["shear"], det_scale=dets["scale"], det_refl=dets["refl"], det_proj=dets["proj"],
    R=tex(R, 4), Ks=tex(Ks, 1), Ks11=Ks[0, 0], Ks12=Ks[0, 1], Ks22=Ks[1, 1],
    f_s=vec(f_s, 4), fx=f_s[0], fy=f_s[1], f_ang=f_ang, delta_b=vec(delta_b * 1000, 4), f_b=vec(f_b, 4),
    trK=float(np.trace(Ks)), detK=float(np.linalg.det(Ks)),
    Kp=tex(Kp, 1), trKp=float(np.trace(Kp)), detKp=float(np.linalg.det(Kp)),
)
