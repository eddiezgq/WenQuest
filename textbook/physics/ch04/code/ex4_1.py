"""4.1、4.2 节的计算：

算例 4.1.1  AGV 在一条直线通道上工作：从充电站 x = 2 m 出发，到货架 x = 14 m 取货（停 4 s），再退回到打包台 x = 8 m。
            每段移动都是“匀加速—匀速—匀减速”（最大速度 1.0 m/s，加速度 0.50 m/s²）。求全程的位移与路程、
            平均速度与平均速率（图 4.1.1）。
算例 4.2.1  由同一段记录的 x–t 图读瞬时速度：曲线的切线斜率；v–t 图与 x–t 图上下对齐（图 4.2.1）。
"""
import numpy as np

from bookout import T, figure, out, style
import _draw as d
from _kin import trapezoid

VM, AM = 1.0, 0.50


def move(x0, x1, vm=VM, am=AM):
    """从 x0 移到 x1 的梯形速度曲线（_kin.trapezoid），返回 (时长, 位置函数, 速度函数)，t 从 0 起。"""
    P, sg = trapezoid(abs(x1 - x0), vm, am), np.sign(x1 - x0)
    return P["T"], (lambda t: x0 + sg * P["x"](t)), (lambda t: sg * np.where(np.asarray(t) < P["T"], P["v"](t), 0.0))


segs = []        # (起始时刻, 时长, x 函数, v 函数)
t0 = 0.0
for kind, a, b in (("move", 2.0, 14.0), ("wait", 14.0, 4.0), ("move", 14.0, 8.0)):
    if kind == "move":
        Tm, xf, vf = move(a, b)
    else:
        Tm, xf, vf = b, (lambda t, a=a: a + 0 * t), (lambda t: 0 * t)
    segs.append((t0, Tm, xf, vf)); t0 += Tm
Ttot = t0


def X(t):
    t = np.asarray(t, float); r = np.zeros_like(t)
    for s0, Tm, xf, _ in segs:
        m = (t >= s0) & (t <= s0 + Tm + 1e-12); r[m] = xf(t[m] - s0)
    return r


def V(t):
    t = np.asarray(t, float); r = np.zeros_like(t)
    for s0, Tm, _, vf in segs:
        m = (t >= s0) & (t < s0 + Tm); r[m] = vf(t[m] - s0)
    return r


disp = 8.0 - 2.0
dist = 12.0 + 6.0
tt = np.linspace(0, Ttot, 4001)
assert abs(np.trapezoid(np.abs(V(tt)), tt) - dist) < 1e-3 and abs(np.trapezoid(V(tt), tt) - disp) < 1e-3
out(T1=segs[0][1], T3=segs[2][1], Ttot=Ttot, disp=disp, dist=dist, vavg=disp / Ttot, savg=dist / Ttot,
    ta=VM / AM, xa=0.5 * AM * (VM / AM) ** 2)

# 算例 4.2.1：在 t = 1.2 s（起步加速中）和倒车开始后 1 s 读切线斜率
tk1, tk2 = 1.2, segs[2][0] + 1.0
out(tk1=tk1, tk2=tk2, vk1=float(V(np.array([tk1]))[0]), vk2=float(V(np.array([tk2]))[0]), xk1=float(X(np.array([tk1]))[0]),
    xk2=float(X(np.array([tk2]))[0]))

plt = style()
# ---- 图 4.1.1：往返一趟的 x–t 图
fig, ax = plt.subplots(figsize=(6.0, 3.0))
ax.plot(tt, X(tt), color=d.INK, lw=2)
for xs, name in ((2, T("充电站", "charger")), (14, T("货架", "shelf")), (8, T("打包台", "packing"))):
    ax.axhline(xs, color="#d5dbde", lw=0.8, zorder=0); ax.text(Ttot + 0.3, xs, name, va="center", fontsize=8.5, color=d.MUTED)
d.arrow(ax, (Ttot + 0.0, 2), (Ttot + 0.0, 8), d.VR, lw=2)
ax.text(Ttot - 0.4, 5, T("位移 6 m", "displacement 6 m"), color=d.VR, ha="right", fontsize=9)
ax.text(5, 11.5, T("去程 12 m", "out 12 m"), color=d.VA, fontsize=9); ax.text(segs[2][0] + 3.6, 13.0, T("回程 6 m", "back 6 m"), color=d.VA, fontsize=9)
ax.set_xlim(0, Ttot + 3.2); ax.set_ylim(0, 16); ax.set_xlabel("t / s"); ax.set_ylabel("x / m"); d.spines(ax)
figure(fig, "fig4_1_1")

# ---- 图 4.2.1：x–t 图的斜率就是 v
fig, axs = plt.subplots(2, 1, figsize=(6.0, 4.6), sharex=True)
ax = axs[0]
ax.plot(tt, X(tt), color=d.INK, lw=2)
for tk, col in ((tk1, d.VA), (tk2, d.VR)):
    xk, vk = float(X(np.array([tk]))[0]), float(V(np.array([tk]))[0])
    ax.plot([tk - 1.2, tk + 2.5], [xk - 1.2 * vk, xk + 2.5 * vk], color=col, lw=1.4, ls="--")
    ax.plot(tk, xk, "o", color=col, ms=5)
ax.set_ylabel("x / m"); ax.set_ylim(0, 16); d.spines(ax)
ax.text(tk1 + 0.6, float(X(np.array([tk1]))[0]) - 1.8, T("切线斜率 > 0", "slope > 0"), color=d.VA, fontsize=8.5)
ax.text(tk2 + 0.6, float(X(np.array([tk2]))[0]) + 0.8, T("切线斜率 < 0", "slope < 0"), color=d.VR, fontsize=8.5)
ax = axs[1]
ax.plot(tt, V(tt), color=d.VA, lw=2)
ax.axhline(0, color=d.MUTED, lw=0.8)
for tk, col in ((tk1, d.VA), (tk2, d.VR)):
    ax.plot(tk, float(V(np.array([tk]))[0]), "o", color=col, ms=5)
ax.fill_between(tt, 0, V(tt), where=V(tt) > 0, color=d.VA, alpha=0.15)
ax.fill_between(tt, 0, V(tt), where=V(tt) < 0, color=d.VR, alpha=0.15)
ax.text(6, 0.4, T("面积 = +12 m", "area = +12 m"), color=d.VA, fontsize=9); ax.text(segs[2][0] + 2.2, -0.45, T("面积 = −6 m", "area = −6 m"), color=d.VR, fontsize=9)
ax.set_xlabel("t / s"); ax.set_ylabel("v / (m/s)"); ax.set_ylim(-1.3, 1.3); d.spines(ax)
fig.tight_layout()
figure(fig, "fig4_2_1")
