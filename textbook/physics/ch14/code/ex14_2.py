"""14.2 节的计算：

算例 14.2.1  称重求重心：装着机械臂的 AGV 停在四个称重传感器上。车轮接地点：前 x = +0.40 m、后 x = −0.40 m，
            左 y = +0.30 m、右 y = −0.30 m。读数（N）：左前 412.0，右前 368.0，左后 335.0，右后 297.0。
            求整车的重量和重心的水平位置（图 14.2.1）。
算例 14.2.2  求重心高度：把前轮抬高，使车身倾斜 10°（绕后轮接地线转），前轮下的两个传感器读数之和变为多少，就能反推重心高度。
            这里先按重心高 0.38 m 算出应有的读数，再由读数反推，核对方法。重心高度知道后，侧向停在斜坡上，坡多陡会翻？
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

xf, xr, yl, yr = 0.40, -0.40, 0.30, -0.30
R = {"FL": 412.0, "FR": 368.0, "RL": 335.0, "RR": 297.0}
W = sum(R.values())
xc = (xf * (R["FL"] + R["FR"]) + xr * (R["RL"] + R["RR"])) / W
yc = (yl * (R["FL"] + R["RL"]) + yr * (R["FR"] + R["RR"])) / W
out(W=W, m=W / 9.81, xc=xc, yc=yc, xc_cm=xc * 100, yc_cm=yc * 100, front=R["FL"] + R["FR"], rear=R["RL"] + R["RR"])

# ---- 重心高度：前轮抬起 β，绕后轮接地线转。a = 重心到后轮接地线的距离（沿车身），h = 重心离接地面的高度（车身坐标）
Lw, beta, h_true = xf - xr, math.radians(10.0), 0.38
a = xc - xr
F_front = W * (a * math.cos(beta) - h_true * math.sin(beta)) / (Lw * math.cos(beta))
F_front = round(F_front, 1)                                         # 传感器读到 0.1 N
h = (a - F_front * Lw / W) / math.tan(beta)
assert abs(h - h_true) < 2e-3
th_right = math.degrees(math.atan((yc - yr) / h))                   # 向右侧翻：重心到右轮接地线的水平距离
th_left = math.degrees(math.atan((yl - yc) / h))
out(beta=10.0, F_front=F_front, h=h, h_cm=h * 100, th_right=th_right, th_left=th_left, a=a)

plt = style()
fig, ax = plt.subplots(figsize=(4.4, 3.4))
ax.add_patch(plt.Rectangle((xr, yr), xf - xr, yl - yr, fill=False, ec=d.INK, lw=1.4))
for k, (x, y) in {"FL": (xf, yl), "FR": (xf, yr), "RL": (xr, yl), "RR": (xr, yr)}.items():
    ax.plot(x, y, "s", color=d.VA, ms=9)
    ax.text(x + (0.03 if x > 0 else -0.03), y + (0.04 if y > 0 else -0.07), f"{R[k]:.0f} N", ha="left" if x > 0 else "right", fontsize=9, color=d.VA)
ax.plot(xc, yc, "x", color=d.VR, ms=10, mew=2.5)
ax.text(xc + 0.03, yc + 0.03, T("重心", "CG"), color=d.VR, fontsize=9.5)
ax.plot(0, 0, "+", color=d.MUTED, ms=10)
ax.annotate("", xy=(0.62, 0), xytext=(0.48, 0), arrowprops=dict(arrowstyle="->", color=d.MUTED))
ax.text(0.50, 0.03, T("前", "front"), color=d.MUTED, fontsize=9)
ax.set_xlim(-0.65, 0.7); ax.set_ylim(-0.48, 0.45); ax.set_aspect("equal")
ax.set_xlabel("x / m"); ax.set_ylabel("y / m"); d.spines(ax)
figure(fig, "fig14_2_1")
