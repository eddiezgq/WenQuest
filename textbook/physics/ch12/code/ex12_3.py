"""12.3 节的计算：

算例 12.3.1  用数值积分核对几种均匀物体的转动惯量：细杆（过中点、过一端）、圆盘、圆环、实心球、薄球壳（质量 1 kg、尺寸 1 m）。
算例 12.3.2  UR5e 小臂（零件库模型 B-ARM-UR5E，数据来自 MuJoCo Menagerie 的 ur5e.xml）：质量 2.275 kg，质心离肘关节 0.196 m，
            绕过质心、平行于肘关节轴的转动惯量 0.0311796 kg·m²。用平行轴定理求它绕肘关节的转动惯量和回转半径；
            与“长 0.392 m 的均匀细杆绕一端”的估算比较；末端再夹 1.0 kg 的负载（离肘关节 0.392 m）时是多少。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

# ---- 数值积分：把物体分成很多小块，求 Σ r² dm
N = 400000
rng = np.random.default_rng(1)
L = 1.0
x = (np.arange(N) + 0.5) / N * L
J_rod_c = float(np.sum((x - L / 2) ** 2) / N)
J_rod_e = float(np.sum(x ** 2) / N)
rr = (np.arange(N) + 0.5) / N                                   # 圆盘：半径 1 的圆环带，面积 ∝ r
J_disk = float(np.sum(rr ** 2 * 2 * rr) / N)                    # dm = 2r dr（总质量 1）
p = rng.normal(size=(N, 3)); p /= np.linalg.norm(p, axis=1)[:, None]
J_shell = float(np.mean(p[:, 0] ** 2 + p[:, 1] ** 2))           # 球面上均匀取点，绕 z 轴
u = rng.random(N) ** (1 / 3)                                    # 球体内均匀取点
J_ball = float(np.mean((u[:, None] * p)[:, 0] ** 2 + (u[:, None] * p)[:, 1] ** 2))
exact = {"rod_c": 1 / 12, "rod_e": 1 / 3, "disk": 1 / 2, "ring": 1.0, "ball": 2 / 5, "shell": 2 / 3}
num = {"rod_c": J_rod_c, "rod_e": J_rod_e, "disk": J_disk, "ring": 1.0, "ball": J_ball, "shell": J_shell}
for k_ in exact:
    assert abs(num[k_] - exact[k_]) < 5e-3, k_
out(**{f"n_{k_}": v for k_, v in num.items()})

# ---- 算例 12.3.2：UR5e 小臂
m, d_c, Ic = 2.275, 0.196, 0.0311796
J_elbow = Ic + m * d_c ** 2
k_g = math.sqrt(J_elbow / m)
Lf = 0.392
J_rod = m * Lf ** 2 / 3
mp = 1.0
J_load = J_elbow + mp * Lf ** 2
out(m=m, d_c=d_c, Ic=Ic, md2=m * d_c ** 2, J_elbow=J_elbow, k_g=k_g, Lf=Lf, J_rod=J_rod, err_rod=(J_elbow - J_rod) / J_elbow,
    mp=mp, J_load=J_load, load_frac=mp * Lf ** 2 / J_load)

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 2.9))
names = [T("细杆（中点）", "rod (centre)"), T("细杆（一端）", "rod (end)"), T("实心球", "solid sphere"), T("圆盘、实心圆柱", "disk, solid cylinder"),
         T("薄球壳", "spherical shell"), T("圆环、薄圆筒", "ring, thin hoop")]
vals = [1 / 12, 1 / 3, 2 / 5, 1 / 2, 2 / 3, 1.0]
labels = ["1/12 ML²", "1/3 ML²", "2/5 MR²", "1/2 MR²", "2/3 MR²", "MR²"]
ax.barh(range(len(vals)), vals, color=[d.VB, d.VB, d.VA, d.VA, d.VA, d.VR], height=0.6)
for i_, (v_, lab) in enumerate(zip(vals, labels)):
    ax.text(v_ + 0.02, i_, lab, va="center", fontsize=9)
ax.set_yticks(range(len(vals))); ax.set_yticklabels(names, fontsize=9); ax.set_xlim(0, 1.3)
ax.set_xlabel(T("J / (ML²) 或 J / (MR²)", "J / (ML²) or J / (MR²)")); d.spines(ax)
figure(fig, "fig12_3_1")
