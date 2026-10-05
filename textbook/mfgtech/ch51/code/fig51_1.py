"""51.1 节的三维图：找正装夹与夹具装夹（图 51.1.1）、直接找正（图 51.1.2）、在机测量与机器人上下料（图 51.1.3）。
模型：factory/digital/models3d（JJ-301-50 与 SH-301 取自数字工厂的数据；四爪卡盘、划针盘、测头、手爪见 locating.py）。"""
import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
L = M.loc()
R = M.r3d()
A, P = C.Assembly, C.Part
g = J.geometry()

# ---- 图 51.1.1：(a) 四爪卡盘装大法兰毛坯，划针盘对着端面上划好的圆找正；(b) 夹具装夹：JJ-301-50 上一放、一靠、一压
fa = L.chuck4(D=320, grips=(118, 128, 122, 112))          # 四个爪各自调整，毛坯在卡盘上偏一点，逐爪敲正
flange = S.cyl("x", (4, -3), 150, 30, 70) + S.cyl("x", (4, -3), 100, 0, 30) - S.cyl("x", (4, -3), 55, -1, 71)
fa.add(P("法兰毛坯（铸件）", flange, "work"))
fa.add(P("划线（找正圆）", S.tube("x", (4, -3), 131, 130, 70, 70.6), "red"))
for q in L.surface_gauge(base_at=(150, -260, -170), tip=(71, -100, 80)).parts:
    fa.add(q)
fa.add(P("车床导轨（局部）", S.box(-60, 300, -320, -200, -200, -170), "steel_dark"))
pa = R.render_png(fa, 760, 580, camera={"dir": [1.0, -1.1, 0.55]},
                  labels=[{"at": (70.6, -3, 128), "text": "端面上预先划好的圆", "style": "text", "pos": [0.7, 0.08], "part": "划线"},
                          {"at": (71, -100, 80), "text": "划针对着划线，转动卡盘看偏多少", "style": "text", "pos": [0.5, 0.93], "part": "划针"},
                          {"at": (15, 0, 135), "text": "四个爪各自调整，逐爪敲正", "style": "text", "pos": [0.04, 0.08], "anchor": "start", "part": "卡爪1"}])
pb = R.render_png(J.assembly("op40"), 760, 580, camera={"dir": M.ISO},
                  labels=[{"at": (30, 0, g["zc"] + 20.15), "text": "一放：轴放进 V 形块", "style": "text", "pos": [0.55, 0.08], "part": "工件"},
                          {"at": (-3, -20, 40), "text": "一靠：轴肩靠住挡板", "style": "text", "pos": [0.03, 0.3], "anchor": "start", "part": "轴向挡板"},
                          {"at": (-20, 30, g["zc"] + 30), "text": "一压：拧紧压板", "style": "text", "pos": [0.2, 0.08], "part": "压板1"}])
R.compose("fig51_1_1", [pa, pb], 2, titles=["(a) 找正装夹：四爪卡盘装大法兰，按划线找正（约 20 min）", "(b) 夹具装夹：SH-301 放到键槽铣夹具上（十几秒）"])

# ---- 图 51.1.2：直接找正：四爪卡盘夹一件已车过外圆的套，千分表打外圆，调卡爪到跳动 0.01 mm 以内，再车内孔
fb = L.chuck4(D=200, grips=(40.6, 40, 39.4, 40))
sleeve = S.cyl("x", (0.6, 0), 40, 0, 70) - S.cyl("x", (0.6, 0), 22, -1, 71)
fb.add(P("套（外圆已车好，待车内孔）", sleeve, "work"))
for q in MA.dial_indicator(tip=(50, 0.6, 40), base_at=(140, 0.6, -60)).parts:
    fb.add(q)
fb.add(P("刀架（局部，表座吸在上面）", S.box(105, 175, -40, 40, -120, -60), "steel_dark"))
R.figure3d("fig51_1_2", fb, 1300, 800, camera={"dir": [0.85, -1.2, 0.6]},
           labels=[{"at": (50, 0.6, 40), "text": "千分表测杆压在已车好的外圆上", "style": "text", "pos": [0.62, 0.1], "part": "表头"},
                   {"at": (0, 0, 70), "text": "看表针，逐个调卡爪：跳动在 0.01 mm 以内再夹紧", "style": "text", "pos": [0.3, 0.92], "part": "卡爪1"}])

# ---- 图 51.1.3：(a) 加工中心用测头测出工件的实际位置，修正坐标系（“自动找正”）；(b) 机器人放料：定位销头部的导向锥面
fc = MA.vise(opening=80)
blk = S.box(-40, 40, -40, 40, 0, 50)
fc.add(P("工件（毛坯，位置每件不同）", S.rot(blk, 0, 0, 3, about=(0, 0, 0)), "work"))
for q in L.touch_probe(45, -12, 25).parts:
    fc.add(q)
pc = R.render_png(fc, 760, 580, camera={"dir": [0.9, -1.3, 0.85]},
                  arrows=[{"from": (80, -12, 28), "to": (48, -12, 28), "color": "#c0504d"}],
                  labels=[{"at": (45, -12, 28), "text": "测球碰到侧面：数控系统记下实际位置", "style": "text", "pos": [0.65, 0.1], "part": "测球"},
                          {"at": (-30, -38, 40), "text": "工件歪了一点也不用敲", "style": "text", "pos": [0.03, 0.9], "anchor": "start", "part": "工件"}])
fd = A("机器人放料")
fd.add(P("夹具底板", S.box(-120, 120, -80, 80, -20, 0), "cast"))
pins = ((-70, -35), (70, 35))
for k, (px, py) in enumerate(pins):
    fd.add(P(f"定位销{k + 1}", E.locating_pin(12, 14, "cyl" if k == 0 else "dia", at=(px, py, 0), flat_dir="x"), "hardened"))
plate = L.plate_with_holes(holes=pins, D=12.02, at=(1.5, -1.0, 22))      # 还没放到位：偏 1.5 mm，悬在销的上方
fd.add(P("工件（板）", plate, "work"))
for sx in (-1, 1):
    fd.add(P(f"手指{sx}", S.box(1.5 + sx * 101.5 + (0 if sx > 0 else -10), 1.5 + sx * 101.5 + (10 if sx > 0 else 0), -15, 15, 26, 72), "hardened"))
fd.add(P("手爪体", S.box(-123, 126, -20, 20, 72, 97) + S.cyl("z", (1.5, -1), 26, 97, 150), "steel"))
pd = R.render_png(fd, 760, 580, camera={"dir": [0.8, -1.3, 0.6]}, section=((0, -35, 0), (0, -1, 0)),
                  labels=[{"at": (-70, -35, 13), "text": "销头的导向锥面：工件偏 1–2 mm 也能滑进去", "style": "text", "pos": [0.03, 0.08], "anchor": "start", "part": "定位销1"},
                          {"at": (70, -35, 10), "text": "一个圆柱销、一个削边销", "style": "text", "pos": [0.75, 0.9], "part": "定位销2"}])
R.compose("fig51_1_3", [pc, pd], 2, titles=["(a) 加工中心：测头测出工件的实际位置，修正坐标系", "(b) 机器人放料：导向锥面把工件“引”到正确位置（过定位销剖开）"])
out(n_fig3d=3)
