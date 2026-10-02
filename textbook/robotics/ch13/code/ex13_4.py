"""算例 13.4.1–13.4.3：DH 参数与指数积的相互换算。

13.4.1 DH → 指数积（定理 13.4.1）：UR 公布的 UR5e 标准 DH 表 → 六个旋量轴与 M；与第 12 章表 12.1.1 比较。
13.4.2 指数积 → DH：只用表 12.1.1 的六个旋量轴（不用轴上的点 q），先由 q* = ω × v 求出每根轴上离原点最近的点，
       再按 13.2 节的步骤建系，得到零件库尺寸下的 DH 表；与指数积在一万组随机关节角下核对。
13.4.3 Panda：Franka 按 Craig 约定公布的 DH 表 → 旋量轴（推论 13.4.1）；与第 12 章表 12.3.1（零件库模型）比较；
       再按定理 13.1.2 改写成标准 DH 表，三者互相核对。
"""
import math

import numpy as np

from _dh import (Model, Rx, Rz, Tz, adjoint, clean, exp6, fk_mdh, fk_sdh, fk_space, inv, lines_to_sdh, mdh_to_poe,
                 screw_revolute, sdh_to_poe, ur_poe, ur_vendor)
from bookout import out, tex, vec

pi = math.pi
rng = np.random.default_rng(134)
N = 10000

# ---------------------------------------------------------------- 13.4.1 UR5e：DH → 指数积
vend = ur_vendor()
Rx90 = Rx(pi / 2)
Sv, Mv = sdh_to_poe(vend, T_nb=Rx90)                 # 末端取第 12 章的 {b}：{6} 再绕 x 转 90°
tab, S12, M12 = ur_poe()
dw = max(float(np.abs(a[:3] - b[:3]).max()) for a, b in zip(Sv, S12))
dv = max(float(np.abs(a[3:] - b[3:]).max()) for a, b in zip(Sv, S12)) * 1000
dM = float(np.linalg.norm(Mv[:3, 3] - M12[:3, 3])) * 1000
F0 = fk_sdh(vend, np.zeros(6), frames=True)
rows_v = []
for i, s in enumerate(Sv, 1):
    q = F0[i - 1][:3, 3]
    rows_v.append(f"{i} & {vec(clean(s[:3], 1e-9), 0)} & {vec(clean(q, 1e-12), 4)} & {vec(clean(s[3:], 1e-12), 4)}")
rows_v = r" \\ ".join(rows_v)
for _ in range(2000):                                 # 定理 13.4.1：指数积与 DH 连乘完全相同
    q = rng.uniform(-pi, pi, 6)
    assert np.allclose(fk_space(Sv, Mv, q), fk_sdh(vend, q) @ Rx90, atol=1e-12)
# 定理的证明步骤：Rot(z, θ) 搬到 {0} 中就是绕 z_{i−1} 轴的 e^{[S_i]θ}
P1 = F0[1]
th = 0.7
assert np.allclose(P1 @ Rz(th) @ inv(P1), exp6(adjoint(P1) @ np.array([0, 0, 1.0, 0, 0, 0]), th), atol=1e-12)

# ---------------------------------------------------------------- 13.4.2 UR5e：指数积 → DH
lines = []
for s in S12:
    w, v = s[:3], s[3:]
    qstar = np.cross(w, v)                            # 轴上离原点最近的点，式 (13.4.5)
    assert abs(qstar @ w) < 1e-12 and np.allclose(-np.cross(w, qstar), v)
    lines.append(("R", w, qstar))
qstars = [clean(l[2], 1e-12) for l in lines]
model, Fm = lines_to_sdh(lines, M12[:3, 3])
T6b = inv(Fm[-1]) @ M12
err_model = 0.0
for _ in range(N):
    q = rng.uniform(-pi, pi, 6)
    err_model = max(err_model, float(np.abs(fk_sdh(model, q) @ T6b - fk_space(S12, M12, q)).max()))
assert err_model < 1e-9


def ang(x):
    k = round(x / (pi / 2))
    assert abs(x - k * pi / 2) < 1e-9
    return {0: "0", 1: r"\pi/2", -1: r"-\pi/2", 2: r"\pi", -2: r"-\pi"}[k]


def num(x, n=4):
    return "0" if abs(x) < 1e-12 else f"{x:.{n}f}".rstrip("0").rstrip(".")


rows_m = r" \\ ".join(f"{i} & {num(a)} & {ang(al)} & {num(d)} & {ang(t) if abs(t) > 1e-12 else '0'}"
                      for i, (a, al, d, t) in enumerate(model, 1))

# ---------------------------------------------------------------- 13.4.3 Panda：Craig 表 → 指数积
franka = [(0, 0, 0.333, 0), (0, -pi / 2, 0, 0), (0, pi / 2, 0.316, 0), (0.0825, pi / 2, 0, 0),
          (-0.0825, -pi / 2, 0.384, 0), (0, pi / 2, 0, 0), (0.088, pi / 2, 0, 0)]       # (a_{i-1}, α_{i-1}, d_i, θ_i)
d_flange = 0.107
T_hand = Tz(d_flange) @ Rz(-pi / 4)                    # 法兰 → 零件库的 hand 坐标系（第 12 章的 {b}）
Sp, Mp = mdh_to_poe(franka, T_nb=T_hand)
pa = Model("B-ARM-PANDA", "link0", "hand", (0, 0, 0), [f"joint{i}" for i in range(1, 8)])
axes_pa = pa.axes()
S_model = [screw_revolute(w, q) for _, w, q in axes_pa]
err_Sp = max(float(np.abs(a - b).max()) for a, b in zip(Sp, S_model))
err_Mp = float(np.abs(Mp - pa.fk(np.zeros(7))).max())
err_pa = 0.0
for _ in range(N):
    q = rng.uniform(-pi, pi, 7)
    Tm = pa.fk(q)
    err_pa = max(err_pa, float(np.abs(fk_space(Sp, Mp, q) - Tm).max()), float(np.abs(fk_mdh(franka, q) @ T_hand - Tm).max()))
assert err_pa < 1e-6
# 库中各连杆坐标系就是 Craig 的连杆坐标系
link_err = max(float(np.abs(fk_mdh(franka, np.zeros(7), frames=True)[i] - pa.link(f"link{i}", np.zeros(7))).max())
               for i in range(1, 8))
assert link_err < 1e-6
# 定理 13.1.2：改写成标准 DH（a、α 上移一行；最后一行取法兰行的 a = α = 0）
sdh_pa = [(franka[i + 1][0], franka[i + 1][1], franka[i][2], 0.0) if i < 6 else (0.0, 0.0, franka[6][2], 0.0) for i in range(7)]
for _ in range(500):
    q = rng.uniform(-pi, pi, 7)
    assert np.allclose(fk_sdh(sdh_pa, q), fk_mdh(franka, q), atol=1e-12)
rows_fr = r" \\ ".join(f"{i} & {num(a)} & {ang(al)} & {num(d)} & \\theta_{i}" for i, (a, al, d, _) in enumerate(franka, 1))
rows_fs = r" \\ ".join(f"{i} & {num(a)} & {ang(al)} & {num(d)} & \\theta_{i}" for i, (a, al, d, _) in enumerate(sdh_pa, 1))

out(rows_v=rows_v, dw=dw, dv=dv, dM=dM, Mv=tex(clean(Mv, 1e-12), 4), qs2=vec(qstars[1], 3), qs5=vec(qstars[4], 3),
    rows_m=rows_m, T6b=tex(clean(T6b), 0), err_model=err_model, N=N,
    rows_fr=rows_fr, rows_fs=rows_fs, err_Sp=err_Sp, err_Mp=err_Mp, err_pa=err_pa, link_err=link_err, d_flange=d_flange)
