"""动画 6.7.1（配图 6.7.1）：差速 AGV 不能侧移，但依次“前进 ε、左转 ε、后退 ε、右转 ε”以后，
朝向不变，位置却向右移了约 ε²。重复几次，就横着“挪”过去——这就是李括号 [V_f, V_r] 给出的新方向。"""
from manim import *
from wq_anim import *
import numpy as np
import math

SC = 9.0
O = np.array([-1.8, 1.0, 0])
E = 0.4


def P(x, y):
    return O + SC * np.array([x, y, 0])


def body(x, y, th):
    return mobile_robot(P(x, y), heading=math.degrees(th), size=0.12 * SC)


class Lesson(Base):
    def construct(self):
        self.title("6.7", "李括号：两个运动交替进行的净效果", "The Lie bracket: the net effect of alternating motions")
        ghost = body(0, 0, 0).set_opacity(0.3)
        self.add(ghost)
        st = {"x": 0.0, "y": 0.0, "th": 0.0}
        r = body(0, 0, 0)
        self.add(r)
        trail = VMobject(color=RED, stroke_width=3)
        trail.set_points_as_corners([P(0, 0), P(0, 0) + RIGHT * 0.001])
        self.add(trail)
        self.caption("差速 AGV 只能前进、后退和原地转向，不能直接侧移", "A differential AGV can drive and spin, but cannot slide sideways")
        names = [("前进 ε", "forward ε"), ("左转 ε", "turn left ε"), ("后退 ε", "back ε"), ("右转 ε", "turn right ε")]
        pts = [P(0, 0)]
        lab = zh(" ", 24, YELLOW).to_corner(UR, buff=0.5).shift(DOWN * 0.8)
        self.add(lab)
        for rep in range(2):
            for k, (kind, sgn) in enumerate((("f", 1), ("r", 1), ("f", -1), ("r", -1))):
                t = ValueTracker(0.0)
                x0, y0, th0 = st["x"], st["y"], st["th"]

                def pose(u, kind=kind, sgn=sgn, x0=x0, y0=y0, th0=th0):
                    if kind == "f":
                        return x0 + sgn * E * u * math.cos(th0), y0 + sgn * E * u * math.sin(th0), th0
                    return x0, y0, th0 + sgn * E * u

                r.add_updater(lambda m, pose=pose, t=t: m.become(body(*pose(t.get_value()))))
                lab.become(zh(names[k][0] + " / " + names[k][1], 24, YELLOW).to_corner(UR, buff=0.5).shift(DOWN * 0.8))
                self.play(t.animate.set_value(1.0), run_time=0.9 if rep == 0 else 0.5, rate_func=smooth)
                r.clear_updaters()
                st["x"], st["y"], st["th"] = pose(1.0)
                pts.append(P(st["x"], st["y"]))
                trail.set_points_as_corners(pts)
            if rep == 0:
                net = Arrow(P(0, 0), P(st["x"], st["y"]), buff=0, color=BLUE, stroke_width=6, max_tip_length_to_length_ratio=0.25)
                self.play(GrowArrow(net))
                self.caption("朝向复原，位置却向右移了约 ε² = 0.16 m", "Heading restored, yet the AGV has moved about ε² = 0.16 m to the right")
        self.caption("再做一遍，又向右挪一步：交替两个运动，得到第三个方向", "Once more, another step right: alternating two motions yields a third direction")
        self.wait(1.2)
        self.card([["李括号", "The Lie bracket"],
                   ["先 A 后 B 再撤销，净效果是 ε²[A, B]", "Do A, then B, then undo both: the net effect is ε²[A, B]"],
                   MathTex(r"e^{\varepsilon A}e^{\varepsilon B}e^{-\varepsilon A}e^{-\varepsilon B} = I + \varepsilon^2[A,B] + O(\varepsilon^3)", font_size=42)])
