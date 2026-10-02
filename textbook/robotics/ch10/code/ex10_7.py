"""算例 10.7.1–10.7.3：刚体需要六个数。

算例 10.7.1：UR5e 夹爪上贴三个标记点 A、B、C（在夹爪坐标系 {b} 中为 (0, 0, 0)、(0.10, 0, 0)、(0.02, 0.06, 0) m）。
  夹爪位姿 R_sb = Rot(ẑ, 30°) Rot(x̂, 180°)，p_sb = (−0.45, −0.20, 0.30) m。由相机测得的三点坐标（9 个数）
  用格拉姆-施密特法（2.7 节）重建 R_sb 与 p_sb（6 个数），验证三个距离约束成立、重建结果与真值一致。
算例 10.7.2：夹爪的角速度 ω = (0.2, −0.1, 0.5) rad/s，A 点速度 v_A = (0.05, 0.10, −0.02) m/s。
  求 B、C 的速度；验证刚体条件 (v_B − v_A)·(r_B − r_A) = 0；由三点的速度反求 ω（最小二乘），与给定值一致；数值求导核对。
算例 10.7.3：夹爪绕过 A 的竖直轴转动，ω = 0.5 rad/s、角加速度 0.3 rad/s²，A 静止。求 B 的加速度，并核对它就是
  10.6 节的牵连加速度 α × r + ω × (ω × r)。
"""
import math

import numpy as np

from _kin import d1, d2, rotx, rotz, skew
from bookout import out

A_b, B_b, C_b = np.array([0.0, 0, 0]), np.array([0.10, 0, 0]), np.array([0.02, 0.06, 0])
R = rotz(math.radians(30)) @ rotx(math.pi)
p = np.array([-0.45, -0.20, 0.30])
A, B, Cm = (R @ q + p for q in (A_b, B_b, C_b))
# 三个距离约束：与位姿无关
dAB, dAC, dBC = np.linalg.norm(B - A), np.linalg.norm(Cm - A), np.linalg.norm(Cm - B)
for (u, w), dd in (((A_b, B_b), dAB), ((A_b, C_b), dAC), ((B_b, C_b), dBC)):
    assert abs(np.linalg.norm(u - w) - dd) < 1e-15
# 格拉姆-施密特重建
x = (B - A) / np.linalg.norm(B - A)
y = (Cm - A) - ((Cm - A) @ x) * x
y /= np.linalg.norm(y)
z = np.cross(x, y)
R_rec = np.column_stack([x, y, z])
p_rec = A - R_rec @ A_b
assert np.allclose(R_rec, R, atol=1e-15) and np.allclose(p_rec, p, atol=1e-15)
assert np.allclose(R_rec.T @ R_rec, np.eye(3)) and abs(np.linalg.det(R_rec) - 1) < 1e-12
# 第三根轴误取 ŷ × x̂：三轴仍正交，但构成左手系，det = −1（镜像，不是转动）
Mirror = np.column_stack([x, y, np.cross(y, x)])
assert abs(np.linalg.det(Mirror) + 1) < 1e-12

# ---------------------------------------------------------------- 算例 10.7.2
w = np.array([0.2, -0.1, 0.5])
vA = np.array([0.05, 0.10, -0.02])
rAB, rAC = B - A, Cm - A
vB = vA + np.cross(w, rAB)
vC = vA + np.cross(w, rAC)
assert abs((vB - vA) @ rAB) < 1e-15 and abs((vC - vA) @ rAC) < 1e-15 and abs((vC - vB) @ (Cm - B)) < 1e-15
# 反求 ω：v_B − v_A = −[r_AB] ω，v_C − v_A = −[r_AC] ω
M = np.vstack([-skew(rAB), -skew(rAC)])
rhs = np.concatenate([vB - vA, vC - vA])
w_rec, *_ = np.linalg.lstsq(M, rhs, rcond=None)
assert np.allclose(w_rec, w, atol=1e-12)
assert np.linalg.matrix_rank(M) == 3
# 只用两点：秩为 2，绕 AB 的转动看不出来
assert np.linalg.matrix_rank(-skew(rAB)) == 2


def expso3(wt):
    th = np.linalg.norm(wt)
    K = skew(wt / th)
    return np.eye(3) + math.sin(th) * K + (1 - math.cos(th)) * K @ K


def marker(t, q):          # 刚体以恒定 ω、v_A 运动时，标记点 q（{b} 中）在 {s} 中的位置
    return A + vA * t + expso3(w * t) @ R @ q if t != 0 else R @ q + p


assert np.allclose(d1(lambda t: marker(t, B_b), 0.0, 1e-6), vB, atol=1e-9)

# ---------------------------------------------------------------- 算例 10.7.3
w0, al = 0.5, 0.3


def B_t(t):
    psi = w0 * t + 0.5 * al * t * t
    return A + rotz(psi) @ (B - A)


wv, alv = np.array([0, 0, w0]), np.array([0, 0, al])
aB = np.cross(alv, rAB) + np.cross(wv, np.cross(wv, rAB))
assert np.allclose(d2(B_t, 0.0, 1e-3), aB, atol=1e-7)
rho = math.hypot(rAB[0], rAB[1])           # B 到转轴的距离
assert abs(np.linalg.norm(aB) - rho * math.hypot(al, w0 ** 2)) < 1e-12

fmt = lambda v: "(" + ", ".join(f"{x:.4f}" for x in v) + ")"
out(Ax=A[0], Ay=A[1], Az=A[2], Bx=B[0], By=B[1], Bz=B[2], Cx=Cm[0], Cy=Cm[1], Cz=Cm[2],
    dAB=dAB, dAC=dAC, dBC=dBC,
    vB=fmt(vB), vC=fmt(vC), vB_mag=float(np.linalg.norm(vB)), w_rec=fmt(w_rec),
    aB=fmt(aB), aB_mag=float(np.linalg.norm(aB)), rho=rho, a_t=rho * al, a_n=rho * w0 ** 2)
