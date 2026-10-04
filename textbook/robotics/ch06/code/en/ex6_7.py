"""Examples of Section 6.7.

First the properties of the Lie bracket are checked: in so(3), [[ω1],[ω2]] = [ω1 × ω2]; in se(3), the matrix
commutator agrees with [ad_V1]V2 (Eqs. (6.7.4), (6.7.6)); antisymmetry and the Jacobi identity; the derivative of the
adjoint matrix, d[Ad_T]/dt = [Ad_T][ad_Vb] (Eq. (6.7.10)).
Example 6.7.1: "forward–left–back–right" of a differential AGV: net displacement ≈ ε²[V1, V2] (Eq. (6.7.8)), with an
               error of order ε³; halving ε makes the sideways shift about a quarter.
Example 6.7.2: small rotations alternately about two axes fixed in {s} (the axes of joints 1 and 2 of the UR5e in the
               zero position): net motion ≈ −ε²[S1, S2], a rotation about an axis through the shoulder along −x;
               whereas when joints 1 and 2 of the UR5e turn back and forth, the end-effector returns exactly to the
               zero position.
Also: the first three terms of the Baker–Campbell–Hausdorff formula (Eq. (6.7.9)): log(e^A e^B) ≈ A + B + ½[A, B],
with a third-order error.
"""
import math

import numpy as np
from scipy.linalg import expm, logm

from _screw import UR_M, UR_S, ad, adjoint, axis_of, bracket, exp6, inv, lie, pose, skew, unbracket, unskew, ur_fk
from bookout import out, vec

rng = np.random.default_rng(67)

# ---------------------------------------------------------------- properties
for _ in range(30):
    w1, w2 = rng.normal(size=(2, 3))
    assert np.allclose(skew(w1) @ skew(w2) - skew(w2) @ skew(w1), skew(np.cross(w1, w2)))
    V1, V2, V3 = rng.normal(size=(3, 6))
    L = lie(V1, V2)
    assert np.allclose(L, ad(V1) @ V2)
    assert np.allclose(L, np.r_[np.cross(V1[:3], V2[:3]), np.cross(V1[:3], V2[3:]) - np.cross(V2[:3], V1[3:])])
    assert np.allclose(lie(V2, V1), -L)
    jac = lie(V1, lie(V2, V3)) + lie(V2, lie(V3, V1)) + lie(V3, lie(V1, V2))
    assert np.allclose(jac, 0, atol=1e-12)
    # derivative of the adjoint matrix: T(t) = T0 e^{[Vb]t}
    T0 = pose(expm(skew(rng.normal(size=3))), rng.normal(size=3))
    h = 1e-6
    dAd = (adjoint(T0 @ expm(bracket(V1) * h)) - adjoint(T0 @ expm(bracket(V1) * -h))) / (2 * h)
    assert np.allclose(dAd, adjoint(T0) @ ad(V1), atol=1e-7)

# ---------------------------------------------------------------- Example 6.7.1: differential AGV
Vf = np.array([0, 0, 0, 1.0, 0, 0])      # forward at 1 m/s (body frame)
Vr = np.array([0, 0, 1.0, 0, 0, 0])      # turn left about its own centre at 1 rad/s
Lfr = lie(Vf, Vr)
assert np.allclose(Lfr, [0, 0, 0, 0, -1, 0])


def maneuver(e, A=Vf, B=Vr):
    """Carry out A, B, −A, −B in turn in the body frame, each for ε: T = e^{[A]ε} e^{[B]ε} e^{−[A]ε} e^{−[B]ε} (postmultiplying)."""
    return expm(bracket(A) * e) @ expm(bracket(B) * e) @ expm(-bracket(A) * e) @ expm(-bracket(B) * e)


res = {}
for e in (0.2, 0.1, 0.05):
    T = maneuver(e)
    pred = expm(bracket(Lfr) * e * e)
    res[e] = (T[:3, 3].copy(), float(np.linalg.norm(T - pred)))
y02, y01 = res[0.2][0][1], res[0.1][0][1]
x02 = res[0.2][0][0]
assert abs(math.atan2(maneuver(0.2)[1, 0], maneuver(0.2)[0, 0])) < 1e-12        # back to the original heading
# closed form: displacement after forward ε, left ε, back ε, right ε is (ε(1 − cos ε), −ε sin ε)
assert np.allclose(res[0.2][0][:2], [0.2 * (1 - math.cos(0.2)), -0.2 * math.sin(0.2)])
# the error is of order ε³
r = res[0.2][1] / res[0.1][1]
assert 6 < r < 10
assert 3.5 < y02 / y01 < 4.5

# ---------------------------------------------------------------- Example 6.7.2: UR5e joints 1 and 2
L12 = lie(UR_S[0], UR_S[1])
s12, q12, h12 = axis_of(L12)
assert np.allclose(s12, [1, 0, 0]) and np.allclose(q12, [0, 0, 0.163]) and abs(h12) < 1e-12
# both axes fixed in {s}; in turn "ε about S1, ε about S2, back about S1, back about S2", each step premultiplying:
# T = e^{−[S2]ε} e^{−[S1]ε} e^{[S2]ε} e^{[S1]ε}, i.e. A = −S2, B = −S1 in Eq. (6.7.8); net effect ε²[S2, S1] = −ε²[S1, S2].
def spatial_seq(e, S1=UR_S[0], S2=UR_S[1]):
    return expm(-bracket(S2) * e) @ expm(-bracket(S1) * e) @ expm(bracket(S2) * e) @ expm(bracket(S1) * e)


errs = []
for e in (0.1, 0.05):
    T = spatial_seq(e)
    errs.append(float(np.linalg.norm(T - expm(-bracket(L12) * e * e))))
assert 6 < errs[0] / errs[1] < 10
T01 = spatial_seq(0.1)
S01 = np.real(unbracket(logm(T01)))
rot_deg = math.degrees(np.linalg.norm(S01[:3]))
s_net = S01[:3] / np.linalg.norm(S01[:3])
assert s_net[0] < -0.99                      # the net rotation is about −x̂
s_net_axis, q_net, h_net = axis_of(S01)
assert np.linalg.norm(q_net - [0, 0, 0.163]) < 0.01
# for comparison: if joints 1 and 2 of the UR5e turn back and forth in the same order, all joint angles return to zero and the end-effector returns exactly to M
th = np.zeros(6)
for j, dth in ((0, 0.1), (1, 0.1), (0, -0.1), (1, -0.1)):
    th[j] += dth
assert np.allclose(ur_fk(th), UR_M)

# ---------------------------------------------------------------- BCH
A, B = bracket(rng.normal(size=6)), bracket(rng.normal(size=6))
bch = []
for e in (0.1, 0.05):
    Lg = np.real(logm(expm(A * e) @ expm(B * e)))
    bch.append(float(np.linalg.norm(Lg - (A + B) * e - 0.5 * (A @ B - B @ A) * e * e)))
assert 6 < bch[0] / bch[1] < 10

out(L12=vec(L12, 3), y02=y02, x02=x02, y01=y01, ratio=y02 / y01, err02=res[0.2][1], err01=res[0.1][1], err_ratio=r,
    rot_deg=rot_deg, S01=vec(S01, 5), s_net=vec(s_net, 3), q_net=vec(q_net, 3), pred_rot_deg=math.degrees(0.01))
