"""图 2.8.1–2.8.2：舵机数据的拟合与残差；三种可以化成直线的模型。"""
import math

import numpy as np

from _data import P, TH, mulberry32
from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

u = (P - 1500) / 1000
c1, c3 = np.polyfit(u, TH, 1), np.polyfit(u, TH, 3)
fig = plt.figure(figsize=(11, 4.6))
gs = fig.add_gridspec(2, 2, width_ratios=[1.4, 1])
a = fig.add_subplot(gs[:, 0])
pp = np.linspace(550, 2450, 400)
a.plot(P, TH, "o", color=INK, ms=5, label=T("实测", "data"))
a.plot(pp, np.polyval(c1, (pp - 1500) / 1000), color=BLUE, lw=1.5, ls="--", label=T("线性模型", "linear"))
a.plot(pp, np.polyval(c3, (pp - 1500) / 1000), color=RED, lw=2, label=T("三次模型", "cubic"))
a.set_xlabel(T("脉宽 p / μs", "pulse width p / μs"))
a.set_ylabel(T("角度 θ / (°)", "angle θ / (°)"))
a.legend(fontsize=9, frameon=False)
clean(a, zero=False)
for k, (c, col, name) in enumerate(((c1, BLUE, T("线性模型的残差 / (°)", "linear residuals / (°)")), (c3, RED, T("三次模型的残差 / (°)", "cubic residuals / (°)")))):
    b = fig.add_subplot(gs[k, 1])
    r = TH - np.polyval(c, u)
    b.axhline(0, color=MUTED, lw=0.8)
    b.vlines(P, 0, r, color=col, lw=1.5)
    b.plot(P, r, "o", color=col, ms=4)
    b.set_ylim(-4.5, 4.5)
    b.set_title(name, fontsize=10)
    clean(b, zero=False)
fig.tight_layout()
figure(fig, "fig2_8_1")

fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(13, 4))
pl = [("Me", 0.387, 0.241), ("V", 0.723, 0.615), ("E", 1.0, 1.0), ("Ma", 1.524, 1.881), ("J", 5.203, 11.86), ("S", 9.537, 29.46)]
names = {"Me": T("水星", "Mercury"), "V": T("金星", "Venus"), "E": T("地球", "Earth"), "Ma": T("火星", "Mars"), "J": T("木星", "Jupiter"), "S": T("土星", "Saturn")}
aa = np.array([p[1] for p in pl])
TT = np.array([p[2] for p in pl])
a1.loglog(aa, TT, "o", color=INK)
xx = np.logspace(-0.6, 1.1, 50)
a1.loglog(xx, xx**1.5, color=RED, lw=1.5, label="$T = a^{3/2}$")
for (k, a_, t_) in pl:
    a1.text(a_ * 1.1, t_ * 0.75, names[k], fontsize=9)
a1.set_xlabel(T("半长轴 a（地球 = 1）", "semi-major axis a (Earth = 1)"))
a1.set_ylabel(T("周期 T / 年", "period T / years"))
a1.legend(fontsize=9, frameon=False)
a1.set_title(T("幂律：双对数坐标下为直线", "Power law: straight on log–log axes"), fontsize=10)
_, g2 = mulberry32(5)
tt = np.arange(0, 61, 5, dtype=float)
Tt = np.array([round((20 + 65 * math.exp(-t / 22) + 0.3 * g2()) * 10) / 10 for t in tt])
s_, i_ = np.polyfit(tt, np.log(Tt - 20), 1)
a2.semilogy(tt, Tt - 20, "o", color=INK)
ts = np.linspace(0, 60, 100)
a2.semilogy(ts, np.exp(i_ + s_ * ts), color=RED, lw=1.5, label=T("指数模型", "exponential model"))
a2.set_xlabel(T("时间 / min", "time / min"))
a2.set_ylabel(T("温差 T − 20 / °C", "excess T − 20 / °C"))
a2.legend(fontsize=9, frameon=False)
a2.set_title(T("指数：半对数坐标下为直线", "Exponential: straight on semi-log axes"), fontsize=10)
lat = math.radians(39.9)
n = np.arange(1, 366, 7, dtype=float)
dec = np.radians(23.44) * np.sin(2 * np.pi * (284 + n) / 365)
day = 2 / 15 * np.degrees(np.arccos(-np.tan(lat) * np.tan(dec)))
A = np.column_stack([np.ones_like(n), np.sin(2 * np.pi * n / 365), np.cos(2 * np.pi * n / 365)])
cf, *_ = np.linalg.lstsq(A, day, rcond=None)
nn = np.linspace(1, 365, 400)
a3.plot(n, day, "o", color=INK, ms=3)
a3.plot(nn, cf[0] + cf[1] * np.sin(2 * np.pi * nn / 365) + cf[2] * np.cos(2 * np.pi * nn / 365), color=RED, lw=1.5,
        label=T("正弦模型", "sinusoidal model"))
a3.set_xlabel(T("一年中的第几天", "day of the year"))
a3.set_ylabel(T("昼长 / h", "day length / h"))
a3.legend(fontsize=9, frameon=False)
a3.set_title(T("周期：北京的昼长", "Periodic: day length in Beijing"), fontsize=10)
clean(a3, zero=False)
fig.tight_layout()
figure(fig, "fig2_8_2")
