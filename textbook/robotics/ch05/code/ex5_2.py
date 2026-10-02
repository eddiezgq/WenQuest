"""算例 5.2.1、5.2.2：齐次变换矩阵的写法与两种用法。

5.2.1 写出 T_ws（UR5e 基座相对工作台）与 T_wc（相机相对工作台：高 0.90 m，光轴偏离竖直 15°），
      按“各列是 {b} 的三根轴和原点”逐列填写，再与“R 与 p 分块拼成”的写法比较。
      用 T_wc 把相机测得的一点 (0.05, −0.02, 0.885) m（齿轮坯顶面上）换到 {w}，并把光轴方向 (0, 0, 1) 当作自由矢量换到 {w}：
      点的第四个分量为 1，加上平移；方向的第四个分量为 0，平移自动消失。与定理 5.1.1 逐项比较。
5.2.2 位移算子：工件在台面上绕自身中心转 90° 并平移；验证定理 5.2.3（距离、叉积不变）。
"""
import math

import numpy as np

from _frames import DEG, P_WC, T, T_wc, T_ws, hdir, hom, is_se3, rot_axis, rot_z, texm, trans, vecm
from bookout import out

# ---------------------------------------------------------------- 算例 5.2.1
Tws = T_ws()
Twc = T_wc()
# 逐列填写：{c} 的三根轴在 {w} 中的分量，以及原点
c15, s15 = math.cos(15 * DEG), math.sin(15 * DEG)
xc = np.array([0, 1, 0.0])
yc = np.array([c15, 0, -s15])
zc = np.array([-s15, 0, -c15])
Twc_cols = np.eye(4)
Twc_cols[:3, 0], Twc_cols[:3, 1], Twc_cols[:3, 2], Twc_cols[:3, 3] = xc, yc, zc, P_WC
assert np.allclose(Twc_cols, Twc, atol=1e-15)
assert is_se3(Twc) and is_se3(Tws)
assert abs(np.dot(np.cross(xc, yc), zc) - 1) < 1e-15              # 右手系

p_c = np.array([0.05, -0.02, 0.885])         # 相机测得齿轮坯顶面上的一点，m
p_w = (Twc @ hom(p_c))[:3]
p_w_thm = Twc[:3, :3] @ p_c + Twc[:3, 3]     # 定理 5.1.1
assert np.allclose(p_w, p_w_thm, atol=1e-15)
axis_w = (Twc @ hdir([0, 0, 1]))
assert abs(axis_w[3]) < 1e-15 and np.allclose(axis_w[:3], zc)
# 光轴与台面（z_w = 0）的交点：从相机原点沿光轴走 t，使 z = 0
t_hit = -P_WC[2] / zc[2]
hit = P_WC + t_hit * zc

# ---------------------------------------------------------------- 算例 5.2.2 位移算子
# 工件（120 mm × 80 mm 的矩形垫块）四个角点，起初中心在 (0.80, 0.45) m；绕自身中心转 90°，再整体平移 (−0.10, 0.20) m
ctr = np.array([0.80, 0.45, 0.0])
corners = np.array([[0.06, 0.04, 0], [-0.06, 0.04, 0], [-0.06, -0.04, 0], [0.06, -0.04, 0]]) + ctr
D = trans(-0.10, 0.20, 0) @ trans(*ctr) @ T(rot_z(math.pi / 2)) @ trans(*(-ctr))      # 一个位移算子
moved = np.array([(D @ hom(p))[:3] for p in corners])
assert is_se3(D)
# 定理 5.2.3：任意两点距离不变，叉积“跟着转”
rng = np.random.default_rng(5)
for _ in range(200):
    G = T(rot_axis(rng.normal(size=3), rng.uniform(-3, 3)), rng.normal(size=3))
    a, b, c = rng.normal(size=(3, 3))
    ga, gb, gc = ((G @ hom(x))[:3] for x in (a, b, c))
    assert abs(np.linalg.norm(ga - gb) - np.linalg.norm(a - b)) < 1e-12
    assert np.allclose(np.cross(gb - ga, gc - ga), G[:3, :3] @ np.cross(b - a, c - a), atol=1e-12)
assert all(abs(np.linalg.norm(moved[i] - moved[j]) - np.linalg.norm(corners[i] - corners[j])) < 1e-15
           for i in range(4) for j in range(4))
# 式 (5.2.7)：绕点 c 转动 = Trans(c) Rot Trans(−c) = [[R, c − R c], [0, 1]]
Rc = T(rot_z(math.pi / 2))
assert np.allclose(trans(*ctr) @ Rc @ trans(*(-ctr)), T(rot_z(math.pi / 2), ctr - rot_z(math.pi / 2) @ ctr))
# 定理 5.2.2：封闭、逆元（式 (5.2.5)、(5.2.6)）
for _ in range(200):
    A = T(rot_axis(rng.normal(size=3), rng.uniform(-3, 3)), rng.normal(size=3))
    B = T(rot_axis(rng.normal(size=3), rng.uniform(-3, 3)), rng.normal(size=3))
    AB = A @ B
    assert is_se3(AB) and np.allclose(AB[:3, 3], A[:3, :3] @ B[:3, 3] + A[:3, 3])
    Ai = T(A[:3, :3].T, -A[:3, :3].T @ A[:3, 3])
    assert np.allclose(A @ Ai, np.eye(4)) and np.allclose(Ai @ A, np.eye(4))
# 中点映为中点（习题 5.2.5 的数值检查）
mid = (corners[0] + corners[2]) / 2
assert np.allclose((D @ hom(mid))[:3], (moved[0] + moved[2]) / 2)

out(
    Tws=texm(Tws, 2), Twc=texm(Twc, 4), c15=c15, s15=s15,
    pw=vecm(p_w, 4), pw_x=p_w[0], pw_y=p_w[1], pw_z=p_w[2],
    axw=vecm(axis_w, 4), hit_x=hit[0], hit_y=hit[1], t_hit=t_hit,
    D=texm(D, 2), D_p=D[:3, 3].tolist(), moved=texm(moved.T, 2),
    m1=vecm(moved[0], 2),
)
