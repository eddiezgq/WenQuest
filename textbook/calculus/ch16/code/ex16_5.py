"""16.5 节：旋转曲面的面积——球面积 4πr² 与阿基米德的“球带面积 = 外切圆柱侧面积”；加百列号角的表面积发散；
服务机器人外壳（圆柱 + 半椭球顶 + 平底）的体积、表面积、喷涂用漆量与壳体质量；零件库三角网格（圆周分成 N 份）的偏差。"""
import math

from scipy import integrate

from bookout import out

r = 1.0
out(sph=integrate.quad(lambda x: 2 * math.pi * math.sqrt(r * r - x * x) * r / math.sqrt(r * r - x * x), -r, r)[0], sph_ex=4 * math.pi)
# 球带：x 从 0.2 到 0.5，面积 2πr·0.3
out(zone=integrate.quad(lambda x: 2 * math.pi * r, 0.2, 0.5)[0], zone_ex=2 * math.pi * 0.3)
# 加百列号角：S(T) = 2π ∫₁^T (1/x)√(1 + 1/x⁴) dx
rows = []
for T in (10, 100, 1e4, 1e6):
    S = integrate.quad(lambda x: 2 * math.pi / x * math.sqrt(1 + x ** -4), 1, T, limit=200)[0]
    rows.append(f"| {T:.0f} | {S:.3f} | {2 * math.pi * math.log(T):.3f} | {math.pi * (1 - 1 / T):.5f} |")
out(horn_tab="\n".join(rows))
# 机器人外壳：半径 R = 150 mm，圆柱段高 H = 400 mm，顶部半椭球（竖直半轴 c = 100 mm），平底
R, H, c = 150.0, 400.0, 100.0
S_side = 2 * math.pi * R * H
S_dome = integrate.quad(lambda t: 2 * math.pi * R * math.cos(t) * math.sqrt((R * math.sin(t)) ** 2 + (c * math.cos(t)) ** 2), 0, math.pi / 2)[0]
S_bot = math.pi * R * R
S_tot = S_side + S_dome + S_bot
V = math.pi * R * R * H + 2 / 3 * math.pi * R * R * c
out(hs_R=R, hs_H=H, hs_c=c, S_side=S_side / 1e6, S_dome=S_dome / 1e6, S_hemi=2 * math.pi * R * R / 1e6, S_bot=S_bot / 1e6, S_tot=S_tot / 1e6,
    V_hs=V / 1e6)
# 喷涂：干膜 30 μm，固体含量 50% → 湿漆体积；外壳 ABS 壁厚 2.5 mm、1.05 g/cm³（只算侧面与顶，底部另装）
paint_mL = (S_side + S_dome) * 0.030 / 0.5 / 1000
shell_kg = (S_side + S_dome) * 2.5 * 1.05e-3 / 1000
out(paint_mL=paint_mL, shell_kg=shell_kg)
# 零件库模型：圆周用 N 边形近似（内接），体积按 N sin(2π/N)/(2π)、侧面积按 N sin(π/N)/π 缩小
rows = []
for N in (12, 24, 48, 96, 360):
    fv = N * math.sin(2 * math.pi / N) / (2 * math.pi)
    fa = N * math.sin(math.pi / N) / math.pi
    rows.append(f"| {N} | {(fv - 1) * 100:+.3f} | {(fa - 1) * 100:+.3f} |")
out(mesh_tab="\n".join(rows))
