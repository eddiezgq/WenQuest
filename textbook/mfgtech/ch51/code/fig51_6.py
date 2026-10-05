"""51.6–51.9 节的三维图：基准不重合（图 51.6.1）、四种定位方式的定位误差（图 51.7.2–51.7.5）、
SH-301 铣键槽的三种定位方案（图 51.8.1）、三坐标测量机验证（图 51.9.2）。
模型：factory/digital/models3d（SH-301、JJ-301-50 取自数字工厂；直径、间隙按算例的数值，放大画出时在图注里写明）。"""
import math

import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
L = M.loc()
R = M.r3d()
A, P = C.Assembly, C.Part
g = J.geometry()
blue, red, green, orange = "#4f7fb8", "#c0504d", "#5a9e6f", "#d98c3a"
LEN = 167.0

# ---- 图 51.6.1：基准不重合：以右端面定位（靠挡块），刀具按右端面对刀车左轴肩；图纸尺寸从左端面标起
q = A("基准不重合")
w = W.sh301("op40")
q.add(w)
q.add(P("定位挡块（靠右端面）", S.box(LEN, LEN + 14, -30, 30, -30, 30), blue))
q.add(P("车刀（车左轴承位轴肩）", S.box(52 - 4, 52, -60, -20, -4, 4) + S.box(48, 52, -20, -17.65 - 0.3, -2, 2), "tool"))
dims = [{"a": (0, -25, 0), "b": (52, -25, 0), "off": (0, -12, 0), "text": "图纸尺寸 52（从左端面）", "color": red},
        {"a": (52, 25, 0), "b": (LEN, 25, 0), "off": (0, 20, 0), "text": "刀具按右端面调好：115", "color": blue},
        {"a": (0, -25, 0), "b": (LEN, -25, 0), "off": (0, -34, 0), "text": "总长 167 ± 0.5：每根不同", "color": "#1d2327"}]
R.figure3d("fig51_6_1", q, 1400, 700, camera={"dir": [0.0, -0.4, 1.0], "up": [0, 1, 0], "fit": [[-10, -70, -20], [LEN + 20, 50, 20]]}, dims=dims,
           labels=[{"at": (LEN, 0, 10), "text": "定位基准：右端面", "style": "text", "pos": [0.88, 0.1], "part": "定位挡块"},
                   {"at": (0, 0, 10), "text": "工序基准：左端面", "style": "text", "pos": [0.03, 0.1], "anchor": "start", "part": "SH-301"}])

# ---- 图 51.7.2：V 形块：直径最大和最小的两根轴（直径差放大到 6 mm），轴心、上母线、下母线的位置
def vb_pair():
    q = A("V 形块")
    q.add(P("V 形块", E.vblock(B=90, L=30, H=45, apex=10, at=(0, 0, 0)), "hardened"))
    for dd, col, op in ((46.0, "work_cut", 0.45), (40.0, orange, 0.55)):
        zc = E.v_axis_height(dd, apex=10)
        q.add(P(f"工件 Ø{dd:g}", S.cyl("x", (0, zc), dd / 2, -10, 10), col, opacity=op))
    return q
z1, z2 = E.v_axis_height(46, apex=10), E.v_axis_height(40, apex=10)
pv = R.render_png(vb_pair(), 900, 640, camera={"dir": [1, 0, 0], "fit": [[0, -70, 0], [0, 70, 75]]}, fontSize=19,
                  points=[{"at": (11, 0, z1), "r": 5, "color": blue, "text": "最大直径的轴心", "dx": 10, "dy": -8},
                          {"at": (11, 0, z2), "r": 5, "color": red, "text": "最小直径的轴心", "dx": 10, "dy": 14},
                          {"at": (11, 0, z1 + 23), "r": 4, "color": blue}, {"at": (11, 0, z2 + 20), "r": 4, "color": red},
                          {"at": (11, 0, z1 - 23), "r": 4, "color": blue}, {"at": (11, 0, z2 - 20), "r": 4, "color": red}],
                  dims=[{"a": (11, 0, z2), "b": (11, 0, z1), "off": (0, -62, 0), "text": "轴心"},
                        {"a": (11, 0, z2 + 20), "b": (11, 0, z1 + 23), "off": (0, 62, 0), "text": "上母线"},
                        {"a": (11, 0, z2 - 20), "b": (11, 0, z1 - 23), "off": (0, 62, 0), "text": "下母线"}])
R.save_figure("fig51_7_2", pv, 900, 640)

# ---- 图 51.7.3：心轴：(a) 孔靠向任意方向（随心轴转），(b) 总靠向一侧（重力），间隙放大到 3 mm
def mandrel_case(side):
    q = A("心轴")
    q.add(P("心轴", S.cyl("x", (0, 0), 15, -20, 30), "hardened"))
    e = 1.5
    ang = [math.radians(a) for a in ((90, 210, 330) if side == "any" else (270, 270, 270))]
    for k, a in enumerate(ang[:3 if side == "any" else 1]):
        cy, cz = e * math.cos(a), e * math.sin(a)
        q.add(P(f"工件{k}", S.cyl("x", (cy, cz), 30, 0, 12 + 0 * k) - S.cyl("x", (cy, cz), 16.5, -1, 13), ("work_cut", orange, green)[k], opacity=0.5))
    return q
cm = {"dir": [1, 0, 0], "fit": [[0, -32, -32], [0, 32, 32]]}
m1 = R.render_png(mandrel_case("any"), 600, 560, camera=cm, fontSize=18,
                  points=[{"at": (13, 0, 0), "r": 4, "color": "#1d2327", "text": "心轴中心", "dx": 8, "dy": -6}])
m2 = R.render_png(mandrel_case("down"), 600, 560, camera=cm, fontSize=18,
                  points=[{"at": (13, 0, 0), "r": 4, "color": "#1d2327", "text": "心轴中心", "dx": 8, "dy": -6},
                          {"at": (13, 0, -1.5), "r": 4, "color": red, "text": "孔心总在下方", "dx": 8, "dy": 18}])
R.compose("fig51_7_3", [m1, m2], 2, titles=["(a) 工件随心轴转：孔心偏向任意方向，变动 X_max", "(b) 工件靠重力压向一侧：变动 (X_max − X_min)/2（间隙放大画出）"])

# ---- 图 51.7.4：一面两销：两孔分别靠向两销相反的两侧，工件转一个角度（间隙放大）
def two_pin_rot(rot):
    q = A("一面两销")
    q.add(P("支承板", S.box(-140, 140, -80, 80, -20, 0), "cast"))
    q.add(P("圆柱销", E.locating_pin(12, 14, "cyl", at=(-100, 0, 0)), "hardened"))
    q.add(P("削边销", E.locating_pin(12, 14, "dia", at=(100, 0, 0), b=4, flat_dir="x"), blue))
    pl = L.plate_with_holes(L=260, B=140, t=12, holes=((-100, 0), (100, 0)), D=30.0, at=(0, 0, 0))
    q.add(P("工件（间隙和转角放大画出）", S.rot(pl, 0, 0, rot), "work_cut", opacity=0.55))
    q.add(P("被镗孔", S.rot(S.tube("z", (40, 0), 14, 12, 0.5, 12.5), 0, 0, rot), red))
    q.add(P("被镗孔（理想位置）", S.tube("z", (40, 0), 14, 13.2, 12.5, 13.0), "#1d2327"))
    return q
ang = math.degrees(math.atan((9 + 9) / 200))
pt = R.render_png(two_pin_rot(ang), 1000, 600, camera={"dir": [0, -0.25, 1], "up": [0, 1, 0], "fit": [[-140, -80, 0], [140, 80, 0]]}, fontSize=19,
                  labels=[{"at": (-100, 0, 14), "text": "圆柱销处：孔靠向 −y", "style": "text", "pos": [0.03, 0.06], "anchor": "start", "part": "圆柱销"},
                          {"at": (100, 0, 14), "text": "削边销处：孔靠向 +y", "style": "text", "pos": [0.97, 0.06], "anchor": "end", "part": "削边销"},
                          {"at": (40, 13, 12), "text": "被镗孔的位置随转角变动", "style": "text", "pos": [0.55, 0.92], "part": "被镗孔"}])
R.save_figure("fig51_7_4", pt, 1000, 600)

# ---- 图 51.7.5：两顶尖：中心孔锥口直径不同，工件沿轴向的位置不同（放大画出）
def centers(dD):
    q = A("中心孔")
    q.add(P("前顶尖", E.center(at=(0, 0, 0)), "hardened"))
    D = 6.7 + dD
    tip = D / 2 / math.tan(math.radians(30))
    shaft = S.cyl("x", (0, 0), 15, 0, 40) - W.center_hole(0.0, 1, d=3.15 + dD * 0.5, D=D)
    q.add(P("工件", S.move(shaft, -tip + 6.7 / 2 / math.tan(math.radians(30)), 0, 0), "work_cut"))
    return q, -tip + 6.7 / 2 / math.tan(math.radians(30))
c0, x0 = centers(0.0)
c1, x1 = centers(6.0)
pc = [R.render_png(c, 700, 420, camera={"dir": [0, -1, 0.15], "fit": [[-20, 0, -22], [30, 0, 16]]}, section=((0, 0, 0), (0, -1, 0)), fontSize=18,
                   dims=[{"a": (-12, 0, -16), "b": (xx, 0, -16), "off": (0, 0, -2), "text": f"顶尖台肩到工件端面 {xx + 12:.1f}"}])
      for c, xx in ((c0, x0), (c1, x1))]
R.compose("fig51_7_5", pc, 2, titles=["(a) 锥口直径 D", "(b) 锥口直径 D + ΔD：工件向顶尖方向移 ΔD/(2tan30°)（ΔD 放大到 6 mm 画出）"])

# ---- 图 51.8.1：SH-301 铣键槽的三种定位方案
ja = J.assembly("op40", with_cutter=True)
pA = R.render_png(ja, 700, 520, camera={"dir": M.ISO})
lb = MA.lathe_centers(LEN, 0.0)
lb.add(W.sh301("op40"))
kx = 52.0 + float(W.plan()["part"]["keyway"]["offset_mm"])
for qq in MA.mill_spindle(kx + 6, 0, 20.15 - 1.0).parts:
    lb.add(qq)
pB = R.render_png(lb, 700, 520, camera={"dir": [0.6, -1.3, 0.8], "fit": [[-60, -60, -40], [230, 60, 180]]})
cc = MA.chuck3(D=160, grip=30, face_x=-10)
lc_ = A("卡盘加后顶尖")
for p_ in cc.parts:
    p_.shape = p_.shape & S.box(-200, 2, -200, 200, -200, 200) if p_.name.startswith("卡爪") else p_.shape
    lc_.add(p_)
lc_.add(W.sh301("op40"))
lc_.add(P("后顶尖", E.center(at=(LEN, 0, 0), toward=-1), "hardened"))
for qq in MA.mill_spindle(kx + 6, 0, 20.15 - 1.0).parts:
    lc_.add(qq)
pC = R.render_png(lc_, 700, 520, camera={"dir": [0.6, -1.3, 0.8], "fit": [[-60, -60, -40], [230, 60, 180]]})
R.compose("fig51_8_1", [pA, pB, pC], 3, titles=["方案 A：V 形块（两段工作面）+ 轴向挡板（JJ-301-50）", "方案 B：两顶尖（顶尖座或分度头）", "方案 C：三爪卡盘短夹持 + 后顶尖"])

# ---- 图 51.9.2：三坐标测量机测键槽对称度
zc2 = E.v_axis_height(35.3, apex=14)
yb, zb = 6.0 - 2.0, zc2 + 17.5                     # 测球（半径 2）贴住键槽一侧（y = 6），高度在槽深中间
cmq = L.cmm(table=(-120, 290, -200, 200), z_table=0.0, probe_at=(kx + 20, yb, zb), bridge_y=yb)
cmq.add(P("V 形支架", E.vblock(B=72, L=12, H=40, apex=14, at=(46, 0, 0)), "hardened"))
cmq.add(P("V 形支架2", E.vblock(B=72, L=20, H=40, apex=14, at=(124, 0, 0)), "hardened"))
sh = W.sh301("op50")
sh.shape = S.move(sh.shape, 0, 0, zc2)
cmq.add(sh)
R.figure3d("fig51_9_2", cmq, 1300, 900, camera={"dir": [0.8, -1.3, 0.7], "fit": [[-40, -120, -20], [220, 120, 180]]},
           labels=[{"at": (kx + 20, yb, zb), "text": "测球依次碰键槽两侧面和齿轮位外圆：算出对称度", "style": "text", "pos": [0.65, 0.1], "part": "测球"},
                   {"at": (46, -30, 30), "text": "轴的两个轴承位架在两个 V 形支架上", "style": "text", "pos": [0.03, 0.9], "anchor": "start", "part": "V 形支架"}])
out(n_fig3d=7, z_shift=z1 - z2, x_shift=x1 - x0, rot_deg=ang)
