"""25.5 节的示意图。

图 25.5.1：算例 25.5.2：上下料动作（T = 最短时间），法兰上装夹爪 + 毛坯（3.8 kg）。六个关节的力矩随时间的变化，
          (a) 关节 1～3，(b) 关节 4～6；点划线为力矩上限（150 N·m、28 N·m）；细虚线为同样姿态下只有重力时的力矩。
图 25.5.2：(a) 算例 25.5.3：同一动作，负载（夹爪 + 毛坯按质量等比放大）加到多大时各关节的力矩峰值达到上限，随动作时间 T 的变化；
              深色阴影：关节 1 的速度超过 180 °/s；浅色阴影：低于第 22 章按加速度、加加速度上限（示意值）求出的最短时间；
          (b) 只看静止：质点负载的重心沿工具方向离法兰 r 时，最不利姿态下能举的最大质量，颜色表示起限制作用的关节；
              虚线为 UR5e 的额定负载 5 kg。
"""
import numpy as np

from _ch25 import TAU_MAX, cell_move, payload_parts, quintic, ur_chain
from bookout import COLORS as C, T, figure, style

plt = style()
thA, thB, T_move = cell_move()
pl = payload_parts()
m_p, c_p, I_pc = pl
ch = ur_chain(payload=pl)
ch_arm = ur_chain()
Z = np.zeros(6)
JC = ["#7a868d", C["z"], C["y"], C["x"], C["accent"], "#9467bd"]

# ---------------------------------------------------------------- 图 25.5.1
ts = np.linspace(0, T_move, 500)
tau = np.array([ch.rnea(*quintic(thA, thB, T_move, t)) for t in ts])
tg = np.array([ch.rnea(quintic(thA, thB, T_move, t)[0], Z, Z) for t in ts])
fig, axs = plt.subplots(1, 2, figsize=(11.0, 4.0))
for k, ax in enumerate(axs):
    for j in range(3 * k, 3 * k + 3):
        ax.plot(ts, tau[:, j], color=JC[j], lw=1.8, label=T(f"关节 {j + 1}", f"joint {j + 1}"))
        ax.plot(ts, tg[:, j], color=JC[j], lw=0.9, ls="--")
    lim = TAU_MAX[3 * k]
    for s in (1, -1):
        ax.axhline(s * lim, color=C["ink"], lw=1.0, ls="-.")
    ax.set_ylim(-1.12 * lim, 1.12 * lim)
    ax.set_xlim(0, T_move)
    ax.set_xlabel(T("时间 t / s", "time t / s"))
    ax.set_ylabel(T("关节力矩 / (N·m)", "joint torque / (N·m)"))
    ax.set_title(T(f"({'ab'[k]}) 关节 {3 * k + 1}～{3 * k + 3}（上限 ±{lim:.0f} N·m）",
                   f"({'ab'[k]}) joints {3 * k + 1}–{3 * k + 3} (limit ±{lim:.0f} N·m)"), fontsize=11)
    ax.legend(fontsize=9, frameon=False, loc="lower left", ncol=3, bbox_to_anchor=(0.0, 0.06))
    ax.grid(alpha=0.25)
fig.tight_layout()
figure(fig, "fig25_5_1")

# ---------------------------------------------------------------- 图 25.5.2
KS = np.linspace(0, 20, 8001)


def limits(Tm, N=500):
    tt = np.linspace(0, Tm, N)
    a = np.array([ch_arm.rnea(*quintic(thA, thB, Tm, t)) for t in tt])
    b = np.array([ch.rnea(*quintic(thA, thB, Tm, t)) for t in tt]) - a
    lim = np.full(6, np.nan)
    for j in range(6):
        P = np.abs(a[:, j][None, :] + KS[:, None] * b[:, j][None, :]).max(1)
        over = np.nonzero(P > TAU_MAX[j])[0]
        if len(over):
            lim[j] = KS[over[0]] * m_p
    return lim


TT = np.array([0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.15, T_move, 1.5, 1.75, 2.0, 2.5])
LL = np.array([limits(Tm) for Tm in TT])
fig, axs = plt.subplots(1, 2, figsize=(11.0, 4.2))
ax = axs[0]
for j in range(6):
    if np.all(np.isnan(LL[:, j])):
        continue
    ax.plot(TT, LL[:, j], "o-", color=JC[j], lw=1.6, ms=3.5, label=T(f"关节 {j + 1}", f"joint {j + 1}"))
T_v = 15 / 8 * np.abs(thB - thA).max() / np.pi              # 五次多项式的峰值速度 = (15/8)|Δθ|/T，上限 180 °/s
ax.axvspan(0.45, T_v, color="#bdbdbd", alpha=0.5, lw=0)
ax.axvspan(T_v, T_move, color="#e6e6e6", alpha=0.6, lw=0)
ax.text(0.5, 72, T("速度超限", "speed\nover limit"), fontsize=9, color=C["ink"])
ax.axhline(5.0, color=C["ink"], lw=1.0, ls="--")
ax.text(2.0, 6.0, T("额定 5 kg", "rated 5 kg"), fontsize=9)
ax.set_xlim(0.45, 2.55)
ax.set_ylim(0, 80)
ax.set_xlabel(T("动作时间 T / s", "move time T / s"))
ax.set_ylabel(T("力矩峰值达上限时的负载 / kg", "payload at the torque limit / kg"))
ax.set_title(T("(a) 上下料动作：负载上限与动作时间", "(a) the loading move: payload limit vs move time"), fontsize=11)
ax.legend(fontsize=9, frameon=False, loc="upper right", ncol=2)
ax.grid(alpha=0.25)
# (b) 静止
rng = np.random.default_rng(255)
Q = np.c_[np.zeros(4000), rng.uniform(-np.pi, np.pi, (4000, 5))]
TA = np.array([ch_arm.rnea(q, Z, Z) for q in Q])
c0 = ur_chain(payload=(1.0, np.zeros(3), np.zeros((3, 3))))
c1 = ur_chain(payload=(1.0, np.array([0, 1.0, 0]), np.zeros((3, 3))))
P0 = np.array([c0.rnea(q, Z, Z) for q in Q]) - TA
P1 = np.array([c1.rnea(q, Z, Z) for q in Q]) - TA
RS = np.linspace(0, 0.6, 61)
mm, jj = [], []
for r in RS:
    TP = P0 + r * (P1 - P0)
    with np.errstate(divide="ignore", invalid="ignore"):
        MM = np.where(np.abs(TP) > 1e-12, (TAU_MAX - np.abs(TA)) / np.abs(TP), np.inf)
    i, j = np.unravel_index(np.argmin(MM), MM.shape)
    mm.append(MM[i, j])
    jj.append(j)
mm, jj = np.array(mm), np.array(jj)
ax = axs[1]
for j in sorted(set(jj)):
    sel = jj == j
    ax.plot(RS[sel], mm[sel], "o", color=JC[j], ms=3.5, label=T(f"关节 {j + 1} 起限制作用", f"joint {j + 1} limits"))
ax.plot(RS, mm, color=C["muted"], lw=0.8)
ax.axhline(5.0, color=C["ink"], lw=1.0, ls="--")
ax.text(0.45, 5.3, T("额定 5 kg", "rated 5 kg"), fontsize=9)
ax.set_xlabel(T("负载重心离法兰的距离 r / m", "CoG distance from the flange r / m"))
ax.set_ylabel(T("静止时能举的最大质量 / kg", "largest static payload / kg"))
ax.set_title(T("(b) 只看静止的力矩上限", "(b) static torque limits only"), fontsize=11)
ax.legend(fontsize=9, frameon=False)
ax.grid(alpha=0.25)
ax.set_ylim(0, 12)
fig.tight_layout()
figure(fig, "fig25_5_2")
