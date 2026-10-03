"""14.4 节：皮珀准则与球形手腕六轴臂的封闭解。

机器人：取 UR5e 的肩高 0.163 m、大臂 0.425 m、小臂 0.392 m、腕长 0.1 m，去掉侧向偏距，腕部三根轴交于腕心
（关节 1 竖直；关节 2、3 水平且平行；关节 4、6 沿小臂方向，关节 5 与之垂直），零位时手臂沿 +x 伸出。

(1) 腕心不受关节 4、5、6 影响（式 (14.4.1)），随机核对。
(2) 算例 14.4.1：目标位姿由 θ* = (30°, 40°, −70°, 20°, 50°, −30°) 算出，求全部 8 组解，逐组代回正运动学。
(3) 三种“翻转”的关系：手腕翻转 (θ4 + π, −θ5, θ6 + π)，前三个关节不变；肩部前后、肘上肘下只改前三个关节。
(4) 解耦：腕心不动、只改变末端姿态时，前三个关节角不变。
(5) 三千组随机位姿：全部有 8 组解（避开奇异位形），每组都代回正运动学核对。
"""
import math

import numpy as np

from _ik import SW, SW_M, SW_PW, SW_S, act, exp6, inv, pose_err, rot, same_solution, sw_fk, sw_ik, wrap
from bookout import T as tr, out

rng = np.random.default_rng(144)

# ---------------------------------------------------------------- (1) 腕心
for _ in range(1000):
    th = rng.uniform(-math.pi, math.pi, 6)
    th2 = th.copy()
    th2[3:] = rng.uniform(-math.pi, math.pi, 3)
    pw1 = act(sw_fk(th) @ inv(SW_M), SW_PW)
    pw2 = act(sw_fk(th2) @ inv(SW_M), SW_PW)
    assert np.allclose(pw1, pw2, atol=1e-12)
    T = sw_fk(th)
    assert np.allclose(pw1, T[:3, 3] - SW["D6"] * T[:3, 0], atol=1e-12)        # 腕心 = 法兰中心沿 x_b 退回 D6

# ---------------------------------------------------------------- (2) 算例 14.4.1
ths = np.radians([30, 40, -70, 20, 50, -30])
Td = sw_fk(ths)
sols = sw_ik(Td)
assert len(sols) == 8
worst = 0.0
for s, lab in sols:
    e = pose_err(sw_fk(s), Td)
    worst = max(worst, *e)
assert worst < 1e-12
assert any(same_solution(s, ths, 1e-9) for s, _ in sols)
pw = Td[:3, 3] - SW["D6"] * Td[:3, 0]

names_sh = {1: tr("前", "front"), -1: tr("后", "back")}
names_el = {1: tr("下", "down"), -1: tr("上", "up")}


def labels(s):
    """肩：腕心在关节 1 转到的竖直平面的前方（沿 x1 正向）为“前”；肘：肘点在肩—腕连线下方为“下”；腕：θ5 > 0 为“不翻”。"""
    t1, t2, t3 = s[:3]
    x1 = np.array([math.cos(t1), math.sin(t1), 0])
    sh = 1 if x1 @ (pw - np.array([0, 0, SW["H1"]])) > 0 else -1
    T2 = exp6(SW_S[0], t1) @ exp6(SW_S[1], t2)
    elbow = act(T2, np.array([SW["L1"], 0, SW["H1"]]))
    sh_pt = np.array([0, 0, SW["H1"]])
    n = np.cross(pw - sh_pt, np.array([-math.sin(t1), math.cos(t1), 0]))     # 手臂平面内、垂直于肩—腕连线、偏上的方向
    if n[2] < 0:
        n = -n
    el = 1 if (elbow - sh_pt) @ n < 0 else -1
    wr = 1 if s[4] > 0 else -1
    return sh, el, wr


rows = []
order = sorted(sols, key=lambda x: (-labels(x[0])[0], -labels(x[0])[1], -labels(x[0])[2]))
for i, (s, _) in enumerate(order, 1):
    sh, el, wr = labels(s)
    deg = [f"{math.degrees(v):.2f}" for v in s]
    mark = tr("（即 θ*）", " (= θ*)") if same_solution(s, ths, 1e-9) else ""
    rows.append(f"| {i} | {names_sh[sh]} | {names_el[el]} | {tr('不翻', 'no') if wr > 0 else tr('翻', 'yes')} | " + " | ".join(deg) + " |")
    if mark:
        star = i
table = "\n".join(rows)

# ---------------------------------------------------------------- (3) 翻转关系
sol_list = [s for s, _ in sols]
for s in sol_list:
    flip = np.array([s[0], s[1], s[2], wrap(s[3] + math.pi), -s[4], wrap(s[5] + math.pi)])
    assert any(same_solution(flip, o, 1e-9) for o in sol_list)                  # 手腕翻转：前三个关节不变
# 前三个关节只有 4 种不同的取值（2 × 2），每种对应 2 组腕部解
firsts = []
for s in sol_list:
    if not any(np.allclose([wrap(a - b) for a, b in zip(s[:3], f)], 0, atol=1e-9) for f in firsts):
        firsts.append(s[:3])
assert len(firsts) == 4
# 肩部前后：θ1 → θ1 + π；肘上肘下：θ3 → −θ3
t1s = sorted({round(math.degrees(f[0]), 6) for f in firsts})
assert len(t1s) == 2 and abs(abs(t1s[1] - t1s[0]) - 180) < 1e-6
for f in firsts:
    assert any(abs(wrap(g[0] - f[0])) < 1e-9 and abs(wrap(g[2] + f[2])) < 1e-9 for g in firsts if g is not f)

# ---------------------------------------------------------------- (4) 解耦：只改变姿态
Rnew = Td[:3, :3] @ rot([0, 1, 0], math.radians(35)) @ rot([1, 0, 0], math.radians(-20))
Tn = np.eye(4)
Tn[:3, :3] = Rnew
Tn[:3, 3] = pw + SW["D6"] * Rnew[:, 0]                 # 腕心保持在 pw
sn = sw_ik(Tn)
for s, _ in sn:
    assert any(np.allclose([wrap(a - b) for a, b in zip(s[:3], f)], 0, atol=1e-9) for f in firsts)

# ---------------------------------------------------------------- (5) 随机位姿
N = 3000
n8 = n_try = 0
worst_r = 0.0
while n_try < N:
    th = rng.uniform(-math.pi, math.pi, 6)
    th[4] = rng.choice([-1, 1]) * rng.uniform(0.05, math.pi - 0.05)          # 避开手腕奇异 sin θ5 = 0
    th[2] = rng.choice([-1, 1]) * rng.uniform(0.05, math.pi - 0.05)          # 避开肘部奇异 sin θ3 = 0
    T = sw_fk(th)
    pwr = T[:3, 3] - SW["D6"] * T[:3, 0]
    if math.hypot(pwr[0], pwr[1]) < 0.01:                                    # 避开肩部奇异：腕心在关节 1 的轴上
        continue
    n_try += 1
    S = sw_ik(T)
    n8 += len(S) == 8
    for s, _ in S:
        worst_r = max(worst_r, *pose_err(sw_fk(s), T))
assert worst_r < 1e-9 and n8 == N

out(pw=f"({pw[0]:.4f}, {pw[1]:.4f}, {pw[2]:.4f})", table=table, star=star, worst=worst, N=N, n8=n8, worst_r=worst_r,
    px=Td[0, 3], py=Td[1, 3], pz=Td[2, 3])
