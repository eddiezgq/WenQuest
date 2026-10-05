"""51.4 节的三维图：欠定位与过定位的实例（图 51.4.1）、一面两孔用两个圆柱销装不上（图 51.4.2）。
模型：factory/digital/models3d（SH-301、JJ-301-50 取自数字工厂；卡盘、顶尖见 machines.py；板形工件见 locating.py）。"""
import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
L = M.loc()
R = M.r3d()
A, P = C.Assembly, C.Part
g = J.geometry()
red, blue = "#c0504d", "#4f7fb8"
LEN = 167.0

# ---- 图 51.4.1
# (a) 欠定位：只有 V 形块、没有轴向挡板——轴可以沿轴线滑动，键槽的轴向位置保证不了
ua = J.assembly("op40")
ua.parts = [p for p in ua.parts if p.number not in (4,)]
pa = R.render_png(ua, 700, 520, fontSize=24, camera={"dir": M.ISO},
                  arrows=[{"from": (20, -30, g["zc"] + 30), "to": (70, -30, g["zc"] + 30), "color": red, "text": "沿轴线可以滑动", "textAt": "end"},
                          {"from": (20, -30, g["zc"] + 30), "to": (-30, -30, g["zc"] + 30), "color": red}])
# (b) 过定位：三爪卡盘长夹持 + 后顶尖。卡盘与尾座不同轴（放大画出），工件被别弯
def chuck_tail(long_grip):
    q = A("一夹一顶")
    grip = 55.0 if long_grip else 12.0
    ch = MA.chuck3(D=160, grip=30.0, face_x=0.0)
    for p in ch.parts:
        if p.name.startswith("卡爪"):
            p.shape = p.shape & S.box(0, grip, -200, 200, -200, 200)
        q.add(p)
    off = 18.0                                    # 尾座中心比主轴中心低（实际零点几毫米，放大画出）
    w = W.sh301("op20").shape
    bb = w.bounding_box()
    import build123d as bd
    w = S.move(w, -bb.min.X - 0.0 + 0.0, 0, 0)
    if long_grip:
        # 长夹持：卡盘端轴线方向被定死，尾座端被顶低，轴弯成一段弧（用分段旋转近似）
        Lw = bb.max.X - bb.min.X
        n = 8
        pieces = None
        for i in range(n):
            x0, x1 = Lw * i / n, Lw * (i + 1) / n
            seg = w & S.box(x0, x1 + 0.01, -50, 50, -50, 50)
            xm = (x0 + x1) / 2
            dz = -off * (xm / Lw) ** 2 * (3 - 2 * xm / Lw)
            slope = -off * 6 * (xm / Lw) * (1 - xm / Lw) / Lw
            import math
            seg = S.move(S.rot(seg, 0, -math.degrees(slope), 0, about=(xm, 0, 0)), 0, 0, dz)
            pieces = seg if pieces is None else pieces + seg
        w = pieces
    else:
        import math
        w = S.rot(w, 0, math.degrees(off / (bb.max.X - bb.min.X)), 0, about=(6, 0, 0))   # 短夹持：卡爪处像一个铰点，轴整体略斜
    q.add(P("工件（粗车坯）", w, "work"))
    tail_z = -off
    q.add(P("后顶尖", E.center(at=(bb.max.X - bb.min.X, 0, tail_z), toward=-1), "hardened"))
    q.add(P("尾座套筒", S.cyl("x", (0, tail_z), 22, bb.max.X - bb.min.X + 70, bb.max.X - bb.min.X + 160), "cast"))
    return q
cam_ct = {"dir": [0.15, -1.3, 0.2], "fit": [[-30, -60, -60], [260, 60, 60]]}
axl = [{"from": (-20, -40, 0), "to": (270, -40, 0), "color": blue, "width": 1.5, "head": 8, "text": "主轴轴线", "dx": -10, "dy": -10},
       {"from": (120, -40, -18), "to": (270, -40, -18), "color": red, "width": 1.5, "head": 8, "text": "尾座轴线", "textAt": "end", "dx": -60, "dy": 24}]
pb = R.render_png(chuck_tail(True), 700, 520, fontSize=22, camera=cam_ct, arrows=axl,
                  labels=[{"at": (20, -15, 15), "text": "长夹持：卡爪“抱”住一段，定死了轴线方向", "style": "text", "pos": [0.35, 0.1], "part": "卡爪"},
                          {"at": (110, -20, -2), "text": "后顶尖又定一次：轴被别弯（不同轴与变形都放大画出）", "style": "text", "pos": [0.03, 0.9], "anchor": "start", "part": "工件"}])
pc = R.render_png(chuck_tail(False), 700, 520, fontSize=22, camera=cam_ct, arrows=axl,
                  labels=[{"at": (6, -15, 15), "text": "短夹持：只限制两个移动", "style": "text", "pos": [0.3, 0.1], "part": "卡爪"},
                          {"at": (130, -20, -2), "text": "轴线方向由后顶尖决定，工件不受别劲", "style": "text", "pos": [0.03, 0.9], "anchor": "start", "part": "工件"}])
R.compose("fig51_4_1", [pa, pb, pc], 3, titles=["(a) 欠定位：没有轴向挡板", "(b) 过定位：长夹持 + 后顶尖", "(c) 改为短夹持：消除过定位"])

# ---- 图 51.4.2：一面两孔：(a) 两个圆柱销——孔距比销距大 0.06（放大画出），第二个孔压在销上，装不下去；(b) 第二个销削边，沿连线方向让开
def two_pins(diamond):
    q = A("一面两销")
    q.add(P("支承板（夹具体）", S.box(-120, 120, -70, 70, -20, 0), "cast"))
    pins = ((-80, 0), (80, 0))
    for k, (px, py) in enumerate(pins):
        kind = "dia" if (diamond and k == 1) else "cyl"
        q.add(P(f"定位销{k + 1}", E.locating_pin(12, 14, kind, at=(px, py, 0), b=4, flat_dir="x"), "hardened" if kind == "cyl" else blue))
    e = 1.6                                        # 孔距比销距大（真实 0.06 mm 级，放大画出）
    holes = ((-80, 0), (80 + e, 0))
    plate = L.plate_with_holes(L=220, B=110, t=18, holes=holes, D=12.4, at=(0, 0, 0))
    if not diamond:                                # 两个圆柱销：第一个孔套进去了，第二个孔压在销头上，工件一头翘着落不下去
        plate = S.rot(plate, 0, -5.0, 0, about=(-80, 0, 0))
    q.add(P("工件（板）", plate, "work_cut" if diamond else "red", opacity=0.75))
    return q
cam2 = {"dir": [0.2, -1.2, 0.6], "fit": [[-120, -70, -20], [120, 70, 40]]}
sec = ((0, 0, 0), (0, -1, 0))
p1 = R.render_png(two_pins(False), 760, 460, camera=cam2, section=sec,
                  labels=[{"at": (80, 0, 14), "text": "孔距与销距差一点，第二个孔压在销头上", "style": "text", "pos": [0.6, 0.1], "part": "定位销2"}])
p2 = R.render_png(two_pins(True), 760, 460, camera=cam2, section=sec,
                  labels=[{"at": (80, 0, 10), "text": "削边销：沿两销连线方向削去两边，让开孔距误差", "style": "text", "pos": [0.6, 0.1], "part": "定位销2"}])
R.compose("fig51_4_2", [p1, p2], 2, titles=["(a) 两个圆柱销：沿连线方向重复限制，装不上", "(b) 一个圆柱销 + 一个削边销：装得上（过两孔中心剖开，孔距差放大画出）"])
out(n_fig3d=2)
