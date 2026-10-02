"""2.6 节的算例：零空间与值域。

算例 2.6.1：平面 3R 臂（第 12 章的尺寸）在 θ = (30°, 60°, −60°) 时，末端位置的雅可比矩阵 J 是 2×3 矩阵。
           求秩、零空间（两行的叉积给出零空间方向，与 SVD 核对）；让末端不动、θ1 从 10° 变到 50° 的自运动
           （逐个 θ1 用 2R 逆解求 θ2、θ3），核对自运动的切向就是零空间方向。
算例 2.6.2：手臂伸直（θ = (30°, 0, 0)）时，秩降为 1，零空间变成二维；四个基本子空间的维数和正交关系。
算例 2.6.3：零空间投影 P = I − J⁺J：J P = 0、P² = P、Pᵀ = P；在最小范数解上叠加 P z，末端速度不变。
"""
import math

import numpy as np

from _la import L3R, arm_points, d, jac
from bookout import out, tex, vec

L1, L2, L3 = L3R
th = np.array([d(30), d(60), d(-60)])
J = jac(th, L3R)
rank = int(np.linalg.matrix_rank(J))
n = np.cross(J[0], J[1])
n /= np.linalg.norm(n)
n = n if n[2] > 0 else -n
n_svd = np.linalg.svd(J)[2][-1]
assert np.allclose(J @ n, 0) and abs(abs(n @ n_svd) - 1) < 1e-12
assert rank == 2 and rank + 1 == 3                              # 秩 + 零化度 = 列数
tip = arm_points(th, L3R)[-1]


def ik_rest(t1, p):
    """给定 θ1 和末端位置 p，用 2R 逆解求 θ2、θ3（与算例同一支：θ3 < 0）。"""
    e = np.array([L1 * math.cos(t1), L1 * math.sin(t1)])
    q = p - e
    r2 = q @ q
    c3 = (r2 - L2 ** 2 - L3 ** 2) / (2 * L2 * L3)
    t3 = -math.acos(max(-1.0, min(1.0, c3)))
    a = math.atan2(q[1], q[0]) - math.atan2(L3 * math.sin(t3), L2 + L3 * math.cos(t3))
    return np.array([t1, a - t1, t3])


assert np.allclose(ik_rest(th[0], tip), th)
family = {deg: ik_rest(d(deg), tip) for deg in (27, 40, 55)}
for q in family.values():
    assert np.allclose(arm_points(q, L3R)[-1], tip)               # 末端没有动
h = 1e-6
tangent = (ik_rest(th[0] + h, tip) - ik_rest(th[0] - h, tip)) / (2 * h)
tangent /= np.linalg.norm(tangent)
assert abs(abs(tangent @ n) - 1) < 1e-8                          # 自运动的切向 = 零空间方向

# ---------------------------------------------------------------- 算例 2.6.2：伸直
th0 = np.array([d(30), 0.0, 0.0])
J0 = jac(th0, L3R)
U0, s0, Vt0 = np.linalg.svd(J0)
rank0 = int(np.sum(s0 > 1e-12))
assert rank0 == 1
N0 = Vt0[rank0:].T                                                # 零空间的一组标准正交基（3×2）
assert np.allclose(J0 @ N0, 0)
left0 = U0[:, rank0:]                                             # 左零空间：末端做不到的速度方向
radial = np.array([math.cos(d(30)), math.sin(d(30))])
assert abs(abs(left0[:, 0] @ radial) - 1) < 1e-12
assert np.allclose(J0.T @ left0, 0)
row0 = Vt0[:rank0].T
assert np.allclose(row0.T @ N0, 0)                                # 行空间 ⟂ 零空间
# 零空间的一个具体基：关节 1、2 各自与关节 3 配合，使末端不动
n_a = np.array([0.0, L3, -(L2 + L3)])                            # 只动关节 2、3
n_b = np.array([L2 + L3, -(L1 + L2 + L3), 0.0])                  # 只动关节 1、2
assert np.allclose(J0 @ n_a, 0) and np.allclose(J0 @ n_b, 0)
assert np.linalg.matrix_rank(np.column_stack([n_a, n_b])) == 2

# ---------------------------------------------------------------- 算例 2.6.3：零空间投影
Jp = np.linalg.pinv(J)
P = np.eye(3) - Jp @ J
assert np.allclose(J @ P, 0) and np.allclose(P @ P, P) and np.allclose(P, P.T)
assert np.allclose(P, np.outer(n, n))
v = np.array([0.1, 0.0])
z = np.array([0.0, 0.0, 1.0])                                    # 希望关节 3 向 0 靠拢（正方向）
thd0 = Jp @ v
thd = thd0 + P @ z
assert np.allclose(J @ thd, v)

out(
    J=tex(J, 4), rank=rank, n=vec(n, 4), tip=vec(tip, 4),
    q27=", ".join(f"{math.degrees(a):.1f}°" for a in family[27]), q40=", ".join(f"{math.degrees(a):.1f}°" for a in family[40]),
    q55=", ".join(f"{math.degrees(a):.1f}°" for a in family[55]),
    J0=tex(J0, 4), s0=s0[0], rank0=rank0, N0=tex(N0, 4), left0=vec(left0[:, 0], 4), n_a=vec(n_a, 3), n_b=vec(n_b, 3),
    P=tex(P, 4), thd0=vec(thd0, 4), thd=vec(thd, 4), Pz=vec(P @ z, 4),
)
