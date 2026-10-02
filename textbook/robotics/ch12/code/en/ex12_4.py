"""Example 12.4.1: the second reading of the PoE, from the first joint outwards; each time a joint turns, the axes beyond it move with it.

e^{[S1]θ1} e^{[S2]θ2} = e^{[S2']θ2} e^{[S1]θ1}, where S2' = [Ad_{e^{[S1]θ1}}] S2 is the new axis of joint 2 after joint 1 has turned (Theorem 12.4.1).
Planar 3R: after θ1 = 30°, the axis of joint 2 moves from q2 = (L1, 0) to (L1 cos 30°, L1 sin 30°).
UR5e: at random joint angles, the two readings give the same tool pose.
"""
import numpy as np

from _poe import adjoint, clean, exp6, fk_space, screw_revolute
from bookout import out, vec

L1, L2, L3 = 0.425, 0.392, 0.1
z = np.array([0, 0, 1.0])
S = [screw_revolute(z, q) for q in ([0, 0, 0], [L1, 0, 0], [L1 + L2, 0, 0])]
M = np.eye(4)
M[0, 3] = L1 + L2 + L3
th = np.radians([30.0, 45.0, -90.0])

E1 = exp6(S[0], th[0])
S2n = adjoint(E1) @ S[1]
q2n = E1[:3, :3] @ np.array([L1, 0, 0])
assert np.allclose(S2n, screw_revolute(z, q2n))
assert np.allclose(E1 @ exp6(S[1], th[1]), exp6(S2n, th[1]) @ E1)

# "Reading outwards": each time a joint turns, move the axes of all later joints to their new places with the adjoint
def fk_forward(Slist, M, theta):
    axes = [np.array(s) for s in Slist]
    T = np.eye(4)
    for i, t in enumerate(theta):
        E = exp6(axes[i], t)
        T = E @ T
        axes = [adjoint(E) @ a if k > i else a for k, a in enumerate(axes)]
    return T @ M


assert np.allclose(fk_forward(S, M, th), fk_space(S, M, th))

# UR5e: the two readings agree
H1, W1, Lu1, W2, Lu2, W3, H2, W4 = 0.163, 0.138, 0.425, 0.131, 0.392, 0.127, 0.1, 0.1
yd = np.array([0, -1.0, 0])
Su = [screw_revolute(w, q) for w, q in [((0, 0, 1.0), (0, 0, H1)), (yd, (0, -W1, H1)), (yd, (-Lu1, -W1 + W2, H1)),
                                         (yd, (-Lu1 - Lu2, -W1 + W2, H1)), ((0, 0, -1.0), (-Lu1 - Lu2, -W1 + W2 - W3, H1)),
                                         (yd, (-Lu1 - Lu2, -W1 + W2 - W3, H1 - H2))]]
Mu = np.array([[1.0, 0, 0, -Lu1 - Lu2], [0, -1, 0, -W1 + W2 - W3 - W4], [0, 0, -1, H1 - H2], [0, 0, 0, 1]])
rng = np.random.default_rng(4)
worst = max(float(np.abs(fk_forward(Su, Mu, q) - fk_space(Su, Mu, q)).max()) for q in rng.uniform(-np.pi, np.pi, (2000, 6)))
assert worst < 1e-12

out(S2n=vec(clean(S2n), 4), q2n=vec(clean(q2n)[:2], 4), worst=worst)
