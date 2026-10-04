"""Examples of Section 2.7: Gram-Schmidt orthonormalization.

Example 2.7.1: three-point teaching of a workpiece frame (user frame). Taught points p0 (origin), p1 (on the x axis) and
           p2 (in the xy plane), in mm. The two taught directions are not exactly perpendicular; Gram-Schmidt gives
           the x and y axes, the third axis is obtained the same way from (0, 0, 1) and checked against the cross
           product x × y; the resulting matrix is a rotation matrix. Written as a QR decomposition. Swapping the order
           gives a different result.
Example 2.7.2: the orientation matrix M given by a sensor (the same as in Example 4.8.2) carries errors; Gram-Schmidt
           by columns: the direction of column 1 is unchanged, the error is pushed onto the last two columns.
Example 2.7.3: three nearly linearly dependent columns (the Läuchli matrix, ε = 1e-8): classical Gram-Schmidt loses
           orthogonality, the modified method keeps it.
"""
import math

import numpy as np

from bookout import out, tex, vec


def gs(A):
    """Classical Gram-Schmidt: returns Q (orthonormal columns) and upper triangular R, A = QR."""
    A = np.asarray(A, float)
    m, n = A.shape
    Q, R = np.zeros((m, n)), np.zeros((n, n))
    for j in range(n):
        w = A[:, j].copy()
        for i in range(j):
            R[i, j] = Q[:, i] @ A[:, j]            # dot product with the original column j
            w -= R[i, j] * Q[:, i]
        R[j, j] = np.linalg.norm(w)
        Q[:, j] = w / R[j, j]
    return Q, R


def mgs(A):
    """Modified Gram-Schmidt: after each projection is subtracted, the next projection is computed from the updated vector."""
    A = np.asarray(A, float)
    m, n = A.shape
    Q, R = np.zeros((m, n)), np.zeros((n, n))
    W = A.copy()
    for j in range(n):
        R[j, j] = np.linalg.norm(W[:, j])
        Q[:, j] = W[:, j] / R[j, j]
        for k in range(j + 1, n):
            R[j, k] = Q[:, j] @ W[:, k]
            W[:, k] -= R[j, k] * Q[:, j]
    return Q, R


# ---------------------------------------------------------------- Example 2.7.1
p0 = np.array([500.0, -200.0, 30.0])
p1 = np.array([800.0, -195.0, 31.0])
p2 = np.array([505.0, 100.0, 29.0])
a1, a2 = p1 - p0, p2 - p0
ang = math.degrees(math.acos(a1 @ a2 / (np.linalg.norm(a1) * np.linalg.norm(a2))))
e1 = a1 / np.linalg.norm(a1)
r12 = e1 @ a2
w2 = a2 - r12 * e1
e2 = w2 / np.linalg.norm(w2)
assert abs(e1 @ e2) < 1e-15
a3 = np.array([0.0, 0.0, 1.0])
w3 = a3 - (e1 @ a3) * e1 - (e2 @ a3) * e2
e3 = w3 / np.linalg.norm(w3)
assert np.allclose(e3, np.cross(e1, e2))                          # agrees with the cross product (Chapter 3)
Rf = np.column_stack([e1, e2, e3])
assert np.allclose(Rf.T @ Rf, np.eye(3)) and abs(np.linalg.det(Rf) - 1) < 1e-12
A = np.column_stack([a1, a2])
Q, R = gs(A)
assert np.allclose(Q @ R, A) and np.allclose(Q[:, 0], e1) and np.allclose(Q[:, 1], e2)
Qn, Rn = np.linalg.qr(A)                                          # numerical library (Householder reflections): columns may differ in sign
S = np.diag(np.sign(np.diag(Rn)))
assert np.allclose(Qn @ S, Q) and np.allclose(S @ Rn, R)
dev_y = math.degrees(math.acos(e2 @ a2 / np.linalg.norm(a2)))     # angle by which the y axis is turned from the taught direction
# swap the order: fix the y axis first
Q2, _ = gs(np.column_stack([a2, a1]))
x_alt = Q2[:, 1]
dx_alt = math.degrees(math.acos(min(1.0, x_alt @ e1)))
assert dx_alt > 0.5

# ---------------------------------------------------------------- Example 2.7.2
def rot_x(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_z(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


R_d = rot_z(math.radians(30)) @ rot_x(math.radians(45))
noise = np.array([[0.004, -0.010, 0.006], [0.008, 0.003, -0.005], [-0.006, 0.009, 0.002]])
M = R_d + noise                                                    # the same as in Example 4.8.2
G, _ = gs(M)
assert np.allclose(G.T @ G, np.eye(3)) and np.linalg.det(G) > 0
turn = [math.degrees(math.acos(min(1.0, G[:, j] @ M[:, j] / np.linalg.norm(M[:, j])))) for j in range(3)]
assert turn[0] < 1e-6 and turn[1] > 0.1 and turn[2] > 0.1
orth_err_M = float(np.abs(M.T @ M - np.eye(3)).max())
dist_G = float(np.linalg.norm(G - M))

# ---------------------------------------------------------------- Example 2.7.3
eps = 1e-8
Lc = np.array([[1, 1, 1], [eps, 0, 0], [0, eps, 0], [0, 0, eps]], float)
Qc, _ = gs(Lc)
Qm, _ = mgs(Lc)
Qh, _ = np.linalg.qr(Lc)
loss_c = float(np.abs(Qc.T @ Qc - np.eye(3)).max())
loss_m = float(np.abs(Qm.T @ Qm - np.eye(3)).max())
loss_h = float(np.abs(Qh.T @ Qh - np.eye(3)).max())
assert loss_c > 0.1 and loss_m < 1e-7 and loss_h < 1e-14

out(
    a1=vec(a1, 0), a2=vec(a2, 0), ang=ang, dot12=float(a1 @ a2), n1=float(np.linalg.norm(a1)), n2=float(np.linalg.norm(w2)),
    na2=float(np.linalg.norm(a2)),
    e1=vec(e1, 4), r12=r12, w2=vec(w2, 3), e2=vec(e2, 4), e3=vec(e3, 4), Rf=tex(Rf, 4), Rqr=tex(R, 3),
    dev_y=dev_y, dx_alt=dx_alt,
    M=tex(M, 4), G=tex(G, 4), turn2=turn[1], turn3=turn[2], orth_err_M=orth_err_M, dist_G=dist_G,
    loss_c=loss_c, loss_m=loss_m, loss_h=loss_h,
)
