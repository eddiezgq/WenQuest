"""52.8 节的三维图：槽系与孔系组合夹具（图 52.8.1）、零点定位系统（图 52.8.2）、3D 打印的仿形软爪（图 52.8.3）。"""
import math

import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
R = M.r3d()
A, P = C.Assembly, C.Part

# ---- 图 52.8.1：(a) 槽系；(b) 孔系（定位销 + 螺钉连接）
pa = R.render_png(TY.modular_fixture(), 700, 520, camera={"dir": [0.9, -1.3, 0.9]})
hg = A("孔系组合夹具")
hg.add(P("孔系基础板", E.hole_grid_plate(400, 300, 30, 50), "steel"))
for k, (x, y) in enumerate(((-75, -25), (75, -25))):
    hg.add(P(f"支承块{k}", S.box(x - 25, x + 25, y - 25, y + 25, 0, 40), "steel"))
    hg.add(P(f"V形块{k}", E.vblock(B=50, L=50, H=30, apex=10, at=(x, y, 40), axis="x"), "hardened"))
hg.add(P("定位块（挡块）", S.box(-160, -125, -55, 5, 0, 70), "steel"))
zc = 40 + E.v_axis_height(36, apex=10)
hg.add(P("工件（轴）", S.cyl("x", (-25, zc), 18, -125, 130), "work"))
for k, x in enumerate((-75, 75)):
    hg.add(P(f"压板{k}", S.box(x - 12, x + 12, -60, 0, zc + 18, zc + 30), "steel"))
    hg.add(P(f"螺钉{k}", S.cyl("z", (x, -50), 5, -10, zc + 40) + S.hexagon("z", (x, -50), 16, zc + 30, zc + 38), "steel_dark"))
for x in (-75, 75):
    for y in (-50, 0):
        hg.add(P(f"定位销{x}{y}", S.cyl("z", (x, y), 5.9, -2, 2), "red"))
pb = R.render_png(hg, 700, 520, camera={"dir": [0.9, -1.3, 0.9]})
R.compose("fig52_8_1", [pa, pb], 2, titles=["(a) 槽系：元件之间用键和 T 形槽螺栓连接，位置无级可调", "(b) 孔系：元件用定位销插在坐标孔里，再用螺钉固定"])

# ---- 图 52.8.2：(a) 零点定位卡盘与拉钉（剖开，锁紧状态）；(b) 托盘带 4 个拉钉，落到工作台的 4 个卡盘上
zp = A("零点定位")
zp.add(P("零点定位卡盘", E.zero_point_chuck(at=(0, 0, 0), D=120, H=50), "steel_dark"))
zp.add(P("拉钉", E.pull_stud(at=(0, 0, 30)), "hardened"))
zp.add(P("托盘（局部）", S.box(-90, 90, -90, 90, 30, 60) - S.cyl("z", (0, 0), 21.2, 29, 39), "steel"))
for k in range(4):
    ang = math.pi / 2 * k
    zp.add(P(f"钢球{k}", S.move(S.bd().Sphere(4.5), 16 * math.cos(ang), 16 * math.sin(ang), 30 - 24), "rubber"))
p1 = R.render_png(zp, 640, 520, camera={"dir": [0.8, -1.3, 0.5]}, section=((0, 0, 0), (0, -1, 0)),
                  labels=[{"at": (0, 0, 10), "text": "拉钉被钢球锁住拉下：定位并夹紧", "style": "text", "pos": [0.55, 0.92], "part": "拉钉"}])
pt = A("托盘")
pt.add(P("工作台（局部）", S.box(-220, 220, -170, 170, -60, -40), "steel_dark"))
for k, (sx, sy) in enumerate(((-120, -100), (120, -100), (-120, 100), (120, 100))):
    pt.add(P(f"零点卡盘{k}", E.zero_point_chuck(at=(sx, sy, 0), D=110, H=40), "steel_dark"))
    pt.add(P(f"拉钉{k}", S.move(E.pull_stud(at=(sx, sy, 0)), 0, 0, 90), "hardened"))
pt.add(P("托盘与夹具", S.box(-180, 180, -150, 150, 90, 120) + S.box(-60, 60, -40, 40, 120, 220), "steel"))
p2 = R.render_png(pt, 760, 520, camera={"dir": [0.9, -1.3, 0.55]})
R.compose("fig52_8_2", [p1, p2], 2, titles=["(a) 零点定位卡盘与拉钉（剖开）", "(b) 托盘底面的 4 个拉钉对准工作台上的 4 个卡盘落下"])

# ---- 图 52.8.3：平口钳上的 3D 打印仿形软爪：(a) 夹住异形件；(b) 把软爪拉开，看按工件形状打印出的型腔
def vise_odd(sep):
    v = MA.vise(opening=70.0)
    odd = (S.cyl("y", (0, -15), 30, -40, 40) & S.box(-34, 34, -45, 45, -45, 20)) + S.cyl("x", (-6, -12), 11, -38, 38)
    v.add(P("工件（异形件）", S.move(odd, 0, 0, 2.5 * sep), "work"))
    for sx in (-1, 1):
        jaw = S.box(min(sx * 22, sx * 35), max(sx * 22, sx * 35), -60, 60, -38, 0) - odd
        v.add(P(f"打印软爪{sx}", jaw, "#8fb0d8"))
    return v
pc = R.render_png(vise_odd(0), 700, 560, camera={"dir": [0.9, -1.3, 1.0]})
one = C.Assembly("软爪")
odd = (S.cyl("y", (0, -15), 30, -40, 40) & S.box(-34, 34, -45, 45, -45, 20)) + S.cyl("x", (-6, -12), 11, -38, 38)
one.add(P("打印软爪", S.box(22, 35, -60, 60, -38, 0) - odd, "#8fb0d8"))
one.add(P("钢制钳口板", S.box(35, 41, -60, 60, -38, 0), "hardened"))
pd = R.render_png(one, 700, 560, camera={"dir": [-1.0, -0.55, 0.35]},
                  labels=[{"at": (25, -6, -12), "text": "按工件形状打印的型腔（凸台的位置）", "style": "text", "pos": [0.5, 0.1], "part": "打印软爪"}])
R.compose("fig52_8_3", [pc, pd], 2, titles=["(a) 打印软爪夹住异形件（装在钢制钳口板上）", "(b) 一个软爪的工作面：按工件形状打印的型腔"])
out(n_fig3d=3)
