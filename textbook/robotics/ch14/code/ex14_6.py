"""14.6 节：SCARA 与 Delta 的逆解。

SCARA（零件库 B-SCA-WQ4：两臂 0.35 m、0.25 m；零位时工具点高 0.242 m；丝杠向下为正，行程 0–0.15 m；
关节 1 限位 ±140°，关节 2 限位 ±145°）：
(1) 算例 14.6.1：工具点到 (0.40, 0.20, 0.15) m、工具 x 轴与 x 轴成 30°。右手、左手两种构型，代回零件库模型核对。
(2) 只有一种构型在限位以内的目标：(−0.30, 0.35) m 一带。用 2.5 mm 的网格统计水平工作区内两种构型各自可用的比例。
(3) 沿直线 x = 0.45 m、y 从 −0.3 m 到 0.3 m 运动：两种构型的关节轨迹都连续，各自的关节 1 转角范围。
Delta（零件库 B-PAR-DELTA，尺寸见 11.5 节）：
(4) 每条支链的逆解就是子问题 3：与式 (11.5.7) 在一万个随机点上比较。
(5) 静止位置 (0, 0, −0.42) m：2³ = 8 种组合的转角，只有一种在限位 −40°～90° 以内。
(6) 沿模型给定的拾取路径（半径 0.12 m、高度 −0.42 m 的水平圆）每 1° 求一次逆解，再用三球求交（式 (11.5.8)）
    求回平台位置，误差小于 10⁻⁹ m；三根主动臂转角的变化范围。
(7) 工作空间沿中心轴向下的边界：支链伸直（主动臂与从动杆共线）时两解合一，但那时转角已超出 90° 的限位；
    实际的下边界由限位决定：主动臂竖直向下。
"""
import math

import numpy as np

from _ik import DELTA, SC, delta_ek, delta_elbow, delta_fk, delta_leg_sp3, delta_leg_trig, fk2r, ik2r, pose_err, rot, scara_ik, scara_model, wrap
from bookout import out

rng = np.random.default_rng(146)
sc = scara_model()
lim1, lim2 = math.radians(140), math.radians(145)
z0 = sc.fk([0, 0, 0, 0])[2, 3]
assert abs(z0 - 0.242) < 1e-12


def scara_T(x, y, z, phi):
    T = np.eye(4)
    T[:3, :3] = rot([0, 0, 1], phi)
    T[:3, 3] = [x, y, z]
    return T


# ---------------------------------------------------------------- (1) 算例 14.6.1
tgt = (0.40, 0.20, 0.15, math.radians(30))
sols = scara_ik(*tgt, z0)
assert len(sols) == 2
worst = 0.0
for s in sols:
    worst = max(worst, *pose_err(sc.fk(s), scara_T(*tgt)))
assert worst < 1e-12
right = [s for s in sols if s[1] > 0][0]                 # θ2 > 0：俯视时肘部在基座—目标连线的右侧
left = [s for s in sols if s[1] < 0][0]
inlim = lambda s: abs(s[0]) <= lim1 and abs(s[1]) <= lim2
assert inlim(right) and inlim(left)
fmt = lambda s: f"({math.degrees(s[0]):.2f}°, {math.degrees(s[1]):.2f}°, {s[2]:.3f}\\ \\mathrm{{m}}, {math.degrees(s[3]):.2f}°)"

# ---------------------------------------------------------------- (2) 限位与两种构型
xy = (-0.30, 0.35)
s2 = scara_ik(xy[0], xy[1], 0.15, 0.0, z0)
ok2 = [inlim(s) for s in s2]
assert sum(ok2) == 1
only = [s for s, k in zip(s2, ok2) if k][0]
other = [s for s, k in zip(s2, ok2) if not k][0]
h = 0.0025
g = np.arange(-0.6, 0.6 + h / 2, h)
n_any = n_both = n_r = n_l = 0
for x in g:
    for y in g:
        ss = ik2r(x, y, SC["L1"], SC["L2"])
        if not ss:
            continue
        okr = any(t[1] > 0 and abs(t[0]) <= lim1 and abs(t[1]) <= lim2 for t in ss)
        okl = any(t[1] < 0 and abs(t[0]) <= lim1 and abs(t[1]) <= lim2 for t in ss)
        n_any += okr or okl
        n_both += okr and okl
        n_r += okr
        n_l += okl
A_any = n_any * h * h
A_both = n_both * h * h

# ---------------------------------------------------------------- (3) 沿直线运动
ys = np.linspace(-0.3, 0.3, 601)
traj = {1: [], -1: []}
for y in ys:
    for s in ik2r(0.45, y, SC["L1"], SC["L2"]):
        traj[1 if s[1] > 0 else -1].append(s)
for k in traj:
    a = np.array(traj[k])
    assert len(a) == len(ys)
    assert np.abs(np.diff(np.unwrap(a[:, 0]))).max() < math.radians(1)   # 连续
r1 = np.degrees(np.array(traj[1])[:, 0])
l1 = np.degrees(np.array(traj[-1])[:, 0])

# ---------------------------------------------------------------- (4) Delta：子问题 3 与式 (11.5.7)
N = 10000
n_cmp = 0
for _ in range(N):
    p = np.array([rng.uniform(-0.25, 0.25), rng.uniform(-0.25, 0.25), rng.uniform(-0.75, -0.3)])
    for k in range(3):
        a = sorted(delta_leg_sp3(k, p))
        b = sorted(delta_leg_trig(k, p))
        assert len(a) == len(b)
        for x, y in zip(a, b):
            assert abs(wrap(x - y)) < 1e-9
        for t in a:
            E = delta_elbow(k, t)
            assert abs(np.linalg.norm(p + DELTA["Rp"] * delta_ek(k) - E) - DELTA["Lb"]) < 1e-12
        n_cmp += len(a)

# ---------------------------------------------------------------- (5) 静止位置的 8 种组合
p0 = np.array([0, 0, -0.42])
leg = [sorted(delta_leg_sp3(k, p0), reverse=True) for k in range(3)]
assert all(len(x) == 2 for x in leg)
lo, hi = math.radians(-40), math.radians(90)
combos = [(a, b, c) for a in leg[0] for b in leg[1] for c in leg[2]]
n_ok = sum(all(lo <= t <= hi for t in cmb) for cmb in combos)
assert len(combos) == 8 and n_ok == 1
th_out, th_in = math.degrees(leg[0][1]), math.degrees(leg[0][0])     # 肘部朝外（取 + 号）、朝内
th_out, th_in = sorted([th_out, th_in], key=abs)[0], sorted([th_out, th_in], key=abs)[1]
for cmb in combos:                                       # 每种组合都满足三条支链的闭环条件
    for k in range(3):
        assert abs(np.linalg.norm(p0 + DELTA["Rp"] * delta_ek(k) - delta_elbow(k, cmb[k])) - DELTA["Lb"]) < 1e-12

# ---------------------------------------------------------------- (6) 沿拾取路径
ang = np.radians(np.arange(0, 360, 1.0))
TH = []
err = 0.0
for a in ang:
    p = np.array([0.12 * math.cos(a), 0.12 * math.sin(a), -0.42])
    th = [min(delta_leg_sp3(k, p), key=lambda t: abs(t - 0.2)) for k in range(3)]   # 肘部朝外的一支
    assert all(lo <= t <= hi for t in th)
    q = delta_fk(th)
    err = max(err, float(np.linalg.norm(q - p)))
    TH.append(th)
TH = np.degrees(np.array(TH))
assert err < 1e-9

# ---------------------------------------------------------------- (7) 沿中心轴向下：支链伸直与关节限位
# 支链伸直（主动臂与从动杆共线）时两解合一。主动臂的方向是从铰点指向 P′_k，它的水平分量 R_p − R_b < 0（朝内），
# 所以伸直时的转角（从朝外的水平方向量起、向下为正）超过 90°：先碰到的是限位 90°（主动臂竖直向下）。
z_str = -math.sqrt((DELTA["La"] + DELTA["Lb"]) ** 2 - (DELTA["Rb"] - DELTA["Rp"]) ** 2)
eps = 1e-6
assert len(delta_leg_sp3(0, np.array([0, 0, z_str + eps]))) == 2 and len(delta_leg_sp3(0, np.array([0, 0, z_str - eps]))) == 0
t_str = math.degrees(math.atan2(-z_str, DELTA["Rp"] - DELTA["Rb"]))
th_str = delta_leg_trig(0, np.array([0, 0, z_str + 1e-12]))
assert abs(math.degrees(th_str[0]) - t_str) < 1e-3 and t_str > 90
z_lim = -DELTA["La"] - math.sqrt(DELTA["Lb"] ** 2 - (DELTA["Rb"] - DELTA["Rp"]) ** 2)       # 主动臂竖直向下（θ = 90°）
t_lim = max(delta_leg_trig(0, np.array([0, 0, z_lim])), key=lambda t: -abs(t - math.pi / 2))
assert abs(t_lim - math.pi / 2) < 1e-9
for dz, inside in ((1e-4, True), (-1e-4, False)):                                          # 再往下，朝外的解就超过 90°
    t_out = min(delta_leg_trig(0, np.array([0, 0, z_lim + dz])))
    assert (t_out <= math.pi / 2) == inside

out(z0=z0, sr=fmt(right), sl=fmt(left), worst=worst, r_t1=math.degrees(right[0]), l_t1=math.degrees(left[0]),
    only_t=f"({math.degrees(only[0]):.1f}°, {math.degrees(only[1]):.1f}°)", other_t=f"({math.degrees(other[0]):.1f}°, {math.degrees(other[1]):.1f}°)",
    only_is_right=int(only[1] > 0),
    A_any=A_any, A_both=A_both, both_pct=100 * n_both / n_any, r_pct=100 * n_r / n_any, l_pct=100 * n_l / n_any,
    r1_lo=r1.min(), r1_hi=r1.max(), l1_lo=l1.min(), l1_hi=l1.max(),
    N=N, n_cmp=n_cmp, th_out=th_out, th_in=th_in, n_ok=n_ok,
    path_err=err, th1_lo=TH[:, 0].min(), th1_hi=TH[:, 0].max(), th2_lo=TH[:, 1].min(), th2_hi=TH[:, 1].max(),
    z_str=z_str, t_str=t_str, z_lim=z_lim)
