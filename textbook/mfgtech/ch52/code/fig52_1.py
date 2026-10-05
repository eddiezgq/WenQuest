"""52.1 节的三维图：试制时平口钳找正与专用夹具（图 52.1.1）、通用夹具（图 52.1.2）、JJ-301-50 三维总成（图 52.1.3）、
按功能着色的爆炸图（图 52.1.4）、A–A 三维剖视（图 52.1.6）、夹具装在键槽铣床上（图 52.1.7）。
模型：factory/digital/models3d（夹具尺寸取自 std/JJ-301-50_fixture.yaml，工件取自 SH-301 工艺规程）。"""
import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
R = M.r3d()
g = J.geometry()

# ---- 图 52.1.1：(a) 平口钳装夹、千分表找正；(b) 专用夹具 JJ-301-50
v = MA.vise(opening=40.3)
w = W.sh301("op40")
w.shape = S.move(S.rot(S.move(w.shape, -82, 0, 0), 0, 0, 90), 0, 0, -22)     # 齿轮位夹在钳口里，轴线沿 y
v.add(w)
for p in MA.dial_indicator(tip=(0, 10, -22 + 20.15), base_at=(150, 30, -47)).parts:
    v.add(p)
v.add(C.Part("铣床工作台", S.box(-200, 260, -170, 170, -132, -102), "steel_dark"))
pa = R.render_png(v, 800, 560, camera={"dir": [1, -1.4, 0.9]},
                  labels=[{"at": (0, 10, -1.8), "text": "千分表打上母线找正", "style": "text", "pos": [0.55, 0.12]},
                          {"at": (-26, -40, -10), "text": "平口钳", "style": "text", "pos": [0.12, 0.8]}])
a = J.assembly("op40")
pb = R.render_png(a, 800, 560, camera={"dir": M.ISO},
                  labels=[{"at": (30, 0, g["zc"] + 20.15), "text": "工件放上就定好位", "style": "text", "pos": [0.5, 0.1]},
                          {"at": (-20, 30, g["zc"] + 15 + 14), "text": "两个压板压紧", "style": "text", "pos": [0.12, 0.2]}])
R.compose("fig52_1_1", [pa, pb], 2, titles=["(a) 试制：平口钳装夹，逐件找正（每件约 8 min）", "(b) 成批：专用夹具 JJ-301-50（每件装夹约 1.5 min）"])

# ---- 图 52.1.2：通用夹具
pngs = [R.render_png(MA.chuck3(), 640, 480, camera={"dir": [1.4, -0.9, 0.7]}),
        R.render_png(MA.vise(), 640, 480, camera={"dir": [1, -1.3, 0.9]}),
        R.render_png(MA.dividing_head(), 640, 480, camera={"dir": [1, -1.3, 0.8]}),
        R.render_png(MA.rotary_table(), 640, 480, camera={"dir": [1, -1.3, 1.0]})]
R.compose("fig52_1_2", pngs, 2, titles=["(a) 三爪自定心卡盘", "(b) 平口钳（机用虎钳）", "(c) 万能分度头", "(d) 回转工作台"])

# ---- 图 52.1.3：三维总成，零件序号（与明细栏一致）
zl, zr = g["zc"] + 15.0, g["zc"] + 35.3 / 2
h = J.data()["clamping"]["strap"]["h"]
labs = [(1, (-60, -45, 0)), (3, (25, -40, 22)), (4, (-3, -30, 55)), (5, (-20, 78, zl + h)), (6, (80, g["heel_y"], 45)),
        (7, (80, g["stud_y"], zr + h + 18)), (8, (-20, g["stud_y"] - 9, zl + h + 8)), (9, (88.5, g["stud_y"], 8)), (10, (148, g["setting_side"] + 16, 25)),
        (13, (J.BODY["x1"] + J.EAR - 8, 0, 4))]
asm = J.assembly("op40")
NAMES = {1: "夹具体", 3: "V 形块", 4: "轴向挡板", 5: "压板", 6: "可调支承", 7: "螺柱", 8: "垫圈螺母", 9: "弹簧", 10: "对刀块", 13: "螺母"}
R.figure3d("fig52_1_3", asm, 1400, 900, camera={"dir": M.ISO}, labels=[{"at": p, "text": str(n), "part": NAMES[n]} for n, p in labs]
           + [{"at": (30, 0, g["zc"] + 20.15), "text": "工件 SH-301（工序 50 前）", "style": "text", "pos": [0.5, 0.06]}])

# ---- 图 52.1.4：按功能着色的爆炸图
func = {1: "cast", 2: "green", 13: "green", 3: "blue", 4: "blue", 5: "steel", 6: "steel", 7: "steel", 8: "steel", 9: "steel", 10: "red"}
ex = J.assembly("op40")
for p in ex.parts:
    if p.number in func:
        p.color = func[p.number]
R.figure3d("fig52_1_4", ex, 1400, 1000, camera={"dir": M.ISO}, explode=1.0,
           texts=[{"pos": [0.04, 0.07], "text": "■ 定位元件（3 V 形块、4 挡板）", "color": "#4f7fb8"},
                  {"pos": [0.04, 0.115], "text": "■ 夹紧装置（5 压板、6 可调支承、7 螺柱、8 垫圈螺母、9 弹簧）", "color": "#7a868d"},
                  {"pos": [0.04, 0.16], "text": "■ 对刀元件（10 对刀块）", "color": "#c0504d"},
                  {"pos": [0.04, 0.205], "text": "■ 连接元件（2 定位键、13 T 形槽螺栓）", "color": "#5a9e6f"},
                  {"pos": [0.04, 0.25], "text": "■ 夹具体（1）", "color": "#9a8f78"}])

# ---- 图 52.1.6：过 V 形块中部的三维剖视（A–A）
sec = J.assembly("op40")
R.figure3d("fig52_1_6", sec, 1300, 900, camera={"dir": [1.25, -0.75, 0.55]}, section=((30, 0, 0), (1, 0, 0)),
           labels=[{"at": (30, 0, J.APEX + 1), "text": "V 形块理论顶点（两工作面交线）", "style": "text", "pos": [0.62, 0.55]},
                   {"at": (30, 0, g["zc"]), "text": "工件轴心", "style": "text", "pos": [0.62, 0.2]},
                   {"at": (30, 14.2, 34.2), "text": "工作面（90°）", "style": "text", "pos": [0.86, 0.42]}])

# ---- 图 52.1.7：装在键槽铣床工作台上：定位键嵌进 T 形槽，对刀块 + 3 mm 塞尺对刀
mt = J.assembly("op40", with_table=True, with_cutter=False)
cx = 144.0
top = g["setting_top"]
cut = S.cyl("z", (cx, 0), 6, top + 3, top + 40) - S.cbox(cx, 0, top + 16, 14, 2, 22) + S.cyl("z", (cx, 0), 6, top + 40, top + 75)
mt.add(C.Part("铣刀（对刀位置）", cut, "tool", tags=("nocut",)))
mt.add(C.Part("塞尺（端面）", S.box(cx - 20, cx + 20, -8, 6.5, top, top + 3), "#e8e2b0"))
mt.add(C.Part("塞尺（侧面）", S.box(cx - 20, cx + 20, 6, 9, top + 3.2, top + 30), "#e8e2b0"))
R.figure3d("fig52_1_7", mt, 1400, 900, camera={"dir": [1.0, -1.1, 0.7], "fit": [[-120, -100, -110], [200, 120, 120]]},
           labels=[{"at": (171, 0, -36), "text": "定位键（夹具体底面）嵌在 T 形槽里，两键靠同一侧", "style": "text", "pos": [0.66, 0.9]},
                   {"at": (cx, 0, top + 1.5), "text": "端面与对刀块底面之间塞 3 mm 塞尺：定槽深", "style": "text", "pos": [0.7, 0.12]},
                   {"at": (cx - 20, 7.5, top + 20), "text": "刀齿外缘与侧面之间塞 3 mm：定键槽中心", "style": "text", "pos": [0.7, 0.2]},
                   {"at": (-82, 0, 2), "text": "T 形槽螺栓压紧 U 形耳座", "style": "text", "pos": [0.12, 0.25]}])
out(n_fig3d=6)
