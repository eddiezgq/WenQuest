"""Examples of Section 2.4: singular value decomposition and manipulability.

Example 2.4.1: the Jacobian matrix J of the planar 2R arm at θ = (30°, 60°) (the same as in Example 2.1.1). Following
               the proof of Theorem 2.4.1, find V and Σ from the eigendecomposition of JᵀJ, then U from
               u_i = J v_i / σ_i; check against the library svd; manipulability σ1σ2 = |det J|.
Example 2.4.2: singular values and condition number with the arm nearly straight (θ2 = 5°), and the joint speed
               needed to move at 0.1 m/s along the "hardest" direction.
Also checked: ‖J‖₂ = σ1 (largest stretch, sampled on the unit circle); ‖J‖_F² = σ1² + σ2²; the error of the best
rank-1 approximation = σ2; manipulability is largest at θ2 = 90°.
"""
import math

import numpy as np

from _la import L2R, arm_points, d, jac
from bookout import out, tex, vec

L1, L2 = L2R
th = [d(30), d(60)]
J = jac(th, L2R)

# ---------------------------------------------------------------- Example 2.4.1: by the steps of the proof
JtJ = J.T @ J
lam, V = np.linalg.eigh(JtJ)
order = np.argsort(lam)[::-1]
lam, V = lam[order], V[:, order]
if V[0, 0] < 0:
    V[:, 0] *= -1
if np.linalg.det(V) < 0:
    V[:, 1] *= -1
sig = np.sqrt(lam)
U = np.column_stack([J @ V[:, i] / sig[i] for i in range(2)])
assert np.allclose(U.T @ U, np.eye(2)) and np.allclose(V.T @ V, np.eye(2))
assert np.allclose(U @ np.diag(sig) @ V.T, J)
s_lib = np.linalg.svd(J, compute_uv=False)
assert np.allclose(s_lib, sig)
w = sig[0] * sig[1]
assert abs(w - abs(np.linalg.det(J))) < 1e-12 and abs(w - L1 * L2 * math.sin(th[1])) < 1e-12
u1_ang = math.degrees(math.atan2(U[1, 0], U[0, 0]))
u2_ang = math.degrees(math.atan2(U[1, 1], U[0, 1]))
cond = sig[0] / sig[1]

# 2-norm = largest stretch; F-norm
t = np.linspace(0, 2 * math.pi, 20001)
stretch = np.linalg.norm(J @ np.vstack([np.cos(t), np.sin(t)]), axis=0)
assert abs(stretch.max() - sig[0]) < 1e-6 and abs(stretch.min() - sig[1]) < 1e-6
assert abs(np.linalg.norm(J, "fro") ** 2 - (sig ** 2).sum()) < 1e-12
A1 = sig[0] * np.outer(U[:, 0], V[:, 0])                          # best rank-1 approximation
assert abs(np.linalg.norm(J - A1, 2) - sig[1]) < 1e-12

# ---------------------------------------------------------------- Example 2.4.2: nearly straight
J5 = jac([d(30), d(5)], L2R)
U5, s5, Vt5 = np.linalg.svd(J5)
cond5 = s5[0] / s5[1]
need = 0.1 / s5[1]                                               # joint speed needed to move along u2 at 0.1 m/s, rad/s
need_fast = 0.1 / s5[0]
tip5 = arm_points([d(30), d(5)], L2R)[-1]
radial = tip5 / np.linalg.norm(tip5)                             # direction from the base to the end-effector
ang_radial = math.degrees(math.acos(min(1.0, abs(float(U5[:, 1] @ radial)))))   # angle between u2 and the radial direction
assert ang_radial < 5

# ---------------------------------------------------------------- sweep of θ2: manipulability largest at 90°
t2 = np.radians(np.arange(1, 180))
ws = [np.prod(np.linalg.svd(jac([0, a], L2R), compute_uv=False)) for a in t2]
assert int(np.degrees(t2[int(np.argmax(ws))]) + 0.5) == 90

out(
    J=tex(J, 4), JtJ=tex(JtJ, 4), lam1=lam[0], lam2=lam[1], s1=sig[0], s2=sig[1], V=tex(V, 4), U=tex(U, 4),
    v1=vec(V[:, 0], 4), v2=vec(V[:, 1], 4), u1=vec(U[:, 0], 4), u2=vec(U[:, 1], 4), u1_ang=u1_ang, u2_ang=u2_ang,
    w=w, cond=cond, fro=float(np.linalg.norm(J, "fro")),
    s1_5=s5[0], s2_5=s5[1], cond5=cond5, need=need, need_fast=need_fast, ang_radial=ang_radial,
    wmax=L1 * L2,
)
