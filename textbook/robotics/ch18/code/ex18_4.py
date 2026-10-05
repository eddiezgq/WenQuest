"""18.4 节：Delta 机器人（零件库 B-PAR-DELTA）的速度、静力、速度能力与拾放节拍。

(1) 算例 18.4.1：静止位置 p = (0, 0, −0.42) m 处的速度关系 A v = B θ̇（式 (18.4.3)），J = A⁻¹B；
    与三球求交的差商比较；肘点公式与零件库模型（关节表 + 节点矩阵）比较。
(2) 静力 τ = Jᵀ f：平台托住 1 kg（平台、吸盘、零件合计，𝔤 = 9.81 m/s²）时的电机力矩。
(3) 算例 18.4.2 与定理 18.4.1 的核对：电机转速不超过 ω_max 时平台能达到的速度。沿 x、y、z 的最大速度，以及各个方向都能保证的速度
    v_g = ω_max / max_k ‖J⁻¹ 的第 k 行‖；用 2000 个随机方向核对 v_g 是各方向最大速度的最小值。
(4) 速度能力地图：z = −0.42 m 的水平截面、y = 0 的竖直截面上的 v_g；v_g ≥ 1.9 m/s 的面积；工作空间内 v_g 的范围。
(5) 算例 18.4.3：25/305/25 mm 的拾放循环（上升 25 mm、水平移动 305 mm、下降 25 mm，再原路返回）。
    每段按匀速走，速度取电机转速限制下的最大值；只计速度限制时的节拍下限。比较不同的放置（中心、高度、方向）。
"""
import math

import numpy as np

from _ch18 import (D_HI, D_LO, D_REST, D_WMAX, DELTA, delbow, delta_AB, delta_fk, delta_ik, delta_J, delta_model_elbows,
                   delta_ok, delta_u, elbow, v_along, v_guaranteed)
from bookout import T, out, tex

deg = math.degrees

# ---------------------------------------------------------------- (1) 静止位置的速度关系
p0 = D_REST
th0 = delta_ik(p0)
A0, B0 = delta_AB(p0, th0)
J0 = np.linalg.solve(A0, B0)
h = 1e-7
Jfd = np.column_stack([(delta_fk(th0 + h * np.eye(3)[k]) - delta_fk(th0 - h * np.eye(3)[k])) / (2 * h) for k in range(3)])
assert np.abs(J0 - Jfd).max() < 1e-7
E_model, entry = delta_model_elbows(th0)
assert np.abs(E_model - np.array([elbow(k, th0[k]) for k in range(3)])).max() < 1e-12
assert abs(entry["robot"]["rest"]["J1"] - th0[0]) < 1e-6
assert abs(entry["robot"]["joints"][0]["limit"]["velocity"] - D_WMAX) < 1e-9
# 随机点上的差商核对
rng = np.random.default_rng(184)
jerr = 0.0
for _ in range(300):
    p = np.array([rng.uniform(-0.25, 0.25), rng.uniform(-0.25, 0.25), rng.uniform(-0.62, -0.32)])
    th = delta_ok(p)
    if th is None:
        continue
    J = delta_J(p, th)
    Jf = np.column_stack([(delta_fk(th + h * np.eye(3)[k]) - delta_fk(th - h * np.eye(3)[k])) / (2 * h) for k in range(3)])
    jerr = max(jerr, np.abs(J - Jf).max())
assert jerr < 1e-6
U0 = delta_u(p0, th0)
B00 = B0[0, 0]

# ---------------------------------------------------------------- (2) 静力
f_up = np.array([0, 0, 9.81])                    # 平台对负载施加向上的力
tau0 = J0.T @ f_up
assert np.allclose(tau0, tau0[0])
# 虚功核对
for k in range(3):
    d = np.eye(3)[k] * 1e-7
    dp = (delta_fk(th0 + d) - delta_fk(th0 - d)) / 2e-7
    assert abs(f_up @ dp - tau0[k]) < 1e-6

# ---------------------------------------------------------------- (3) 速度能力
vx, vy, vz = (v_along(J0, d) for d in np.eye(3))
vg0 = v_guaranteed(J0)
dirs = rng.normal(size=(2000, 3))
dirs /= np.linalg.norm(dirs, axis=1)[:, None]
vmin_dirs = min(v_along(J0, d) for d in dirs)
assert vmin_dirs >= vg0 - 1e-12 and vmin_dirs < vg0 * 1.02       # v_g 是下确界，随机方向的最小值略大于它
Ji = np.linalg.inv(J0)
kk = np.linalg.norm(Ji, axis=1).argmax()
d_worst = Ji[kk] / np.linalg.norm(Ji[kk])
assert abs(v_along(J0, d_worst) - vg0) < 1e-12                    # 最慢的方向是 J⁻¹ 第 k 行的方向
lci0 = np.linalg.svd(J0)[1][-1] / np.linalg.svd(J0)[1][0]

# ---------------------------------------------------------------- (4) 速度能力地图
hh = 0.01
g = np.arange(-0.45, 0.45 + hh / 2, hh)
vg_slice, A2 = [], 0.0
for x in g:
    for y in g:
        th = delta_ok(np.array([x, y, -0.42]))
        if th is None:
            continue
        v = v_guaranteed(delta_J(np.array([x, y, -0.42]), th))
        vg_slice.append(v)
        if v >= 1.9:
            A2 += hh * hh
vg_slice = np.array(vg_slice)
A_slice = len(vg_slice) * hh * hh
hv = 0.02
vg_all = []
for x in np.arange(-0.5, 0.5 + 1e-9, hv):
    for y in np.arange(-0.5, 0.5 + 1e-9, hv):
        for z in np.arange(-0.8, -0.15, hv):
            p = np.array([x, y, z])
            th = delta_ok(p)
            if th is not None:
                vg_all.append(v_guaranteed(delta_J(p, th)))
vg_all = np.array(vg_all)
vg_ax = []
for z in np.arange(-0.30, -0.701, -0.05):
    th = delta_ok(np.array([0, 0, z]))
    vg_ax.append((z, v_guaranteed(delta_J(np.array([0, 0, z]), th))))
z_best_axis = max(vg_ax, key=lambda t: t[1])


# ---------------------------------------------------------------- (5) 拾放循环
def cycle(c, ax, zp, n=241):
    """25/305/25 mm 循环：中心 (c[0], c[1])，拾放高度 zp，水平移动沿 ax（0 为 x，1 为 y）。
    返回 (各段最大匀速, 往返一次的时间, 路径上的点与电机转速)；有点在工作空间外时返回 None。"""
    a = np.zeros(3)
    a[ax] = 0.1525
    c3 = np.array([c[0], c[1], zp])
    P0, P1 = c3 - a, c3 - a + [0, 0, 0.025]
    P2, P3 = c3 + a + [0, 0, 0.025], c3 + a
    segs, vs, ttot = [(P0, P1), (P1, P2), (P2, P3)], [], 0.0
    track = []
    for S0, S1 in segs:
        L = np.linalg.norm(S1 - S0)
        d = (S1 - S0) / L
        vm = 1e9
        pts = []
        for s in np.linspace(0, 1, n):
            p = S0 + s * (S1 - S0)
            th = delta_ok(p)
            if th is None:
                return None
            J = delta_J(p, th)
            vm = min(vm, v_along(J, d))
            pts.append((p, J, d))
        vs.append(vm)
        for p, J, d_ in pts:
            track.append((ttot + np.linalg.norm(p - S0) / vm, np.linalg.solve(J, vm * d_)))
        ttot += L / vm
    return vs, 2 * ttot, track


base = cycle((0.0, 0.0), 0, -0.45)
th_place = [delta_ok(np.array([0.1525, 0, z]))[0] for z in (-0.45, -0.425)]       # 放置点一侧主动臂 1 的转角
vg_ends = [v_guaranteed(delta_J(np.array([x, 0, z]), delta_ok(np.array([x, 0, z])))) for x in (-0.1525, 0.1525) for z in (-0.45, -0.425)]
vs_base, t_base, track_base = base
wmax_track = max(np.abs(w).max() for _, w in track_base)
assert abs(wmax_track - D_WMAX) < 1e-6                    # 每段最慢的那一点上有一台电机正好到上限
res = []
for cx in (-0.1, -0.05, 0.0, 0.05, 0.1):
    for cy in (-0.1, -0.05, 0.0, 0.05, 0.1):
        for zp in (-0.40, -0.45, -0.50, -0.55, -0.60):
            for ax in (0, 1):
                r = cycle((cx, cy), ax, zp, n=61)
                if r is not None:
                    res.append((r[1], cx, cy, zp, ax))
res.sort()
best, worst = res[0], res[-1]
r_best = cycle(best[1:3], best[4], best[3])
t_best = r_best[1]
t_worst = cycle(worst[1:3], worst[4], worst[3])[1]
r_hi = cycle((0.0, 0.0), 0, -0.40)
dirname = lambda ax: T("x", "x") if ax == 0 else T("y", "y")

out(th0=deg(th0[0]), J0=tex(J0, 4), A0=tex(A0, 4), B00=B00, u1=tex(U0[0], 4), jerr=jerr,
    tau0=tau0[0], vx=vx, vy=vy, vz=vz, vg0=vg0, vmin_dirs=vmin_dirs, lci0=lci0, wmax=D_WMAX, wmax_deg=deg(D_WMAX),
    vg_slice_min=vg_slice.min(), vg_slice_max=vg_slice.max(), A_slice=A_slice, A2=A2, A2_pct=100 * A2 / A_slice,
    vg_all_min=vg_all.min(), vg_all_max=vg_all.max(), vg_all_med=np.median(vg_all), n_all=len(vg_all),
    z_best_axis=z_best_axis[0], vg_best_axis=z_best_axis[1],
    vs1=vs_base[0], vs2=vs_base[1], vs3=vs_base[2], t_base=t_base, cpm_base=60 / t_base,
    t_best=t_best, cpm_best=60 / t_best, b_cx=best[1], b_cy=best[2], b_z=best[3], b_dir=dirname(best[4]),
    t_worst=t_worst, w_cx=worst[1], w_cy=worst[2], w_z=worst[3], w_dir=dirname(worst[4]), n_place=len(res),
    t_hi=r_hi[1], gain_pct=100 * (t_worst - t_best) / t_best,
    xend=0.1525, thp_a=deg(min(th_place[0], th_place[1])), thp_b=deg(max(th_place[0], th_place[1])), vg_end_min=min(vg_ends), vg_end_max=max(vg_ends))
