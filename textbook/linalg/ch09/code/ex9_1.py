"""9.1 节：线性映射的例子——求导、积分、旋转、投影、反射都满足 T(au + bv) = aT(u) + bT(v)；平移不满足（T(0) ≠ 0）。
用随机的系数和向量检验可加性与齐次性。"""
import numpy as np

from _poly import D, I, ptex
from _num import sci
from bookout import out, tex

rng = np.random.default_rng(9)
p, q = np.array([2.0, -1, 3, 0]), np.array([1.0, 4, 0, -2])      # p = 2 − x + 3x²，q = 1 + 4x − 2x³
a, b = 3.0, -2.0
out(p=ptex(p), q=ptex(q), Dp=ptex(D(p)), Dq=ptex(D(q)), comb=ptex(a * p + b * q), Dcomb=ptex(D(a * p + b * q)),
    combD=ptex(a * D(p) + b * D(q)), Ip=ptex(I(p)))
# 2×2 的三个几何映射
t = np.radians(30)
Rot = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
u = np.array([np.cos(t), np.sin(t)])                       # 30° 方向的直线
Proj = np.outer(u, u)
Refl = 2 * Proj - np.eye(2)
out(Rot=tex(Rot, 4), Proj=tex(Proj, 4), Refl=tex(Refl, 4))
err = 0.0
for M in (Rot, Proj, Refl):
    for _ in range(100):
        x, y = rng.normal(size=2), rng.normal(size=2)
        c, d = rng.normal(size=2)
        err = max(err, float(np.abs(M @ (c * x + d * y) - (c * M @ x + d * M @ y)).max()))
out(lin_err=sci(err, 1))
# 平移 T(x) = x + s 不是线性映射
s = np.array([1.0, 0.5])
Tr = lambda x: x + s
x, y = np.array([1.0, 2.0]), np.array([-0.5, 1.0])
out(tr0=tex(Tr(np.zeros(2)), 1), trsum=tex(Tr(x + y), 1), sumtr=tex(Tr(x) + Tr(y), 1))
# AGV：车体坐标中的速度 → 世界坐标中的速度（航向 θ = 30°），是旋转
vb = np.array([0.4, 0.1])
out(vb=tex(vb, 1), vw=tex(Rot @ vb, 4))
