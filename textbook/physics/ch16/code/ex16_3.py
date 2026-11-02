"""16.3 节的计算：

算例 16.3.1  水下机器人质量 24.0 kg，排开海水的体积 21.5 L（ρ = 1025 kg/m³）。浮力多大？在水中的“视重”多大？
            要用密度 400 kg/m³ 的浮力材料把它配成中性浮力（不沉不浮），要加多少体积的浮力材料（图 16.3.1）？
算例 16.3.2  称王冠：一顶“金冠”在空气中称 1.000 kg，浸没在水中称得 0.940 kg。它的密度多大？是纯金吗（金 19.3 g/cm³）？
"""
import numpy as np

from bookout import T, figure, out, style
import _draw as d

g, rho = 9.81, 1025.0
m, V = 24.0, 21.5e-3
Fb = rho * g * V
W = m * g
rf = 400.0
Vf = (W - Fb) / ((rho - rf) * g)
out(Fb=Fb, W=W, net=W - Fb, Vf_L=Vf * 1000, mf=rf * Vf)

ma, mw = 1.000, 0.940
Vc = (ma - mw) / 1000.0
out(rho_c=ma / Vc / 1000, V_cm3=Vc * 1e6)

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 2.9))
vv = np.linspace(0, 6, 100)
ax.plot(vv, W + rf * vv * 1e-3 * g - Fb - rho * vv * 1e-3 * g, color=d.VR, lw=2)
ax.axhline(0, color=d.MUTED, lw=0.7); ax.axvline(Vf * 1000, color=d.MUTED, lw=0.8, ls=":")
ax.text(Vf * 1000 + 0.1, 8, T(f"中性浮力：{Vf * 1000:.2f} L", f"neutral: {Vf * 1000:.2f} L"), fontsize=8.5)
ax.text(0.2, -12, T("上浮", "rises"), fontsize=8.5, color=d.MUTED); ax.text(0.2, 12, T("下沉", "sinks"), fontsize=8.5, color=d.MUTED)
ax.set_xlabel(T("加的浮力材料 / L", "buoyancy foam added / L")); ax.set_ylabel(T("重力 − 浮力 / N", "weight − buoyancy / N"))
d.spines(ax)
figure(fig, "fig16_3_1")
