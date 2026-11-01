"""16.2 节：体积的切片法与祖暅原理——牟合方盖与球的体积（截面积之比 π : 4）；祖暅的做法：立方体减去牟合方盖，
截面积 4z² 与倒置的方锥相同；AGV 料斗（正四棱台，《九章算术》方亭公式）；由 CT 断层的截面积求体积。"""
import math

from scipy import integrate

from _quad import simpson, trap
from bookout import out

r = 1.0
V_mouhe = integrate.quad(lambda z: 4 * (r * r - z * z), -r, r)[0]
V_ball = integrate.quad(lambda z: math.pi * (r * r - z * z), -r, r)[0]
V_out = integrate.quad(lambda z: 4 * z * z, -r, r)[0]          # 立方体 − 牟合方盖
out(V_mouhe=V_mouhe, V_ball=V_ball, ratio=V_ball / V_mouhe, V_out=V_out, V_cube=8 * r ** 3)
# AGV 料斗：上口 0.6 m 见方，下口 0.2 m 见方，高 0.5 m
a, b, h = 0.6, 0.2, 0.5
side = lambda z: b + (a - b) * z / h
V_slice = integrate.quad(lambda z: side(z) ** 2, 0, h)[0]
V_fang = h / 3 * (a * a + a * b + b * b)
V_wrong = h * (a * a + b * b) / 2            # 误用“上下底面积的平均 × 高”
out(hop_a=a, hop_b=b, hop_h=h, V_slice=V_slice, V_fang=V_fang, V_wrong=V_wrong, wrong_pct=(V_wrong - V_fang) / V_fang * 100)
# CT 断层：一个器官形状的物体，z 从 −24 到 24 mm，截面近似椭圆，半轴随 z 变化
c = 24.0
def A(z):                      # mm²
    s = max(1 - (z / c) ** 2, 0.0)
    ax = 30 * math.sqrt(s) * (1 + 0.15 * math.sin(math.pi * z / c))
    by = 20 * math.sqrt(s) * (1 - 0.1 * math.cos(math.pi * z / (2 * c)))
    return math.pi * ax * by
V_ct = integrate.quad(A, -c, c, limit=200)[0]
rows = []
for dz in (2.0, 4.0, 6.0, 12.0):
    n = int(round(2 * c / dz))
    vt = trap(A, -c, c, n)
    vs = simpson(A, -c, c, n) if n % 2 == 0 else float("nan")
    rows.append(f"| {dz:g} | {n + 1} | {vt / 1000:.2f} | {(vt - V_ct) / V_ct * 100:+.2f} | {vs / 1000:.2f} | {(vs - V_ct) / V_ct * 100:+.1e} |")
out(V_ct=V_ct / 1000, ct_tab="\n".join(rows))
