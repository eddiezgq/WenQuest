"""8.9 接触应力：赫兹理论（算例 8.9.1–8.9.3，图 8.9.1）。
1. WQR-105 第二级齿轮（m = 3，z = 20 / 70，α = 20°，齿宽 40 mm——数字工厂参数配置器的布置）在节点啮合：两齿面看成两个圆柱，
   曲率半径 ρ = (d/2)·sin α；单位齿宽的法向力 F′ = F_t / (b·cos α)；额定转矩和跑合试验台的起动峰值两种情况。
   这只是“赫兹接触”本身；齿面接触强度的计算（重合度、载荷分配、各种系数）在第 29 章。
2. AGV 驱动轮：MC 尼龙轮（直径 150 mm、宽 50 mm，本书设定）压在钢板地面上，每轮 1500 N（本书设定），线接触。
3. 6207 轴承：受径向力 2000 N（第 7 章输出轴轴承 A 的量级）时载荷最大的钢球与内圈滚道的点接触（椭圆接触，Hamrock–Brewe 近似）。
   钢球直径、球数、沟曲率、节圆直径取常见样本的典型值（零件库里没有）。最大钢球载荷按施特里贝克 Q_max = 5F_r / Z。
线接触对称轴下的主切应力：τ₁ 最大约 0.30 p₀，在深度约 0.78a 处（McEwen）。"""
import math
import sys
from pathlib import Path

import numpy as np

import _ch8 as H
from bookout import T, figure, out, style

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ch07" / "code"))
import _ch7 as C7                     # noqa: E402

ST = H.mat("40Cr-QT")                 # 钢对钢（齿轮、轴承钢的 E、ν 相同量级）
Es_steel = H.E_star(ST["E"], ST["nu"], ST["E"], ST["nu"])
# 1. 齿轮
g = C7.TM.GEARS
m2, z3, z4, ALPHA, B = g["m2"], g["z3"], g["z4"], C7.TM.ALPHA, 40.0
d3, d4 = m2 * z3, m2 * z4
rho1, rho2 = d3 / 2 * math.sin(ALPHA), d4 / 2 * math.sin(ALPHA)
Rg = 1 / (1 / rho1 + 1 / rho2)
Tq_mid = C7.TM.torques(C7.RATED)["mid"]
Ft = 2 * Tq_mid * 1e3 / d3
_, yb, _ = C7.bench()
peak_ratio = max(yb) / C7.RATED
gear = {}
for k, f in (("rated", 1.0), ("peak", peak_ratio)):
    Fp = Ft * f / (B * math.cos(ALPHA))
    a, p0 = H.hertz_line(Fp, Rg, Es_steel)
    gear[k] = (Fp, a, p0)
# 2. AGV 轮（MC 尼龙：E ≈ 3000 MPa，ν ≈ 0.4，本书取值）
E_NY, NU_NY = 3000.0, 0.4
Es_agv = H.E_star(E_NY, NU_NY, ST["E"], ST["nu"])
R_W, B_W, F_W = 75.0, 50.0, 1500.0
a_w, p_w = H.hertz_line(F_W / B_W, R_W, Es_agv)
# 3. 6207 钢球与内圈
DW, ZB, F_GROOVE, DPW = 11.112, 9, 0.52, 53.5          # 钢球直径、球数、内圈沟曲率系数、节圆直径（本书取的典型值）
Fr = 2000.0
Qmax = 5 * Fr / ZB
r_in_race = (DPW - DW) / 2                              # 内圈滚道底半径
Rx = 1 / (2 / DW + 1 / r_in_race)                       # 滚动方向
Ry = 1 / (2 / DW - 1 / (F_GROOVE * DW))                 # 横向（凹沟）
ab, bb, p_b = H.hertz_point(Qmax, Rx, Ry, Es_steel)

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0))
Fp, a, p0 = gear["rated"]
x = np.linspace(-1.5 * a, 1.5 * a, 300)
a0.plot(x, np.where(np.abs(x) < a, p0 * np.sqrt(np.clip(1 - (x / a) ** 2, 0, None)), 0), color="#d62728", lw=1.4, label=T("额定转矩", "rated torque"))
Fp2, a2, p02 = gear["peak"]
x2 = np.linspace(-1.5 * a2, 1.5 * a2, 300)
a0.plot(x2, np.where(np.abs(x2) < a2, p02 * np.sqrt(np.clip(1 - (x2 / a2) ** 2, 0, None)), 0), color="#9467bd", lw=1.2, ls="--", label=T("起动峰值", "start peak"))
a0.set_xlabel(T("离接触中线的距离 / mm", "Distance from the contact centerline / mm"), fontsize=7.0)
a0.set_ylabel(T("接触压力 / MPa", "Contact pressure / MPa"), fontsize=7.2)
a0.legend(fontsize=6.3, frameon=False)
a0.tick_params(labelsize=6.3)
a0.set_title(T("(a) 第二级齿面在节点的接触压力", "(a) Contact pressure at the pitch point, stage 2"), fontsize=7.4)
zs = np.linspace(0, 3, 200)
vals = np.array([H.line_subsurface(z) for z in zs])
a1.plot(-vals[:, 0], zs, color="#1f77b4", lw=1.2, label="−σx / p₀")
a1.plot(-vals[:, 1], zs, color="#2ca02c", lw=1.2, label="−σz / p₀")
a1.plot(vals[:, 2], zs, color="#d62728", lw=1.6, label="τ₁ / p₀")
k = int(np.argmax(vals[:, 2]))
a1.plot(vals[k, 2], zs[k], "ko", ms=3.5)
a1.text(vals[k, 2] + 0.03, zs[k], f"{vals[k, 2]:.2f} p₀, z = {zs[k]:.2f}a", fontsize=6.4, va="center")
a1.invert_yaxis()
a1.set_xlabel(T("应力 / p₀", "Stress / p₀"), fontsize=7.2)
a1.set_ylabel(T("深度 z / a", "Depth z / a"), fontsize=7.2)
a1.legend(fontsize=6.3, frameon=False, loc="lower right")
a1.tick_params(labelsize=6.3)
a1.set_title(T("(b) 线接触中线下的应力（无因次）", "(b) Stresses below a line contact (nondimensional)"), fontsize=7.4)
fig.tight_layout()
figure(fig, "fig8_9_1")

out(m2=m2, z3=z3, z4=z4, B=B, d3=d3, d4=d4, rho1=rho1, rho2=rho2, Rg=Rg, Es=Es_steel, T_mid=Tq_mid, Ft=Ft, peak_ratio=peak_ratio,
    Fp_r=gear["rated"][0], a_r=gear["rated"][1], p0_r=gear["rated"][2], tau_r=0.30 * gear["rated"][2], z_r=0.78 * gear["rated"][1],
    Fp_p=gear["peak"][0], a_p=gear["peak"][1], p0_p=gear["peak"][2], tau_k=float(vals[k, 2]), z_k=float(zs[k]),
    E_ny=E_NY, R_w=R_W, B_w=B_W, F_w=F_W, a_w=a_w, p_w=p_w, Es_agv=Es_agv,
    Dw=DW, Zb=ZB, fg=F_GROOVE, Dpw=DPW, Fr=Fr, Qmax=Qmax, Rx=Rx, Ry=Ry, a_b=ab, b_b=bb, p_b=p_b, ratio_ab=ab / bb, ratio_bg=p_b / gear["rated"][2])
