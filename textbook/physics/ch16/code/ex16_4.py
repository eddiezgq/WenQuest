"""16.4 节的计算：

算例 16.4.1  浇花的水管内径 20 mm，体积流量 0.30 L/s，接一个出口直径 6.0 mm 的喷嘴。管中和喷嘴出口的平均流速各多大？
            每秒流出多少千克水？
算例 16.4.2  理想流体（不可压缩、无黏性、无旋）绕圆柱的稳定流动：流函数 ψ = U(r − a²/r) sin θ。画出流线，标出一根流管；
            流线挤在一起的地方流速大（图 16.4.1）。圆柱表面的流速 2U sin θ，最大是来流的 2 倍。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

Q, D1, D2 = 0.30e-3, 0.020, 0.0060
v1, v2 = Q / (math.pi * D1 ** 2 / 4), Q / (math.pi * D2 ** 2 / 4)
out(v1=v1, v2=v2, ratio=v2 / v1, mdot=Q * 1000)

U, a = 1.0, 1.0
x = np.linspace(-4, 4, 400); y = np.linspace(-2.5, 2.5, 300)
X, Y = np.meshgrid(x, y)
Rr = np.hypot(X, Y); Th = np.arctan2(Y, X)
psi = U * (Rr - a * a / np.maximum(Rr, 1e-9)) * np.sin(Th)
psi[Rr < a] = np.nan
plt = style()
fig, ax = plt.subplots(figsize=(5.2, 3.2))
levels = np.linspace(-2.4, 2.4, 17)
ax.contour(X, Y, psi, levels=levels, colors=d.VA, linewidths=1.0, linestyles="solid")
tube = np.where((psi >= 0.3) & (psi <= 0.6), 1.0, np.nan)
ax.contourf(X, Y, tube, levels=[0.5, 1.5], colors=[d.VR], alpha=0.25)
ax.add_patch(plt.Circle((0, 0), a, color="#cfd8df"))
ax.text(-3.9, 0.75, T("一根流管", "a flow tube"), fontsize=8.5, color=d.VR)
ax.annotate("", xy=(-3.0, -2.2), xytext=(-3.9, -2.2), arrowprops=dict(arrowstyle="->", color=d.INK))
ax.text(-3.9, -2.05, T("来流", "oncoming flow"), fontsize=8)
ax.set_aspect("equal"); ax.set_xlim(-4, 4); ax.set_ylim(-2.5, 2.5); ax.axis("off")
figure(fig, "fig16_4_1")
# 核对：圆柱表面 θ = 90° 处流速 2U
th = math.pi / 2; eps = 1e-6
vt = U * (1 + a * a / a ** 2) * math.sin(th)
out(v_top=vt)
