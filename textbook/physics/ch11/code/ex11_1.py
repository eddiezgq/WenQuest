"""11.1 节的计算：

算例 11.1.1  四足机器人（Go2，按 15 kg 计）从 0.30 m 高的台阶上落下：落地前的速度和动量；
            腿几乎不弯、0.020 s 内停下，与屈腿缓冲、0.12 s 内停下，地面的平均支持力各多大（以体重计）。
算例 11.1.2  把腿的缓冲看成弹簧—阻尼器：F = kx + cẋ（x 为身体下降的压缩量，c 按阻尼比 0.3 取），
            k = 3000、6000、20000 N/m 三种，数值计算地面力随时间的变化：峰值、压缩量、身体停止下降所用的时间；
            验证在这段时间内 ∫F dt = mv₀ + mgΔt（图 11.1.2）。
图 11.1.1    同样的动量变化、两种作用时间的力（半正弦脉冲，略去重力），配动画 11.1.1。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

m, h = 15.0, 0.30
v0 = math.sqrt(2 * g * h)
p0 = m * v0
W = m * g
out(m=m, h=h, v0=v0, p0=p0, W=W)
for name, dt in (("hard", 0.020), ("soft", 0.12)):
    Fnet = p0 / dt
    out(**{f"dt_{name}": dt, f"Fnet_{name}": Fnet, f"F_{name}": Fnet + W, f"BW_{name}": (Fnet + W) / W})


def land(k, zeta=0.3, h_=h, dt=1e-5, Tmax=0.6):
    """身体向下为正：m ẍ = mg − F，F = max(0, kx + cẋ)，x 从 0 开始，初速 v0。返回时间、力、压缩量、停止下降的时刻。"""
    c = 2 * zeta * math.sqrt(k * m)
    x, v = 0.0, math.sqrt(2 * g * h_)
    ts, Fs, xs = [0.0], [0.0], [0.0]
    t_stop = None
    t = 0.0
    while t < Tmax:
        F = max(0.0, k * x + c * v) if x > 0 else 0.0                # 脚离地（x < 0）时没有地面力
        a = g - F / m
        v += a * dt; x += v * dt; t += dt
        if t_stop is None and v <= 0:
            t_stop = t
        ts.append(t); Fs.append(max(0.0, k * x + c * v) if x > 0 else 0.0); xs.append(x)
    return np.array(ts), np.array(Fs), np.array(xs), t_stop


res = {}
for k in (3000.0, 6000.0, 20000.0):
    t, F, x, ts_ = land(k)
    i = t <= ts_
    J = float(np.sum((F[i][1:] + F[i][:-1]) / 2 * np.diff(t[i])))
    assert abs(J - (p0 + W * ts_)) < 0.02 * p0                   # 动量定理（含重力的冲量）
    res[k] = (t, F, x, ts_)
    tag = f"{int(k)}"
    out(**{f"Fpk_{tag}": float(F.max()), f"BWpk_{tag}": float(F.max()) / W, f"xmax_{tag}": float(x.max()) * 1000,
           f"tstop_{tag}": ts_, f"J_{tag}": J, f"Jcalc_{tag}": p0 + W * ts_})
out(zeta=0.3)

plt = style()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 2.9))
cols = {3000.0: d.VB, 6000.0: d.VA, 20000.0: d.VR}
for k, (t, F, x, ts_) in res.items():
    sl = slice(None, None, 50)
    a1.plot(t[sl] * 1000, F[sl] / W, color=cols[k], lw=2, label=f"k = {k:.0f} N/m")
    a2.plot(t[sl] * 1000, x[sl] * 1000, color=cols[k], lw=2)
a1.axhline(1, color=d.MUTED, lw=0.7, ls="--"); a1.text(430, 0.45, T("体重", "body weight"), fontsize=8, color=d.MUTED)
a1.set_xlabel(T("落地后的时间 / ms", "time after touchdown / ms")); a1.set_ylabel(T("地面力 / 体重", "ground force / body weight"))
a1.set_xlim(0, 500); a1.legend(frameon=False, fontsize=8); d.spines(a1)
a1.set_title(T("(a) 地面力：越硬峰值越高、越短", "(a) ground force: stiffer is higher and shorter"), fontsize=9.5)
a2.axhline(120, color=d.MUTED, lw=0.7, ls="--"); a2.text(260, 124, T("腿的最大行程 120 mm", "leg travel limit 120 mm"), fontsize=8, color=d.MUTED)
a2.set_xlabel(T("落地后的时间 / ms", "time after touchdown / ms")); a2.set_ylabel(T("身体下降量 / mm", "body drop / mm"))
a2.set_xlim(0, 500); a2.set_ylim(0, 160); d.spines(a2)
a2.set_title(T("(b) 压缩量：越软越深", "(b) compression: softer goes deeper"), fontsize=9.5)
fig.tight_layout()
figure(fig, "fig11_1_2")

# ---- 图 11.1.1：同样的冲量，两种作用时间（半正弦脉冲，略去重力）
fig, ax = plt.subplots(figsize=(4.8, 2.9))
tt = np.linspace(0, 0.16, 800)
for T_, col, lab in ((0.020, d.VR, T("0.02 s 停下", "stopped in 0.02 s")), (0.12, d.VA, T("0.12 s 停下", "stopped in 0.12 s"))):
    A_ = math.pi * p0 / (2 * T_)
    F_ = np.where(tt <= T_, A_ * np.sin(math.pi * tt / T_), 0.0)
    ax.fill_between(tt * 1000, F_, color=col, alpha=0.25, lw=0); ax.plot(tt * 1000, F_, color=col, lw=2, label=lab)
ax.text(45, 1500, T(f"两块面积相等 = Δp = {p0:.1f} N·s", f"equal areas = Δp = {p0:.1f} N·s"), fontsize=9)
ax.set_xlabel(T("落地后的时间 / ms", "time after touchdown / ms")); ax.set_ylabel(T("地面力 − 重力 / N", "ground force − weight / N"))
ax.set_xlim(0, 160); ax.legend(frameon=False, fontsize=8.5); d.spines(ax)
figure(fig, "fig11_1_1")
