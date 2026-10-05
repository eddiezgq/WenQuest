"""动画 3.3.1（配图 3.3.1）：电流流入型与流出型数字量输入。PNP 传感器把输出接到 L+，电流从输入端子流入、经公共端回到 M；
NPN 传感器把输出接到 M，电流从 L+ 经公共端、输入端子流出；接错时输入两端同为 24 V，没有电流。"""
from manim import *
from wq_anim import *

LP, MP = 1.6, -1.8                       # L+ and M rails


def rails():
    g = VGroup(Line([-6, LP, 0], [6, LP, 0], color=INK, stroke_width=4), Line([-6, MP, 0], [6, MP, 0], color=INK, stroke_width=4),
               Text("L+", font=LATIN, font_size=22, color=INK).move_to([-6.4, LP, 0]), Text("M", font=LATIN, font_size=22, color=INK).move_to([-6.4, MP, 0]))
    return g


def sensor(pnp):
    box = RoundedRectangle(width=2.0, height=2.0, corner_radius=0.1, color=MUTED).move_to([-3.6, -0.1, 0])
    lab = Text("PNP" if pnp else "NPN", font=LATIN, font_size=22, color=INK).move_to([-3.6, 0.55, 0])
    sw = Line([-3.9, 0.15 if pnp else -0.35, 0], [-3.3, -0.1, 0], color=YELLOW, stroke_width=5)
    brown = Line([-4.3, LP, 0], [-4.3, 0.9, 0], color="#c08040", stroke_width=4)
    blue = Line([-4.3, -1.1, 0], [-4.3, MP, 0], color="#4080d0", stroke_width=4)
    out = Line([-3.3, -0.1, 0], [0.4, -0.1, 0], color=INK, stroke_width=4)
    y = 0.15 if pnp else -0.35                   # the output transistor sits on the L+ side (PNP) or the M side (NPN)
    inner = Line([-4.3, 0.9 if pnp else -1.1, 0], [-4.3, y, 0], color=INK, stroke_width=3)
    to_sw = Line([-4.3, y, 0], [-3.9, y, 0], color=INK, stroke_width=3)
    return VGroup(box, lab, sw, brown, blue, out, inner, to_sw)


def plc(into):
    box = RoundedRectangle(width=3.6, height=2.0, corner_radius=0.1, color=MUTED).move_to([2.2, -0.1, 0])
    lab = Text("PLC 输入", font=CJK, font_size=22, color=INK).move_to([2.2, 0.55, 0])
    term = Dot([0.4, -0.1, 0], color=INK)
    r = Rectangle(width=0.7, height=0.3, color=INK).move_to([1.2, -0.1, 0])
    tri = Triangle(color=INK).scale(0.2).rotate(-PI / 2 if into else PI / 2).move_to([2.4, -0.1, 0])
    bar = Line([2.6 if into else 2.2, -0.35, 0], [2.6 if into else 2.2, 0.15, 0], color=INK, stroke_width=4)
    wires = VGroup(Line([0.4, -0.1, 0], [0.85, -0.1, 0], color=INK), Line([1.55, -0.1, 0], [2.2, -0.1, 0], color=INK),
                   Line([2.6, -0.1, 0], [4.4, -0.1, 0], color=INK), Line([4.4, -0.1, 0], [4.4, MP if into else LP, 0], color=INK, stroke_width=4))
    com = Text("公共端 → " + ("M" if into else "L+"), font=CJK, font_size=18, color=MUTED).move_to([5.5, 0.3, 0])
    return VGroup(box, lab, term, r, tri, bar, wires, com)


def flow(points, color=RED):
    path = VMobject(color=color, stroke_width=7).set_points_as_corners(points)
    return path


class Lesson(Base):
    def construct(self):
        self.title("3.3", "电流从哪里来：两种数字量输入", "Where the current comes from: two kinds of digital input")
        r = rails()
        self.play(Create(r))
        cases = [
            (True, True, [[-4.3, LP, 0], [-4.3, 0.15, 0], [-3.9, 0.15, 0], [-3.3, -0.1, 0], [0.4, -0.1, 0], [4.4, -0.1, 0], [4.4, MP, 0]],
             "PNP 传感器把输出接到 L+：电流从输入端子流入，经公共端回到 M", "PNP: the output goes to L+; current flows into the input and back to M via the common", True),
            (False, False, [[4.4, LP, 0], [4.4, -0.1, 0], [0.4, -0.1, 0], [-3.3, -0.1, 0], [-3.9, -0.35, 0], [-4.3, -0.35, 0], [-4.3, MP, 0]],
             "NPN 传感器把输出接到 M：电流从 L+ 经公共端，从输入端子流出", "NPN: the output goes to M; current flows from L+ through the common and out of the input", True),
            (True, False, None, "PNP 传感器配公共端接 L+ 的输入：两端都是 24 V，没有电流——传感器的灯亮着，PLC 读到 0",
             "PNP sensor, input common to L+: both ends at 24 V, no current; the sensor's lamp is on, the PLC reads 0", False),
        ]
        cur = None
        for pnp, into, pts, zh_t, en_t, ok in cases:
            scene = VGroup(sensor(pnp), plc(into))
            if cur is None:
                self.play(FadeIn(scene)); cur = scene
            else:
                self.play(Transform(cur, scene))
            if ok:
                p = flow(pts)
                dot = Dot(radius=0.09, color=RED)
                self.play(Create(p), run_time=1.2)
                self.play(MoveAlongPath(dot, p, rate_func=linear, run_time=2.5))
                self.play(FadeOut(dot), run_time=0.2)
                self.caption(zh_t, en_t)
                self.play(FadeOut(p))
            else:
                v1 = Text("24 V", font=LATIN, font_size=24, color=ORANGE).move_to([0.4, 0.5, 0])
                v2 = Text("24 V", font=LATIN, font_size=24, color=ORANGE).move_to([4.4, 0.5, 0])
                cross = Cross(scale_factor=0.4, stroke_color=RED).move_to([2.4, -0.1, 0])
                self.play(FadeIn(v1), FadeIn(v2), Create(cross))
                self.caption(zh_t, en_t)
        self.card([["先看电流方向，再看接线", "Look at the current direction first"],
                   ["公共端接 M：电流流入输入端子，配 PNP 传感器", "Common to M: current flows into the input; use PNP sensors"],
                   ["公共端接 L+：电流从输入端子流出，配 NPN 传感器", "Common to L+: current flows out of the input; use NPN sensors"],
                   ["“源型”“漏型”各家叫法相反，以接线图为准", "'Sourcing' and 'sinking' mean opposite things to different makers"]])
