"""6.5 节的计算：

算例 6.5.1  重力加速度随纬度的变化（WGS 84 正常重力公式，图 6.5.1）；
算例 6.5.2  UR5e 竖直提起零件时腕部力传感器的读数（图 6.5.2）；
算例 6.5.3  弹簧劲度系数的测定：最小二乘拟合与标准不确定度（图 6.5.3，仿真数据）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d


# ---- 算例 6.5.1：WGS 84 椭球面上的正常重力（Somigliana 公式）
G_E, K_S, E2 = 9.780_325_3359, 0.001_931_852_652_41, 0.006_694_379_990_13   # g_e、k_s、e_E²（WGS 84）


def g_normal(lat_deg: float, h: float = 0.0) -> float:
    s2 = math.sin(math.radians(lat_deg)) ** 2
    return G_E * (1 + K_S * s2) / math.sqrt(1 - E2 * s2) - 3.086e-6 * h      # 高度修正取一阶近似


cities = {"guangzhou": 23.13, "shanghai": 31.23, "beijing": 39.90, "harbin": 45.75}
gs = {k: g_normal(v) for k, v in cities.items()}
g_eq, g_pole = g_normal(0), g_normal(90)
assert abs(g_eq - 9.780_325_3359) < 1e-9 and 9.8321 < g_pole < 9.8322
spread_pct = 100 * (g_pole - g_eq) / g_eq

# ---- 算例 6.5.2：竖直提起零件；力传感器读数 F = m (g + a)
m = 2.0
a_up = 3.0
F_static = m * g
F_acc = m * (g + a_up)           # 向上加速
F_dec = m * (g - a_up)           # 向上运动、减速（加速度向下）
# 一次完整的提升：0.2 s 加速、0.4 s 匀速、0.2 s 减速
tt = np.linspace(-0.2, 1.0, 1201)
acc = np.where((tt >= 0) & (tt < 0.2), a_up, np.where((tt >= 0.6) & (tt < 0.8), -a_up, 0.0))
reading = m * (g + acc)
v_max = a_up * 0.2
rise = v_max * 0.2 + v_max * 0.4        # 加速段和减速段各走 v_max*0.1，匀速段 v_max*0.4

# ---- 算例 6.5.3：弹簧标定（仿真数据）
rng = np.random.default_rng(65)
k_true = 2000.0                           # N/m
masses = np.arange(0.0, 1.01, 0.1)        # 砝码，kg
F = masses * g
x = F / k_true * 1000 + rng.normal(0, 0.03, masses.size)       # 读数，mm；读数的标准差 0.03 mm
slope, icpt = np.polyfit(F, x, 1)                                  # x = F/k + x0，单位 mm/N
resid = x - (slope * F + icpt)
n = F.size
s_res = math.sqrt(np.sum(resid ** 2) / (n - 2))
u_slope = s_res / math.sqrt(np.sum((F - F.mean()) ** 2))
k_fit = 1000 / slope
u_k = k_fit * u_slope / slope
assert abs(k_fit - k_true) < 3 * u_k

out(K_S=K_S, E2=E2, g_eq=g_eq, g_pole=g_pole, spread_pct=spread_pct, **{"g_" + k: v for k, v in gs.items()},
    lat_shanghai=cities["shanghai"], lat_beijing=cities["beijing"], dg_100m=3.086e-6 * 100, dev_gz_pct=100 * (g - gs['guangzhou']) / gs['guangzhou'],
    g_lhasa=g_normal(29.65, 3650), dev_lhasa_pct=100 * (g - g_normal(29.65, 3650)) / g_normal(29.65, 3650), m=m, a_up=a_up, F_static=F_static, F_acc=F_acc, F_dec=F_dec, v_max=v_max, rise_cm=100 * rise,
    k_fit=k_fit, u_k=u_k, U_k=2 * u_k, u_k_rel=100 * u_k / k_fit, x0=icpt, s_res=s_res, n_pts=n, x_max=float(x.max()))

plt = style()
# 图 6.5.1
lat = np.linspace(0, 90, 181)
fig, ax = plt.subplots(figsize=(5.6, 3.1))
ax.plot(lat, [g_normal(v) for v in lat], color="#1d6fb8", lw=2)
names = {"guangzhou": T("广州", "Guangzhou"), "shanghai": T("上海", "Shanghai"), "beijing": T("北京", "Beijing"), "harbin": T("哈尔滨", "Harbin")}
for k, v in cities.items():
    ax.plot([v], [gs[k]], "o", color=d.FORCE, ms=5)
    ax.annotate(names[k], (v, gs[k]), xytext=(4, -12), textcoords="offset points", fontsize=9, color=d.INK)
ax.axhline(g, color=d.MUTED, ls="--", lw=1)
ax.text(2, g + 0.0006, T("本书默认 g = 9.81 m/s²", "default in this book g = 9.81 m/s²"), fontsize=9, color=d.MUTED)
ax.set_xlabel(T("纬度 / (°)", "latitude / (°)")); ax.set_ylabel(T("$g$ / (m/s²)", "$g$ / (m/s²)"))
ax.set_xlim(0, 90)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
figure(fig, "fig6_5_1")
# 图 6.5.2
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5.6, 3.8), sharex=True)
ax1.plot(tt, acc, color=d.ACC, lw=2)
ax1.set_ylabel(T("$a$ / (m/s²)", "$a$ / (m/s²)")); ax1.set_ylim(-4, 4); ax1.axhline(0, color=d.MUTED, lw=0.8)
ax2.plot(tt, reading, color=d.FORCE, lw=2)
ax2.axhline(F_static, color=d.MUTED, ls="--", lw=1)
ax2.text(0.82, F_static + 0.6, T("静止时 $mg$", "at rest $mg$"), fontsize=9, color=d.MUTED)
ax2.set_ylabel(T("读数 $F$ / N", "reading $F$ / N")); ax2.set_xlabel(T("时间 $t$ / s", "time $t$ / s"))
ax2.set_ylim(10, 28)
for ax in (ax1, ax2):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig6_5_2")
# 图 6.5.3
fig, ax = plt.subplots(figsize=(5.6, 3.2))
ax.plot(F, x, "o", color=d.INK, ms=5, label=T("读数", "readings"))
ff = np.linspace(0, F.max() * 1.05, 2)
ax.plot(ff, slope * ff + icpt, color="#1d6fb8", lw=1.5, label=T("最小二乘直线", "least-squares line"))
ax.set_xlabel(T("拉力 $F$ / N", "force $F$ / N")); ax.set_ylabel(T("伸长 $x$ / mm", "extension $x$ / mm"))
ax.legend(frameon=False)
ins = ax.inset_axes([0.62, 0.12, 0.35, 0.3])
ins.axhline(0, color=d.MUTED, lw=0.8)
ins.plot(F, resid * 1000, "o", color=d.FORCE, ms=3)
ins.set_title(T("残差 / μm", "residual / μm"), fontsize=8)
ins.tick_params(labelsize=7)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
figure(fig, "fig6_5_3")
