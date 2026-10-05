"""50.6 节的三维图：SH-301 终检（工序 70）的几项检验（图 50.6.3）：(a) 外径千分尺测轴承位直径；(b) 偏摆仪两顶尖支承、千分表测径向圆跳动；
(c) 键槽对称度用对称度量规（示意）。量具为简化的示意模型；模型：factory/digital/models3d。"""
import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
R = M.r3d()
A, P = C.Assembly, C.Part
LEN = 167.0

# (a) 外径千分尺测左轴承位 Ø35 k6（竖直放，测砧、测微螺杆夹住外圆）
qa = A("千分尺")
qa.add(W.sh301("op60"))
x = 46.0
frame = S.box(x - 4, x + 4, -40, -32, -32, 32) + S.box(x - 4, x + 4, -40, 0, -32, -26) + S.box(x - 4, x + 4, -40, 0, 26, 32)
qa.add(P("尺架", frame, "#c9a24a"))
qa.add(P("测砧", S.cyl("z", (x, 0), 3, -26, -17.5), "hardened"))
qa.add(P("测微螺杆与微分筒", S.cyl("z", (x, 0), 3, 17.5, 32) + S.cyl("z", (x, 0), 7, 32, 70), "steel"))
pa = R.render_png(qa, 640, 480, camera={"dir": [0.5, -1.2, 0.5], "fit": [[0, -45, -35], [100, 20, 75]]}, fontSize=19,
                  labels=[{"at": (x, 0, -17.5), "text": "每件测两处轴承位、齿轮位直径", "style": "text", "pos": [0.55, 0.92], "part": "测砧"}])
# (b) 偏摆仪：两顶尖支承，千分表测轴承位径向圆跳动，转动工件看表针变化
qb = MA.lathe_centers(LEN, 0.0)
qb.parts = [p for p in qb.parts if p.name in ("前顶尖", "后顶尖")]
qb.add(P("偏摆仪底座与顶尖座", S.box(-70, LEN + 70, -40, 40, -90, -70) + S.box(-70, -40, -20, 20, -70, 10) + S.box(LEN + 25, LEN + 70, -20, 20, -70, 10), "cast"))
qb.add(W.sh301("op60"))
for p in MA.dial_indicator(tip=(46, 0, 17.5), base_at=(46, -60, -70)).parts:
    qb.add(p)
pb = R.render_png(qb, 640, 480, camera={"dir": [0.5, -1.2, 0.6], "fit": [[-80, -90, -95], [LEN + 80, 50, 100]]}, fontSize=19,
                  labels=[{"at": (46, 0, 17.5), "text": "转一圈，表针最大变化 ≤ 0.012", "style": "text", "pos": [0.55, 0.08], "part": "表头"}])
# (c) 对称度量规：塞块插进键槽，两侧量爪靠齿轮位外圆，千分表读两侧差（示意）
qc = A("对称度")
qc.add(W.sh301("op60"))
k = W.plan()["part"]["keyway"]
xk = 52.0 + float(k["offset_mm"]) + float(k["L"]) / 2
qc.add(P("量规塞块（插入键槽）", S.box(xk - 15, xk + 15, -6, 6, 15, 30), "hardened"))
qc.add(P("V 形量座（骑在齿轮位上）", S.prism("yz", [(-32, 10), (-20, 10), (0, 30), (20, 10), (32, 10), (32, 38), (-32, 38)], xk - 25, xk + 25)
         - S.box(xk - 16, xk + 16, -7, 7, 14, 39), "steel"))
pc = R.render_png(qc, 640, 480, camera={"dir": [1.0, -0.8, 0.6], "fit": [[xk - 40, -40, -25], [xk + 40, 40, 45]]}, fontSize=19,
                  labels=[{"at": (xk, -20, 30), "text": "塞块对 V 形量座的偏移 = 键槽对称度（示意）", "style": "text", "pos": [0.5, 0.08]}])
R.compose("fig50_6_3", [pa, pb, pc], 3, titles=["(a) 外径千分尺测轴承位直径", "(b) 偏摆仪测径向圆跳动（两顶尖支承）", "(c) 键槽对称度的检验（示意）"])
out(n_fig3d=1)
