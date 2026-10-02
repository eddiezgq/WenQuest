"""Examples 12.1.1 and 12.1.2: joint screws.

12.1.1 Planar 3R arm (with the upper-arm and forearm lengths of the UR5e): the three joint screws and the home pose M.
12.1.2 UR5e: write ω and q of the six joints from the dimensions of the parts-library model, compute S = (ω, −ω × q),
       and compare them one by one with "the axes read directly from the node matrices of the model" (the two sources must agree).
"""
import numpy as np

from _poe import Model, clean, exp6, expm_series, bracket, screw_revolute
from bookout import out, tex, vec

# ---------------------------------------------------------------- Example 12.1.1, planar 3R
L1, L2, L3 = 0.425, 0.392, 0.1
z = np.array([0, 0, 1.0])
q3r = [np.zeros(3), np.array([L1, 0, 0]), np.array([L1 + L2, 0, 0])]
S3r = [screw_revolute(z, q) for q in q3r]
M3r = np.eye(4)
M3r[0, 3] = L1 + L2 + L3

# The two ways of computing the exponential agree: Eq. (12.1.5) and the series definition
t = np.radians(30)
for S in S3r:
    assert np.allclose(exp6(S, t), expm_series(bracket(S) * t), atol=1e-12)

# Joint 2 turns 30°: the tool turns 30° about (L1, 0)
T2 = exp6(S3r[1], t) @ M3r
p_tip = T2[:3, 3]
r = L2 + L3
assert np.allclose(p_tip, [L1 + r * np.cos(t), r * np.sin(t), 0])

# ---------------------------------------------------------------- Example 12.1.2, UR5e
H1, W1, L1u, W2, L2u, W3, H2, W4 = 0.163, 0.138, 0.425, 0.131, 0.392, 0.127, 0.1, 0.1   # dimensions from the joint table of the model (m)
yd = -np.array([0, 1.0, 0])     # −ŷ
table = [  # (ω, q); the frame {s} is the robot's base frame
    (np.array([0, 0, 1.0]), np.array([0, 0, H1])),
    (yd, np.array([0, -W1, H1])),
    (yd, np.array([-L1u, -W1 + W2, H1])),
    (yd, np.array([-L1u - L2u, -W1 + W2, H1])),
    (np.array([0, 0, -1.0]), np.array([-L1u - L2u, -W1 + W2 - W3, H1])),
    (yd, np.array([-L1u - L2u, -W1 + W2 - W3, H1 - H2])),
]
Sur = [screw_revolute(w, q) for w, q in table]
Mur = np.array([[1.0, 0, 0, -L1u - L2u], [0, -1, 0, -W1 + W2 - W3 - W4], [0, 0, -1, H1 - H2], [0, 0, 0, 1]])

ur = Model("B-ARM-UR5E", "base", "wrist_3_link", (0, W4, 0))
read = ur.screws()
for (w, q), S, (name, kind, w_m, q_m, S_m) in zip(table, Sur, read):
    assert np.allclose(w, w_m, atol=1e-9) and np.allclose(S, S_m, atol=1e-9), name
assert np.allclose(Mur, ur.fk(np.zeros(6)), atol=1e-6)

rows = []
for i, ((w, q), S) in enumerate(zip(table, Sur), 1):
    rows.append(f"{i} & {vec(clean(w), 3)} & {vec(clean(q), 3)} & {vec(clean(S[3:]), 3)}")
out(S2=vec(S3r[1], 3), S3=vec(S3r[2], 3), M3r=tex(M3r, 3),
    L123=L1 + L2 + L3, L12=L1 + L2, tip_x=p_tip[0], tip_y=p_tip[1],
    ur_rows=r" \\ ".join(rows), Mur=tex(clean(Mur), 3), ur_x=-L1u - L2u, ur_y=-W1 + W2 - W3 - W4, ur_z=H1 - H2,
    yoff=-W1 + W2, yoff2=-W1 + W2 - W3)
