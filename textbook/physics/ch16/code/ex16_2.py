"""16.2 节的计算：

算例 16.2.1  水下机器人下潜到 300 m 深的海水中（ρ = 1025 kg/m³）。绝对压强和表压各多大？直径 100 mm 的观察窗受多大的力？
            每下潜 10 m 压强增加多少？（图 16.2.1a）
算例 16.2.2  大气压随高度的变化：等温大气 p = p₀ exp(−h/H)，H = RT/(Mg)，取 T = 288 K、M = 0.029 kg/mol。
            地面附近每升高 1 m 气压降低多少？无人机的气压计分辨率 1 Pa，对应多少高度？（图 16.2.1b）
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import atm, R as Rgas
import _draw as d

g, rho = 9.81, 1025.0
h = 300.0
pg = rho * g * h
dw = 0.100
out(p_abs_MPa=(atm + pg) / 1e6, pg_MPa=pg / 1e6, F_kN=pg * math.pi * dw ** 2 / 4 / 1000, dp10=rho * g * 10 / 1000, atm_kPa=atm / 1000)

Tk, Mm = 288.0, 0.029
H = Rgas * Tk / (Mm * g)
rho_air = atm * Mm / (Rgas * Tk)
dpdh = rho_air * g
out(H_km=H / 1000, rho_air=rho_air, dpdh=dpdh, res_cm=1 / dpdh * 100, p_8848=atm * math.exp(-8848 / H) / 1000, p_8848_frac=math.exp(-8848 / H))

plt = style()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 2.9))
z = np.linspace(0, 1000, 100)
a1.plot((atm + rho * g * z) / 1e6, z, color=d.VA, lw=2); a1.invert_yaxis()
a1.set_xlabel(T("绝对压强 / MPa", "absolute pressure / MPa")); a1.set_ylabel(T("水深 / m", "depth / m")); d.spines(a1)
a1.set_title(T("(a) 海水中", "(a) in seawater"), fontsize=9.5)
hh = np.linspace(0, 20000, 200)
a2.plot(atm * np.exp(-hh / H) / 1000, hh / 1000, color=d.VR, lw=2)
a2.set_xlabel(T("气压 / kPa", "air pressure / kPa")); a2.set_ylabel(T("海拔 / km", "altitude / km")); d.spines(a2)
a2.set_title(T("(b) 等温大气", "(b) isothermal atmosphere"), fontsize=9.5)
fig.tight_layout()
figure(fig, "fig16_2_1")
