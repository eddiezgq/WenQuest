"""13.1 节的计算：

算例 13.1.1  光滑水平桌面上，0.20 kg 的小块系在穿过桌面小孔的细绳上，绕小孔做半径 0.50 m、速率 1.2 m/s 的圆周运动。
            在桌下慢慢拉绳，使半径变为 0.25 m。小块的角动量、速率、动能怎样变？拉力做了多少功？
算例 13.1.2  有心力下的运动：质点受指向固定点 O 的力（这里取与距离平方成反比的引力，单位任取），数值积分求轨道，
            验证相等时间内位置矢量扫过的面积相等（图 13.1.1）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

m, r0, v0, r1 = 0.20, 0.50, 1.2, 0.25
L0 = m * r0 * v0
v1 = L0 / (m * r1)
K0, K1 = 0.5 * m * v0 ** 2, 0.5 * m * v1 ** 2
# 拉力做的功：慢慢拉时 F = mv²/r = L²/(m r³)，W = ∫F(−dr)
rr = np.linspace(r0, r1, 200001)
F = L0 ** 2 / (m * rr ** 3)
W = float(np.sum(0.5 * (F[1:] + F[:-1]) * -np.diff(rr)))
assert abs(W - (K1 - K0)) < 1e-6
out(m=m, r0=r0, v0=v0, r1=r1, L0=L0, v1=v1, K0=K0, K1=K1, W=W, ratioK=K1 / K0, F0=m * v0 ** 2 / r0, F1=m * v1 ** 2 / r1)

# ---- 算例 13.1.2：有心力下的轨道（GM = 1，r = 1 处以 1.25 倍圆轨道速度出发：椭圆轨道）
GM, dt = 1.0, 1e-4
x, y, vx, vy = 1.0, 0.0, 0.0, 1.25
pts = [(x, y)]
Ls = []
nsteps = 0
while True:                                                     # 速度韦尔莱法，跑满一圈
    r3 = (x * x + y * y) ** 1.5
    ax_, ay_ = -GM * x / r3, -GM * y / r3
    vx += 0.5 * dt * ax_; vy += 0.5 * dt * ay_
    x += dt * vx; y += dt * vy
    r3 = (x * x + y * y) ** 1.5
    ax_, ay_ = -GM * x / r3, -GM * y / r3
    vx += 0.5 * dt * ax_; vy += 0.5 * dt * ay_
    nsteps += 1
    pts.append((x, y)); Ls.append(x * vy - y * vx)
    if nsteps > 1000 and y >= 0 and pts[-2][1] < 0:
        break
P = np.array(pts)
Tper = nsteps * dt
Ls = np.array(Ls)
out(L_orb=1.25, L_drift=float((Ls.max() - Ls.min()) / 1.25), Tper=Tper, rmin=float(np.hypot(P[:, 0], P[:, 1]).min()),
    rmax=float(np.hypot(P[:, 0], P[:, 1]).max()))
# 把一个周期分成 8 段相等的时间，算每段扫过的面积
n8 = len(P) // 8
areas = []
for k in range(8):
    seg = P[k * n8:(k + 1) * n8 + 1]
    areas.append(0.5 * float(np.sum(seg[:-1, 0] * seg[1:, 1] - seg[1:, 0] * seg[:-1, 1])))
areas = np.array(areas)
out(area_spread=float((areas.max() - areas.min()) / areas.mean()), area_each=float(areas.mean()), area_rate=1.25 / 2)
assert (areas.max() - areas.min()) / areas.mean() < 1e-4

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 3.2))
ax.plot(P[::20, 0], P[::20, 1], color=d.INK, lw=1.2)
cols = [d.VA, d.VB]
for k in range(8):
    seg = P[k * n8:(k + 1) * n8 + 1:40]
    poly = np.vstack([[0, 0], seg, [0, 0]])
    ax.fill(poly[:, 0], poly[:, 1], color=cols[k % 2], alpha=0.30, lw=0)
ax.plot(0, 0, "o", color=d.VR, ms=6); ax.text(0.08, -0.25, "O", color=d.VR, fontsize=10)
ax.set_aspect("equal"); ax.set_xlabel("x"); ax.set_ylabel("y")
ax.set_title(T("相等时间内扫过的面积相等", "equal areas in equal times"), fontsize=9.5)
d.spines(ax)
figure(fig, "fig13_1_1")
