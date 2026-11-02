"""32.3 节的计算：RV 减速器，与谐波、行星的比较。

(1) RV 的两级：第一级行星（减速比 i1），第二级摆线针轮（针齿比摆线轮多 1 个齿）；总减速比的结构式（教材式 (32.3.1)），
    用零件库 RV-N 的一组标准减速比核对量级。
(2) 算例 32.3.1：零件库三种减速器的额定转矩与质量、外径、背隙：Harmonic Drive CSF（减速比 100，杯型组件，不含外壳和输出轴承）、
    Nabtesco RV-N（含主轴承）、Neugart PLE（一级、减速比 5，带壳体和输出轴承）。转矩密度 = 额定转矩 / 质量。
    图 32.3.2：额定转矩—质量（对数坐标）。
(3) 能不能用谐波做重载工业臂的 J2：零件库 CSF 最大的 32 号额定 137 N·m；RV-N 从 245 到 7000 N·m。
"""
import numpy as np

from _ch32 import library
from bookout import COLORS as C, T, figure, out, style

csf = [r for r in library("D-RDC-HD-CSF") if r["ratio"] == "100"]
rv = library("D-RDC-NABTESCO-RVN")
ple = [r for r in library("D-RDC-NEUGART-PLE") if r["ratio"] == "5"]
H = [(int(r["size_code"]), float(r["T_rated_Nm"]), float(r["mass_kg"]), float(r["OD_mm"])) for r in csf]
R = [(r["size"], float(r["T0_Nm"]), float(r["mass_kg"]), float(r["OD_mm"]), float(r["backlash_arcmin"])) for r in rv]
P = [(r["size_code"], float(r["T2D_Nm"]), float(r["mass_max_kg"]), float(r["D_mm"]), float(r["backlash_arcmin"])) for r in ple]
dens = {"h": np.median([t / m for _, t, m, _ in H]), "r": np.median([t / m for _, t, m, _, _ in R]), "p": np.median([t / m for _, t, m, _, _ in P])}
out(h_dens=dens["h"], r_dens=dens["r"], p_dens=dens["p"], h_max=max(t for _, t, _, _ in H), r_min=min(t for _, t, _, _, _ in R),
    r_max=max(t for _, t, _, _, _ in R), p_bl80=[b for s, _, _, _, b in P if s == "PLE080"][0], p_bl60=[b for s, _, _, _, b in P if s == "PLE060"][0],
    rv_bl=R[0][4])
# 同一档转矩（约 140 N·m）比一比：CSF-32-100 与 PLE120-5、RV-25N（RV 最小的一档）
h32 = [x for x in H if x[0] == 32][0]
p120 = [x for x in P if x[0] == "PLE120"][0]
r25 = [x for x in R if x[0] == "RV-25N"][0]
out(h32_T=h32[1], h32_m=h32[2], h32_D=h32[3], p120_T=p120[1], p120_m=p120[2], p120_D=p120[3], p120_bl=p120[4],
    r25_T=r25[1], r25_m=r25[2], r25_D=r25[3])
assert dens["h"] > dens["r"] and h32[2] < r25[2]
# RV 的结构式：第一级行星 i1，第二级摆线针轮（摆线轮 z_c 个齿、针齿 z_c + 1 个），曲柄轴输入、输出盘：i = 1 + i1·z_p（i1 = z_行星/z_太阳）
z_s, z_pl, z_p = 12, 36, 40
i_rv = 1 + (z_pl / z_s) * z_p
out(z_s=z_s, z_pl=z_pl, z_p=z_p, i_rv=i_rv)

plt = style()
fig, ax = plt.subplots(figsize=(7.6, 4.6))
ax.scatter([m for _, _, m, _ in H], [t for _, t, _, _ in H], s=40, color=C["x"], label=T("谐波 CSF（i = 100，杯型组件）", "strain wave CSF (i = 100, component set)"))
ax.scatter([m for _, _, m, _, _ in R], [t for _, t, _, _, _ in R], s=40, color=C["z"], label=T("RV-N（含主轴承）", "RV-N (with main bearing)"))
ax.scatter([m for _, _, m, _, _ in P], [t for _, t, _, _, _ in P], s=40, color=C["y"], label=T("行星 PLE（一级，i = 5）", "planetary PLE (1 stage, i = 5)"))
for s, t, m, _ in H:
    ax.annotate(str(s), (m, t), xytext=(4, -10), textcoords="offset points", fontsize=7, color=C["x"])
for s, t, m, _, _ in R[::3]:
    ax.annotate(s, (m, t), xytext=(4, -10), textcoords="offset points", fontsize=7, color=C["z"])
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel(T("质量 / kg", "mass / kg"))
ax.set_ylabel(T("额定转矩 / (N·m)", "rated torque / (N·m)"))
ax.axhline(137, color=C["muted"], lw=0.8, ls=":")
ax.text(0.1, 150, T("WQ-CR5 的 J2 用 32 号，额定 137 N·m", "WQ-CR5's J2: size 32, 137 N·m"), fontsize=8, color=C["muted"])
ax.legend(fontsize=8, frameon=False, loc="lower right")
ax.set_title(T("零件库三种减速器的额定转矩与质量", "Rated torque against mass, three reducer types in the library"), fontsize=11)
fig.tight_layout()
figure(fig, "fig32_3_2")
