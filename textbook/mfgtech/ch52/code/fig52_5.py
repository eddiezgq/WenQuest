"""52.5 节的图：活塞式气缸与膜片气室（剖开，图 52.5.1）、气动夹紧回路（图 52.5.2）、转角缸的动作（图 52.5.3）、
JJ-301-50 的气动方案（图 52.5.5）、电永磁吸盘与真空吸盘（图 52.5.4）。"""
import math

import _mfg as M
from bookout import T, figure, out, style

C, W, J, E, TY, MA, S = M.m3d()
R = M.r3d()
A, P = C.Assembly, C.Part
g = J.geometry()

# ---- 图 52.5.1：(a) 活塞式气缸；(b) 膜片式气室（都沿轴线剖开）
cy = A("气缸")
cy.add(P("缸筒", S.tube("x", (0, 0), 30, 25, 0, 120), "steel"))
cy.add(P("后端盖", S.cyl("x", (0, 0), 34, -14, 0) - S.cyl("y", (-7, 18), 3, -40, 0), "cast"))
cy.add(P("前端盖", S.cyl("x", (0, 0), 34, 120, 136) - S.cyl("x", (0, 0), 8.2, 119, 137), "cast"))
cy.add(P("活塞", S.cyl("x", (0, 0), 24.8, 50, 70) - S.tube("x", (0, 0), 25, 22, 54, 57) - S.tube("x", (0, 0), 25, 22, 63, 66), "steel_dark"))
cy.add(P("密封圈", S.tube("x", (0, 0), 25, 22, 54, 57) + S.tube("x", (0, 0), 25, 22, 63, 66), "rubber"))
cy.add(P("活塞杆", S.cyl("x", (0, 0), 8, 70, 190), "hardened"))
cy.add(P("气口", S.cyl("z", (-7, 0), 4, 0, 44) + S.cyl("z", (128, 0), 4, 0, 44), "steel_dark", tags=("nocut",)))
pa = R.render_png(cy, 760, 520, camera={"dir": [0.6, -1.3, 0.6]}, section=((0, 0, 0), (0, -1, 0)),
                  labels=[{"at": (60, 0, 23.5), "text": "活塞与密封圈", "style": "text", "pos": [0.42, 0.1], "part": "活塞"},
                          {"at": (30, 0, -27), "text": "无杆腔：推力 πD²p/4·η", "style": "text", "pos": [0.2, 0.9]},
                          {"at": (100, 0, -27), "text": "有杆腔：拉力 π(D²−d²)p/4·η", "style": "text", "pos": [0.7, 0.9]}])
dp = A("膜片气室")
dp.add(P("上壳", S.cyl("x", (0, 0), 50, 0, 18) - S.cyl("x", (0, 0), 44, 4, 19), "cast"))
dp.add(P("下壳", S.cyl("x", (0, 0), 50, 22, 40) - S.cyl("x", (0, 0), 44, 21, 36) - S.cyl("x", (0, 0), 6.2, 35, 41), "cast"))
dp.add(P("橡胶膜片", S.cyl("x", (0, 0), 50, 18, 22), "rubber"))
dp.add(P("推杆与托盘", S.cyl("x", (0, 0), 30, 22, 28) + S.cyl("x", (0, 0), 6, 28, 90), "hardened"))
dp.add(P("回位弹簧", S.tube("x", (0, 0), 18, 16, 28, 36), "steel_dark"))
pb = R.render_png(dp, 760, 520, camera={"dir": [0.6, -1.3, 0.6]}, section=((0, 0, 0), (0, -1, 0)),
                  labels=[{"at": (20, 0, 40), "text": "橡胶膜片：没有滑动密封，行程短", "style": "text", "pos": [0.55, 0.1], "part": "橡胶膜片"}])
R.compose("fig52_5_1", [pa, pb], 2, titles=["(a) 活塞式气缸（剖开）", "(b) 膜片式气室（剖开）"])

# ---- 图 52.5.2：气动夹紧回路（GB/T 786.1 一类图形符号的简化画法）
plt = style()
fig, ax = plt.subplots(figsize=(7.4, 3.6))
ax.set_xlim(0, 100); ax.set_ylim(0, 50); ax.axis("off")
def box(x, y, w, h, t):
    ax.add_patch(plt.Rectangle((x, y), w, h, fc="white", ec=M.INK, lw=1.0)); ax.text(x + w / 2, y - 3.2, t, ha="center", va="top", fontsize=7)
def line(xs, ys, **k):
    ax.plot(xs, ys, color=k.pop("c", M.INK), lw=k.pop("lw", 1.0), **k)
ax.add_patch(plt.Circle((6, 25), 3.2, fc="white", ec=M.INK)); ax.text(6, 25, "▲", ha="center", va="center", fontsize=6); ax.text(6, 19, T("气源", "air supply"), ha="center", fontsize=7)
box(13, 21, 12, 8, T("过滤减压阀（调到 0.5 MPa）", "filter-regulator 0.5 MPa")); ax.text(19, 25, "⊘", ha="center", va="center", fontsize=9)
box(31, 21, 8, 8, T("压力开关", "pressure switch")); ax.text(35, 25, "P", ha="center", va="center", fontsize=8)
box(45, 21, 18, 8, T("二位五通电磁阀", "5/2 solenoid valve")); line([54, 54], [21, 29]); ax.annotate("", xy=(52, 27), xytext=(47, 23), arrowprops=dict(arrowstyle="-|>", lw=0.7)); ax.annotate("", xy=(56, 23), xytext=(61, 27), arrowprops=dict(arrowstyle="-|>", lw=0.7))
box(68, 33, 8, 6, T("单向阀（保压）", "check valve")); ax.text(72, 36, "◇", ha="center", va="center", fontsize=8)
ax.add_patch(plt.Rectangle((80, 31), 16, 10, fc="white", ec=M.INK, lw=1.0)); line([88, 88], [31, 41]); line([88, 99], [36, 36], lw=2.0); ax.text(88, 44, T("转角缸 ×2（拉紧夹紧）", "swing clamps x2 (pull)"), ha="center", fontsize=7)
for xs in ([9.2, 13], [25, 31], [39, 45]):
    line(xs, [25, 25])
line([60, 60, 68], [29, 36, 36]); line([76, 80], [36, 36]); line([50, 50, 84, 84], [29, 46, 46, 41])
ax.text(25, 9, T("气压低于设定值 → 不许启动主轴", "below set pressure → spindle interlocked"), ha="center", fontsize=7, color=M.RED)
ax.text(78, 9, T("夹紧到位（位置开关）→ 机床、机器人", "clamped (position switch) → machine, robot"), ha="center", fontsize=7, color=M.ACCENT)
figure(fig, "fig52_5_2")

# ---- 图 52.5.3：转角缸的动作：松开（压板转开、抬起）→ 转 90°（抬起）→ 下拉夹紧
def swing(ang, dz):
    q = A("转角缸")
    q.add(P("底座", S.box(-50, 80, -60, 60, -20, 0), "cast"))
    q.add(P("工件", S.box(-40, 20, -40, 40, 0, 30), "work"))
    for n, s in E.swing_clamp(at=(50, 0, 6), arm=48, ang_deg=ang).items():
        q.add(P(n, S.move(s, 0, 0, dz if n != "缸体" else 0), "steel_dark" if n != "压板" else "steel"))
    return q
ps = [R.render_png(swing(a_, dz), 560, 480, camera={"dir": [0.9, -1.3, 0.8], "fit": [[-50, -60, -20], [100, 60, 80]]}) for a_, dz in ((90, 8), (180, 8), (180, 0))]
R.compose("fig52_5_3", ps, 3, titles=["(a) 松开：压板转开、抬起", "(b) 活塞杆一边上提一边转 90°", "(c) 再直线下拉，压紧"])

# ---- 图 52.5.5：JJ-301-50 的气动方案：两个转角缸代替移动压板；挡板上有到位检测
pn = J.assembly("op40")
pn.parts = [p for p in pn.parts if not p.name.startswith(("压板", "垫圈螺母", "弹簧", "螺柱", "可调支承"))]
for k, (sx, zt) in enumerate(zip(J.STRAP_X, (g["zc"] + 15.0, g["zc"] + 35.3 / 2))):
    z0 = zt - 24
    pn.add(P(f"转角缸座{k + 1}", S.box(sx - 30, sx + 30, 22, 78, 0, z0 - 12), "cast"))
    for n, s in E.swing_clamp(at=(sx, 50, z0), arm=54, ang_deg=-90).items():
        pn.add(P(f"转角缸{k + 1}{n}", s, "steel_dark" if n != "压板" else "steel"))
# 气检：挡板贴轴肩的面上开 Ø2 气孔，轴肩靠实时堵住气孔，背压开关发出“到位”信号
pn.add(P("气检接头与气管", S.cyl("x", (-24, g["zc"] - 5), 3, -14, -6) + S.cyl("x", (-24, g["zc"] - 5), 1.6, -40, -14)
         + S.cyl("z", (-40, -24), 1.6, 4, g["zc"] - 5), "red"))
R.figure3d("fig52_5_5", pn, 1400, 900, camera={"dir": M.ISO},
           labels=[{"at": (80, 30, g["zc"] + 35.3 / 2 + 6), "text": "气动转角缸（直接压工件）", "style": "text", "pos": [0.68, 0.1], "part": "转角缸2"},
                   {"at": (-10, -24, g["zc"] - 5), "text": "气检：轴肩靠实挡板时堵住气孔，背压开关发出到位信号", "style": "text", "pos": [0.3, 0.06], "part": "气检"}])

# ---- 图 52.5.4：电永磁吸盘与真空吸盘
mg = A("电永磁吸盘")
plate = S.box(-150, 150, -100, 100, -50, 0)
for k in range(-6, 7):
    plate = plate - S.box(k * 22 - 2, k * 22 + 2, -95, 95, -1.2, 0.1)
mg.add(P("吸盘", plate, "steel_dark"))
mg.add(P("工件（钢板）", S.box(-110, 110, -70, 70, 0, 12), "work"))
mg.add(P("接线盒", S.box(150, 175, -30, 30, -45, -10), "red"))
vc = A("真空吸盘")
vp = S.box(-150, 150, -100, 100, -40, 0)
for i in range(-5, 6):
    for j in range(-3, 4):
        vp = vp - S.cyl("z", (i * 25, j * 25), 2, -10, 1)
vc.add(P("真空吸盘", vp, "steel"))
vc.add(P("密封条", S.box(-125, 125, -80, -76, 0, 2) + S.box(-125, 125, 76, 80, 0, 2) + S.box(-125, -121, -80, 80, 0, 2) + S.box(121, 125, -80, 80, 0, 2), "rubber"))
vc.add(P("工件（铝板）", S.box(-130, 130, -85, 85, 2, 8), "#d8dde2", opacity=0.55))
vc.add(P("真空接头", S.cyl("x", (0, -20), 6, 150, 180), "steel_dark"))
R.compose("fig52_5_4", [R.render_png(mg, 700, 480, camera={"dir": [0.9, -1.3, 1.0]}), R.render_png(vc, 700, 480, camera={"dir": [0.9, -1.3, 1.0]})], 2,
          titles=["(a) 电永磁吸盘：只在充磁、退磁时通电，断电不松开", "(b) 真空吸盘：密封条围出的面积 × 真空度（工件画成半透明）"])
out(n_fig=5)
