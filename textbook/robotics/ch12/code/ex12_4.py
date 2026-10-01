"""算例 12.4.1：指数积的第二种读法——从第一个关节往后，每转一个关节，后面的关节轴跟着走。

e^{[S1]θ1} e^{[S2]θ2} = e^{[S2']θ2} e^{[S1]θ1}，其中 S2' = [Ad_{e^{[S1]θ1}}] S2 是关节 1 转过以后关节 2 的新轴（定理 12.4.1）。
平面 3R：θ1 = 30° 后，关节 2 的轴从 q2 = (L1, 0) 移到 (L1 cos 30°, L1 sin 30°)。
UR5e：随机关节角下，两种读法给出同一个末端位姿。
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

# “往后读”：每转一个关节，就把后面所有关节的轴用伴随矩阵搬到新位置
def fk_forward(Slist, M, theta):
    axes = [np.array(s) for s in Slist]
    T = np.eye(4)
    for i, t in enumerate(theta):
        E = exp6(axes[i], t)
        T = E @ T
        axes = [adjoint(E) @ a if k > i else a for k, a in enumerate(axes)]
    return T @ M


assert np.allclose(fk_forward(S, M, th), fk_space(S, M, th))

# UR5e：两种读法一致
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
