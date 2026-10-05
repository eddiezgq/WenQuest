"""52.7 节的三维图：车床夹具（图 52.7.1）、铣床夹具（图 52.7.2）、五种钻模（图 52.7.3）、加工中心的立柱式多面夹具（图 52.7.4）。"""
import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
R = M.r3d()
A, P = C.Assembly, C.Part

# ---- 图 52.7.1：(a) 心轴；(b) 角铁式（带平衡块）；(c) 两顶尖 + 鸡心夹头（SH-301 工序 40）
p1 = R.render_png(TY.lathe_mandrel(), 600, 480, camera={"dir": [0.9, -1.2, 0.7]})
p2 = R.render_png(TY.lathe_angle_plate(), 600, 480, camera={"dir": [1.2, -1.0, 0.6]},
                  labels=[{"at": (45, -70, 95), "text": "平衡块", "style": "text", "pos": [0.8, 0.12], "part": "平衡块"},
                          {"at": (90, -40, -70), "text": "支架（一面两销定位）", "style": "text", "pos": [0.95, 0.88], "anchor": "end", "part": "工件"}])
lc = MA.lathe_centers(167.0, 0.0)
w = W.sh301("op40")
lc.add(w)
dog = S.tube("x", (0, 0), 26, 15, 12, 26) + S.box(12, 26, -6, 6, 24, 60) + S.cyl("z", (19, 4), 4, 26, 34)
lc.add(P("鸡心夹头", dog, "steel_dark"))
lc.add(P("拨盘拨杆", S.box(-60, -40, -6, 6, 40, 70) + S.box(-40, 20, -6, 6, 52, 64), "steel"))
p3 = R.render_png(lc, 900, 480, camera={"dir": [0.5, -1.3, 0.5]}, fontSize=24,
                  labels=[{"at": (19, -6, 45), "text": "鸡心夹头夹左轴端，拨盘带动", "style": "text", "pos": [0.03, 0.9], "anchor": "start", "part": "鸡心夹头"},
                          {"at": (180, -9, 0), "text": "后顶尖（尾座）", "style": "text", "pos": [0.97, 0.9], "anchor": "end", "part": "后顶尖"}])
R.compose("fig52_7_1", [p1, p2, p3], 3, titles=["(a) 心轴：以内孔和端面定位", "(b) 角铁式：对面装平衡块", "(c) 两顶尖与鸡心夹头（SH-301 精车）"])

# ---- 图 52.7.2：铣床夹具
q1 = R.render_png(TY.mill_multi(4), 700, 520, camera={"dir": [0.8, -1.3, 0.9]})
q2 = R.render_png(TY.mill_circular(6), 700, 520, camera={"dir": [0.8, -1.3, 0.9]},
                  labels=[{"at": (150, 0, 90), "text": "这个工位在铣削", "style": "text", "pos": [0.8, 0.12], "part": "铣刀"}])
R.compose("fig52_7_2", [q1, q2], 2, titles=["(a) 直线进给的多件铣夹具：一次装四件，联动夹紧", "(b) 圆周进给铣夹具：回转工作台上六个工位，边铣边装卸"])

# ---- 图 52.7.3：五种钻模
cams = {"dir": [0.9, -1.3, 0.9]}
d = [R.render_png(TY.drill_fixed(), 560, 460, camera=cams),
     R.render_png(TY.drill_indexing(6), 560, 460, camera={"dir": [-0.9, -1.3, 0.8]}),
     R.render_png(TY.drill_tumble(), 560, 460, camera={"dir": [0.7, -1.3, 0.9]}),
     R.render_png(TY.drill_cover(), 560, 460, camera=cams),
     R.render_png(TY.drill_column(1.0), 560, 460, camera=cams),
     R.render_png(TY.drill_column(0.0), 560, 460, camera=cams)]
R.compose("fig52_7_3", d, 3, titles=["(a) 固定式（钻杠杆小头孔）", "(b) 回转式（钻套筒的径向孔）", "(c) 翻转式（三个面上的孔）",
                                     "(d) 盖板式（法兰盘上 6 个孔）", "(e) 滑柱式：压下手柄，钻模板压紧工件", "(e′) 滑柱式：抬起钻模板，装卸工件"])

# ---- 图 52.7.4：加工中心的立柱式多面夹具（零点定位托盘，液压转角缸）
R.figure3d("fig52_7_4", TY.tombstone(2), 1200, 900, camera={"dir": [1.0, -1.2, 0.7]},
           labels=[{"at": (-100, -100, 0), "text": "零点定位卡盘（托盘快换）", "style": "text", "pos": [0.03, 0.92], "anchor": "start", "part": "零点卡盘"},
                   {"at": (112, 0, 120), "text": "液压转角缸", "style": "text", "pos": [0.85, 0.3], "part": "转角缸"}])
out(n_fig3d=4)
