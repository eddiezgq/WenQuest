"""14.3 节：帕登-卡汉子问题。

(1) 引理 14.3.1 的三个不变量：轴上的点不动；到轴上一点的距离不变；沿轴方向的分量不变（随机核对）。
(2) 算例 14.3.1（子问题 1）：UR5e 的关节 1 转多少，零位时的法兰中心才到达 y 轴正方向上同样高度、同样半径的点。
(3) 算例 14.3.2（子问题 2）：UR5e 零位，关节 5、6 的轴交于 P56。求 θ5、θ6，使末端 x 轴转到方向 (1, 1, −1)/√3。
(4) 算例 14.3.3（子问题 3）：UR5e 零位，转关节 3，使腕部点 q4 到肩部点 q2 的距离为 0.6 m。
(5) 一万组随机数据：三个子问题的解代回原方程；由已知角度造出的数据，原来的角度必在解中；
    任意给的数据（不保证有解）时，子问题 2、3 有 0 个、2 个解的比例。
(6) 平面 2R 臂就是“子问题 3 + 子问题 1”：与 14.2 节的公式比较。
"""
import math

import numpy as np

from _ik import UR_M, UR_Q, UR_S, UR_W, P56, act, exp6, ik2r, rot, sp1, sp1_ok, sp2, sp3, ur_fk, wrap
from bookout import out, vec

rng = np.random.default_rng(143)


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def rot_about(w, r, t, p):                               # 绕过 r、方向 w 的轴转 t（式 (12.1.2)）
    return r + rot(w, t) @ (np.asarray(p, float) - r)


# ---------------------------------------------------------------- (1) 三个不变量
for _ in range(1000):
    w, r, p, t = unit(rng.normal(size=3)), rng.normal(size=3), rng.normal(size=3), rng.uniform(-math.pi, math.pi)
    k = rng.normal()
    on = r + k * w
    assert np.allclose(rot_about(w, r, t, on), on, atol=1e-12)
    assert abs(np.linalg.norm(rot_about(w, r, t, p) - on) - np.linalg.norm(p - on)) < 1e-12
    assert abs(w @ (rot_about(w, r, t, p) - r) - w @ (p - r)) < 1e-12

# ---------------------------------------------------------------- (2) 算例 14.3.1：子问题 1
p0 = UR_M[:3, 3]                                       # 零位法兰中心
rad = math.hypot(p0[0], p0[1])
q_target = np.array([0.0, rad, p0[2]])
t1 = sp1(UR_W[0], UR_Q[0], p0, q_target)
assert sp1_ok(UR_W[0], UR_Q[0], p0, q_target)
assert np.allclose(act(exp6(UR_S[0], t1), p0), q_target, atol=1e-12)
assert np.allclose(ur_fk([t1, 0, 0, 0, 0, 0])[:3, 3], q_target, atol=1e-12)
u0 = p0 - UR_Q[0]
phi_p = math.degrees(math.atan2(p0[1], p0[0]))
bad_q = q_target + np.array([0, 0, 0.05])             # 高度不同：条件 (14.3.3) 的第一条不满足
assert not sp1_ok(UR_W[0], UR_Q[0], p0, bad_q)

# ---------------------------------------------------------------- (3) 算例 14.3.2：子问题 2（轴 5、6 交于 P56）
xb = UR_M[:3, 0]                                       # 零位时末端 x 轴 (1, 0, 0)
d = unit([1, 1, -1])
s2 = sp2(UR_W[4], UR_W[5], P56, P56 + xb, P56 + d)
assert len(s2) == 2
k12 = UR_W[4] @ UR_W[5]
alpha_beta = []
for t5, t6, c in s2:
    R = rot(UR_W[4], t5) @ rot(UR_W[5], t6)
    assert np.allclose(R @ xb, d, atol=1e-12)
    T = ur_fk([0, 0, 0, 0, t5, t6])
    assert np.allclose(T[:3, 0], d, atol=1e-12)          # 正运动学：末端 x 轴确实转到了 d
    alpha_beta.append(c - P56)
u2 = xb
a2 = (k12 * (UR_W[5] @ u2) - UR_W[4] @ d) / (k12 * k12 - 1)
b2 = (k12 * (UR_W[4] @ d) - UR_W[5] @ u2) / (k12 * k12 - 1)
n2 = np.cross(UR_W[4], UR_W[5])
g2 = (u2 @ u2 - a2 * a2 - b2 * b2 - 2 * a2 * b2 * k12) / (n2 @ n2)
s2d = sorted([(math.degrees(t5), math.degrees(t6)) for t5, t6, _ in s2], reverse=True)

# ---------------------------------------------------------------- (4) 算例 14.3.3：子问题 3
delta = 0.6
s3 = sp3(UR_W[2], UR_Q[2], UR_Q[3], UR_Q[1], delta)
assert len(s3) == 2
for t in s3:
    q4 = act(exp6(UR_S[2], t), UR_Q[3])
    assert abs(np.linalg.norm(q4 - UR_Q[1]) - delta) < 1e-12
    T = ur_fk([0, 0, t, 0, 0, 0])
W2 = 0.131
L1, L2 = 0.425, 0.392
dprime = math.sqrt(delta ** 2 - W2 ** 2)              # 沿轴方向的偏距 W2 先扣除
cos_d = (L1 ** 2 + L2 ** 2 - dprime ** 2) / (2 * L1 * L2)
check = sorted(wrap(math.pi + sg * math.acos(cos_d)) for sg in (1, -1))
assert np.allclose(sorted(s3), check, atol=1e-12)
s3d = sorted(math.degrees(t) for t in s3)

# ---------------------------------------------------------------- (5) 随机数据
N = 10000
worst = 0.0
n0 = {2: 0, 3: 0}
for _ in range(N):
    # 子问题 1
    w, r, p, t = unit(rng.normal(size=3)), rng.normal(size=3), rng.normal(size=3), rng.uniform(-math.pi, math.pi)
    q = rot_about(w, r, t, p)
    s = sp1(w, r, p, q)
    assert abs(wrap(s - t)) < 1e-9
    # 子问题 2：两轴交于 r
    w1, w2 = unit(rng.normal(size=3)), unit(rng.normal(size=3))
    ta, tb = rng.uniform(-math.pi, math.pi, 2)
    q = r + rot(w1, ta) @ rot(w2, tb) @ (p - r)
    sols = sp2(w1, w2, r, p, q)
    assert any(abs(wrap(a - ta)) < 1e-7 and abs(wrap(b - tb)) < 1e-7 for a, b, _ in sols)
    for a, b, _ in sols:
        worst = max(worst, float(np.linalg.norm(r + rot(w1, a) @ rot(w2, b) @ (p - r) - q)))
    n0[2] += len(sp2(w1, w2, r, p, r + unit(rng.normal(size=3)) * np.linalg.norm(p - r))) == 0
    # 子问题 3
    qq = rng.normal(size=3)
    dl = float(np.linalg.norm(rot_about(w, r, t, p) - qq))
    sols = sp3(w, r, p, qq, dl)
    assert any(abs(wrap(a - t)) < 1e-6 for a in sols)
    for a in sols:
        worst = max(worst, abs(float(np.linalg.norm(rot_about(w, r, a, p) - qq)) - dl))
    n0[3] += len(sp3(w, r, p, qq, rng.uniform(0, 4))) == 0
assert worst < 1e-9

# ---------------------------------------------------------------- (6) 平面 2R = 子问题 3 + 子问题 1
z = np.array([0, 0, 1.0])
for _ in range(1000):
    th = rng.uniform(-math.pi, math.pi, 2)
    tip = np.array([L1 * math.cos(th[0]) + L2 * math.cos(th[0] + th[1]), L1 * math.sin(th[0]) + L2 * math.sin(th[0] + th[1]), 0])
    tip0, q2 = np.array([L1 + L2, 0, 0]), np.array([L1, 0, 0])
    for b in sp3(z, q2, tip0, np.zeros(3), float(np.linalg.norm(tip))):    # 关节 2：末端到基座的距离
        a = sp1(z, np.zeros(3), rot_about(z, q2, b, tip0), tip)            # 关节 1：转到目标
        assert any(abs(wrap(a - x)) < 1e-9 and abs(wrap(b - y)) < 1e-9 for x, y in ik2r(tip[0], tip[1], L1, L2))

out(p0=vec(p0, 3), rad=rad, qt=vec(q_target, 4), t1_deg=math.degrees(t1), phi_p=phi_p,
    d=vec(d, 4), a2=a2, b2=b2, g2=g2, g=math.sqrt(g2), k12=k12,
    s2a=f"({s2d[0][0]:.2f}°, {s2d[0][1]:.2f}°)", s2b=f"({s2d[1][0]:.2f}°, {s2d[1][1]:.2f}°)",
    c1=vec(alpha_beta[0], 4), c2=vec(alpha_beta[1], 4),
    delta=delta, dprime=dprime, cos_d=cos_d, s3a=s3d[0], s3b=s3d[1], acos_d=math.degrees(math.acos(cos_d)),
    N=N, worst=worst, sp2_none=100 * n0[2] / N, sp3_none=100 * n0[3] / N)
