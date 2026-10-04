"""Examples 10.7.1–10.7.3: a rigid body needs six numbers.

Example 10.7.1: three markers A, B, C are stuck on the UR5e gripper (at (0, 0, 0), (0.10, 0, 0), (0.02, 0.06, 0) m in the
  gripper frame {b}). Gripper pose R_sb = Rot(ẑ, 30°) Rot(x̂, 180°), p_sb = (−0.45, −0.20, 0.30) m. From the coordinates
  of the three points measured by the camera (9 numbers), rebuild R_sb and p_sb (6 numbers) with the Gram–Schmidt process
  (Section 2.7); check that the three distance constraints hold and that the result agrees with the true values.
Example 10.7.2: angular velocity of the gripper ω = (0.2, −0.1, 0.5) rad/s, velocity of point A v_A = (0.05, 0.10, −0.02) m/s.
  Find the velocities of B and C; check the rigid-body condition (v_B − v_A)·(r_B − r_A) = 0; recover ω from the velocities
  of the three points (least squares) and compare with the given value; check by numerical differentiation.
Example 10.7.3: the gripper turns about the vertical axis through A, ω = 0.5 rad/s, angular acceleration 0.3 rad/s², A at
  rest. Find the acceleration of B and check that it is the transport acceleration α × r + ω × (ω × r) of Section 10.6.
"""
import math

import numpy as np

from _kin import d1, d2, rotx, rotz, skew
from bookout import out

A_b, B_b, C_b = np.array([0.0, 0, 0]), np.array([0.10, 0, 0]), np.array([0.02, 0.06, 0])
R = rotz(math.radians(30)) @ rotx(math.pi)
p = np.array([-0.45, -0.20, 0.30])
A, B, Cm = (R @ q + p for q in (A_b, B_b, C_b))
# the three distance constraints: independent of the pose
dAB, dAC, dBC = np.linalg.norm(B - A), np.linalg.norm(Cm - A), np.linalg.norm(Cm - B)
for (u, w), dd in (((A_b, B_b), dAB), ((A_b, C_b), dAC), ((B_b, C_b), dBC)):
    assert abs(np.linalg.norm(u - w) - dd) < 1e-15
# Gram–Schmidt reconstruction
x = (B - A) / np.linalg.norm(B - A)
y = (Cm - A) - ((Cm - A) @ x) * x
y /= np.linalg.norm(y)
z = np.cross(x, y)
R_rec = np.column_stack([x, y, z])
p_rec = A - R_rec @ A_b
assert np.allclose(R_rec, R, atol=1e-15) and np.allclose(p_rec, p, atol=1e-15)
assert np.allclose(R_rec.T @ R_rec, np.eye(3)) and abs(np.linalg.det(R_rec) - 1) < 1e-12
# third axis wrongly taken as ŷ × x̂: the axes are still orthogonal but left-handed, det = −1 (a mirror image, not a rotation)
Mirror = np.column_stack([x, y, np.cross(y, x)])
assert abs(np.linalg.det(Mirror) + 1) < 1e-12

# ---------------------------------------------------------------- Example 10.7.2
w = np.array([0.2, -0.1, 0.5])
vA = np.array([0.05, 0.10, -0.02])
rAB, rAC = B - A, Cm - A
vB = vA + np.cross(w, rAB)
vC = vA + np.cross(w, rAC)
assert abs((vB - vA) @ rAB) < 1e-15 and abs((vC - vA) @ rAC) < 1e-15 and abs((vC - vB) @ (Cm - B)) < 1e-15
# recover ω: v_B − v_A = −[r_AB] ω, v_C − v_A = −[r_AC] ω
M = np.vstack([-skew(rAB), -skew(rAC)])
rhs = np.concatenate([vB - vA, vC - vA])
w_rec, *_ = np.linalg.lstsq(M, rhs, rcond=None)
assert np.allclose(w_rec, w, atol=1e-12)
assert np.linalg.matrix_rank(M) == 3
# two points only: rank 2, a rotation about AB cannot be seen
assert np.linalg.matrix_rank(-skew(rAB)) == 2


def expso3(wt):
    th = np.linalg.norm(wt)
    K = skew(wt / th)
    return np.eye(3) + math.sin(th) * K + (1 - math.cos(th)) * K @ K


def marker(t, q):          # position in {s} of marker q (given in {b}) when the body moves with constant ω and v_A
    return A + vA * t + expso3(w * t) @ R @ q if t != 0 else R @ q + p


assert np.allclose(d1(lambda t: marker(t, B_b), 0.0, 1e-6), vB, atol=1e-9)

# ---------------------------------------------------------------- Example 10.7.3
w0, al = 0.5, 0.3


def B_t(t):
    psi = w0 * t + 0.5 * al * t * t
    return A + rotz(psi) @ (B - A)


wv, alv = np.array([0, 0, w0]), np.array([0, 0, al])
aB = np.cross(alv, rAB) + np.cross(wv, np.cross(wv, rAB))
assert np.allclose(d2(B_t, 0.0, 1e-3), aB, atol=1e-7)
rho = math.hypot(rAB[0], rAB[1])           # distance of B from the axis
assert abs(np.linalg.norm(aB) - rho * math.hypot(al, w0 ** 2)) < 1e-12

fmt = lambda v: "(" + ", ".join(f"{x:.4f}" for x in v) + ")"
out(Ax=A[0], Ay=A[1], Az=A[2], Bx=B[0], By=B[1], Bz=B[2], Cx=Cm[0], Cy=Cm[1], Cz=Cm[2],
    dAB=dAB, dAC=dAC, dBC=dBC,
    vB=fmt(vB), vC=fmt(vC), vB_mag=float(np.linalg.norm(vB)), w_rec=fmt(w_rec),
    aB=fmt(aB), aB_mag=float(np.linalg.norm(aB)), rho=rho, a_t=rho * al, a_n=rho * w0 ** 2)
