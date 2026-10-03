"""Examples of Section 3.4.

Example 3.4.1: polishing a workpiece surface tilted 20°. "Projecting the velocity onto the surface" is a projection
           tensor P: in the surface frame {b}, P_b = diag(1, 1, 0); in the base frame {a}, P_a = R_ab P_b R_abᵀ,
           which should equal I − n nᵀ. The command velocity v_cmd is perpendicular to the normal after projection;
           if diag(1, 1, 0) is wrongly used directly in {a}, the tool digs into the surface at some speed. Compare the
           traces, determinants and eigenvalues of the two sets of components.
Example 3.4.2: a rectangular plate tilted 30° in a gripper (a first look at the inertia tensor).
           I_b = m/12 diag(b²+c², a²+c², a²+b²), I_t = R_tb I_b R_tbᵀ; checked by computing once more in the tool
           frame {t} by "dividing the plate into small pieces and summing directly". When spinning about the tool
           z axis at 1 r/s, L = I ω is not parallel to ω.
Also checked: R[a]Rᵀ = [Ra] (Theorem 3.4.4); symmetry, trace, determinant and eigenvalues do not change under a
change of frame.
"""
import math

import numpy as np

from _vec import d, rot_x, rot_z, skew
from bookout import out, tex, vec

# ---------------------------------------------------------------- Example 3.4.1: projection tensor
R_ab = rot_x(d(20))                                   # surface frame {b} relative to base {a}: tilted 20° about x
P_b = np.diag([1.0, 1.0, 0.0])
P_a = R_ab @ P_b @ R_ab.T                             # Eq. (3.4.4)
n_a = R_ab[:, 2]                                      # surface normal = z axis of {b}
assert np.allclose(P_a, np.eye(3) - np.outer(n_a, n_a))                 # Eq. (3.4.8): the two methods agree
# component form (3.4.5): sum term by term
P_sum = np.array([[sum(R_ab[i, k] * R_ab[j, l] * P_b[k, l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)])
assert np.allclose(P_sum, P_a)
v_cmd = np.array([0.05, 0.10, 0.0])                    # command velocity (base frame), m/s
v = P_a @ v_cmd
assert abs(v @ n_a) < 1e-15                           # along the surface after projection
v_wrong = P_b @ v_cmd                                 # wrong: the component matrix of {b} used in {a}
dig = float(v_wrong @ n_a)                            # velocity along the normal (negative = digging into the surface)
# compute once in {b} and convert back to {a}
assert np.allclose(R_ab @ (P_b @ (R_ab.T @ v_cmd)), v)
# invariants
for M in (P_a, P_b):
    assert abs(np.trace(M) - 2) < 1e-12 and abs(np.linalg.det(M)) < 1e-12
assert np.allclose(np.sort(np.linalg.eigvalsh(P_a)), [0, 1, 1])
# turning the surface frame by any angle about the normal leaves the components of P unchanged: P depends only on the normal
for t in (0.3, 1.0, 2.5):
    R2 = R_ab @ rot_z(t)
    assert np.allclose(R2 @ P_b @ R2.T, P_a)

# ---------------------------------------------------------------- Example 3.4.2: inertia tensor (first look)
a, b, c, m = 0.30, 0.20, 0.02, 2.0
I_b = m / 12 * np.diag([b * b + c * c, a * a + c * c, a * a + b * b])     # the plate's own principal frame {b}
R_tb = rot_x(d(30))                                   # plate tilted 30° about x relative to the tool frame {t}
I_t = R_tb @ I_b @ R_tb.T
# second method: divide the plate into N small pieces and sum directly in {t} by Eq. (3.4.9)  I = Σ m_k (|r|² I − r rᵀ) = −Σ m_k [r]²
nx, ny, nz = 120, 80, 8
xs = (np.arange(nx) + 0.5) / nx * a - a / 2
ys = (np.arange(ny) + 0.5) / ny * b - b / 2
zs = (np.arange(nz) + 0.5) / nz * c - c / 2
X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
pts_b = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
pts_t = pts_b @ R_tb.T
mk = m / len(pts_t)
r2 = np.einsum("ki,ki->k", pts_t, pts_t)
I_sum = mk * (r2.sum() * np.eye(3) - pts_t.T @ pts_t)
assert np.allclose(I_sum, I_t, rtol=2e-3, atol=1e-7)                       # the error of the midpoint sum is within about one part in a thousand
r0 = pts_t[0]
assert np.allclose(-skew(r0) @ skew(r0), (r0 @ r0) * np.eye(3) - np.outer(r0, r0))   # Eq. (3.2.16)
w = np.array([0.0, 0.0, 2 * math.pi])                 # 1 r/s about the tool z axis
L = I_t @ w
ang_Lw = math.degrees(math.acos(L @ w / (np.linalg.norm(L) * np.linalg.norm(w))))
assert abs(np.trace(I_t) - np.trace(I_b)) < 1e-15 and abs(np.linalg.det(I_t) - np.linalg.det(I_b)) < 1e-15
assert np.allclose(np.sort(np.linalg.eigvalsh(I_t)), np.sort(np.diag(I_b)))
assert np.allclose(I_t, I_t.T)

# ---------------------------------------------------------------- Theorem 3.4.4: R[a]Rᵀ = [Ra], Eq. (3.4.6)
rng = np.random.default_rng(11)
for _ in range(100):
    q = rng.normal(size=4)
    q /= np.linalg.norm(q)
    w0, x0, y0, z0 = q
    R = np.array([[1 - 2 * (y0 * y0 + z0 * z0), 2 * (x0 * y0 - w0 * z0), 2 * (x0 * z0 + w0 * y0)],
                  [2 * (x0 * y0 + w0 * z0), 1 - 2 * (x0 * x0 + z0 * z0), 2 * (y0 * z0 - w0 * x0)],
                  [2 * (x0 * z0 - w0 * y0), 2 * (y0 * z0 + w0 * x0), 1 - 2 * (x0 * x0 + y0 * y0)]])   # random rotation matrix
    av = rng.normal(size=3)
    assert np.allclose(R @ skew(av) @ R.T, skew(R @ av))

out(
    s20=math.sin(d(20)), c20=math.cos(d(20)), R_ab=tex(R_ab, 4), P_a=tex(P_a, 4), n_a=vec(n_a, 4),
    v=vec(v, 4), v1=v[0], v2=v[1], v3=v[2], dig_mm=-dig * 1000, v_speed=float(np.linalg.norm(v)),
    cmd_speed=float(np.linalg.norm(v_cmd)),
    I_b=tex(I_b * 1e3, 3), I_t=tex(I_t * 1e3, 3), Ixx=I_b[0, 0] * 1e3, Iyy=I_b[1, 1] * 1e3, Izz=I_b[2, 2] * 1e3,
    Iyz=I_t[1, 2] * 1e3, trI=np.trace(I_b) * 1e3, L=vec(L * 1e3, 2), ang_Lw=ang_Lw, w=2 * math.pi,
    I_err=float(np.abs(I_sum - I_t).max() / np.abs(I_t).max()),
)
