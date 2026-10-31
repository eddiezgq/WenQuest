"""7.6 机器中的力流：WQR-105 在额定输出转矩下，力从电机经齿轮、轴、轴承到箱体和地脚螺栓，沿途每处的力有多大（算例 7.6.1，图 7.6.1）。
三根轴的转矩、啮合力和六个轴承的径向力用数字孪生的模型（twin/models.py，与第 33 章同一套几何、效率）；
箱体：啮合力是内力，各轴承传给箱体的力合起来为零，只剩一个力偶 = 输出转矩 − 输入转矩（两级减速，输入、输出同向转），
由地脚螺栓传给机架。力偶的轴线与轴平行，所以抵抗它的是沿箱体长度方向（三根轴排开的方向）的螺栓间距：
4 个螺栓，这个方向的中心距取本书设定值（箱长 410 mm，两端凸缘各外伸 20 mm）。
输出轴的支点按数字孪生的简化布置（A 版轴段），与第 33 章 B 版的数值不同。效率按本程序的转矩和转速由功率算出。"""
import math

import numpy as np

import _ch7 as H
from bookout import T, figure, out, style

TM = H.TM
g = TM.GEARS
Tq = TM.torques(H.RATED)
d1, d2, d3, d4 = g["m1"] * g["z1"], g["m1"] * g["z2"], g["m2"] * g["z3"], g["m2"] * g["z4"]
a12, a34 = (d1 + d2) / 2, (d3 + d4) / 2
Ft12, Ft34 = 2 * Tq["in"] * 1000 / d1, 2 * Tq["mid"] * 1000 / d3
Fr12, Fr34 = Ft12 * math.tan(TM.ALPHA), Ft34 * math.tan(TM.ALPHA)
Fn12, Fn34 = math.hypot(Ft12, Fr12), math.hypot(Ft34, Fr34)
BRG = TM.bearing_loads(H.RATED)
M_r = Tq["out"] - Tq["in"]                         # 箱体受到的反力偶（地脚螺栓承担）N·m
B_FOOT = 410 + 2 * 20                              # 地脚螺栓沿箱长方向的中心距 mm（本书设定）
F_bolt = M_r * 1000 / (2 * B_FOOT)                 # 每个螺栓的力的变化 N（4 个螺栓，两端各 2 个：一端拉力增加，另一端拉力减小）
n = TM.speeds()
P_in = Tq["in"] * n["in"] * 2 * math.pi / 60 / 1000
P_out = Tq["out"] * n["out"] * 2 * math.pi / 60 / 1000

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.6, 3.4), gridspec_kw={"width_ratios": [1.1, 1.0]})
# (a) 力流示意：三根轴在一个平面里（俯视），粗细表示力的大小
y_in, y_mid, y_out = 0, a12, a12 + a34
def shaft(y, x0, x1, lw):
    a0.plot([x0, x1], [y, y], color=H.INK, lw=lw, solid_capstyle="butt")
shaft(y_in, -60, 130, 1.5)
shaft(y_mid, 0, 120, 2.5)
shaft(y_out, 0, 200, 4)
for y, x, d, c in ((y_in, 35, d1, "#9ecae1"), (y_mid, 35, d2, "#9ecae1"), (y_mid, 85, d3, "#fdae6b"), (y_out, 82, d4, "#fdae6b")):
    a0.add_patch(__import__("matplotlib.patches", fromlist=["Rectangle"]).Rectangle((x - 9, y - d / 2), 18, d, fc=c, ec=H.INK, lw=0.6, alpha=0.8))
xb = {"in-A": (0, y_in), "in-B": (120, y_in), "mid-A": (0, y_mid), "mid-B": (120, y_mid), "out-A": (46, y_out), "out-B": (124.5, y_out)}
fmax = max(BRG.values())
for k, (x, y) in xb.items():
    a0.plot(x, y, "s", ms=4 + 8 * BRG[k] / fmax, color="#d62728")
    right = x > 60
    a0.text(x + (11 if right else -11), y - 16, f"{BRG[k]:.0f} N", fontsize=5.8, ha="left" if right else "right", color="#d62728")
a0.text(-62, y_in + 8, T(f"电机\n{Tq['in']:.1f} N·m", f"motor\n{Tq['in']:.1f} N·m"), fontsize=6.2)
a0.text(205, y_out, T(f"负载\n{Tq['out']:.0f} N·m", f"load\n{Tq['out']:.0f} N·m"), fontsize=6.2, va="center")
a0.text(-28, y_mid + 14, T(f"中间轴\n{Tq['mid']:.1f} N·m", f"intermediate\n{Tq['mid']:.1f} N·m"), fontsize=6.2, ha="right")
a0.add_patch(__import__("matplotlib.patches", fromlist=["Rectangle"]).Rectangle((-20, -60), 240, y_out + d4 / 2 + 75, fill=False, ec=H.MUTED, lw=0.8, ls="--"))
a0.text(220, -55, T(f"箱体：反力偶 {M_r:.0f} N·m", f"housing: reaction couple {M_r:.0f} N·m"), fontsize=6.2, ha="right", color=H.MUTED)
a0.set_aspect("equal")
a0.set_xlim(-95, 250)
a0.axis("off")
a0.set_title(T("(a) 力流：轴的转矩、轴承的径向力（红色方块）", "(a) Force flow: shaft torques, bearing radial loads (red squares)"), fontsize=7.4)
# (b) 沿途的力
labels = [T("啮合力（第一级）", "mesh force, stage 1"), T("啮合力（第二级）", "mesh force, stage 2")] + \
         [T(f"轴承 {k}", f"bearing {k}") for k in xb] + [T("地脚螺栓（每个，力的变化）", "foot bolt (each, change)")]
vals = [Fn12, Fn34] + [BRG[k] for k in xb] + [F_bolt]
cols = ["#9ecae1", "#fdae6b"] + ["#d62728"] * 6 + [H.MUTED]
a1.barh(range(len(vals)), vals, color=cols)
for i, v in enumerate(vals):
    a1.text(v + 50, i, f"{v:.0f}", va="center", fontsize=6.0)
a1.set_yticks(range(len(vals)))
a1.set_yticklabels(labels, fontsize=6.2)
a1.invert_yaxis()
a1.set_xlim(0, max(vals) * 1.2)
a1.set_xlabel(T("力 / N", "Force / N"), fontsize=7.2)
a1.tick_params(labelsize=6.3)
a1.set_title(T("(b) 沿途的力（额定转矩 350 N·m）", "(b) Forces along the path (rated 350 N·m)"), fontsize=7.4)
fig.tight_layout()
figure(fig, "fig7_6_1")

out(T_in=Tq["in"], T_mid=Tq["mid"], T_out=Tq["out"], d1=d1, d2=d2, d3=d3, d4=d4, a12=a12, a34=a34, Ft12=Ft12, Fr12=Fr12, Fn12=Fn12,
    Ft34=Ft34, Fr34=Fr34, Fn34=Fn34, **{"B_" + k.replace("-", "_"): v for k, v in BRG.items()}, M_r=M_r, b_foot=B_FOOT, F_bolt=F_bolt,
    eta=100 * P_out / P_in, eta_twin=100 * TM.ETA, ratio=TM.RATIO, n_in=n["in"], n_out=n["out"], P_in=P_in, P_out=P_out, loss=1000 * (P_in - P_out),
    ratio_out_in=Fn34 / Fn12, gain=Tq["out"] / Tq["in"])
