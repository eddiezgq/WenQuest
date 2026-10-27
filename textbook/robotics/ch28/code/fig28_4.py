"""28.4 节的示意图。

图 28.4.2：(a) Go2 静止站立时四只脚的地面力：MuJoCo 的解与最小范数解，竖直分量相同，MuJoCo 多出把脚往里拉的侧向内力；
          (b) 足端离地 0.3 m 落下：地面合力的竖直分量（10 ms 平均）与体重之比，关节刚度 kp = 60、100 N·m/rad；
          (c) 同一过程中机身的高度。
图 28.4.1：失重时摆腿翻身。(a) 大腿、小腿相对站立姿态的转角：只来回转大腿（一条线段）与按方框转一圈；
          (b) 机身的俯仰角：来回转回到原处，转一圈净转过一个角度，反着转则反向。
"""
import math

import mujoco
import numpy as np

from _ch28 import G, GO2_HOME, go2_contacts, go2_feet, go2_model, go2_pd, quat2R, skew
from bookout import COLORS as C, T, figure, style

plt = style()
m, d = go2_model()
feet = go2_feet(m, d)
M = float(m.body_subtreemass[1])
W = M * G
mujoco.mj_resetDataKeyframe(m, d, 0)
while d.time < 2.0:
    go2_pd(m, d, GO2_HOME, 60.0, 2.0)
    mujoco.mj_step(m, d)
F, pos = go2_contacts(m, d, feet)
c = d.subtree_com[1].copy()
G6 = np.zeros((6, 12))
for k in range(4):
    G6[0:3, 3 * k:3 * k + 3] = np.eye(3)
    G6[3:6, 3 * k:3 * k + 3] = skew(pos[k] - c)
fmn = (np.linalg.pinv(G6) @ np.r_[0, 0, W, 0, 0, 0]).reshape(4, 3)
fig, axs = plt.subplots(1, 3, figsize=(13.4, 3.9))
ax = axs[0]
names = [T("左前", "FL"), T("右前", "FR"), T("左后", "RL"), T("右后", "RR")]
x = np.arange(4)
ax.bar(x - 0.3, F[:, 2], 0.2, color=C["z"], label=T("MuJoCo：竖直", "MuJoCo: vertical"))
ax.bar(x - 0.1, fmn[:, 2], 0.2, color=C["z"], alpha=0.45, label=T("最小范数：竖直", "minimum norm: vertical"))
ax.bar(x + 0.1, F[:, 1], 0.2, color=C["x"], label=T("MuJoCo：侧向 f_y", "MuJoCo: sideways f_y"))
ax.bar(x + 0.3, fmn[:, 1], 0.2, color=C["x"], alpha=0.45, label=T("最小范数：侧向", "minimum norm: sideways"))
ax.axhline(0, color=C["ink"], lw=0.6)
ax.set_xticks(x)
ax.set_xticklabels(names)
ax.set_ylabel(T("地面力 / N", "ground force / N"))
ax.set_title(T("(a) 静止站立时四只脚的力", "(a) foot forces when standing still"), fontsize=11)
ax.legend(fontsize=7.8, frameon=False, loc="upper left", ncol=2)
ax.set_ylim(-15, 60)
ax.grid(alpha=0.25, axis="y")
k10 = 5
mujoco.mj_resetDataKeyframe(m, d, 0)
mujoco.mj_forward(m, d)
Z_TOUCH = float(d.qpos[2]) - min(float(d.geom_xpos[g][2] - m.geom_size[g][0]) for g in feet)   # 脚刚碰到地面时机身原点的高度
for kp, kd, col in ((60.0, 2.0, C["z"]), (100.0, 3.0, C["x"])):
    mujoco.mj_resetDataKeyframe(m, d, 0)
    d.qpos[2] = Z_TOUCH + 0.3
    ts, fz, zb = [], [], []
    while d.time < 0.8:
        go2_pd(m, d, GO2_HOME, kp, kd)
        mujoco.mj_step(m, d)
        Fc, _ = go2_contacts(m, d, feet)
        ts.append(d.time)
        fz.append(Fc[:, 2].sum())
        zb.append(d.qpos[2])
    fzs = np.convolve(fz, np.ones(k10) / k10, "same")
    axs[1].plot(ts, fzs / W, color=col, lw=1.6, label=f"kp = {kp:.0f}")
    axs[2].plot(ts, np.array(zb) * 1000, color=col, lw=1.6, label=f"kp = {kp:.0f}")
axs[1].axhline(1, color=C["muted"], lw=1, ls="--")
axs[1].set_xlabel(T("时间 / s", "time / s"))
axs[1].set_ylabel(T("地面合力 / 体重", "total ground force / weight"))
axs[1].set_title(T("(b) 从 0.3 m 落下：地面力", "(b) dropped from 0.3 m: ground force"), fontsize=11)
axs[1].legend(fontsize=8.5, frameon=False)
axs[1].grid(alpha=0.25)
axs[2].axhline(Z_TOUCH * 1000, color=C["muted"], lw=1, ls=":")
axs[2].text(0.02, Z_TOUCH * 1000 + 4, T("脚刚着地时", "feet just touching"), fontsize=8.5, color=C["muted"])
axs[2].set_xlabel(T("时间 / s", "time / s"))
axs[2].set_ylabel(T("机身原点高度 / mm", "height of the base origin / mm"))
axs[2].set_title(T("(c) 机身的高度", "(c) height of the base"), fontsize=11)
axs[2].legend(fontsize=8.5, frameon=False)
axs[2].set_ylim(200, 600)
axs[2].grid(alpha=0.25)
fig.tight_layout()
figure(fig, "fig28_4_2")

# ---------------------------------------------------------------- 图 28.4.1
m0, d0 = go2_model(gravity=False)
A_ = 0.6


def run(seq, T_=0.5):
    mujoco.mj_resetDataKeyframe(m0, d0, 0)
    d0.qpos[2] = 1.0
    q = GO2_HOME.copy()
    ts, ps, qq = [], [], []
    for dth, dca in seq:
        q0, q1 = q.copy(), q.copy()
        q1[1::3] += dth
        q1[2::3] += dca
        t0 = d0.time
        while d0.time < t0 + T_:
            s = (d0.time - t0) / T_
            s = s * s * (3 - 2 * s)
            go2_pd(m0, d0, q0 + (q1 - q0) * s, 60.0, 2.0)
            mujoco.mj_step(m0, d0)
            Rb = quat2R(d0.qpos[3:7])
            ts.append(d0.time)
            ps.append(math.degrees(math.atan2(-Rb[2, 0], Rb[0, 0])))
            qq.append((d0.qpos[8] - GO2_HOME[1], d0.qpos[9] - GO2_HOME[2]))
        q = q1
    return np.array(ts), np.array(ps), np.array(qq)


fig, axs = plt.subplots(1, 2, figsize=(10.4, 3.9), gridspec_kw=dict(width_ratios=[1, 1.5]))
runs = ((T("来回转大腿", "thigh back and forth"), [(A_, 0), (-A_, 0)], C["muted"]),
        (T("方框：先大腿后小腿", "square: thigh first"), [(A_, 0), (0, A_), (-A_, 0), (0, -A_)] * 3, C["z"]),
        (T("方框反着转", "square reversed"), [(0, A_), (A_, 0), (0, -A_), (-A_, 0)] * 3, C["x"]))
for lab, seq, col in runs:
    ts, ps, qq = run(seq)
    axs[0].plot(np.degrees(qq[:, 0]), np.degrees(qq[:, 1]), color=col, lw=1.6 if col != C["muted"] else 3, alpha=0.9, label=lab)
    axs[1].plot(ts, ps, color=col, lw=1.6, label=lab)
axs[0].set_xlabel(T("大腿转角 / (°)", "thigh angle / (°)"))
axs[0].set_ylabel(T("小腿转角 / (°)", "calf angle / (°)"))
axs[0].set_title(T("(a) 关节的路线", "(a) path of the joints"), fontsize=11)
axs[0].set_aspect("equal")
axs[0].grid(alpha=0.25)
axs[0].legend(fontsize=8, frameon=False, loc="center")
axs[1].set_xlabel(T("时间 / s", "time / s"))
axs[1].set_ylabel(T("机身俯仰角 / (°)", "body pitch / (°)"))
axs[1].set_title(T("(b) 总角动量为零，机身照样能转", "(b) zero total angular momentum, yet the body turns"), fontsize=11)
axs[1].legend(fontsize=8.5, frameon=False, loc="lower left")
axs[1].grid(alpha=0.25)
fig.tight_layout()
figure(fig, "fig28_4_1")
