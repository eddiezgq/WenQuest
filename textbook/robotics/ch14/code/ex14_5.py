"""14.5 节：UR5e 的 8 组解。

旋量轴与零位位姿 M 取表 12.1.1（零件库模型尺寸）。逆解按 14.5 节的三步（_ik.ur_ik）：
  θ1：腕点沿 ω2 方向的分量（式 (14.5.3)）；θ5、θ6：方向上的子问题 2；θ3、θ2、θ4：子问题 3、1、1。

(1) 算例 14.5.1：目标位姿取算例 12.3.1 的末端位姿（θ* = (30°, −60°, 90°, −120°, −90°, 45°)），求 8 组解，
    逐组用零件库三维模型（与指数积无关的另一种算法）计算末端位姿，与目标比较，位置误差必须小于 10⁻⁹ m。
(2) 另一种解法：Hawkins (2013) 基于标准 DH 参数的公式（第 13 章），得到同样的 8 组解。
(3) 数值法从 200 个随机初值出发，找到的不同的解恰好是这 8 组。
(4) 三千组随机位姿：解的个数的分布；每一组解都与零件库模型核对。
(5) 选解：离当前关节角最近的一组（URScript 的 get_inverse_kin 也是这样选的）。
(6) 三种奇异：肩部 ρ = d4、肘部 θ3 = 0 时两支解合一；手腕 θ5 = 0 时 θ6 可任取，解成为一族。
"""
import math

import numpy as np

from _ik import (D4, RX90, UR_M, UR_Q, UR_S, W4, YD, act, distinct, exp6, inv, numeric_ik, pose_err, same_solution,
                 ur_fk, ur_ik, ur_ik_234, ur_ik_dh, ur_model, ur_ordered, ur_points, wrap)
from bookout import T as tr, out, tex, vec

ur = ur_model()
rng = np.random.default_rng(145)

# ---------------------------------------------------------------- (1) 算例 14.5.1
ths = np.radians([30, -60, 90, -120, -90, 45])
Td = ur_fk(ths)
assert pose_err(Td, ur.fk(ths))[0] < 1e-9
pd, Rd = Td[:3, 3], Td[:3, :3]
pw = pd - W4 * Rd[:, 1]                                        # 腕点 = 法兰中心沿法线退回 W4，式 (14.5.1)
rho = math.hypot(pw[0], pw[1])
base = math.degrees(math.atan2(pw[0], -pw[1]))
gam = math.degrees(math.atan2(math.sqrt(rho * rho - D4 * D4), D4))
sols = ur_ik(Td)
assert len(sols) == 8
t1s = sorted({round(math.degrees(s[0]), 9) for s, _ in sols}, reverse=True)

# 第 2 步的中间量（取 θ1 的第一个值）
t1a = sols[0][0][0]
Rg = exp6(UR_S[0], -t1a)[:3, :3] @ Rd @ UR_M[:3, :3].T
v = Rg.T @ YD
c5 = float(v @ YD)
t5a = math.degrees(math.acos(c5))
# 第 3 步的中间量（取第一组 θ5、θ6）
s0 = sols[0][0]
g = exp6(UR_S[0], -s0[0]) @ Td @ inv(UR_M) @ exp6(UR_S[5], -s0[5]) @ exp6(UR_S[4], -s0[4])
p4 = act(g, UR_Q[3])
dl = float(np.linalg.norm(p4 - UR_Q[1]))


rows, worst_p, worst_R = [], 0.0, 0.0
star = None
sols_ordered = []
for i, (s, (sh, el, noflip)) in enumerate(ur_ordered(sols), 1):
    ep, eR = pose_err(ur.fk(s), Td)                           # 零件库模型：与指数积无关的另一种算法
    worst_p, worst_R = max(worst_p, ep), max(worst_R, eR)
    assert ep < 1e-9 and eR < 1e-9
    if same_solution(s, ths, 1e-9):
        star = i
    sols_ordered.append(s)
    m, e = f"{ep:.1e}".split("e")
    rows.append(f"| {i} | {sh} | {tr('上', 'up') if el == 'up' else tr('下', 'down')} | "
                f"{tr('不翻', 'no') if noflip else tr('翻', 'yes')} | " + " | ".join(f"{math.degrees(x):.2f}" for x in s) +
                f" | ${m}\\times 10^{{{int(e)}}}$ |")
assert star is not None
table = "\n".join(rows)
below = [i for i, s in enumerate(sols_ordered, 1) if ur_points(s)[2:, 2].min() < 0]     # 肩以外的关节或连杆转折点低于安装面

# 手腕翻转的两组：θ5 反号，θ6 相差 π；前五个关节中 θ2、θ3、θ4 也变（腕部不是球形手腕）
for s in sols_ordered:
    partner = [o for o in sols_ordered if abs(wrap(o[0] - s[0])) < 1e-9 and abs(o[4] + s[4]) < 1e-9]
    assert partner and abs(abs(wrap(partner[0][5] - s[5])) - math.pi) < 1e-9

# ---------------------------------------------------------------- (2) Hawkins (2013) 的 DH 公式
dh = ur_ik_dh(Td @ inv(RX90))
assert len(dh) == 8 and all(any(same_solution(s, d, 1e-9) for d in dh) for s in sols_ordered)

# ---------------------------------------------------------------- (3) 数值法清点
found = [numeric_ik(ur_fk, Td, rng.uniform(-math.pi, math.pi, 6)) for _ in range(200)]
D = distinct(found)
assert len(D) == 8 and all(any(same_solution(d, s, 1e-6) for s in sols_ordered) for d in D)
n_conv = sum(x is not None for x in found)

# ---------------------------------------------------------------- (4) 三千组随机位姿
N = 3000
hist = {k: 0 for k in (0, 2, 4, 6, 8)}
wp = wR = 0.0
for _ in range(N):
    th = rng.uniform(-math.pi, math.pi, 6)
    T = ur_fk(th)
    S = ur_ik(T)
    hist[len(S)] += 1
    assert any(same_solution(s, th, 1e-6) for s, _ in S)
    for s, _ in S:
        e = pose_err(ur.fk(s), T)
        wp, wR = max(wp, e[0]), max(wR, e[1])
assert wp < 1e-9 and wR < 1e-9 and hist[0] == 0
# 不一定能到达的位姿：在 1.2 m 见方的空间内随机取法兰中心和姿态
hist_any = {k: 0 for k in (0, 2, 4, 6, 8)}
for _ in range(2000):
    T = np.eye(4)
    q = rng.normal(size=4)
    q /= np.linalg.norm(q)
    a, b, c, d = q
    T[:3, :3] = [[1 - 2 * (c * c + d * d), 2 * (b * c - a * d), 2 * (b * d + a * c)],
                 [2 * (b * c + a * d), 1 - 2 * (b * b + d * d), 2 * (c * d - a * b)],
                 [2 * (b * d - a * c), 2 * (c * d + a * b), 1 - 2 * (b * b + c * c)]]
    T[:3, 3] = rng.uniform([-0.6, -0.6, -0.3], [0.6, 0.6, 0.9])
    hist_any[len(ur_ik(T))] += 1

# ---------------------------------------------------------------- (5) 选解：离当前关节角最近
cur = np.radians([25, -55, 85, -115, -85, 40])
dist = [math.sqrt(sum(wrap(a - b) ** 2 for a, b in zip(s, cur))) for s in sols_ordered]
near = int(np.argmin(dist)) + 1
assert near == star
dist_sorted = sorted(dist)

# ---------------------------------------------------------------- (6) 三种奇异
# 手腕：θ5 = 0 时轴 6 与轴 2、3、4 平行，θ6 可任取，每取一个 θ6，θ2、θ3、θ4 由第 3 步求出（一族解）
t_w = ths.copy()
t_w[4] = 0.0
Tw = ur_fk(t_w)
Sw = [s for s, _ in ur_ik(Tw) if abs(wrap(s[0] - ths[0])) < 1e-9]
n_w = len(distinct(Sw, 1e-6))
for t6 in np.radians([-150, -60, 0, 45, 120]):
    fam = ur_ik_234(Tw, ths[0], 0.0, t6)
    assert fam
    for t2, t3, t4 in fam:
        assert max(pose_err(ur.fk([ths[0], t2, t3, t4, 0.0, t6]), Tw)) < 1e-9
# 肘部：θ3 = 0（小臂与大臂成一直线）时肘上、肘下两支合一
t_e = ths.copy()
t_e[2] = 0.0
Te = ur_fk(t_e)
Se = [s for s, lab in ur_ik(Te) if abs(wrap(s[0] - ths[0])) < 1e-9 and lab[1] == -1]
n_e = len(distinct(Se, 1e-6))
# 肩部：腕点离基座轴线恰为 d4 时 θ1 两支合一
Ts = Td.copy()
pw_s = Ts[:3, 3] - W4 * Ts[:3, 1]
Ts[:2, 3] += pw_s[:2] / np.linalg.norm(pw_s[:2]) * (D4 - np.linalg.norm(pw_s[:2]))
pw_s = Ts[:3, 3] - W4 * Ts[:3, 1]
assert abs(math.hypot(pw_s[0], pw_s[1]) - D4) < 1e-12
n_s = len({round(s[0], 9) for s, _ in ur_ik(Ts)})

out(pd=vec(pd, 4), pw=vec(pw, 4), rho=rho, base=base, gam=gam, t1a=t1s[0], t1b=t1s[1],
    v=vec(v, 4), c5=c5, t5a=t5a, p4=vec(p4, 4), dl=dl,
    table=table, star=star, worst_p=worst_p, worst_R=worst_R,
    n_conv=n_conv, N=N, h8=100 * hist[8] / N, h6=100 * hist[6] / N, h4=100 * hist[4] / N, h2=100 * hist[2] / N,
    wp=wp, wR=wR, a0=100 * hist_any[0] / 2000, a8=100 * hist_any[8] / 2000,
    cur=vec(np.degrees(cur), 0), near=near, dmin=math.degrees(dist_sorted[0]), d2=math.degrees(dist_sorted[1]),
    n_w=n_w, n_e=n_e, n_s=n_s, d4=D4, below=tr('、', ', ').join(str(i) for i in below), n_below=len(below))
