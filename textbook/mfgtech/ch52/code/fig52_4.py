"""52.4 节的三维图：斜楔夹紧（图 52.4.1）、四种螺旋夹紧（图 52.4.2）、圆偏心夹紧的松开与夹紧（图 52.4.4）、
铰链夹紧（图 52.4.5）、定心夹紧机构（图 52.4.6）、联动夹紧（图 52.4.7）。尺寸与本节算例一致（楔角 8°、M10 压板 l1 = 40、l2 = 50、
圆偏心 D = 40、e = 2），其余为示意。"""
import math

import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
R = M.r3d()
A = C.Assembly
P = C.Part
red, blue = "#c0504d", "#4f7fb8"

# ---- 图 52.4.1：斜楔夹紧（斜楔推动滑柱，滑柱上的压头压工件）
a = A("斜楔")
a.add(P("夹具体", S.box(-90, 90, -40, 40, -30, 0) + S.box(-90, -70, -40, 40, 0, 120) + S.box(-90, 90, -40, 40, 120, 140) - S.cyl("z", (20, 0), 12.5, 115, 141), "cast"))
a.add(P("工件", S.box(-40, 60, -30, 30, 0, 40), "work"))
alpha = 8.0
wy = 26.0
# 薄端在左、厚端在右：Q 从右向左推，斜楔向薄端方向移动，滑柱上方的楔越来越厚，把滑柱往下压（夹紧）；反向拉出即松开
t_a = math.tan(math.radians(alpha))
wedge = S.prism("xz", [(-60, 120), (100, 120), (100, 120 - 6 - 160 * t_a), (-60, 120 - 6)], -wy / 2, wy / 2)
z_under = 120 - 6 - (20 + 60) * t_a          # 滑柱处斜楔下表面的高度
a.add(P("斜楔", wedge, "hardened"))
plunger = S.cyl("z", (20, 0), 12, 40, z_under) + S.cyl("z", (20, 0), 16, 40, 46)
a.add(P("滑柱与压头", plunger, "steel"))
pa = R.render_png(a, 760, 600, camera={"dir": [0.6, -1.3, 0.5]},
                  arrows=[{"from": (150, 0, 108), "to": (102, 0, 108), "color": red, "text": "Q", "dx": 4, "dy": -10},
                          {"from": (20, -35, 75), "to": (20, -35, 42), "color": blue, "text": "W", "dx": 8}],
                  labels=[{"at": (40, -wy / 2, 108), "text": f"斜楔（楔角 α = {alpha:g}°）", "style": "text", "pos": [0.55, 0.12], "part": "斜楔"}])
# 斜楔—杠杆组合：气缸推斜楔，斜楔经滚子推杠杆
b = A("斜楔杠杆")
b.add(P("夹具体", S.box(-100, 120, -30, 30, -30, 0) + S.box(60, 80, -30, 30, 0, 90), "cast"))
b.add(P("工件", S.box(-90, 20, -25, 25, 0, 30), "work"))
lever = S.box(-60, 112, -10, 10, 40, 52) + S.cyl("y", (70, 46), 8, -14, 14)
b.add(P("杠杆", lever, "steel"))
b.add(P("压头", S.cyl("z", (-50, 0), 8, 30, 40), "steel"))
b.add(P("滚子", S.cyl("y", (102, 30), 9, -9, 9), "hardened"))
b.add(P("滚子叉架（固定在杠杆上）", S.box(94, 110, 9.5, 13, 24, 40) + S.box(94, 110, -13, -9.5, 24, 40) + S.cyl("y", (102, 30), 3, -14, 14), "steel"))
b.add(P("斜楔", S.prism("xz", [(85, 0), (180, 0), (180, 21), (115, 21)], -12, 12), "hardened"))
b.add(P("活塞杆", S.cyl("x", (0, 10), 6, 178, 205), "steel_dark"))
b.add(P("气缸", S.cyl("x", (0, 10), 26, 205, 285) + S.box(280, 290, -30, 30, -20, 40), "steel_dark"))
pb = R.render_png(b, 760, 600, camera={"dir": [0.6, -1.3, 0.55]},
                  arrows=[{"from": (-50, -40, 75), "to": (-50, -40, 42), "color": blue, "text": "W", "dx": 8}],
                  labels=[{"at": (140, -12, 12), "text": "斜楔（不要求自锁时 15°–30°）", "style": "text", "pos": [0.55, 0.88], "part": "斜楔"}])
R.compose("fig52_4_1", [pa, pb], 2, titles=["(a) 斜楔—滑柱：Q 推斜楔向薄端方向移动，滑柱压紧 W（手动楔角 6°–8°，能自锁）", "(b) 斜楔—杠杆：气缸推斜楔，经滚子推杠杆压紧"])

# ---- 图 52.4.2：四种螺旋夹紧
pngs = []
# (a) 螺钉 + 活动压块
c1 = A("螺钉压块")
c1.add(P("夹具体", S.box(-60, 60, -30, 30, -20, 0) + S.box(-60, -40, -30, 30, 0, 90) + S.box(-60, 60, -30, 30, 90, 110) - S.cyl("z", (10, 0), 6, 89, 111), "cast"))
c1.add(P("工件", S.box(-30, 50, -25, 25, 0, 40), "work"))
for n, s in E.swivel_screw_clamp(at=(10, 0, 40), d=12, L=78).items():
    c1.add(P(n, s, "steel" if n == "压块" else "steel_dark"))
pngs.append(R.render_png(c1, 640, 520, camera={"dir": [0.8, -1.3, 0.6]}, labels=[{"at": (10, -12, 43), "text": "活动压块：不拧动工件", "style": "text", "pos": [0.6, 0.85], "part": "压块"}]))
# (b) 移动压板（JJ-301-50 的件 5）：l1 = 40、l2 = 50
c2 = A("移动压板")
c2.add(P("夹具体", S.box(-40, 140, -40, 40, -25, 0) + S.box(80, 110, -20, 20, 0, 34), "cast"))
c2.add(P("工件", S.box(-30, 20, -30, 30, 0, 40), "work"))
c2.add(P("压板", S.box(-10, 105, -16, 16, 40, 54) - S.cbox(45, 0, 47, 22, 11, 16), "steel"))
c2.add(P("螺柱", S.cyl("z", (40, 0), 5, -10, 72), "steel_dark"))
c2.add(P("螺母", S.cyl("z", (40, 0), 10, 54, 58) + S.hexagon("z", (40, 0), 16, 58, 66), "steel_dark"))
c2.add(P("可调支承", S.cyl("z", (90, 0), 5, 34, 40), "steel_dark"))
pngs.append(R.render_png(c2, 640, 520, camera={"dir": [0.3, -1.4, 0.45]},
                         dims=[{"a": (0, -16, 54), "b": (40, -16, 54), "off": (0, 0, 22), "text": "l₁ = 40"},
                               {"a": (40, -16, 54), "b": (90, -16, 54), "off": (0, 0, 22), "text": "l₂ = 50"}],
                         arrows=[{"from": (0, -35, 80), "to": (0, -35, 42), "color": blue, "text": "W（压工件）", "dx": -100}]))
# (c) 回转压板：压板绕螺柱转开，让出装卸空间
c3 = A("回转压板")
c3.add(P("夹具体", S.box(-60, 80, -50, 50, -25, 0), "cast"))
c3.add(P("工件", S.cyl("z", (0, 0), 30, 0, 40), "work"))
c3.add(P("支柱", S.cyl("z", (55, 0), 9, 0, 40), "steel"))
c3.add(P("压板（夹紧位置）", S.box(-10, 70, -12, 12, 40, 52) - S.cyl("z", (55, 0), 6, 39, 53), "steel"))
c3.add(P("压板（转开位置）", S.rot(S.box(-10, 70, -12, 12, 40, 52) - S.cyl("z", (55, 0), 6, 39, 53), 0, 0, 75, about=(55, 0, 0)), "steel", opacity=0.3))
c3.add(P("螺母", S.hexagon("z", (55, 0), 16, 52, 60) + S.cyl("z", (55, 0), 5, 0, 66), "steel_dark"))
pngs.append(R.render_png(c3, 640, 520, camera={"dir": [0.8, -1.3, 0.9]}))
# (d) 钩形压板
c4 = A("钩形压板")
c4.add(P("夹具体", S.box(-60, 80, -50, 50, -25, 0), "cast"))
c4.add(P("工件", S.tube("z", (0, 0), 30, 18, 0, 40), "work"))
c4.add(P("导套", S.tube("z", (45, 0), 15, 9.2, 0, 30), "cast"))
# 钩形压板：立柱在导套里可以转动和上下移动，横臂末端向下伸出钩头压在工件端面上；拧螺母把钩头往下拉
c4.add(P("钩形压板", S.cyl("z", (45, 0), 9, -20, 62) + S.box(12, 55, -10, 10, 46, 58) + S.box(12, 26, -10, 10, 40, 46), "steel"))
c4.add(P("螺母", S.hexagon("z", (45, 0), 16, 58, 66) + S.cyl("z", (45, 0), 5, 58, 72), "steel_dark"))
pngs.append(R.render_png(c4, 640, 520, camera={"dir": [0.8, -1.3, 0.8]}))
R.compose("fig52_4_2", pngs, 2, titles=["(a) 螺钉与活动压块", "(b) 移动压板（JJ-301-50 的件 5）", "(c) 回转压板：压板转开让出装卸空间（浅色为转开位置）", "(d) 钩形压板：钩头转开即可取件"])

# ---- 图 52.4.4：圆偏心夹紧（D = 40、e = 2、手柄 100）
def ecc(angle):
    """圆偏心—压板：压板右端铰在立柱上（支点 x = 55），偏心轮压压板左端（x = −60），压头在中间（x = −20）压工件；
    偏心轮的转轴装在夹具体上的两个支架里（工件两侧）。夹紧时（angle 0）偏心轮最低点正好贴住压板。"""
    q = A("偏心")
    zs, zt = 82.0, 60.0                         # 偏心轮转轴高度、压板顶面高度：zs − e − D/2 = zt
    q.add(P("夹具体", S.box(-90, 80, -30, 30, -25, 0) + S.box(45, 65, -14, 14, 0, 66), "cast"))
    q.add(P("工件", S.box(-40, 0, -12, 12, 0, 30), "work"))
    q.add(P("压板", S.box(-75, 62, -10, 10, 48, zt), "steel"))
    q.add(P("压头", S.cyl("z", (-20, 0), 7, 30, 48), "steel"))
    q.add(P("压板铰销", S.cyl("y", (55, 54), 4, -16, 16), "steel_dark"))
    q.add(P("偏心轮", E.eccentric(at=(-60, 0, zs), D=40, e=2, B=16, handle=80, angle_deg=angle), "hardened"))
    q.add(P("偏心轮支架（后）", S.box(-70, -50, 12, 22, 0, zs + 10) - S.cyl("y", (-60, zs), 4, 11, 23), "cast"))
    q.add(P("偏心轮支架（前，半透明画出）", S.box(-70, -50, -22, -12, 0, zs + 10) - S.cyl("y", (-60, zs), 4, -23, -11), "cast", opacity=0.3))
    q.add(P("转轴", S.cyl("y", (-60, zs), 4, -24, 24), "steel_dark"))
    return q
ec_cam = {"dir": [0.25, -1.4, 0.35], "fit": [[-170, -30, -25], [80, 30, 180]]}
pe = [R.render_png(ecc(-120), 640, 520, camera=ec_cam), R.render_png(ecc(0), 640, 520, camera=ec_cam)]
R.compose("fig52_4_4", pe, 2, titles=["(a) 松开：手柄抬起，偏心轮离开压板（间隙约 3 mm）", "(b) 夹紧：扳下手柄，偏心轮压下压板左端，压头压紧工件"])

# ---- 图 52.4.5：铰链夹紧（气缸 + 单臂铰链 + 杠杆）与快速夹钳
h = A("铰链")
# 单臂铰链：杠杆支点在 x = 20；右端销 B(95, 76) 接连杆；连杆下端 C 由水平气缸沿 −x 推动，在导轨上滑动；
# C 从右边推向 B 的正下方，连杆越来越接近竖直，把杠杆右端往上顶的力越来越大，杠杆左端的压头向下压紧工件
zp, xB, zC = 76.0, 95.0, 26.0
xC = xB + 8.0                                  # 夹紧位置：连杆离竖直还差约 9°（不越过死点）
h.add(P("夹具体", S.box(-120, 240, -30, 30, -25, 0) + S.box(10, 30, -30, 30, 0, zp) + S.box(80, 240, -30, 30, 0, zC - 8), "cast"))
h.add(P("工件", S.box(-110, -20, -25, 25, 0, 30), "work"))
lev = S.box(-80, 100, -8, 8, zp - 6, zp + 6)
h.add(P("杠杆", lev, "steel"))
h.add(P("支点销与销", S.cyl("y", (20, zp), 5, -14, 14) + S.cyl("y", (xB, zp), 4, -12, 12) + S.cyl("y", (xC, zC), 4, -12, 12), "steel_dark"))
h.add(P("压头", S.cyl("z", (-70, 0), 7, 30, zp - 6), "steel"))
L_link = math.hypot(xC - xB, zp - zC)
ux, uz = (xB - xC) / L_link, (zp - zC) / L_link
nx, nz = -uz * 6, ux * 6
h.add(P("连杆", S.prism("xz", [(xC + nx, zC + nz), (xB + nx, zp + nz), (xB - nx, zp - nz), (xC - nx, zC - nz)], -5, 5), "hardened"))
h.add(P("滑块", S.box(xC - 10, xC + 14, -12, 12, zC - 8, zC + 8), "steel"))
h.add(P("气缸缸体", S.rot(E.cylinder_pneu(50, 40, at=(170, 0, zC), axis="x")["缸体"], 0, 0, 180, about=(170, 0, zC)), "steel_dark"))
h.add(P("活塞杆（推向 −x）", S.cyl("x", (0, zC), 9, xC + 14, 170), "steel_dark"))
ph = R.render_png(h, 760, 600, camera={"dir": [0.4, -1.4, 0.5]},
                  arrows=[{"from": (-70, -40, 62), "to": (-70, -40, 34), "color": blue, "text": "W", "dx": 8},
                          {"from": (165, -40, zC + 14), "to": (125, -40, zC + 14), "color": red, "text": "气缸推力", "textAt": "end", "dx": -10, "dy": -12}],
                  labels=[{"at": (99, -5, 51), "text": "连杆接近竖直：增力最大", "style": "text", "pos": [0.7, 0.12], "part": "连杆"},
                          {"at": (20, -14, zp), "text": "杠杆支点", "style": "text", "pos": [0.4, 0.1]}])
tg = A("快速夹钳")
tg.add(P("底板", S.box(-90, 90, -40, 40, -15, 0), "cast"))
tg.add(P("工件", S.box(20, 90, -30, 30, 0, 25), "work"))
for n, s in E.toggle_clamp(at=(-10, 0, 0)).items():
    tg.add(P(n, S.move(s, 0, 0, 0), "steel_dark" if n != "手柄" else red))
pt = R.render_png(tg, 760, 600, camera={"dir": [0.4, -1.4, 0.6]})
R.compose("fig52_4_5", [ph, pt], 2, titles=["(a) 气动单臂铰链夹紧：连杆越接近竖直，增力越大", "(b) 快速夹钳：压杆越过死点后锁住"])

# ---- 图 52.4.6：定心夹紧机构
cpngs = [R.render_png(MA.chuck3(160, 40), 640, 520, camera={"dir": [1.4, -0.9, 0.7]})]
cl = A("弹簧夹头")
cl.add(P("主轴端（锥孔）", S.cyl("x", (0, 0), 45, -90, 0) - S.revolve([(-91, 0), (-91, 25), (-18, 25), (-6, 32), (1, 32), (1, 0)], "x", (0, 0)), "steel"))
cl.add(P("弹簧夹头", E.collet(30, 70, at=(0, 0, 0)), "hardened"))
cl.add(P("工件", S.cyl("x", (0, 0), 15, -60, 60), "work"))
cpngs.append(R.render_png(cl, 640, 520, camera={"dir": [0.9, -1.1, 0.8]}, section=((0, 0, 0), (0, -1, 0))))
md = A("胀胎心轴")
md.add(P("心轴体", S.cyl("x", (0, 0), 14, -80, 80) + S.cyl("x", (0, 0), 30, -80, -60), "steel"))
md.add(P("薄壁胀套", S.tube("x", (0, 0), 20, 14, -50, 50), "hardened"))
md.add(P("液性塑料", S.tube("x", (0, 0), 17.5, 14, -40, 40), "#7fb07f"))
md.add(P("工件（薄壁套）", S.tube("x", (0, 0), 30, 20, -45, 45), "work"))
md.add(P("加压螺钉", S.cyl("z", (-70, 0), 4, 0, 35) + S.hexagon("z", (-70, 0), 12, 35, 42), "steel_dark"))
cpngs.append(R.render_png(md, 640, 520, camera={"dir": [0.9, -1.1, 0.8]}, section=((0, 0, 0), (0, -1, 0))))
sv = A("对称钳口")
sv.add(P("钳体", S.box(-120, 120, -40, 40, -40, 0), "cast"))
sv.add(P("双向螺杆", S.cyl("x", (0, -25), 8, -130, 130) + S.cyl("x", (0, -25), 14, 130, 140), "steel_dark"))
for sx in (-1, 1):
    v0 = sx * 20 / math.sin(math.radians(45))        # V 的顶点（两工作面交线）离中心 r/sin45°
    jaw = S.box(min(sx * 10, sx * 60), max(sx * 10, sx * 60), -30, 30, 0, 40) - S.prism("xz", [(v0, 20), (v0 - sx * 60, 80), (v0 - sx * 60, -40)], -31, 31)
    sv.add(P(f"V形钳口{sx}", jaw, "hardened"))
sv.add(P("工件", S.cyl("y", (0, 20), 20, -45, 45), "work"))
cpngs.append(R.render_png(sv, 640, 520, camera={"dir": [0.6, -1.3, 0.8]}))
R.compose("fig52_4_6", cpngs, 2, titles=["(a) 三爪自定心卡盘", "(b) 弹簧夹头（剖开）：拉进锥孔后收缩", "(c) 液性塑料胀胎心轴（剖开）：薄壁套均匀胀开", "(d) 双向螺杆带动两个 V 形钳口对称移动"])

# ---- 图 52.4.7：联动夹紧
pm = R.render_png(TY.mill_multi(4), 760, 600, camera={"dir": [0.8, -1.3, 0.9]},
                  labels=[{"at": (25, 0, 33), "text": "浮动压块：一块压两根", "style": "text", "pos": [0.45, 0.1], "part": "浮动压块"},
                          {"at": (75, -14, -64), "text": "平衡杠杆把一个螺母的力平分给两根拉杆", "style": "text", "pos": [0.5, 0.92], "part": "平衡杠杆"}])
fl = A("浮动压板")
fl.add(P("夹具体", S.box(-110, 110, -40, 40, -25, 0) + S.box(-15, 15, 20, 40, 0, 110) + S.box(-15, 15, -20, 40, 110, 125), "cast"))
fl.add(P("工件 1", S.box(-95, -25, -25, 25, 0, 40), "work"))
fl.add(P("工件 2（高 1 mm）", S.box(25, 95, -25, 25, 0, 41), "work"))
fl.add(P("浮动压板", S.rot(S.box(-80, 80, -12, 12, 50, 62), 0, -0.7, 0, about=(0, 0, 56)) + S.cyl("z", (-60, 0), 6, 40, 50) + S.cyl("z", (60, 0), 6, 41, 50), "steel"))
fl.add(P("螺钉", S.cyl("z", (0, 0), 6, 62, 125) + S.cyl("z", (0, 0), 10, 125, 135) + S.cyl("x", (0, 132), 3, -30, 30), "steel_dark"))
pl = R.render_png(fl, 760, 600, camera={"dir": [0.3, -1.4, 0.5]},
                  arrows=[{"from": (-60, -40, 85), "to": (-60, -40, 52), "color": blue, "text": "W/2", "dx": 6}, {"from": (60, -40, 85), "to": (60, -40, 52), "color": blue, "text": "W/2", "dx": 6}],
                  labels=[{"at": (0, -12, 56), "text": "浮动压板可以摆动，两件高低不同也都压得到", "style": "text", "pos": [0.5, 0.08], "part": "浮动压板"}])
R.compose("fig52_4_7", [pm, pl], 2, titles=["(a) 多件联动：一个螺母压紧四根小轴", "(b) 浮动压板：一个螺钉同时压紧两个工件"])
out(n_fig3d=6)
