"""10.1 节：正交子空间与正交补。平面 V: x + y + z = 0 的正交补是直线 span{(1, 1, 1)}；任一向量唯一地分解为 v + w（v ∈ V，w ∈ V⊥），
勾股定理 ‖b‖² = ‖v‖² + ‖w‖²。接触任务：末端贴着斜面滑动，允许的速度在切平面里，接触力沿法线，两者正交，功率为零。"""
import numpy as np
import scipy.linalg as sla

from bookout import out, vec

n = np.array([1.0, 1, 1])
V = sla.null_space(n[None, :])                 # V 的一组（标准正交）基
b = np.array([1.0, 2, 6])
w = (n @ b) / (n @ n) * n                       # b 在 V⊥ 上的分量
v = b - w
out(b=vec(b, 0), w=vec(w, 0), v=vec(v, 0), vn=float(v @ n), dimV=V.shape[1],
    pyth_l=float(b @ b), pyth_r=float(v @ v + w @ w))
# 两个子空间正交但不互为正交补：x 轴与 y 轴（在 ℝ³ 中）
ex, ey = np.array([1.0, 0, 0]), np.array([0.0, 1, 0])
out(xy=float(ex @ ey))
# 接触：斜面法向 nrm（与水平面成 20°），末端速度在切平面内，接触力沿法向
t = np.radians(20)
nrm = np.array([-np.sin(t), 0, np.cos(t)])
t1, t2 = np.array([np.cos(t), 0, np.sin(t)]), np.array([0.0, 1, 0])   # 切平面的基：沿坡向上、沿坡水平
vel = 0.05 * t1 + 0.02 * t2                    # 一个允许的末端速度（m/s）
f = 15.0 * nrm                                 # 15 N 的接触力
out(nrm=vec(nrm, 4), vel=vec(vel, 4), f=vec(f, 3), t1=vec(t1, 4), t1n=float(t1 @ nrm), power=round(float(f @ vel), 12) + 0.0)
