"""Examples of Section 2.2: the matrix of a linear transformation, the determinant and area, invariants under similarity transformations.

Example 2.2.1: the stiffness matrix of a compliant wrist in its own frame {b} is K_b = diag(2000, 500) N/m; {b} is turned 30° relative
               to the base {s}. Find K_s and the restoring force for a 1 mm push along x_s; check by computing again in {b};
               compare tr and det.
Example 2.2.2: the same transformation in a slanted basis (the two columns of P are not perpendicular); the trace, determinant and
               characteristic polynomial of the similar matrix are unchanged.
Also checked: columns of a transformation matrix = images of the basis vectors; linearity; parallelogram area = |det| (Lagrange's
identity); determinants of the four basic transformations.
"""
import math

import numpy as np

from _la import d, rot2
from bookout import out, tex, vec

# ---------------------------------------------------------------- basic transformations
TR = {"rot": rot2(d(30)), "shear": np.array([[1.0, 0.5], [0.0, 1.0]]), "scale": np.array([[1.5, 0.0], [0.0, 0.5]]),
      "refl": np.array([[1.0, 0.0], [0.0, -1.0]]), "proj": np.array([[1.0, 0.0], [0.0, 0.0]])}
dets = {k: float(np.linalg.det(A)) for k, A in TR.items()}
e1, e2 = np.array([1.0, 0.0]), np.array([0.0, 1.0])
rng = np.random.default_rng(2)
for A in TR.values():
    assert np.allclose(A @ e1, A[:, 0]) and np.allclose(A @ e2, A[:, 1])        # columns = images of the basis vectors
    x, y, al, be = rng.normal(size=2), rng.normal(size=2), 0.7, -1.3
    assert np.allclose(A @ (al * x + be * y), al * (A @ x) + be * (A @ y))      # linearity
    a, b = A[:, 0], A[:, 1]                                                   # Lagrange's identity: |a|²|b|² − (a·b)² = (det)²
    assert abs((a @ a) * (b @ b) - (a @ b) ** 2 - np.linalg.det(A) ** 2) < 1e-12

# ---------------------------------------------------------------- Example 2.2.1
Kb = np.diag([2000.0, 500.0])                                    # N/m
phi = d(30)
R = rot2(phi)                                                    # R_sb: its columns are the two axes of {b} written in {s}
Ks = R @ Kb @ R.T
delta_s = np.array([0.001, 0.0])                                 # push 1 mm along x_s
f_s = Ks @ delta_s
delta_b = R.T @ delta_s
f_b = Kb @ delta_b
assert np.allclose(R @ f_b, f_s)                                 # both routes give the same force
f_ang = math.degrees(math.atan2(f_s[1], f_s[0]))
assert abs(np.trace(Ks) - np.trace(Kb)) < 1e-9 and abs(np.linalg.det(Ks) - np.linalg.det(Kb)) < 1e-6
assert np.allclose(Ks, Ks.T)

# ---------------------------------------------------------------- Example 2.2.2: a slanted basis
P = np.array([[1.0, 0.5], [0.0, 1.0]])                            # new basis vectors (1, 0) and (0.5, 1), not perpendicular
Kp = np.linalg.inv(P) @ Ks @ P
assert abs(np.trace(Kp) - np.trace(Ks)) < 1e-9 and abs(np.linalg.det(Kp) - np.linalg.det(Ks)) < 1e-6
assert np.allclose(np.poly(Kp), np.poly(Ks))                      # same characteristic polynomial
assert not np.allclose(Kp, Kp.T)                                  # no longer symmetric in a slanted basis

out(
    det_rot=dets["rot"], det_shear=dets["shear"], det_scale=dets["scale"], det_refl=dets["refl"], det_proj=dets["proj"],
    R=tex(R, 4), Ks=tex(Ks, 1), Ks11=Ks[0, 0], Ks12=Ks[0, 1], Ks22=Ks[1, 1],
    f_s=vec(f_s, 4), fx=f_s[0], fy=f_s[1], f_ang=f_ang, delta_b=vec(delta_b * 1000, 4), f_b=vec(f_b, 4),
    trK=float(np.trace(Ks)), detK=float(np.linalg.det(Ks)),
    Kp=tex(Kp, 1), trKp=float(np.trace(Kp)), detKp=float(np.linalg.det(Kp)),
)
