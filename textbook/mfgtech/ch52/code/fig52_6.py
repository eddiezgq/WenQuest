"""52.6 节的三维图：对刀块的四种形式（图 52.6.1）、定位键与 T 形槽（图 52.6.2）、四种钻套（图 52.6.3，剖开）、
箱体端面螺孔的盖板式钻模（图 52.6.5）、镗套与镗模（图 52.6.6）、分度装置（图 52.6.7）。"""
import math

import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
R = M.r3d()
A, P = C.Assembly, C.Part
red, blue = "#c0504d", "#4f7fb8"
feel = "#e8e2b0"

# ---- 图 52.6.1：对刀块（铣刀与塞尺在对刀位置）
def sb(kind):
    q = A(kind)
    q.add(P("夹具体（局部）", S.box(-30, 30, -30, 40, -36, -30), "cast"))
    if kind == "round":
        q.add(P("对刀块", E.setting_block("round", at=(0, -10, -12), size=20) + S.box(-12, 12, -10, 10, -30, -24), "hardened"))
        q.add(P("塞尺", S.box(-14, 14, -8, 8, -12, -9), feel))
        q.add(P("铣刀（圆柱铣刀端面局部）", S.cyl("z", (0, 0), 18, -9, 10), "tool"))
    elif kind == "square":
        q.add(P("对刀块", E.setting_block("square", at=(0, 0, -12), size=20), "hardened"))
        q.add(P("塞尺（顶面）", S.box(-12, 12, 0, 20, -12, -9), feel))
        q.add(P("塞尺（侧面）", S.box(-12, 12, -3, 0, -26, -9), feel))
        q.add(P("铣刀（三面刃局部）", S.cyl("y", (0, -9), 22, -40, -3) & S.box(-30, 30, -45, -3, -9, 40), "tool"))
    elif kind == "angle":
        q.add(P("对刀块", E.setting_block("angle", at=(0, 0, -12), size=20), "hardened"))
        q.add(P("塞尺（底面）", S.box(-12, 12, -16, -3, -12, -9), feel))
        q.add(P("塞尺（侧面）", S.box(-12, 12, -3, 0, -9, 4), feel))
        q.add(P("键槽铣刀", S.cyl("z", (0, -9), 6, -9, 40) - S.cbox(0, -9, 10, 14, 2, 20), "tool"))
    else:
        q.add(P("对刀块", E.setting_block("side", at=(0, 0, -6), size=20), "hardened"))
        q.add(P("塞尺", S.box(-12, 12, -3, 0, -30, -4), feel))
        q.add(P("铣刀（侧刃局部）", S.cyl("z", (0, -15), 12, -40, 10), "tool"))
    return q
cam = {"dir": [0.9, -1.2, 0.8]}
R.compose("fig52_6_1", [R.render_png(sb(k), 600, 480, camera=cam) for k in ("round", "square", "angle", "side")], 2,
          titles=["(a) 圆形对刀块：只对高度", "(b) 方形对刀块：对高度和一个侧面", "(c) 直角对刀块（内直角）：铣刀放进内角，两个方向一次对好", "(d) 侧装对刀块：只对侧面"])

# ---- 图 52.6.2：定位键在 T 形槽里（剖开）：(a) 居中，两侧都有间隙；(b) 两键推向同一侧
def key(shift):
    q = A("定位键")
    q.add(P("工作台（局部）", S.box(-60, 60, -60, 60, -40, 0) - S.box(-61, 61, -10.5, 10.5, -18, 1) - S.box(-61, 61, -16, 16, -32, -18), "steel_dark"))
    q.add(P("夹具体（局部）", S.box(-60, 60, -60, 60, 0, 25) - S.box(-15, 15, -9.0, 9.0, -1, 6), "cast"))
    q.add(P("定位键 18 h8", S.box(-12, 12, -8.98 + shift, 8.98 + shift, -8, 6) - S.cyl("z", (0, shift), 3.4, -9, 7), "green"))
    return q
kc = {"dir": [-1.0, -0.35, 0.25], "fit": [[0, -32, -36], [0, 32, 26]]}
R.compose("fig52_6_2", [R.render_png(key(0.0), 640, 480, camera=kc, section=((0, 0, 0), (-1, 0, 0))),
                        R.render_png(key(-1.52), 640, 480, camera=kc, section=((0, 0, 0), (-1, 0, 0)))], 2,
          titles=["(a) 键在槽中间：两侧都有间隙（放大画出），夹具可以转一个小角度", "(b) 两个键都推向槽的同一侧再拧紧"])

# ---- 图 52.6.3：钻套（沿轴线剖开）
def bush(kind):
    q = A(kind)
    q.add(P("钻模板", S.box(-40, 40, -40, 40, -22, 0) - S.cyl("z", (0, 0), 12 if kind == "fixed" else 15.1, -23, 1), "steel"))
    if kind == "special":
        q.parts.clear()
        q.add(P("钻模板", S.box(-40, 40, -40, 40, -22, 0) - S.cyl("z", (0, 0), 12, -23, 1), "steel"))
        q.add(P("工件（斜面）", S.rot(S.box(-60, 60, -50, 50, -80, -40), 0, 25, 0, about=(0, 0, -40)), "work"))
        q.add(P("加长钻套（下端按斜面切斜）", (S.tube("z", (0, 0), 12, 5, -50, 0) + S.tube("z", (0, 0), 15, 5, 0, 4))
                - S.rot(S.box(-30, 30, -30, 30, -80, -40), 0, 25, 0, about=(0, 0, -40)), "hardened"))
        return q
    for n, s in E.drill_bushing(kind, d=10, D=24 if kind == "fixed" else 24, H=22, at=(0, 0, 0)).items():
        q.add(P(n, s, "hardened" if n == "钻套" else ("steel" if n == "衬套" else "steel_dark")))
    return q
bc = {"dir": [0.7, -1.2, 0.8]}
R.compose("fig52_6_3", [R.render_png(bush(k), 600, 480, camera=bc, section=((0, 0, 0), (0, -1, 0))) for k in ("fixed", "renew", "quick", "special")], 2,
          titles=["(a) 固定钻套：直接压入钻模板", "(b) 可换钻套：装在衬套里，螺钉压住防转", "(c) 快换钻套：台肩开缺口，转开即可取出", "(d) 特殊钻套：在斜面上钻孔，加长并切斜"])

# ---- 图 52.6.5：箱体端面 4×M8 螺孔的盖板式钻模（合箱后的箱体组件，简化）
bx = A("盖板式钻模")
box = S.box(-100, 100, -70, 70, 0, 160) - S.box(-88, 88, -58, 58, 12, 150)
box = box + S.cyl("y", (0, 90), 52, -76, -58) - S.cyl("y", (0, 90), 36, -90, -40)
bx.add(P("箱体组件 SA-000（箱座 + 箱盖，简化）", box, "work"))
plate = S.cyl("y", (0, 90), 62, -94, -76) + S.box(-62, 62, -94, -76, 0, 90)
holes = [(45 * math.cos(math.radians(45 + 90 * k)), 90 + 45 * math.sin(math.radians(45 + 90 * k))) for k in range(4)]
for hx, hz in holes:
    plate = plate - S.cyl("y", (hx, hz), 6, -95, -75)
bx.add(P("钻模板", plate, "steel"))
bx.add(P("短圆柱销 Ø72 g6", S.cyl("y", (0, 90), 35.99, -76, -64), "hardened"))
for k, (hx, hz) in enumerate(holes):
    bx.add(P(f"钻套{k + 1}", S.tube("y", (hx, hz), 6, 3.4, -94, -82) + S.tube("y", (hx, hz), 8, 3.4, -98, -94), "hardened"))
for sx in (-45, 45):
    bx.add(P(f"支承钉{sx}", S.cyl("y", (sx, -4), 5, -94, -70) + S.box(sx - 8, sx + 8, -94, -84, -6, 8), "hardened"))
R.figure3d("fig52_6_5", bx, 1300, 900, camera={"dir": [0.9, -1.4, 0.55]},
           labels=[{"at": (0, -94, 30), "text": "钻模板以轴承孔（短销）和端面定位", "style": "text", "pos": [0.04, 0.08], "anchor": "start", "part": "钻模板"},
                   {"at": (45, -98, -2), "text": "两个支承钉靠箱座底面防转", "style": "text", "pos": [0.68, 0.9], "part": "支承钉"},
                   {"at": (holes[0][0], -98, holes[0][1] + 7), "text": "4 个固定钻套（Ø6.8 F7）", "style": "text", "pos": [0.72, 0.12], "part": "钻套"}])

# ---- 图 52.6.6：(a) 固定镗套与回转镗套（剖开）；(b) 双面导向的镗模
bb = A("镗套")
bb.add(P("镗模支架（局部）", S.box(-40, 40, -12, 12, 0, 90) - S.cyl("y", (-0, 45), 27, -13, 13), "cast"))
bb.add(P("回转镗套（装在滚动轴承里）", S.tube("y", (0, 45), 26.9, 16, -12, 12), "steel"))
bb.add(P("滚动轴承（示意）", S.tube("y", (0, 45), 26.9, 22, -10, 10), "rubber"))
bb.add(P("内套", S.tube("y", (0, 45), 21.9, 16, -16, 16), "hardened"))
bb.add(P("镗杆", S.cyl("y", (0, 45), 15.9, -70, 70), "tool"))
fb = A("固定镗套")
fb.add(P("镗模支架（局部）", S.box(-40, 40, -12, 12, 0, 90) - S.cyl("y", (0, 45), 22, -13, 13), "cast"))
fb.add(P("固定镗套", S.tube("y", (0, 45), 22, 16, -12, 12) + S.tube("y", (0, 45), 28, 16, -18, -12), "hardened"))
fb.add(P("镗杆", S.cyl("y", (0, 45), 15.95, -70, 70), "tool"))
p1 = R.render_png(fb, 520, 440, camera={"dir": [1.0, -0.9, 0.6]}, section=((0, 0, 0), (1, 0, 0)))
p2 = R.render_png(bb, 520, 440, camera={"dir": [1.0, -0.9, 0.6]}, section=((0, 0, 0), (1, 0, 0)))
p3 = R.render_png(TY.boring_jig(), 720, 520, camera={"dir": [0.9, -1.3, 0.8]})
R.compose("fig52_6_6", [p1, p2, p3], 3, titles=["(a) 固定镗套（剖开）", "(b) 回转镗套（剖开）：套随镗杆转", "(c) 双面导向的镗模：孔的位置由镗套决定"])

# ---- 图 52.6.7：分度装置：(a) 回转式钻模的分度盘与对定销；(b) 圆锥对定销（剖开）消除间隙
pa = R.render_png(TY.drill_indexing(6), 760, 560, camera={"dir": [-1.0, -1.2, 0.7]},
                  labels=[{"at": (-87, -10, 80 + 48), "text": "对定销插在分度孔里", "style": "text", "pos": [0.04, 0.08], "anchor": "start", "part": "对定销"},
                          {"at": (-94, -40, 80), "text": "分度盘（6 个分度孔）", "style": "text", "pos": [0.04, 0.9], "anchor": "start", "part": "分度盘"}])
cp = A("圆锥对定销")
cp.add(P("分度盘（局部）", S.box(-30, 30, -20, 20, -14, 0) - S.revolve([(-15, 0), (-15, 4), (1, 6.5), (1, 0)], "z", (0, 0)), "steel"))
cp.add(P("对定销导套", S.box(-25, 25, -20, 20, 4, 40) - S.cyl("z", (0, 0), 7.05, 3, 41), "cast"))
cp.add(P("圆锥对定销", S.revolve([(-14, 0), (-14, 3.8), (0, 6.3), (2, 7), (40, 7), (40, 0)], "z", (0, 0)) + S.cyl("z", (0, 0), 10, 40, 48), "hardened"))
cp.add(P("拉钮", S.cyl("z", (0, 0), 12, 48, 58), "steel_dark"))
pb = R.render_png(cp, 560, 560, camera={"dir": [0.9, -1.2, 0.5]}, section=((0, 0, 0), (0, -1, 0)))
R.compose("fig52_6_7", [pa, pb], 2, titles=["(a) 回转式钻模：拔出对定销、转 60°、插入，钻下一个孔", "(b) 圆锥对定销（剖开）：锥面插紧，消除间隙"])
out(n_fig3d=6)
