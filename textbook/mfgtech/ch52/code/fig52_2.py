"""52.2 节的三维图：JJ-301-50 的夹紧点与受力（图 52.2.2）、辅助支承（图 52.2.3）、薄壁套的四种夹法（图 52.2.4）。"""
import math

import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
R = M.r3d()
g = J.geometry()
zc, Rg = g["zc"], 40.3 / 2

# ---- 图 52.2.2：夹紧点与受力。只留工件、V 形块、挡板、压板，其余半透明
a = J.assembly("op40")
keep = ("工件", "V 形块", "轴向挡板", "压板", "夹具体")
for p in a.parts:
    if not p.name.startswith(keep):
        p.opacity = 0.18
h = J.data()["clamping"]["strap"]["h"]
zl, zr = zc + 15.0, zc + 35.3 / 2
arrows = [{"from": (-20, 0, zl + h + 45), "to": (-20, 0, zl + h + 2), "color": "#c0504d", "text": "W（左压板）", "dx": 8},
          {"from": (80, 0, zr + h + 45), "to": (80, 0, zr + h + 2), "color": "#c0504d", "text": "W（右压板）", "dx": 8}]
s45 = math.sin(math.radians(45))
for xl in (9.0, 51.0):                       # 两段工作面的中点
    sy = -1                                  # 只画前面的一个工作面（后面的对称）
    cp = (xl, sy * Rg * s45, zc - Rg * s45)
    out_ = (xl, cp[1] + sy * 30 * s45, cp[2] - 30 * s45)
    arrows.append({"from": out_, "to": cp, "color": "#4f7fb8", "text": "N", "dx": -22, "dy": 8})
arrows.append({"from": (-45, -19, zc), "to": (-7, -19, zc), "color": "#4f7fb8", "text": "挡板反力", "dx": -10, "dy": -14})
k = W.plan()["part"]["keyway"]
xk = 52.0 + float(k["offset_mm"]) + g["work_x0"] + 10
arrows.append({"from": (xk + 40, 0, zc + 22), "to": (xk + 4, 0, zc + 22), "color": "#e0a030", "text": "轴向切削力（朝挡板）", "dx": 4, "dy": -18})
R.figure3d("fig52_2_2", a, 1400, 900, camera={"dir": [0.85, -1.35, 0.8], "fit": [[-90, -70, -35], [130, 70, 140]]}, arrows=arrows,
           labels=[{"at": (30, -12, zc + Rg - 0.5), "text": "键槽在齿轮位上母线（压板不能放这里）", "style": "text", "pos": [0.5, 0.06], "part": "工件"}]) 

# ---- 图 52.2.3：辅助支承。悬伸的板件：三个支承钉定位，压板压在支承上方；加工面在悬伸端，下面加弹簧自位式辅助支承
b = C.Assembly("辅助支承")
b.add(C.Part("夹具体", S.box(-40, 260, -60, 60, -30, 0), "cast"))
for x, y in ((0, -35), (0, 35), (110, 0)):
    b.add(C.Part(f"支承钉{x}{y}", E.support_pin("A", 16, 12, at=(x, y, 12)), "hardened"))
    b.add(C.Part(f"垫座{x}{y}", S.cyl("z", (x, y), 13, 0, 4), "cast"))
plate = S.box(-25, 240, -45, 45, 12, 30)
b.add(C.Part("工件（悬伸板）", plate, "work"))
b.add(C.Part("辅助支承座", S.box(192, 228, -18, 18, 0, 2), "cast"))
plunger = S.cyl("z", (210, 0), 8, 2, 12)
b.add(C.Part("辅助支承", plunger + S.cyl("z", (210, 0), 13, -2, 2), "blue"))
b.add(C.Part("锁紧螺钉", S.cyl("y", (210, 7), 3.5, -40, -10) + S.cyl("y", (210, 7), 6, -48, -40), "steel_dark"))
for x in (0, 110):
    b.add(C.Part(f"压板{x}", S.box(x - 12, x + 12, -20, 20, 30, 42), "steel"))
b.add(C.Part("面铣刀", S.cyl("z", (215, 0), 32, 30.2, 52) + S.cyl("z", (215, 0), 14, 52, 90), "tool", tags=("nocut",)))
R.figure3d("fig52_2_3", b, 1400, 820, camera={"dir": [0.5, -1.4, 0.45]}, section=((0, 0, 0), (0, -1, 0)),
           arrows=[{"from": (0, 0, 80), "to": (0, 0, 44), "color": "#c0504d", "text": "W"}, {"from": (110, 0, 80), "to": (110, 0, 44), "color": "#c0504d", "text": "W"},
                   {"from": (245, -60, 24), "to": (215, -30, 24), "color": "#e0a030", "text": "切削力", "dx": 6}],
           labels=[{"at": (110, 0, 6), "text": "支承钉（三个：左端前后各一、中间一个，前面一个已剖去）", "style": "text", "pos": [0.3, 0.88], "part": "支承钉"},
                   {"at": (210, 0, 7), "text": "辅助支承：定位、夹紧之后再顶上并锁紧", "style": "text", "pos": [0.66, 0.9], "part": "辅助支承"},
                   {"at": (215, 0, 70), "text": "加工面在悬伸端", "style": "text", "pos": [0.78, 0.12]}])

# ---- 图 52.2.4：薄壁套的四种夹法
ROUT, RIN, BW = 40.0, 36.0, 30.0
sleeve = lambda: S.tube("x", (0, 0), ROUT, RIN, 0, BW)  # noqa: E731
pngs = []
# (a) 三爪硬爪
ca = C.Assembly("a")
body = S.cyl("x", (0, 0), 85, -60, -2)
ca.add(C.Part("卡盘", body, "steel"))
for k in range(3):
    ca.add(C.Part(f"爪{k}", S.rot(S.box(-2, 26, -9, 9, ROUT, ROUT + 26), 120 * k, 0, 0), "hardened"))
ca.add(C.Part("薄壁套", sleeve(), "work"))
pngs.append(R.render_png(ca, 640, 520, camera={"dir": [1.3, -0.8, 0.6]}))
# (b) 扇形软爪（按工件外圆车出）
cb = C.Assembly("b")
cb.add(C.Part("卡盘", body, "steel"))
for k in range(3):
    arc = S.tube("x", (0, 0), ROUT + 16, ROUT, -2, 26) & S.prism("yz", [(0, 0), (120 * math.cos(math.radians(60)), 120 * math.sin(math.radians(60))),
                                                                        (-120 * math.cos(math.radians(60)), 120 * math.sin(math.radians(60)))], -3, 27)
    cb.add(C.Part(f"软爪{k}", S.rot(arc, 120 * k, 0, 0), "#c9b28a"))
cb.add(C.Part("薄壁套", sleeve(), "work"))
pngs.append(R.render_png(cb, 640, 520, camera={"dir": [1.3, -0.8, 0.6]}))
# (c) 开缝弹性套（整圈接触）
cc = C.Assembly("c")
cc.add(C.Part("卡盘", body, "steel"))
for k in range(3):
    cc.add(C.Part(f"爪{k}", S.rot(S.box(-2, 26, -9, 9, ROUT + 8, ROUT + 30), 120 * k, 0, 0), "hardened"))
split = S.tube("x", (0, 0), ROUT + 8, ROUT, -2, 26) - S.box(-3, 27, -1.5, 1.5, 0, 60)
cc.add(C.Part("开缝套", split, "#c9b28a"))
cc.add(C.Part("薄壁套", sleeve(), "work"))
pngs.append(R.render_png(cc, 640, 520, camera={"dir": [1.3, -0.8, 0.6]}))
# (d) 轴向压紧端面：工件端面靠在夹具端面上，压盖从另一端压
cd = C.Assembly("d")
cd.add(C.Part("夹具体（端面定位）", S.cyl("x", (0, 0), 60, -40, 0) + S.cyl("x", (0, 0), RIN - 0.2, 0, 8), "steel"))
cd.add(C.Part("薄壁套", sleeve(), "work"))
cd.add(C.Part("压盖", S.tube("x", (0, 0), ROUT + 2, 18, BW, BW + 10), "steel_dark"))
for k in range(3):
    ang = math.radians(90 + 120 * k)
    cd.add(C.Part(f"拉杆{k}", S.cyl("x", (24 * math.cos(ang), 24 * math.sin(ang)), 4, -30, BW + 14), "steel_dark"))
pngs.append(R.render_png(cd, 640, 520, camera={"dir": [1.3, -0.8, 0.6]}, arrows=[{"from": (BW + 50, 0, 46), "to": (BW + 12, 0, 46), "color": "#c0504d", "text": "轴向力", "dx": 4}]))
R.compose("fig52_2_4", pngs, 2, titles=["(a) 三个硬爪：三点集中受力，变形最大", "(b) 三个扇形软爪：接触面宽，变形小得多",
                                        "(c) 开缝弹性套：整圈接触，几乎只有均匀压缩", "(d) 改为轴向压紧端面：径向不受力"])
out(n_fig3d=3)
