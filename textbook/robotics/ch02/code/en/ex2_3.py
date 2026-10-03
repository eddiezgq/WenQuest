"""Examples of Section 2.3: eigenvalues and eigenvectors.

Example 2.3.1: the measured stiffness matrix of the compliant wrist, K = [[1600, 650], [650, 900]] N/m; find the
               principal stiffnesses and principal directions and compare them with the datasheet
               (2000 N/m, 500 N/m, principal direction 30°). The formula solution of the characteristic equation and
               the library function eigh check each other.
Example 2.3.2: non-symmetric cases: rotation (complex eigenvalues), shear (only one eigendirection), stretching a
               rubber sheet (two eigendirections that are not perpendicular).
Also: sum of eigenvalues = trace, product = determinant (including a random 4×4 matrix); spectral decomposition
K = QΛQᵀ; power iteration converges like (λ2/λ1)^k.
"""
import math

import numpy as np

from _la import d, rot2
from bookout import out, tex, vec

# ---------------------------------------------------------------- Example 2.3.1
K = np.array([[1600.0, 650.0], [650.0, 900.0]])                  # N/m, measured
tr, det = float(np.trace(K)), float(np.linalg.det(K))
disc = (tr / 2) ** 2 - det
lam1, lam2 = tr / 2 + math.sqrt(disc), tr / 2 - math.sqrt(disc)   # λ² − tr λ + det = 0
v1 = np.array([K[0, 1], lam1 - K[0, 0]])
v1 /= np.linalg.norm(v1)
v2 = np.array([K[0, 1], lam2 - K[0, 0]])
v2 /= np.linalg.norm(v2)
v2 = v2 if v2[1] > 0 else -v2                                    # take the one pointing upwards
assert np.allclose(K @ v1, lam1 * v1) and np.allclose(K @ v2, lam2 * v2)
assert abs(v1 @ v2) < 1e-12                                       # symmetric matrix: eigenvectors orthogonal
w, Q = np.linalg.eigh(K)
assert np.allclose(sorted(w), sorted([lam1, lam2]))
assert abs(lam1 + lam2 - tr) < 1e-9 and abs(lam1 * lam2 - det) < 1e-6
phi1 = math.degrees(math.atan2(v1[1], v1[0]))
phi1_formula = 0.5 * math.degrees(math.atan2(2 * K[0, 1], K[0, 0] - K[1, 1]))   # tan 2φ = 2k12 / (k11 − k22)
assert abs(phi1 - phi1_formula) < 1e-9
Qm = np.column_stack([v1, v2])
assert np.allclose(Qm @ np.diag([lam1, lam2]) @ Qm.T, K)         # spectral decomposition
assert lam2 > 0                                                  # positive definite
delta = np.array([0.001, 0.0])
energy = 0.5 * delta @ K @ delta                                 # J

# ---------------------------------------------------------------- Example 2.3.2
Rm = rot2(d(30))
wr = np.linalg.eigvals(Rm)
assert np.allclose(sorted(wr.imag), [-0.5, 0.5]) and np.allclose(wr.real, math.cos(d(30)))
Sh = np.array([[1.0, 1.0], [0.0, 1.0]])
assert np.linalg.matrix_rank(Sh - np.eye(2)) == 1                # eigenvalue 1 has only one direction
A = np.array([[1.5, 0.5], [0.0, 1.0]])                           # rubber sheet: stretched 1.5 times along x, with a little shear
wa, Va = np.linalg.eig(A)
ang_a = sorted((math.degrees(math.atan2(v[1], v[0])) % 180) for v in Va.T)
assert np.allclose(sorted(wa), [1.0, 1.5]) and np.allclose(ang_a, [0.0, 135.0])
Pa = Va
assert np.allclose(Pa @ np.diag(wa) @ np.linalg.inv(Pa), A)      # diagonalizable, but P is not an orthogonal matrix

# general n: sum = trace, product = determinant
rng = np.random.default_rng(7)
B = rng.normal(size=(4, 4))
wb = np.linalg.eigvals(B)
assert abs(wb.sum() - np.trace(B)) < 1e-9 and abs(np.prod(wb) - np.linalg.det(B)) < 1e-9

# ---------------------------------------------------------------- power iteration
x = np.array([1.0, 0.0])
hist = []
for k in range(1, 40):
    x = K @ x
    x /= np.linalg.norm(x)
    hist.append(float(x @ K @ x))                                # Rayleigh quotient
    if abs(hist[-1] - lam1) / lam1 < 1e-10:
        break
n_iter = k
ratio = lam2 / lam1
err5 = abs(hist[4] - lam1) / lam1

out(
    K=tex(K, 0), tr=tr, det=round(det), disc=round(disc), sq=math.sqrt(disc), lam1=lam1, lam2=lam2, v1=vec(v1, 4), v2=vec(v2, 4),
    phi1=phi1, phi2=phi1 + 90, dlam1=lam1 - 2000, dlam2=lam2 - 500, dphi=phi1 - 30, ang2phi=2 * phi1,
    energy_mJ=energy * 1000, Rre=math.cos(d(30)),
    n_iter=n_iter, ratio=ratio, err5=err5,
)
