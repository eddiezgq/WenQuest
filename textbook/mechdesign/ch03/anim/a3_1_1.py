"""动画 3.1.1（配图 3.1.1、3.2.1）：玻璃盒——轴承座（6207 用）向三个投影面投影，再把投影面展开成三视图；最后把主视图右半剖开，得到半剖视图。"""
import math

from manim import *
from wq_anim import *

# 轴承座尺寸（mm），与程序 3.8.1 按 6207 推出的相同
L, Wb, W, tb, H, Ro, D, D2, Lh, dh = 155, 43, 31, 13, 50, 48, 72, 64, 122, 11
S = 0.022                       # 屏幕单位 / mm
GAP = 22                        # 物体到投影面的距离（mm）
YV, ZH, XW = Wb / 2 + GAP, -GAP, L / 2 + GAP      # 正面 V（物体后面）、水平面 H（下面）、侧面 W（右边）


def arc(cx, cz, r, a0, a1, n=40):
    return [(cx + r * math.cos(a0 + (a1 - a0) * k / n), cz + r * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]


# 三个视图（视图坐标）：可见线、虚线
FRONT_V = [[(-L / 2, 0), (L / 2, 0), (L / 2, tb), (Ro, tb), (Ro, H)] + arc(0, H, Ro, 0, math.pi) + [(-Ro, H), (-Ro, tb), (-L / 2, tb), (-L / 2, 0)],
           arc(0, H, D / 2, 0, 2 * math.pi), arc(0, H, D2 / 2, 0, 2 * math.pi)]
FRONT_H = [[(s * Lh / 2 + e, 0), (s * Lh / 2 + e, tb)] for s in (-1, 1) for e in (-dh / 2, dh / 2)]
TOP_V = [[(-L / 2, -Wb / 2), (L / 2, -Wb / 2), (L / 2, Wb / 2), (-L / 2, Wb / 2), (-L / 2, -Wb / 2)],
         [(-Ro, -W / 2), (Ro, -W / 2), (Ro, W / 2), (-Ro, W / 2), (-Ro, -W / 2)]] + \
        [[(s * Lh / 2 + dh / 2 * math.cos(t), dh / 2 * math.sin(t)) for t in [k * math.pi / 16 for k in range(33)]] for s in (-1, 1)]
SEAT = 21                       # 轴承孔深（从前端面开），其余是挡肩孔 Ø64
TOP_H = [[(s * D / 2, -W / 2), (s * D / 2, -W / 2 + SEAT)] for s in (-1, 1)] + [[(s * D2 / 2, -W / 2 + SEAT), (s * D2 / 2, W / 2)] for s in (-1, 1)] + \
        [[(-D / 2, -W / 2 + SEAT), (D / 2, -W / 2 + SEAT)]]
LEFT_V = [[(-Wb / 2, 0), (Wb / 2, 0), (Wb / 2, tb), (W / 2, tb), (W / 2, H + Ro), (-W / 2, H + Ro), (-W / 2, tb), (-Wb / 2, tb), (-Wb / 2, 0)]]
LEFT_H = [[(W / 2, H + s * D / 2), (W / 2 - SEAT, H + s * D / 2)] for s in (-1, 1)] + [[(W / 2 - SEAT, H + s * D2 / 2), (-W / 2, H + s * D2 / 2)] for s in (-1, 1)] + \
         [[(W / 2 - SEAT, H - D / 2), (W / 2 - SEAT, H + D / 2)]]


class Lesson(Base):
    def construct(self):
        self.title("3.1", "从三维模型到三视图", "From a 3D model to three views")
        cam = ValueTracker(0.0)      # 0 = 斜着看，1 = 正对着正面看
        unf = ValueTracker(0.0)      # 0 = 投影面立着，1 = 展开到一个平面

        def scr(p):
            x, y, z = p
            c = cam.get_value()
            u = x + (1 - c) * 0.55 * y
            v = z + (1 - c) * 0.38 * y
            return np.array([u * S - 0.6, v * S - 0.2, 0])

        def on_V(q):
            return (q[0], YV, q[1])

        def on_H(q):
            a, r = unf.get_value() * PI / 2, YV - q[1]
            return (q[0], YV - r * math.cos(a), ZH - r * math.sin(a))

        def on_W(q):
            a, y = unf.get_value() * PI / 2, -q[0]
            r = YV - y
            return (XW + r * math.sin(a), YV - r * math.cos(a), q[1])

        def lines(polys, f, color, dashed=False, width=3):
            g = VGroup()
            for p in polys:
                m = VMobject(stroke_color=color, stroke_width=width).set_points_as_corners([scr(f(q)) for q in p])
                g.add(DashedVMobject(m, num_dashes=max(4, len(p) * 3)) if dashed else m)
            return g

        def plane(corners, color):
            return Polygon(*[scr(c) for c in corners], stroke_color=color, stroke_width=1.5, fill_color=color, fill_opacity=0.08)

        # 物体（线框）
        def body():
            g = VGroup()
            for y in (-W / 2, W / 2):
                g.add(lines([FRONT_V[0][3:-3]], lambda q, y=y: (q[0], y, q[1]), STEEL, width=3))
            for y in (-Wb / 2, Wb / 2):
                g.add(lines([[(-L / 2, 0), (L / 2, 0), (L / 2, tb), (-L / 2, tb), (-L / 2, 0)]], lambda q, y=y: (q[0], y, q[1]), STEEL, width=3))
            for x, z in ((-L / 2, 0), (L / 2, 0), (-L / 2, tb), (L / 2, tb), (-Ro, H), (Ro, H)):
                ys = (-Wb / 2, Wb / 2) if abs(x) > Ro else (-W / 2, W / 2)
                g.add(lines([[(x, ys[0]), (x, ys[1])]], lambda q, z=z: (q[0], q[1], z), STEEL, width=3))
            g.add(lines([FRONT_V[1]], lambda q: (q[0], -W / 2, q[1]), STEEL, width=3))
            return g

        obj = always_redraw(body)
        self.play(Create(obj), run_time=2)
        self.caption("码垛输送线滚筒的轴承座：先看它的三维形状", "A pillow block for a palletizing conveyor roller: first its 3D shape")
        pV = always_redraw(lambda: plane([(-L / 2 - 10, YV, -10), (L / 2 + 10, YV, -10), (L / 2 + 10, YV, H + Ro + 10), (-L / 2 - 10, YV, H + Ro + 10)], BLUE))
        pH = always_redraw(lambda: plane([on_H((-L / 2 - 10, -Wb / 2 - 10)), on_H((L / 2 + 10, -Wb / 2 - 10)), on_H((L / 2 + 10, YV)), on_H((-L / 2 - 10, YV))], GREEN))
        pW = always_redraw(lambda: plane([on_W((-YV, -10)), on_W((Wb / 2 + 10, -10)), on_W((Wb / 2 + 10, H + Ro + 10)), on_W((-YV, H + Ro + 10))], ORANGE))
        self.play(FadeIn(pV), FadeIn(pH), FadeIn(pW))
        self.caption("第一角画法：物体放在观察者和投影面之间，三个投影面像一个玻璃盒", "First-angle: the object sits between the viewer and the planes, like a glass box")
        fv = always_redraw(lambda: VGroup(lines(FRONT_V, on_V, WHITE), lines(FRONT_H, on_V, GREY_B, True, 2)))
        tv = always_redraw(lambda: VGroup(lines(TOP_V, on_H, WHITE), lines(TOP_H, on_H, GREY_B, True, 2)))
        lv = always_redraw(lambda: VGroup(lines(LEFT_V, on_W, WHITE), lines(LEFT_H, on_W, GREY_B, True, 2)))
        self.play(Create(fv), run_time=1.5)
        self.caption("从前往后看，投到正面：主视图", "Looking from the front onto the vertical plane: the front view")
        self.play(Create(tv), run_time=1.5)
        self.caption("从上往下看，投到水平面：俯视图", "Looking down onto the horizontal plane: the top view")
        self.play(Create(lv), run_time=1.5)
        self.caption("从左往右看，投到右边的侧面：左视图；看不见的轮廓画虚线", "Looking from the left onto the side plane: the left view; hidden edges dashed")
        self.play(FadeOut(obj))
        self.play(unf.animate.set_value(1), cam.animate.set_value(1), run_time=3.5)
        self.caption("把水平面向下、侧面向右转平：俯视图在主视图下方，左视图在右方", "Fold the planes flat: top view below the front view, left view on its right")
        al = VGroup(*[DashedLine(scr(on_V((x, 0))), scr(on_H((x, -Wb / 2))), color=YELLOW, stroke_width=2) for x in (-L / 2, L / 2)],
                    *[DashedLine(scr(on_V((L / 2, z))), scr(on_W((Wb / 2, z))), color=YELLOW, stroke_width=2) for z in (tb, H + Ro)])
        self.play(Create(al))
        self.caption("长对正、高平齐、宽相等", "Length aligned, height aligned, width equal", wait=2)
        self.play(FadeOut(al), FadeOut(pV), FadeOut(pH), FadeOut(pW))
        # 半剖：主视图右半换成剖视——剖到的实体画剖面线，虚线不再画
        cut = VGroup()
        for poly in ([(0, H + D / 2), (0, H + Ro), *arc(0, H, Ro, PI / 2, 0, 20), (Ro, tb), (L / 2, tb), (L / 2, 0), (Lh / 2 + dh / 2, 0),
                      (Lh / 2 + dh / 2, tb - 0.01), (Lh / 2 - dh / 2, tb - 0.01), (Lh / 2 - dh / 2, 0), (0, 0), (0, H - D / 2), *arc(0, H, D / 2, -PI / 2, PI / 2, 40)],):   # 剖切面过轴线，正好在轴承孔（Ø72）一段
            cut.add(Polygon(*[scr(on_V(q)) for q in poly], stroke_width=0, fill_color=STEEL, fill_opacity=0.35))
        self.play(FadeOut(fv), FadeIn(VGroup(lines(FRONT_V, on_V, WHITE))), run_time=0.6)    # 半剖以后不再画虚线
        self.play(FadeIn(cut))
        self.caption("对称的零件常用半剖视：一半画外形，一半画内部；剖到的实体画剖面线（这里用色块表示），虚线不再画", "Half section: outside on one half, inside on the other; cut material is hatched (shaded here); no hidden lines", wait=2)
        self.card([["三视图", "Three views"],
                   ["主视图、俯视图、左视图：长对正、高平齐、宽相等", "Front, top, left: length aligned, height aligned, width equal"],
                   ["我国用第一角画法（GB/T 14692），美国用第三角画法", "China uses first-angle projection (GB/T 14692); the US uses third-angle"],
                   ["图由三维模型投影生成：模型改了，视图一起变", "Views are projected from the 3D model: change the model and the views follow"]])
