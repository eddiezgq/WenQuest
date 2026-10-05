"""5.3 热处理：WQR-105 第二级小齿轮 GR-203（20CrMnTi，m = 3）的渗碳层深度——碳在奥氏体中的扩散（有限差分），
扩散系数随温度和含碳量变化（Tibbetts 1980 的经验式）；回火参数（霍洛蒙–杰夫）。算例 5.3.2（渗碳）、5.3.1（回火参数），图 5.3.1。"""
import math

import numpy as np

import _ch5 as H
from bookout import T, figure, out, style

C0 = 0.20             # 20CrMnTi 的含碳量 %（GB/T 3077：0.17–0.23）
CS = 0.90             # 炉气碳势（表面含碳量）%，本书设定
C_ECD = 0.40          # 以含碳量 0.40% 处的深度近似有效硬化层深度（约 550 HV 处，按含碳量估计）
M_GEAR = 3.0          # GR-203 模数（数字工厂齿轮数据）
ECD_RANGE = (0.15 * M_GEAR, 0.25 * M_GEAR)       # 有效硬化层深度的常用经验范围 0.15m–0.25m
R_CAL = 1.987         # 气体常数 cal/(mol·K)（Tibbetts 式用 cal）
TARGET = 0.6          # 本例要求的有效硬化层深度 mm


def D(C, Tk):
    """碳在奥氏体中的扩散系数 mm²/s（Tibbetts G. G., J. Appl. Phys. 51 (1980) 4813：D = 0.47 exp(−1.6C) exp(−(37000 − 6600C)/RT) cm²/s）"""
    return 0.47 * np.exp(-1.6 * C) * np.exp(-(37000 - 6600 * C) / (R_CAL * Tk)) * 100.0


def carburize(T_c, hours, L=5.0, dx=0.01):
    """一维扩散，表面含碳量恒为 CS，内部初始为 C0。返回 x（mm）与各时刻（小时数列表）的含碳量分布"""
    Tk = T_c + 273.15
    x = np.arange(0, L + dx / 2, dx)
    c = np.full(x.size, C0)
    c[0] = CS
    dmax = float(D(CS, Tk))
    dt = 0.4 * dx * dx / dmax
    out_, t, k = {}, 0.0, 0
    targets = sorted(hours)
    while k < len(targets):
        Dm = D(0.5 * (c[1:] + c[:-1]), Tk)               # 界面上的扩散系数
        flux = -Dm * (c[1:] - c[:-1]) / dx
        c[1:-1] -= dt * (flux[1:] - flux[:-1]) / dx
        c[0] = CS
        t += dt
        while k < len(targets) and t >= targets[k] * 3600:
            out_[targets[k]] = c.copy()
            k += 1
    return x, out_


def ecd(x, c):
    if c[-1] >= C_ECD or c[1] < C_ECD:
        raise ValueError("有效硬化层超出计算区域或不足一个网格")
    i = np.argmax(c < C_ECD)
    return float(np.interp(C_ECD, [c[i], c[i - 1]], [x[i], x[i - 1]]))


HOURS = [1, 2, 3, 4, 5, 6, 8, 10]
res = {}
for Tc in (900, 930, 950):
    x, prof = carburize(Tc, HOURS)
    res[Tc] = {h: ecd(x, prof[h]) for h in HOURS}
    if Tc == 930:
        prof930 = prof


def time_for(Tc, depth):
    hs = HOURS
    ds = [res[Tc][h] for h in hs]
    return float(np.interp(depth, ds, hs))


t930 = time_for(930, TARGET)
t900 = time_for(900, TARGET)
# 抛物线规律：深度 ∝ √t —— 深度加倍，时间约为 4 倍
r_sqrt = res[930][8] / res[930][2]

# 算例 5.3.1：回火参数 P = T(20 + lg t)，T 为热力学温度，t 为小时
P = (520 + 273.15) * (20 + math.log10(2.0))
t560 = 10 ** (P / (560 + 273.15) - 20)

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0))
for h, c in zip((2, 4, 6, 8), ("#c6dbef", "#6baed6", "#2171b5", "#08306b")):
    a0.plot(x, prof930[h], color=c, lw=1.1, label=f"{h} h")
a0.axhline(C_ECD, color="#d62728", lw=0.7, ls="--")
a0.text(1.25, C_ECD + 0.01, T("0.40%：有效硬化层的界限（近似）", "0.40%: effective case limit (approx.)"), fontsize=6.4, color="#d62728")
a0.set_xlim(0, 2.5)
a0.set_xlabel(T("离表面的深度 / mm", "Depth below surface / mm"), fontsize=7.5)
a0.set_ylabel(T("含碳量 / %", "Carbon / %"), fontsize=7.5)
a0.legend(fontsize=6.5, frameon=False)
a0.tick_params(labelsize=6.5)
a0.set_title(T("(a) 930 °C 渗碳，表面碳势 0.9%", "(a) Carburizing at 930 °C, carbon potential 0.9%"), fontsize=7.8)
for Tc, c in ((900, "#2ca02c"), (930, "#1f77b4"), (950, "#d62728")):
    a1.plot(HOURS, [res[Tc][h] for h in HOURS], "o-", ms=3, color=c, lw=1, label=f"{Tc} °C")
a1.axhspan(*ECD_RANGE, color="#999", alpha=0.15)
a1.text(6.2, ECD_RANGE[0] + 0.02, T("0.15m–0.25m（m = 3）", "0.15m–0.25m (m = 3)"), fontsize=6.4, color=H.MUTED)
a1.set_xlabel(T("渗碳时间 / h", "Time / h"), fontsize=7.5)
a1.set_ylabel(T("有效硬化层深度 / mm", "Effective case depth / mm"), fontsize=7.5)
a1.legend(fontsize=6.5, frameon=False)
a1.tick_params(labelsize=6.5)
a1.set_title(T("(b) 有效硬化层深度随时间、温度", "(b) Case depth versus time and temperature"), fontsize=7.8)
fig.tight_layout()
figure(fig, "fig5_3_1")

out(R_cal=R_CAL, C0=C0, CS=CS, C_ECD=C_ECD, m=M_GEAR, ecd_lo=ECD_RANGE[0], ecd_hi=ECD_RANGE[1], target=TARGET,
    t930=t930, t900=t900, e930_2=res[930][2], e930_8=res[930][8], r_sqrt=r_sqrt,
    D930_02=float(D(0.2, 930 + 273.15)) * 1e-6, D930_09=float(D(0.9, 930 + 273.15)) * 1e-6,
    D930_02_m=float(D(0.2, 930 + 273.15)) * 1e-6 * 1e11, D930_09_m=float(D(0.9, 930 + 273.15)) * 1e-6 * 1e11,
    P=P, t560_min=t560 * 60)
