"""Examples of Section 2.6: null space and range.

Example 2.6.1: for the planar 3R arm (dimensions of Chapter 12) at θ = (30°, 60°, −60°), the Jacobian J of the end-effector
           position is a 2×3 matrix. Find the rank and the null space (the cross product of the two rows gives the
           null-space direction, checked against the SVD); a self-motion with the end-effector fixed and θ1 going from 27° to 55°
           (for each θ1, θ2 and θ3 from the 2R inverse solution); check that the tangent of the self-motion is the
           null-space direction.
Example 2.6.2: with the arm straight (θ = (30°, 0, 0)) the rank drops to 1 and the null space becomes two-dimensional;
           dimensions and orthogonality of the four fundamental subspaces.
Example 2.6.3: null-space projection P = I − J⁺J: J P = 0, P² = P, Pᵀ = P; adding P z to the minimum-norm solution
           leaves the end-effector velocity unchanged.
"""
import math

import numpy as np

from _la import L3R, arm_points, d, jac
from bookout import out, tex, vec

L1, L2, L3 = L3R
th = np.array([d(30), d(60), d(-60)])
J = jac(th, L3R)
rank = int(np.linalg.matrix_rank(J))
n = np.cross(J[0], J[1])
n /= np.linalg.norm(n)
n = n if n[2] > 0 else -n
n_svd = np.linalg.svd(J)[2][-1]
assert np.allclose(J @ n, 0) and abs(abs(n @ n_svd) - 1) < 1e-12
assert rank == 2 and rank + 1 == 3                              # rank + nullity = number of columns
tip = arm_points(th, L3R)[-1]


def ik_rest(t1, p):
    """Given θ1 and the end-effector position p, find θ2, θ3 from the 2R inverse solution (same branch as the example: θ3 < 0)."""
    e = np.array([L1 * math.cos(t1), L1 * math.sin(t1)])
    q = p - e
    r2 = q @ q
    c3 = (r2 - L2 ** 2 - L3 ** 2) / (2 * L2 * L3)
    t3 = -math.acos(max(-1.0, min(1.0, c3)))
    a = math.atan2(q[1], q[0]) - math.atan2(L3 * math.sin(t3), L2 + L3 * math.cos(t3))
    return np.array([t1, a - t1, t3])


assert np.allclose(ik_rest(th[0], tip), th)
family = {deg: ik_rest(d(deg), tip) for deg in (27, 40, 55)}
for q in family.values():
    assert np.allclose(arm_points(q, L3R)[-1], tip)               # the end-effector has not moved
h = 1e-6
tangent = (ik_rest(th[0] + h, tip) - ik_rest(th[0] - h, tip)) / (2 * h)
tangent /= np.linalg.norm(tangent)
assert abs(abs(tangent @ n) - 1) < 1e-8                          # tangent of the self-motion = null-space direction

# ---------------------------------------------------------------- Example 2.6.2: arm straight
th0 = np.array([d(30), 0.0, 0.0])
J0 = jac(th0, L3R)
U0, s0, Vt0 = np.linalg.svd(J0)
rank0 = int(np.sum(s0 > 1e-12))
assert rank0 == 1
N0 = Vt0[rank0:].T                                                # an orthonormal basis of the null space (3×2)
assert np.allclose(J0 @ N0, 0)
left0 = U0[:, rank0:]                                             # left null space: the end-effector velocity direction that cannot be produced
radial = np.array([math.cos(d(30)), math.sin(d(30))])
assert abs(abs(left0[:, 0] @ radial) - 1) < 1e-12
assert np.allclose(J0.T @ left0, 0)
row0 = Vt0[:rank0].T
assert np.allclose(row0.T @ N0, 0)                                # row space ⟂ null space
# a concrete basis of the null space: joints 1 and 2 each paired with joint 3 so that the end-effector stays still
n_a = np.array([0.0, L3, -(L2 + L3)])                            # moves joints 2 and 3 only
n_b = np.array([L2 + L3, -(L1 + L2 + L3), 0.0])                  # moves joints 1 and 2 only
assert np.allclose(J0 @ n_a, 0) and np.allclose(J0 @ n_b, 0)
assert np.linalg.matrix_rank(np.column_stack([n_a, n_b])) == 2

# ---------------------------------------------------------------- Example 2.6.3: null-space projection
Jp = np.linalg.pinv(J)
P = np.eye(3) - Jp @ J
assert np.allclose(J @ P, 0) and np.allclose(P @ P, P) and np.allclose(P, P.T)
assert np.allclose(P, np.outer(n, n))
v = np.array([0.1, 0.0])
z = np.array([0.0, 0.0, 1.0])                                    # we want joint 3 to move towards 0 (positive direction)
thd0 = Jp @ v
thd = thd0 + P @ z
assert np.allclose(J @ thd, v)

out(
    J=tex(J, 4), rank=rank, n=vec(n, 4), tip=vec(tip, 4),
    q27=", ".join(f"{math.degrees(a):.1f}°" for a in family[27]), q40=", ".join(f"{math.degrees(a):.1f}°" for a in family[40]),
    q55=", ".join(f"{math.degrees(a):.1f}°" for a in family[55]),
    J0=tex(J0, 4), s0=s0[0], rank0=rank0, N0=tex(N0, 4), left0=vec(left0[:, 0], 4), n_a=vec(n_a, 3), n_b=vec(n_b, 3),
    P=tex(P, 4), thd0=vec(thd0, 4), thd=vec(thd, 4), Pz=vec(P @ z, 4),
)
