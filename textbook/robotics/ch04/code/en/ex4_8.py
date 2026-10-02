"""Examples of Section 4.8.

Example 4.8.1: the difference between the desired orientation R_d and the measured orientation R: the three methods
(angle of rotation, quaternion, Frobenius norm) agree; the error vector.
Example 4.8.2: a "rotation matrix" with measurement noise, no longer orthogonal, orthonormalized by the Gram-Schmidt
process and by the singular value decomposition; their distances from the original matrix compared.
Also: the numerical drift of cumulative orientation updates (data for Figure 4.8.1).
"""
import math

import numpy as np

from _rot import is_rotation, rot_axis, rot_x, rot_z, skew
from bookout import out, tex, vec

d, deg = math.radians, math.degrees


def angle(R):
    return math.acos(max(-1.0, min(1.0, (np.trace(R) - 1) / 2)))


def vee(W):
    return np.array([W[2, 1], W[0, 2], W[1, 0]])


def log_vec(R):
    t = angle(R)
    if t < 1e-12:
        return np.zeros(3)
    return vee((R - R.T) / (2 * math.sin(t))) * t


def q_from_R(R):
    q0 = 0.5 * math.sqrt(max(0.0, 1 + np.trace(R)))
    return np.concatenate([[q0], vee(R - R.T) / (4 * q0)])


def gram_schmidt(M):
    x = M[:, 0] / np.linalg.norm(M[:, 0])
    y = M[:, 1] - (x @ M[:, 1]) * x
    y /= np.linalg.norm(y)
    return np.column_stack([x, y, np.cross(x, y)])


def svd_project(M):
    U, _, Vt = np.linalg.svd(M)
    D = np.diag([1, 1, np.sign(np.linalg.det(U @ Vt))])
    return U @ D @ Vt


# ---------------------------------------------------------------- Example 4.8.1
R_d = rot_z(d(30)) @ rot_x(d(45))
err_axis = np.array([0.3, -0.2, 0.9]) / np.linalg.norm([0.3, -0.2, 0.9])
R = R_d @ rot_axis(err_axis, d(2))          # measured orientation: 2° off the desired one, about some body axis
R_err = R_d.T @ R
th_trace = angle(R_err)
th_quat = 2 * math.acos(abs(float(q_from_R(R_d) @ q_from_R(R))))
fro = float(np.linalg.norm(R - R_d))
th_fro = 2 * math.asin(fro / (2 * math.sqrt(2)))
assert abs(th_trace - d(2)) < 1e-12 and abs(th_quat - d(2)) < 1e-9 and abs(th_fro - d(2)) < 1e-12
e = log_vec(R_err)
assert np.allclose(e, err_axis * d(2))
e_small = vee((R_err - R_err.T) / 2)          # small-angle approximation
# bi-invariance: d(Q R1, Q R2) = d(R1, R2) = d(R1 Q, R2 Q)
Q = rot_axis([1, 2, 3], 0.7)
assert abs(angle((Q @ R_d).T @ (Q @ R)) - th_trace) < 1e-12 and abs(angle((R_d @ Q).T @ (R @ Q)) - th_trace) < 1e-12

# ---------------------------------------------------------------- Example 4.8.2
noise = np.array([[0.004, -0.010, 0.006], [0.008, 0.003, -0.005], [-0.006, 0.009, 0.002]])
M = R_d + noise
assert not is_rotation(M, 1e-4)
G, S = gram_schmidt(M), svd_project(M)
assert is_rotation(G) and is_rotation(S)
dist_G, dist_S = float(np.linalg.norm(G - M)), float(np.linalg.norm(S - M))
assert dist_S <= dist_G
orth_err_M = float(np.abs(M.T @ M - np.eye(3)).max())

# ---------------------------------------------------------------- drift (Figure 4.8.1)
w = np.array([0.3, -0.5, 0.8])
dt, steps = 0.001, 20000
R1, R2, R3 = np.eye(3), np.eye(3), np.eye(3)
E = rot_axis(w, np.linalg.norm(w) * dt)
drift1, drift2, drift3 = [], [], []
for k in range(1, steps + 1):
    R1 = R1 @ (np.eye(3) + skew(w) * dt)               # first-order update
    R2 = R2 @ E                                        # Rodrigues (exact) update
    R3 = R3 @ (np.eye(3) + skew(w) * dt)
    if k % 100 == 0:                                   # first-order update + orthonormalization every 100 steps
        R3 = svd_project(R3)
    if k % 200 == 0:
        drift1.append(float(np.abs(R1.T @ R1 - np.eye(3)).max()))
        drift2.append(float(np.abs(R2.T @ R2 - np.eye(3)).max()))
        drift3.append(float(np.abs(R3.T @ R3 - np.eye(3)).max()))
det1 = float(np.linalg.det(R1))

out(R_d=tex(R_d), err_axis=vec(err_axis), th_deg=deg(th_trace), th_quat_deg=deg(th_quat), fro=fro, th_fro_deg=deg(th_fro),
    e=vec(e), e_small=vec(e_small), e_norm_deg=deg(float(np.linalg.norm(e))),
    M=tex(M), G=tex(G), S=tex(S), dist_G=dist_G, dist_S=dist_S, orth_err_M=orth_err_M,
    drift1=drift1[-1], drift2=drift2[-1], drift3=drift3[-1], det1=det1, steps=steps,
    _drift1=drift1, _drift2=drift2, _drift3=drift3)
