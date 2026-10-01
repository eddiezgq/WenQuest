"""算例 12.1.1、12.1.2：关节旋量。

12.1.1 平面 3R 臂（取 UR5e 大臂、小臂的长度）：三个关节旋量和零位位姿 M。
12.1.2 UR5e：按零件库模型的尺寸写出六个关节的 ω、q，算出 S = (ω, −ω × q)，
       并与“从模型节点矩阵直接读出的转轴”逐个比较（两种来源应一致）。
"""
import numpy as np

from _poe import Model, clean, exp6, expm_series, bracket, screw_revolute
from bookout import out, tex, vec

# ---------------------------------------------------------------- 算例 12.1.1 平面 3R
L1, L2, L3 = 0.425, 0.392, 0.1
z = np.array([0, 0, 1.0])
q3r = [np.zeros(3), np.array([L1, 0, 0]), np.array([L1 + L2, 0, 0])]
S3r = [screw_revolute(z, q) for q in q3r]
M3r = np.eye(4)
M3r[0, 3] = L1 + L2 + L3

# 指数的两种算法一致：式 (12.1.5) 与级数定义
t = np.radians(30)
for S in S3r:
    assert np.allclose(exp6(S, t), expm_series(bracket(S) * t), atol=1e-12)

# 转动关节 2 转 30°：末端绕 (L1, 0) 转过 30°
T2 = exp6(S3r[1], t) @ M3r
p_tip = T2[:3, 3]
r = L2 + L3
assert np.allclose(p_tip, [L1 + r * np.cos(t), r * np.sin(t), 0])

# ---------------------------------------------------------------- 算例 12.1.2 UR5e
H1, W1, L1u, W2, L2u, W3, H2, W4 = 0.163, 0.138, 0.425, 0.131, 0.392, 0.127, 0.1, 0.1   # 模型关节表中的尺寸 (m)
yd = -np.array([0, 1.0, 0])     # −ŷ
table = [  # (ω, q)，坐标系 {s} 为机器人基座坐标系
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
