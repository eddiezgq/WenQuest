"""图 10.7.1：里程计标定的效果。控制器按图纸参数（r = 75 mm，b = 400 mm）规划“走 2 m、左转 90°”四次的正方形，
算出每个轮子该转的角度；实际参数是 r = 74.5 mm、b = 412 mm，小车真实走出的轨迹（黑）并不闭合。用图纸参数由编码器推算的轨迹（蓝虚线）
以为自己走了正方形；用标定后的参数推算的轨迹（红）与真实轨迹重合。"""
import numpy as np

from _fig import BLUE, INK, MUTED, RED, T, figure, plt

from _agv import b_nom, b_true, calibrated, r_nom, r_true

r_cal, k_cal, *_ = calibrated()              # 与程序 10.7.1 同一次标定
b_cal = r_cal / k_cal


def wheel_plan():
    """按图纸参数规划：直线段两轮同转 2/r，原地左转 90° 两轮反转 (π/2)(b/2)/r；分成小步。"""
    steps = []
    for _ in range(4):
        steps += [((2.0 / r_nom) / 200, (2.0 / r_nom) / 200)] * 200
        a = (np.pi / 2) * (b_nom / 2) / r_nom / 100
        steps += [(a, -a)] * 100            # (φ_R, φ_L)：右轮前转、左轮后转 → 左转
    return steps


def integrate(steps, r, b):
    x, y, th = 0.0, 0.0, 0.0
    pts = [(x, y)]
    for pr, pl in steps:
        d, dth = r * (pr + pl) / 2, r * (pr - pl) / b
        x += d * np.cos(th + dth / 2); y += d * np.sin(th + dth / 2); th += dth
        pts.append((x, y))
    return np.array(pts)


steps = wheel_plan()
true = integrate(steps, r_true, b_true)
nom = integrate(steps, r_nom, b_nom)
cal = integrate(steps, r_cal, b_cal)
fig, ax = plt.subplots(figsize=(6.0, 5.4))
ax.plot(*true.T, color=INK, lw=2.5, label=T("真实轨迹", "true path"))
ax.plot(*nom.T, color=BLUE, lw=2, ls="--", label=T("图纸参数推算", "odometry, drawing values"))
ax.plot(*cal.T, color=RED, lw=1.2, label=T("标定参数推算", "odometry, calibrated values"))
ax.plot(0, 0, "o", color=INK, ms=6)
ax.text(0.05, -0.18, T("起点", "start"), fontsize=10)
ax.plot(*true[-1], "x", color=INK, ms=9, mew=2)
ax.text(*(true[-1] + np.array([0.08, 0.05])), T(f"真实终点（偏 {np.linalg.norm(true[-1]) * 100:.0f} cm）", f"true end ({np.linalg.norm(true[-1]) * 100:.0f} cm off)"), fontsize=10)
ax.set_aspect("equal"); ax.legend(frameon=False, fontsize=10, loc="center")
ax.set_xlabel("x / m"); ax.set_ylabel("y / m")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_title(T("按图纸参数走正方形：里程计以为回到了起点", "a planned square: odometry thinks it is back at the start"), fontsize=11)
figure(fig, "fig10_7_1")
