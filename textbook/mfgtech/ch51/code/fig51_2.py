"""51.2 节的三维图：SH-301 在各道工序和装配中的基准（图 51.2.2）、基准由基面体现（图 51.2.3）。
模型：factory/digital/models3d（SH-301 各工序状态取自工艺规程；JJ-301-50 取自夹具数据；轴承见 locating.py）。"""
import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
L = M.loc()
R = M.r3d()
A, P = C.Assembly, C.Part
g = J.geometry()
zc, rg = g["zc"], g["d_g"] / 2
blue, red, green = "#4f7fb8", "#c0504d", "#5a9e6f"
LEN = 167.0
k = W.plan()["part"]["keyway"]
r_bot = 20.0 - float(k["t"])                     # 成品槽底离轴线 15（d − t₁ = 35）

# ---- 图 51.2.2：(a) 两顶尖：精车、磨削和偏摆仪测跳动，定位基准、测量基准都是两中心孔连线
lc = MA.lathe_centers(LEN, 0.0)
lc.add(W.sh301("op40"))
pa = R.render_png(lc, 760, 460, fontSize=19, camera={"dir": [0.45, -1.3, 0.45], "fit": [[-80, -60, -60], [250, 60, 70]]},
                  arrows=[{"from": (-40, -30, 0), "to": (LEN + 40, -30, 0), "color": blue, "width": 2, "head": 10}],
                  labels=[{"at": (LEN / 2, -30, 0), "text": "定位基准、测量基准：两中心孔的连线", "style": "text", "pos": [0.5, 0.1]},
                          {"at": (-6, 0, 0), "text": "前顶尖", "style": "text", "pos": [0.12, 0.88], "part": "前顶尖"},
                          {"at": (LEN + 6, 0, 0), "text": "后顶尖", "style": "text", "pos": [0.85, 0.88], "part": "后顶尖"}])
# (b) 铣键槽：在 V 形块上定位，定位基准是齿轮位外圆的轴线；工序尺寸 H 从下母线量起（过键槽中部剖开）
vb = J.assembly("op50")
xs = 52.0 + float(k["offset_mm"]) + float(k["L"]) / 2 + g["work_x0"]
pb = R.render_png(vb, 760, 460, fontSize=19, camera={"dir": [-1.0, -0.35, 0.15], "fit": [[xs, -45, 0], [xs, 45, 95]]}, section=((xs, 0, 0), (-1, 0, 0)),
                  dims=[{"a": (xs, 22, zc - rg), "b": (xs, 22, zc + r_bot), "off": (0, 30, 0), "text": "H"}],
                  points=[{"at": (xs, 0, zc), "r": 5, "color": blue, "text": "定位基准：外圆轴线", "dx": -150, "dy": -14},
                          {"at": (xs, 0, zc - rg), "r": 5, "color": red, "text": "工序基准：下母线", "dx": 10, "dy": 22}])
# (c) 装配：两轴承位装进箱体的轴承孔，齿轮靠轴肩——装配基准是两轴承位（设计基准 A–B 公共轴线）和齿轮定位轴肩
asm = A("装配")
asm.add(W.sh301("op60"))
for n, s in L.bearing(35.3, 62, 12, at=(40, 0, 0)).items():
    asm.add(P(f"左轴承{n}", s, "steel" if n != "保持架" else "steel_dark"))
for n, s in L.bearing(35.3, 72, 17, at=(LEN - 30 - 25 + 4, 0, 0)).items():
    asm.add(P(f"右轴承{n}", s, "steel" if n != "保持架" else "steel_dark"))
gear = S.cyl("x", (0, 0), 62, 52, 92) + S.cyl("x", (0, 0), 34, 92, 112) - S.cyl("x", (0, 0), 20.15, 51, 113)
gear = gear - S.box(52, 112, -6, 6, 15, 25)
asm.add(P("齿轮（剖开）", gear, "#d9c48f"))
house = S.box(20, 160, -90, 90, -110, 110) - S.cyl("x", (0, 0), 31, 39, 53) - S.cyl("x", (0, 0), 36, 109, 131) - S.box(52, 112, -80, 80, -100, 100) \
    - S.cyl("x", (0, 0), 24, 10, 41) - S.cyl("x", (0, 0), 24, 129, 170)
asm.add(P("箱体（局部，剖开）", house, "cast"))
pc = R.render_png(asm, 760, 460, fontSize=19, camera={"dir": [0.5, -1.3, 0.5], "fit": [[-10, 0, -110], [175, 0, 110]]}, section=((0, 0, 0), (0, -1, 0)),
                  labels=[{"at": (46, 0, 17.65), "text": "装配基准：两轴承位（设计基准 A–B）", "style": "text", "pos": [0.5, 0.07], "part": "SH-301"},
                          {"at": (52, 0, 19), "text": "齿轮靠轴肩：轴向的装配基准", "style": "text", "pos": [0.03, 0.92], "anchor": "start", "part": "齿轮"}])
R.compose("fig51_2_2", [pa, pb, pc], 2, titles=["(a) 两顶尖：精车、磨削、测跳动", "(b) V 形块：铣键槽（剖开）", "(c) 装配：轴承与齿轮（剖开）"])

# ---- 图 51.2.3：基准由基面体现：(a) 中心孔的锥面贴住顶尖的锥面，体现出轴线；(b) 外圆贴住 V 形块的两个工作面，体现出轴线
ch = A("中心孔与顶尖")
ch.add(P("工件左端（局部）", S.cyl("x", (0, 0), 15, 0, 40) - W.center_hole(0.0, 1), "work"))
import math
tip = 6.7 / 2 / math.tan(math.radians(30))          # 顶尖锥面贴住中心孔 60° 锥面时，尖端伸进孔里的深度
ch.add(P("前顶尖", E.center(at=(tip, 0, 0)), "hardened"))
p1 = R.render_png(ch, 700, 480, camera={"dir": [0.3, -1.0, 0.25], "fit": [[-30, 0, -18], [30, 0, 18]]}, section=((0, 0, 0), (0, -1, 0)),
                  arrows=[{"from": (-35, 0, 0), "to": (42, 0, 0), "color": blue, "width": 2, "head": 9}],
                  labels=[{"at": (2.0, 0, 1.6), "text": "定位基面：中心孔 60° 锥面", "style": "text", "pos": [0.55, 0.12], "part": "工件"},
                          {"at": (30, 0, 0), "text": "定位基准：轴线（看不见，由锥面体现）", "style": "text", "pos": [0.55, 0.9]}])
vb2 = A("V 形块与外圆")
for q in J.assembly("op40").parts:
    if q.number == 3 or q.name.startswith("工件"):
        vb2.add(q)
p2 = R.render_png(vb2, 700, 480, camera={"dir": [-1.0, -0.3, 0.3], "fit": [[9, -42, 0], [9, 42, 80]]}, section=((9, 0, 0), (-1, 0, 0)),
                  points=[{"at": (9, -rg * 0.7071, zc - rg * 0.7071), "r": 6, "color": red, "text": "", "dx": 0},
                          {"at": (9, rg * 0.7071, zc - rg * 0.7071), "r": 6, "color": red, "text": "定位基面：外圆与两工作面接触", "dx": 12, "dy": 30},
                          {"at": (9, 0, zc), "r": 5, "color": blue, "text": "定位基准：外圆轴线", "dx": 10, "dy": -12}])
R.compose("fig51_2_3", [p1, p2], 2, titles=["(a) 两顶尖：基面是中心孔锥面", "(b) V 形块：基面是外圆表面"])
out(n_fig3d=2, r_bot=r_bot)
