"""53.7 节的三维图：SH-301 从毛坯到成品的四个状态，标出六个轴向面 L、S1–S4、R（图 53.7.2），与跟踪图的竖线一一对应。
模型：factory/digital/models3d/workpiece.py（各状态由工艺规程的工序简图数据生成）。"""
import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
R = M.r3d()
A, P = C.Assembly, C.Part
states = [("blank", "毛坯 Ø50 × 182"), ("op20", "工序 20 粗车后（轴肩留 0.8）"), ("op40", "工序 40 精车后"), ("op60", "工序 60 磨削后（成品）")]
q = A("四个状态")
gap = 70.0
pts = []
for i, (st, _) in enumerate(states):
    w = W.sh301(st)
    w.shape = S.move(w.shape, 0, 0, -i * gap)
    w.name = f"SH-301 {st}"
    q.add(w)
segs, x0 = W.segments("op40")
xs = [0.0]
for _, Lk in segs:
    xs.append(xs[-1] + Lk)
names = ["L", "S1", "S2", "S3", "S4", "R"]
for x, n in zip(xs, names):
    q.add(P(f"面 {n}", S.box(x - 0.4, x + 0.4, -1, 1, -3 * gap - 35, 35), "#c0504d", opacity=0.35))
texts = [{"pos": [0.02, 0.17 + 0.235 * i], "text": t, "fontSize": 34, "anchor": "start"} for i, (_, t) in enumerate(states)]
R.figure3d("fig53_7_2", q, 1400, 900, camera={"dir": [0, -1, 0.0], "fit": [[-70, 0, -3 * gap - 30], [185, 0, 40]]}, fontSize=18,
           points=[{"at": (x, -30, 32), "r": 5, "color": "#c0504d", "text": n, "dx": -6, "dy": -10} for x, n in zip(xs, names)], texts=texts)
out(n_fig3d=1)
