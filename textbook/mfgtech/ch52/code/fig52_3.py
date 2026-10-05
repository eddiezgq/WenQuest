"""52.3 节的三维图：铣键槽时切削力的三个分力（图 52.3.1）；V 形块上的轴的四种失效方式（图 52.3.3）。"""
import math

import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
R = M.r3d()
g = J.geometry()
zc, Rg = g["zc"], 40.3 / 2
k = W.plan()["part"]["keyway"]
x_mid = 52.0 + float(k["offset_mm"]) + float(k["L"]) / 2 + g["work_x0"]
z_cut = zc + Rg - 1.03 * 3                                # 正在铣第 4 层

# ---- 图 52.3.1：铣刀在键槽里，三个分力
a = J.assembly("op40")
a.parts = [p for p in a.parts if p.name.startswith(("工件", "V 形块", "轴向挡板", "压板", "夹具体"))]
w = next(p for p in a.parts if p.name.startswith("工件"))
slot = S.cbox(x_mid + 6, 0, z_cut + 15, float(k["L"]) - 12, 12, 30) + S.cyl("z", (x_mid + 6 + (float(k["L"]) - 12) / 2, 0), 6, z_cut, z_cut + 40)
w.shape = w.shape - slot
a.add(C.Part("键槽铣刀", S.move(J.cutter(0, 0), x_mid - float(k["L"]) / 2 + 6 + 12, 0, z_cut), "tool"))
xc = x_mid - float(k["L"]) / 2 + 18
arr = [{"from": (xc + 6, 0, z_cut + 2), "to": (xc - 34, 0, z_cut + 2), "color": "#c0504d", "text": "Fx（沿进给，朝挡板）", "textAt": "end", "dx": -60, "dy": -12},
       {"from": (xc, -6, z_cut + 2), "to": (xc, -46, z_cut + 2), "color": "#4f7fb8", "text": "Fy（横向）", "textAt": "end", "dx": 6, "dy": 18},
       {"from": (xc + 2, -12, z_cut + 2), "to": (xc + 2, -12, z_cut + 36), "color": "#5a9e6f", "text": "Fz（螺旋刃把工件往上拔）", "dx": 8, "textAt": "end"}]
R.figure3d("fig52_3_1", a, 1400, 900, camera={"dir": [0.75, -1.3, 0.85], "fit": [[-60, -60, 0], [100, 60, 140]]}, arrows=arr,
           texts=[{"pos": [0.04, 0.08], "text": "坐标：x 沿进给方向（铣刀朝挡板走），y 横向，z 向上"}])

# ---- 图 52.3.3：四种失效方式（端面方向看剖面；(d) 从侧面看）
def base():
    b = J.assembly("op40")
    b.parts = [p for p in b.parts if p.name.startswith(("工件", "V 形块", "压板2", "夹具体", "轴向挡板"))]
    return b

end = {"dir": [-1.0, -0.22, 0.18], "fit": [[30, -45, 0], [30, 45, 95]]}
sec = ((30, 0, 0), (-1, 0, 0))
top = (30, 0, zc + Rg)
s45 = math.sin(math.radians(45))
pa = R.render_png(base(), 640, 560, camera=end, section=sec,
                  arrows=[{"from": (30, 0, zc + Rg - 2), "to": (30, 0, zc + Rg + 34), "color": "#5a9e6f", "text": "K·Fz", "dx": 8},
                          {"from": (30, 16, zc + 72), "to": (30, 16, zc + 40), "color": "#c0504d", "text": "W + G", "dx": -60}])
pb = R.render_png(base(), 640, 560, camera=end, section=sec,
                  arrows=[{"from": (30, 40, zc + Rg - 4), "to": (30, 4, zc + Rg - 4), "color": "#4f7fb8", "text": "K·Fy", "dx": -50, "dy": -10},
                          {"from": (30, Rg * s45 + 24 * s45, zc - Rg * s45 - 24 * s45), "to": (30, Rg * s45, zc - Rg * s45), "color": "#7a868d", "text": "N₁ → 0（被推离的一面卸载）", "dx": 8}])
pc = R.render_png(base(), 640, 560, camera=end, section=sec,
                  arrows=[{"from": (30, 40, zc + Rg), "to": (30, 4, zc + Rg), "color": "#4f7fb8", "text": "K·Fy（对轴线的力矩 K·Fy·r_f）", "dx": -60, "dy": -10},
                          {"from": (30, -Rg * s45 + 14 * s45, zc - Rg * s45 - 14 * s45), "to": (30, -Rg * s45 - 14 * s45, zc - Rg * s45 + 14 * s45), "color": "#e0a030",
                           "text": "摩擦力 μN", "dx": -80, "dy": 18},
                          {"from": (30, Rg * s45 + 14 * s45, zc - Rg * s45 + 14 * s45), "to": (30, Rg * s45 - 14 * s45, zc - Rg * s45 - 14 * s45), "color": "#e0a030"}])
side = {"dir": [0.15, -1.0, 0.25], "fit": [[-60, -30, 0], [125, 30, 100]]}
pd = R.render_png(base(), 640, 560, camera=side,
                  arrows=[{"from": (x_mid, -25, zc + Rg + 6), "to": (x_mid + 40, -25, zc + Rg + 6), "color": "#c0504d", "text": "背离挡板的 K·Fx", "dx": -20, "dy": -16},
                          {"from": (45, -25, zc - Rg + 5), "to": (15, -25, zc - Rg + 5), "color": "#e0a030", "text": "V 形块对工件的摩擦力", "dx": -10, "dy": 26}])
R.compose("fig52_3_3", [pa, pb, pc, pd], 2, titles=["(a) 被向上拔起：W + G ≥ K·Fz", "(b) 被横向推出 V 形块：W + G ≥ K·Fy·tan(α/2)",
                                                     "(c) 绕自身轴线转动：摩擦力矩 ≥ K·Fy·r_f", "(d) 沿轴线打滑（背离挡板的那一段）"])
out(n_fig3d=2)
