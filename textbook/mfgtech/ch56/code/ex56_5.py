"""算例 56.5.1：铸件套筒的粗基准（示意零件）。毛坯外圆 Ø80 不加工，铸孔 Ø46 因型芯偏移与外圆偏心 e；内孔要镗到 Ø52。
方案 A 以外圆（不加工面）为粗基准：镗出的孔与外圆同轴，壁厚均匀，但镗孔余量一边大一边小；
方案 B 以毛坯内孔为粗基准：余量均匀，但孔跟着型芯偏，壁厚一边厚一边薄。卡盘定心误差取 TIR 0.05（示意）。画图 56.5.3。"""
import numpy as np

import _mfg as M
from bookout import T, figure, out, style

D_out, d_core, d_bore, e, tir = 80.0, 46.0, 52.0, 2.0, 0.05
th = np.linspace(0, 2 * np.pi, 361)
R_out = D_out / 2
# 毛坯内孔中心在 (e, 0)：方向 θ 上毛坯孔壁到外圆中心的距离（近似）r_core(θ) = d_core/2 + e·cosθ
r_core = d_core / 2 + e * np.cos(th)
# A：孔与外圆同轴（偏 tir/2）
wall_A = R_out - (d_bore / 2 + tir / 2 * np.cos(th))
allow_A = d_bore / 2 - r_core
# B：孔与毛坯孔同轴
wall_B = R_out - (d_bore / 2 + e * np.cos(th))
allow_B = np.full_like(th, (d_bore - d_core) / 2)

plt = style()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.6, 2.5), sharex=True)
deg = np.degrees(th)
for a, y1, y2, ttl in ((a1, wall_A, wall_B, T("壁厚 / mm", "wall / mm")), (a2, allow_A, allow_B, T("镗孔余量（单边）/ mm", "boring allowance / mm"))):
    a.plot(deg, y1, color=M.GREEN, lw=1.4, label=T("A 以外圆为粗基准", "A: outer surface"))
    a.plot(deg, y2, color=M.RED, lw=1.4, label=T("B 以毛坯内孔为粗基准", "B: cored hole"))
    a.set_ylabel(ttl); a.grid(lw=0.3, alpha=0.5); a.set_xticks([0, 90, 180, 270, 360])
a1.set_ylim(10, 18); a2.set_ylim(-0.5, 6)
a1.legend(fontsize=6.5, loc="upper center")
for a in (a1, a2):
    a.set_xlabel(T("圆周位置 / °（0° 为型芯偏向的一侧）", "position round the bore / °"))
figure(fig, "fig56_5_3")

out(D_out=D_out, d_core=d_core, d_bore=d_bore, e=e, tir=tir, wall_A_min=wall_A.min(), wall_A_max=wall_A.max(), wall_B_min=wall_B.min(),
    wall_B_max=wall_B.max(), allow_A_min=allow_A.min(), allow_A_max=allow_A.max(), allow_B=float(allow_B[0]))
