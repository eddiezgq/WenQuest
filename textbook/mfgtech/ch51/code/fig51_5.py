"""51.5 节的三维图：平面定位元件（图 51.5.2）、外圆定位元件（图 51.5.3）、内孔定位元件（图 51.5.4）、中心孔与组合表面定位（图 51.5.5）。
结构按夹具标准件（JB/T 8004–8045 系列）的典型形式简化，尺寸示意；模型：factory/digital/models3d（elements.py、locating.py、machines.py）。"""
import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
L = M.loc()
R = M.r3d()
A, P = C.Assembly, C.Part
blue = "#4f7fb8"


def tile(parts, cam, w=520, h=420, section=None, **kw):
    q = A("t")
    for n, s, c, *op in parts:
        q.add(P(n, s, c, opacity=op[0] if op else 1.0))
    return R.render_png(q, w, h, camera={"dir": cam}, section=section, **kw)


base = lambda: S.box(-40, 40, -30, 30, -26, -12)  # noqa: E731
# ---- 图 51.5.2：平面定位
sa = tile([("A 型", E.support_pin("A", 16, 10, at=(-25, 0, 0)), "hardened"), ("B 型", E.support_pin("B", 16, 10, at=(0, 0, 0)), "hardened"),
           ("C 型", E.support_pin("C", 16, 10, at=(25, 0, 0)), "hardened")], [0.8, -1.3, 0.9])
sp = tile([("A 型支承板", E.support_plate(90, 18, 12, "A", at=(0, -16, 0), n=3), "hardened"), ("B 型支承板", E.support_plate(90, 18, 12, "B", at=(0, 16, 0), n=3), "hardened")],
          [0.8, -1.3, 1.0])
adj = tile([("可调支承", E.adjustable_support(16, at=(0, 0, 0), H=40), "steel_dark"), ("支座", S.box(-25, 25, -25, 25, -50, -24) - S.cyl("z", (0, 0), 8, -51, -23), "cast"),
            ("毛坯（局部）", S.box(-40, 40, -30, 30, 0, 14), "work", 0.45)], [0.8, -1.3, 0.6])
sas = L.self_aligning_support(at=(0, 0, 0), span=40)
sa2 = tile([("摆块", sas["摆块"], blue), ("支座", sas["支座"], "cast"), ("销", sas["销"], "steel_dark"),
            ("工件（不平的毛坯面，局部）", S.rot(S.box(-45, 45, -25, 25, 0, 12), 0, -3, 0), "work", 0.45)], [0.6, -1.3, 0.5])
aux = E.auxiliary_support(16, at=(0, 0, 0))
ax_ = tile([("支座", aux["body"], "cast"), ("柱塞", aux["plunger"], blue), ("锁紧螺钉", aux["lock"], "steel_dark")], [0.8, -1.2, 0.6], section=((0, 0, 0), (0, -1, 0)))
R.compose("fig51_5_2", [sa, sp, adj, sa2, ax_], 3, titles=["(a) 支承钉：A 平头（精基准）、B 球头（毛坯面）、C 网纹（侧面）", "(b) 支承板：A 型光面、B 型斜槽（容屑）",
                                                          "(c) 可调支承：按批调高度，锁紧螺母锁住", "(d) 自位支承：两点接触，只起一个支承点的作用",
                                                          "(e) 辅助支承（剖开）：定位夹紧后再顶上锁紧，不参与定位"])

# ---- 图 51.5.3：外圆定位
zc = E.v_axis_height(40, apex=14)
v1 = tile([("V 形块", E.vblock(B=72, L=40, H=40, apex=14, at=(0, 0, 0)), "hardened"), ("工件", S.cyl("x", (0, zc), 20, -60, 60), "work", 0.5)], [0.9, -1.3, 0.8])
sl = tile([("定位套", L.locating_sleeve(40.05, 40, at=(0, 0, 0)), "hardened"), ("工件", S.cyl("x", (0, 0), 20, -40, 30), "work", 0.5)], [0.9, -1.2, 0.6],
          section=((0, 0, 0), (0, -1, 0)))
hb = L.half_bore_seat(60, 50, at=(0, 0, 0))
h1 = tile([("下座", hb["下座"], "hardened"), ("上盖", S.move(hb["上盖"], 0, 0, 25), "steel"), ("螺栓", S.move(hb["螺栓"], 0, 0, 25), "steel_dark"),
           ("工件（大轴）", S.cyl("x", (0, 0), 30, -60, 60), "work", 0.5)], [0.9, -1.3, 0.7])
ck = MA.chuck3(D=160, grip=40)
for p_ in ck.parts:
    pass
ck.add(P("工件", S.cyl("x", (0, 0), 20, 0, 70), "work", opacity=0.6))
c1 = R.render_png(ck, 520, 420, camera={"dir": [1.3, -0.9, 0.7]})
col = A("弹簧夹头")
col.add(P("弹簧夹头", E.collet(30, 70, at=(0, 0, 0)), "hardened"))
col.add(P("锥套（主轴端，剖开示意）", S.revolve([(-60, 24), (-18, 24), (-6, 30), (6, 30), (6, 40), (-60, 40)], "x", (0, 0)), "steel_dark"))
col.add(P("工件", S.cyl("x", (0, 0), 15, -40, 50), "work", opacity=0.6))
c2 = R.render_png(col, 520, 420, camera={"dir": [0.9, -1.2, 0.6]}, section=((0, 0, 0), (0, -1, 0)))
R.compose("fig51_5_3", [v1, sl, h1, c1, c2], 3, titles=["(a) V 形块：对中，轴线总在对称面内", "(b) 定位套（剖开）：外圆插入孔中，靠配合间隙定心",
                                                         "(c) 半圆孔定位座：下半定位，上盖压紧（上盖抬起画出）", "(d) 三爪自定心卡盘：既定位又夹紧",
                                                         "(e) 弹簧夹头（剖开）：拉进锥孔时均匀收缩"])

# ---- 图 51.5.4：内孔定位
pins = tile([("圆柱销", E.locating_pin(16, 14, "cyl", at=(-22, 0, 0)), "hardened"), ("削边销", E.locating_pin(16, 14, "dia", at=(22, 0, 0), b=5), blue)], [0.8, -1.3, 1.0])
cone = tile([("锥销", L.cone_pin(20, at=(0, 0, 0)), "hardened"), ("工件（孔口）", S.box(-40, 40, -30, 30, 6, 22) - S.cyl("z", (0, 0), 10.5, 5, 23), "work", 0.5)],
            [0.8, -1.2, 0.5], section=((0, 0, 0), (0, -1, 0)))
md, nut = E.mandrel(30, 60, at=(0, 0, 0))
m1 = tile([("心轴", md, "hardened"), ("螺母", nut, "steel_dark"), ("工件（套）", S.cyl("x", (0, 0), 30, 0, 50) - S.cyl("x", (0, 0), 15.02, -1, 51), "work", 0.5)],
          [0.9, -1.2, 0.6], section=((0, 0, 0), (0, -1, 0)))
tm = tile([("小锥度心轴（锥度放大画出）", L.taper_mandrel(35, 120, at=(0, 0, 0), exaggerate=40), "hardened"),
           ("工件（齿坯）", S.cyl("x", (0, 0), 45, 50, 80) - S.cyl("x", (0, 0), 17.5 + 0.5 * 40 / 1000 * 65, 49, 81), "work", 0.5)], [0.9, -1.2, 0.6],
          section=((0, 0, 0), (0, -1, 0)))
ex = L.expanding_mandrel(35, 60, at=(0, 0, 0))
em = tile([("心轴体", ex["心轴体"], "steel"), ("弹性套", ex["弹性套"], blue), ("拉杆", ex["拉杆"], "steel_dark"),
           ("工件", S.cyl("x", (0, 0), 40, 5, 55) - S.cyl("x", (0, 0), 17.5, 4, 56), "work", 0.5)], [0.9, -1.2, 0.6], section=((0, 0, 0), (0, -1, 0)))
R.compose("fig51_5_4", [pins, cone, m1, tm, em], 3, titles=["(a) 圆柱销与削边销（菱形销）", "(b) 锥销（剖开）：插在孔口，限制三个移动",
                                                            "(c) 间隙配合心轴（剖开）：装卸方便，有间隙误差", "(d) 小锥度心轴（剖开，锥度放大）：楔紧，无间隙",
                                                            "(e) 胀胎心轴（剖开）：拉杆拉动，开缝套胀开撑紧内孔"])

# ---- 图 51.5.5：中心孔与组合表面：(a) 浮动前顶尖与端面驱动器（剖开）；(b) 一面两销定位箱体
fd = L.face_driver(at=(0, 0, 0), D=60)
q = A("端面驱动器")
for n, s in fd.items():
    q.add(P(n, s, {"驱动器体": "steel", "驱动齿": "red", "浮动顶尖": "hardened", "弹簧": "rubber"}[n]))
q.add(P("工件（轴端，剖开）", S.cyl("x", (0, 0), 25, 0, 70) - W.center_hole(0.0, 1, d=4, D=8.5), "work"))
pf = R.render_png(q, 700, 480, camera={"dir": [0.3, -1.2, 0.4], "fit": [[-55, 0, -32], [50, 0, 32]]}, section=((0, 0, 0), (0, -1, 0)),
                  labels=[{"at": (-1.5, 0, 19), "text": "驱动齿压进端面：传扭矩，并确定轴向位置", "style": "text", "pos": [0.5, 0.08], "part": "驱动齿"},
                          {"at": (-20, 0, 6), "text": "浮动顶尖：弹簧顶出，只定心", "style": "text", "pos": [0.4, 0.92], "part": "浮动顶尖"}])
bx = A("一面两销")
bx.add(P("夹具底板", S.box(-140, 140, -100, 100, -25, 0), "cast"))
for k, (px, py) in enumerate(((-110, -70), (110, 70))):
    bx.add(P(f"定位销{k + 1}", E.locating_pin(12, 12, "cyl" if k == 0 else "dia", at=(px, py, 0), b=4, flat_dir="x"), "hardened" if k == 0 else blue))
for x in (-60, 60):
    bx.add(P(f"支承板{x}", E.support_plate(120, 22, 8, at=(x, 0, 8), n=2), "hardened"))
box = TY.box_part(L=250, B=170, at=(0, 0, 8))
for px, py in ((-110, -70), (110, 70)):
    box = box - S.cyl("z", (px, py), 6.01, 7, 30)
bx.add(P("箱座（简化）", box, "work", opacity=0.55))
pbx = R.render_png(bx, 700, 480, camera={"dir": [0.9, -1.3, 0.9]},
                   labels=[{"at": (-110, -70, 12), "text": "圆柱销", "style": "text", "pos": [0.12, 0.85], "part": "定位销1"},
                           {"at": (110, 70, 12), "text": "削边销", "style": "text", "pos": [0.85, 0.12], "part": "定位销2"},
                           {"at": (60, -11, 8), "text": "支承板：底面三个自由度", "style": "text", "pos": [0.75, 0.9], "part": "支承板60"}])
R.compose("fig51_5_5", [pf, pbx], 2, titles=["(a) 浮动前顶尖与端面驱动器（剖开）：顶尖定心、端面定轴向", "(b) 一面两销：底面 + 圆柱销 + 削边销，限制六个自由度"])
out(n_fig3d=4)
