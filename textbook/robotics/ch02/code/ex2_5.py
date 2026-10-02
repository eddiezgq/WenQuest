"""2.5 节的算例：最小二乘与伪逆。

算例 2.5.1：平面工具中心点（TCP）标定。工具尖端在法兰坐标系中的位置 t、固定顶针在基座坐标系中的位置 c 都未知；
           机器人以 5 个不同姿态让尖端碰到顶针，记下法兰的位置 p_i 和转角 φ_i。每次接触给出 R(φ_i) t − c = −p_i。
           数据由“真值 + 0.3 mm 的随机误差”生成（随机数种子固定），解正规方程，并与 QR、SVD、伪逆三种解法核对。
算例 2.5.2：弹簧秤的直线拟合（生活中的例子）。
算例 2.5.3：平面 3R 臂（第 12 章的尺寸）在 θ = (30°, 60°, −60°) 时，末端要以 0.1 m/s 沿 x 方向运动，
           求关节速度的最小范数解 J⁺v，并与另一个解比较。
另外核对：残差与 A 的各列正交；cond(AᵀA) = cond(A)²；彭罗斯的四个条件；只用 2 次接触与用 5、10 次接触的误差（蒙特卡罗）。
"""
import math

import numpy as np

from _la import L3R, d, jac, rot2
from bookout import out, tex, vec

t_true = np.array([0.120, 0.035])        # m，工具尖端在法兰坐标系中
c_true = np.array([0.650, 0.150])        # m，顶针在基座坐标系中
SIG = 0.0003                             # m，每次接触的位置误差（标准差）


def poses(n):
    return np.radians(np.linspace(-40, 80, n))


def build(phis, ps):
    A = np.vstack([np.hstack([rot2(f), -np.eye(2)]) for f in phis])
    b = np.concatenate([-p for p in ps])
    return A, b


def measure(phis, rng):
    return [c_true - rot2(f) @ t_true + rng.normal(0, SIG, 2) for f in phis]


# ---------------------------------------------------------------- 算例 2.5.1
rng = np.random.default_rng(20261001)
phis = poses(5)
ps = measure(phis, rng)
A, b = build(phis, ps)
AtA, Atb = A.T @ A, A.T @ b
x = np.linalg.solve(AtA, Atb)                                     # 正规方程
r = b - A @ x
assert np.allclose(A.T @ r, 0, atol=1e-12)                        # 残差与各列正交
Q, Rq = np.linalg.qr(A)
x_qr = np.linalg.solve(Rq, Q.T @ b)
x_svd = np.linalg.lstsq(A, b, rcond=None)[0]
x_pinv = np.linalg.pinv(A) @ b
assert np.allclose(x, x_qr) and np.allclose(x, x_svd) and np.allclose(x, x_pinv)
t_hat, c_hat = x[:2], x[2:]
err_t = float(np.linalg.norm(t_hat - t_true)) * 1000              # mm
err_c = float(np.linalg.norm(c_hat - c_true)) * 1000
rms = float(np.sqrt((r ** 2).mean())) * 1000
condA = float(np.linalg.cond(A))
condAtA = float(np.linalg.cond(AtA))
assert abs(condAtA - condA ** 2) / condA ** 2 < 1e-8
# 毕达哥拉斯：任意 x' 的残差平方和 = 最小值 + ‖A(x − x')‖²
xo = x + np.array([0.001, -0.002, 0.0005, 0.001])
assert abs(np.sum((b - A @ xo) ** 2) - (np.sum(r ** 2) + np.sum((A @ (x - xo)) ** 2))) < 1e-15

# 只用 2 次接触：4 个方程、4 个未知数，恰好可解，误差全部进入结果
A2, b2 = build(phis[[0, 4]], [ps[0], ps[4]])
x2 = np.linalg.solve(A2, b2)
err_t2 = float(np.linalg.norm(x2[:2] - t_true)) * 1000

# 蒙特卡罗：t 的估计误差（均方根）随接触次数的变化
mc = {}
rng_mc = np.random.default_rng(7)
for n in (2, 5, 10):
    e = []
    for _ in range(4000):
        ph = poses(n)
        Am, bm = build(ph, measure(ph, rng_mc))
        e.append(np.linalg.lstsq(Am, bm, rcond=None)[0][:2] - t_true)
    mc[n] = float(np.sqrt(np.mean(np.sum(np.array(e) ** 2, axis=1)))) * 1000
assert mc[2] > mc[5] > mc[10]

# ---------------------------------------------------------------- 算例 2.5.2：弹簧秤
m = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])                     # kg
y = np.array([0.3, 10.2, 19.6, 30.4, 40.1, 49.6])                # mm
Al = np.column_stack([m, np.ones_like(m)])
kb = np.linalg.solve(Al.T @ Al, Al.T @ y)
assert np.allclose(kb, np.polyfit(m, y, 1))
rl = y - Al @ kb
assert abs(rl.sum()) < 1e-12 and abs(rl @ m) < 1e-12              # 残差之和为 0，与 m 正交
sse = float(rl @ rl)

# ---------------------------------------------------------------- 算例 2.5.3：冗余臂的最小范数解
th3 = [d(30), d(60), d(-60)]
J = jac(th3, L3R)
v = np.array([0.1, 0.0])
Jp = J.T @ np.linalg.inv(J @ J.T)
assert np.allclose(Jp, np.linalg.pinv(J))
thd = Jp @ v
assert np.allclose(J @ thd, v)
n = np.linalg.svd(J)[2][-1]                                       # 零空间方向（2.6 节）
assert np.allclose(J @ n, 0)
thd_other = thd + 0.2 * n
assert np.allclose(J @ thd_other, v) and np.linalg.norm(thd_other) > np.linalg.norm(thd)
assert abs(thd @ n) < 1e-12                                       # 最小范数解与零空间正交
for M, Mp in ((J, Jp), (A, np.linalg.pinv(A))):                   # 彭罗斯条件
    assert np.allclose(M @ Mp @ M, M) and np.allclose(Mp @ M @ Mp, Mp)
    assert np.allclose((M @ Mp).T, M @ Mp) and np.allclose((Mp @ M).T, Mp @ M)

out(
    phis_deg=", ".join(f"{math.degrees(f):.0f}°" for f in phis),
    P=tex(np.array(ps) * 1000, 1), A_top=tex(A[:2], 4), AtA=tex(AtA, 4), Atb=tex(Atb * 1000, 1),
    t_hat=vec(t_hat * 1000, 2), c_hat=vec(c_hat * 1000, 2), err_t=err_t, err_c=err_c, rms=rms,
    condA=condA, condAtA=condAtA, err_t2=err_t2, mc2=mc[2], mc5=mc[5], mc10=mc[10],
    k=kb[0], b0=kb[1], sse=sse,
    J3=tex(J, 4), Jp=tex(Jp, 4), thd=vec(thd, 4), thd_norm=float(np.linalg.norm(thd)),
    thd_other=vec(thd_other, 4), other_norm=float(np.linalg.norm(thd_other)), n=vec(n, 4),
)
