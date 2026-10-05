"""4.4 几何公差的评定：SH-301 轴承位的圆度。同一组三坐标测点，用最小二乘圆（LSCI）和最小区域圆（MZCI）评定，
结果不同；GB/T 1182 / ISO 1101 规定的公差带是最小区域（算例 4.4.1，图 4.4.1）。"""
import math
import random

import numpy as np
from scipy.optimize import linprog

import _ch4 as H
from bookout import T, figure, out, style

# ---------------------------------------------------------------- 测点：Ø35 轴承位一个截面，三坐标扫描 N 点
N = 360
R0 = 35.0095 / 2                     # 截面实际半径（mm），取轴承位实测直径的平均值
E = (0.0062, -0.0038)               # 装夹偏心（mm）：工件轴线与转台轴线不重合，评定时要去掉
LOBES = [(2, 0.0008, 0.4), (3, 0.00105, 1.1), (5, 0.0003, 2.0)]   # (波数, 幅值 mm, 相位)：椭圆、三棱（磨削时的振动、中心孔误差）
NOISE = 0.0002                      # 随机误差（表面粗糙度、测头）的标准差
TOL = 0.004                         # 圆度公差（本书 SH-301 轴承位：按 GB/T 275 对普通级轴承配合面的建议取）
rng = random.Random(44)
th = np.array([2 * math.pi * k / N for k in range(N)])
form = sum(a * np.cos(n * th + ph) for n, a, ph in LOBES) + np.array([rng.gauss(0, NOISE) for _ in range(N)])
r_true = R0 + form
x = r_true * np.cos(th) + E[0]
y = r_true * np.sin(th) + E[1]
# 测量机给的是 (x, y)；以测点的形心为原点算极坐标
r = np.hypot(x - x.mean(), y - y.mean())
t = np.arctan2(y - y.mean(), x - x.mean())
c, s = np.cos(t), np.sin(t)

# ---------------------------------------------------------------- 最小二乘圆（线性化：r ≈ R + a cosθ + b sinθ，偏心远小于半径时成立）
A = np.column_stack([np.ones_like(r), c, s])
R_ls, a_ls, b_ls = np.linalg.lstsq(A, r, rcond=None)[0]
res_ls = r - (R_ls + a_ls * c + b_ls * s)
rnd_ls = res_ls.max() - res_ls.min()

# ---------------------------------------------------------------- 最小区域圆：两同心圆包住全部测点、半径差最小（线性规划）
# 变量 [a, b, R_in, w]：R_in ≤ r_i − a c_i − b s_i ≤ R_in + w，最小化 w
cost = [0, 0, 0, 1]
A_ub = np.vstack([np.column_stack([c, s, np.ones_like(r), np.zeros_like(r)]),          # a c + b s + R_in ≤ r
                  np.column_stack([-c, -s, -np.ones_like(r), -np.ones_like(r)])])      # r ≤ a c + b s + R_in + w
b_ub = np.concatenate([r, -r])
lp = linprog(cost, A_ub=A_ub, b_ub=b_ub, bounds=[(None, None)] * 3 + [(0, None)], method="highs")
a_mz, b_mz, Rin_mz, rnd_mz = lp.x
res_mz = r - (a_mz * c + b_mz * s + Rin_mz)
n_contact = int(np.sum(np.abs(res_mz) < 1e-7) + np.sum(np.abs(res_mz - rnd_mz) < 1e-7))
centre_shift = math.hypot(a_mz - a_ls, b_mz - b_ls) * 1000          # μm
ecc = math.hypot(*E) * 1000

# ---------------------------------------------------------------- 图
plt = style()
fig = plt.figure(figsize=(7.4, 3.3))
MAG = 2500                          # 偏差放大倍数（极坐标图上把微米放大）
base = 22.0                         # 图上的基圆半径（任意单位）：偏差 1 μm 放大成 2.5


def polar(ax, res, inner, outer, color, title, lab):
    ang = np.append(t, t[0])
    ax.plot(np.cos(ang) * (base + MAG * np.append(res, res[0])), np.sin(ang) * (base + MAG * np.append(res, res[0])), color=H.INK, lw=0.6)
    for rr, ls in ((inner, "-"), (outer, "-")):
        q = np.linspace(0, 2 * math.pi, 200)
        ax.plot(np.cos(q) * (base + MAG * rr), np.sin(q) * (base + MAG * rr), color=color, lw=0.9, ls=ls)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=8)
    ax.text(0, -base - MAG * outer - 4, lab, ha="center", va="top", fontsize=7.2, color=color)


a1 = fig.add_subplot(1, 3, 1)
polar(a1, res_ls - res_ls.mean(), res_ls.min() - res_ls.mean(), res_ls.max() - res_ls.mean(), "#1f77b4",
      T("(a) 最小二乘圆", "(a) Least-squares circle"), T("圆度 ", "roundness ") + f"{rnd_ls * 1000:.1f} μm")
a2 = fig.add_subplot(1, 3, 2)
polar(a2, res_mz - rnd_mz / 2, -rnd_mz / 2, rnd_mz / 2, "#2ca02c",
      T("(b) 最小区域圆", "(b) Minimum-zone circles"), T("圆度 ", "roundness ") + f"{rnd_mz * 1000:.1f} μm")
a3 = fig.add_subplot(1, 3, 3)
deg = np.degrees(t) % 360
o = np.argsort(deg)
a3.plot(deg[o], 1000 * res_mz[o], color=H.INK, lw=0.6)
a3.axhline(0, color="#2ca02c", lw=0.8)
a3.axhline(1000 * rnd_mz, color="#2ca02c", lw=0.8)
a3.axhline(1000 * TOL, color="#d62728", lw=0.8, ls="--")
a3.text(5, 1000 * TOL + 0.1, T("公差 ", "tolerance ") + f"{TOL * 1000:.0f} μm", fontsize=6.6, color="#d62728", va="bottom")
a3.set_xlabel(T("角度 / (°)", "Angle / (°)"), fontsize=7.5)
a3.set_ylabel(T("到内圆的距离 / μm", "Distance from inner circle / μm"), fontsize=7.5)
a3.tick_params(labelsize=6.5)
a3.set_xlim(0, 360)
a3.set_title(T("(c) 展开：最小区域", "(c) Unrolled: minimum zone"), fontsize=8)
fig.tight_layout()
figure(fig, "fig4_4_1")

assert rnd_mz <= rnd_ls + 1e-9
out(N=N, ecc=ecc, rnd_ls=rnd_ls * 1000, rnd_mz=rnd_mz * 1000, tol=TOL * 1000, n_contact=n_contact, centre_shift=centre_shift,
    ok_ls=T("合格", "conforms") if rnd_ls <= TOL else T("不合格", "does not conform"),
    ok_mz=T("合格", "conforms") if rnd_mz <= TOL else T("不合格", "does not conform"),
    diff_pct=100 * (rnd_ls - rnd_mz) / rnd_mz, mag=MAG)
