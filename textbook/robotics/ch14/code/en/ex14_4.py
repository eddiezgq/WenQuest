"""Section 14.4: Pieper's criterion and the closed-form solution of a six-axis arm with a spherical wrist.

Robot: the UR5e shoulder height 0.163 m, upper arm 0.425 m, forearm 0.392 m and wrist length 0.1 m, with the sideways
offsets removed and the three wrist axes meeting at the wrist centre (joint 1 vertical; joints 2 and 3 horizontal and
parallel; joints 4 and 6 along the forearm, joint 5 perpendicular to them); in the zero position the arm reaches out
along +x.

(1) The wrist centre is not affected by joints 4, 5, 6 (Eq. (14.4.1)), checked at random.
(2) Example 14.4.1: the target pose is computed from θ* = (30°, 40°, −70°, 20°, 50°, −30°); find all 8 solutions and
    substitute each back into the forward kinematics.
(3) The three kinds of "flip": wrist flip (θ4 + π, −θ5, θ6 + π) with the first three joints unchanged; shoulder
    front/back and elbow up/down change only the first three joints.
(4) Decoupling: with the wrist centre fixed and only the end-effector orientation changed, the first three joint angles
    do not change.
(5) Three thousand random poses: all have 8 solutions (singular configurations avoided), each checked against the
    forward kinematics.
"""
import math

import numpy as np

from _ik import SW, SW_M, SW_PW, SW_S, act, exp6, inv, pose_err, rot, same_solution, sw_fk, sw_ik, wrap
from bookout import T as tr, out

rng = np.random.default_rng(144)

# ---------------------------------------------------------------- (1) wrist centre
for _ in range(1000):
    th = rng.uniform(-math.pi, math.pi, 6)
    th2 = th.copy()
    th2[3:] = rng.uniform(-math.pi, math.pi, 3)
    pw1 = act(sw_fk(th) @ inv(SW_M), SW_PW)
    pw2 = act(sw_fk(th2) @ inv(SW_M), SW_PW)
    assert np.allclose(pw1, pw2, atol=1e-12)
    T = sw_fk(th)
    assert np.allclose(pw1, T[:3, 3] - SW["D6"] * T[:3, 0], atol=1e-12)        # wrist centre = flange centre moved back D6 along x_b

# ---------------------------------------------------------------- (2) Example 14.4.1
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
    """Shoulder: "front" if the wrist centre is in front (along +x1) in the vertical plane joint 1 has turned to; elbow:
    "down" if the elbow point is below the shoulder–wrist line; wrist: "not flipped" if θ5 > 0."""
    t1, t2, t3 = s[:3]
    x1 = np.array([math.cos(t1), math.sin(t1), 0])
    sh = 1 if x1 @ (pw - np.array([0, 0, SW["H1"]])) > 0 else -1
    T2 = exp6(SW_S[0], t1) @ exp6(SW_S[1], t2)
    elbow = act(T2, np.array([SW["L1"], 0, SW["H1"]]))
    sh_pt = np.array([0, 0, SW["H1"]])
    n = np.cross(pw - sh_pt, np.array([-math.sin(t1), math.cos(t1), 0]))     # direction in the arm plane, perpendicular to the shoulder–wrist line, pointing upwards
    if n[2] < 0:
        n = -n
    el = 1 if (elbow - sh_pt) @ n < 0 else -1
    wr = 1 if s[4] > 0 else -1
    return sh, el, wr


rows = []
order = sorted(sols, key=lambda x: (-labels(x[0])[0], -labels(x[0])[1], -labels(x[0])[2]))
for i, (s, _) in enumerate(order, 1):
    sh, el, wr = labels(s)
    deg = [f"{math.degrees(v):.2f}".replace("-", "−") for v in s]
    mark = tr("（即 θ*）", " (= θ*)") if same_solution(s, ths, 1e-9) else ""
    rows.append(f"| {i} | {names_sh[sh]} | {names_el[el]} | {tr('不翻', 'no') if wr > 0 else tr('翻', 'yes')} | " + " | ".join(deg) + " |")
    if mark:
        star = i
table = "\n".join(rows)

# ---------------------------------------------------------------- (3) flip relations
sol_list = [s for s, _ in sols]
for s in sol_list:
    flip = np.array([s[0], s[1], s[2], wrap(s[3] + math.pi), -s[4], wrap(s[5] + math.pi)])
    assert any(same_solution(flip, o, 1e-9) for o in sol_list)                  # wrist flip: first three joints unchanged
# the first three joints take only 4 different sets of values (2 × 2), each with 2 wrist solutions
firsts = []
for s in sol_list:
    if not any(np.allclose([wrap(a - b) for a, b in zip(s[:3], f)], 0, atol=1e-9) for f in firsts):
        firsts.append(s[:3])
assert len(firsts) == 4
# shoulder front/back: θ1 → θ1 + π; elbow up/down: θ3 → −θ3
t1s = sorted({round(math.degrees(f[0]), 6) for f in firsts})
assert len(t1s) == 2 and abs(abs(t1s[1] - t1s[0]) - 180) < 1e-6
for f in firsts:
    assert any(abs(wrap(g[0] - f[0])) < 1e-9 and abs(wrap(g[2] + f[2])) < 1e-9 for g in firsts if g is not f)

# ---------------------------------------------------------------- (4) decoupling: change only the orientation
Rnew = Td[:3, :3] @ rot([0, 1, 0], math.radians(35)) @ rot([1, 0, 0], math.radians(-20))
Tn = np.eye(4)
Tn[:3, :3] = Rnew
Tn[:3, 3] = pw + SW["D6"] * Rnew[:, 0]                 # wrist centre kept at pw
sn = sw_ik(Tn)
for s, _ in sn:
    assert any(np.allclose([wrap(a - b) for a, b in zip(s[:3], f)], 0, atol=1e-9) for f in firsts)

# ---------------------------------------------------------------- (5) random poses
N = 3000
n8 = n_try = 0
worst_r = 0.0
while n_try < N:
    th = rng.uniform(-math.pi, math.pi, 6)
    th[4] = rng.choice([-1, 1]) * rng.uniform(0.05, math.pi - 0.05)          # avoid the wrist singularity sin θ5 = 0
    th[2] = rng.choice([-1, 1]) * rng.uniform(0.05, math.pi - 0.05)          # avoid the elbow singularity sin θ3 = 0
    T = sw_fk(th)
    pwr = T[:3, 3] - SW["D6"] * T[:3, 0]
    if math.hypot(pwr[0], pwr[1]) < 0.01:                                    # avoid the shoulder singularity: wrist centre on the axis of joint 1
        continue
    n_try += 1
    S = sw_ik(T)
    n8 += len(S) == 8
    for s, _ in S:
        worst_r = max(worst_r, *pose_err(sw_fk(s), T))
assert worst_r < 1e-9 and n8 == N

out(pw=f"({pw[0]:.4f}, {pw[1]:.4f}, {pw[2]:.4f})", table=table, star=star, worst=worst, N=N, n8=n8, worst_r=worst_r,
    px=Td[0, 3], py=Td[1, 3], pz=Td[2, 3])
