"""4.4 节的计算：

图 4.4.1    匀加速直线运动的 v–t 图：直线下的梯形面积就是位移，由此得到 x = v₀t + at²/2。
算例 4.4.1  两台 AGV 在同一条通道上以 1.2 m/s 一前一后行驶。前车急停，减速度 2.0 m/s²；后车的激光雷达发现前车减速后
            再过 0.30 s 才开始制动（检测与通信的延迟），减速度只有 1.5 m/s²（满载）。两车至少要相距多远才不会相撞？
            （图 4.4.2）
算例 4.4.2  停车距离 = 反应距离 v t_r + 制动距离 v²/(2a)：在 0～2 m/s 的速度范围内比较空载（2.5 m/s²）和满载（1.5 m/s²），
            t_r = 0.30 s。AGV 的激光雷达防护区要比停车距离长（图 4.4.3）。
"""
import numpy as np

from bookout import T, figure, out, style
import _draw as d

# ---- 算例 4.4.1
v0, a1, a2, tr = 1.2, 2.0, 1.5, 0.30
t1s = v0 / a1; s1 = v0 ** 2 / (2 * a1)                # 前车：停车时间、停车距离
t2s = tr + v0 / a2; s2 = v0 * tr + v0 ** 2 / (2 * a2)  # 后车
need = s2 - s1


def xlead(t):
    t = np.minimum(np.asarray(t, float), t1s); return v0 * t - 0.5 * a1 * t ** 2


def xfol(t):
    t = np.asarray(t, float); u = np.clip(t - tr, 0, v0 / a2)
    return v0 * np.minimum(t, tr) + v0 * u - 0.5 * a2 * u ** 2


tt = np.linspace(0, 1.4, 1401)
gap = need + xlead(tt) - xfol(tt)                     # 初始间距取“刚好不撞”的值
assert abs(gap.min()) < 1e-9 and np.argmin(gap) >= np.searchsorted(tt, t2s) - 1
out(v0=v0, a1=a1, a2=a2, tr=tr, t1s=t1s, s1=s1, t2s=t2s, s2=s2, react=v0 * tr, brake2=v0 ** 2 / (2 * a2), need=need)

# ---- 算例 4.4.2
vs = np.linspace(0, 2.0, 201)
stop = lambda v, a: v * tr + v ** 2 / (2 * a)
out(st_full_15=stop(1.5, 1.5), st_empty_15=stop(1.5, 2.5), st_full_10=stop(1.0, 1.5), st_full_20=stop(2.0, 1.5),
    ratio=stop(2.0, 1.5) / stop(1.0, 1.5))

plt = style()
# ---- 图 4.4.1：v–t 图下的面积
fig, ax = plt.subplots(figsize=(4.4, 3.0))
vv0, aa, t_ = 0.6, 0.4, 3.0
ax.fill([0, t_, t_, 0], [0, 0, vv0, vv0], color=d.VA, alpha=0.18)
ax.fill([0, t_, t_], [vv0, vv0, vv0 + aa * t_], color=d.VR, alpha=0.18)
ax.plot([0, t_], [vv0, vv0 + aa * t_], color=d.INK, lw=2)
ax.text(t_ / 2, vv0 / 2, r"$v_0 t$", ha="center", va="center", color=d.VA, fontsize=12)
ax.text(t_ * 0.66, vv0 + aa * t_ * 0.33, r"$\frac{1}{2}at^2$", ha="center", va="center", color=d.VR, fontsize=12)
ax.annotate("", xy=(t_ + 0.12, vv0 + aa * t_), xytext=(t_ + 0.12, vv0), arrowprops=dict(arrowstyle="<->", color=d.MUTED))
ax.text(t_ + 0.2, vv0 + aa * t_ / 2, r"$at$", color=d.MUTED, fontsize=11, va="center")
ax.set_xticks([0, t_]); ax.set_xticklabels(["0", "t"]); ax.set_yticks([0, vv0, vv0 + aa * t_]); ax.set_yticklabels(["0", r"$v_0$", r"$v$"])
ax.set_xlim(0, t_ + 0.7); ax.set_ylim(0, 2.0); ax.set_xlabel(T("时间", "time")); ax.set_ylabel(T("速度", "velocity")); d.spines(ax)
figure(fig, "fig4_4_1")

# ---- 图 4.4.2：前后两车
fig, axs = plt.subplots(1, 2, figsize=(7.4, 2.9))
ax = axs[0]
ax.plot(tt, xlead(tt) + need, color=d.VA, lw=2, label=T("前车", "leader"))
ax.plot(tt, xfol(tt), color=d.VR, lw=2, label=T("后车", "follower"))
ax.axvline(tr, color=d.MUTED, lw=0.8, ls=":"); ax.text(tr + 0.02, 0.05, T("后车开始制动", "follower brakes"), fontsize=8, color=d.MUTED)
ax.set_xlabel("t / s"); ax.set_ylabel(T("前车车尾、后车车头的位置 / m", "leader rear, follower front / m")); ax.legend(frameon=False, fontsize=8.5); d.spines(ax)
ax = axs[1]
ax.plot(tt, gap, color=d.INK, lw=2)
ax.set_xlabel("t / s"); ax.set_ylabel(T("两车间距 / m", "gap / m")); d.spines(ax)
ax.text(0.5, need * 0.75, T(f"开始时需要 {need:.2f} m，\n两车都停下时间距恰好为零", f"needs {need:.2f} m at the start;\nzero gap when both have stopped"), fontsize=8.5)
fig.tight_layout()
figure(fig, "fig4_4_2")

# ---- 图 4.4.3：停车距离与速度
fig, ax = plt.subplots(figsize=(4.8, 3.1))
ax.plot(vs, stop(vs, 1.5), color=d.VR, lw=2, label=T("满载 a = 1.5 m/s²", "loaded a = 1.5 m/s²"))
ax.plot(vs, stop(vs, 2.5), color=d.VA, lw=2, label=T("空载 a = 2.5 m/s²", "empty a = 2.5 m/s²"))
ax.plot(vs, vs * tr, color=d.MUTED, lw=1, ls="--", label=T("其中的反应距离", "reaction part"))
ax.set_xlabel("v / (m/s)"); ax.set_ylabel(T("停车距离 / m", "stopping distance / m")); ax.legend(frameon=False, fontsize=8.5); d.spines(ax)
figure(fig, "fig4_4_3")
