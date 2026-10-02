"""动画 11.4.1（配图 11.4.1）：平面 3R 臂（0.425、0.392、0.1 m）。灵巧区内的点 A：末端不动，工具朝向转一整圈，手臂都跟得上；
外缘附近的点 B：工具朝向只能在一小段范围内变化，超出范围手臂就够不着了。"""
from manim import *
from wq_anim import *
import numpy as np

L1, L2, L3 = 0.425, 0.392, 0.1
K = 2.55
O = np.array([-0.6, 0.05, 0.0])
PA = np.array([-0.45, 0.25])
PB = np.array([0.6, -0.6]) * 0.86 / np.hypot(0.6, 0.6)


def X(p):
    return O + K * np.array([p[0], p[1], 0.0])


def ik3(p, phi):
    w = p - L3 * np.array([np.cos(phi), np.sin(phi)])
    c2 = (w @ w - L1 ** 2 - L2 ** 2) / (2 * L1 * L2)
    if abs(c2) > 1:
        return None
    t2 = np.arccos(c2)
    t1 = np.arctan2(w[1], w[0]) - np.arctan2(L2 * np.sin(t2), L1 + L2 * np.cos(t2))
    e = L1 * np.array([np.cos(t1), np.sin(t1)])
    return [np.zeros(2), e, w, p]


def arm(p, phi):
    pts = ik3(p, phi)
    g = VGroup()
    tip = X(p)
    tool_dir = np.array([np.cos(phi), np.sin(phi), 0.0])
    if pts is None:
        g.add(Line(tip - K * L3 * tool_dir, tip, color=RED, stroke_width=6))
        g.add(Cross(scale_factor=0.18, stroke_color=RED).move_to(tip - K * L3 * tool_dir))
        return g
    for a, b, wdt in zip(pts[:-1], pts[1:], (12, 9, 6)):
        g.add(Line(X(a), X(b), color=BLUE, stroke_width=wdt))
    for a in pts[:-1]:
        g.add(Dot(X(a), radius=0.07, color=WHITE))
    return g


class Lesson(Base):
    def construct(self):
        self.title("11.4", "可达与灵巧：末端到得了，朝向随意吗", "Reachable and dexterous")
        rings = VGroup(Circle(K * (L1 + L2 + L3), color=BLUE_E, fill_color=BLUE_E, fill_opacity=0.25, stroke_width=2).move_to(X((0, 0))),
                       Circle(K * (L1 + L2 - L3), color=BLUE_D, fill_color=BLUE_D, fill_opacity=0.45, stroke_width=2).move_to(X((0, 0))))
        lab = VGroup(zh("浅：可达", 22, INK), zh("深：灵巧", 22, INK)).arrange(DOWN, aligned_edge=LEFT).to_corner(UR, buff=0.6).shift(DOWN * 0.8)
        self.play(FadeIn(rings), FadeIn(lab), FadeIn(Square(0.2, color=GREY_B, fill_opacity=1).move_to(X((0, 0)))), run_time=0.8)
        phi = ValueTracker(0.0)
        a = always_redraw(lambda: arm(PA, phi.get_value()))
        dA = Dot(X(PA), color=YELLOW, radius=0.08)
        self.play(FadeIn(a), FadeIn(dA), run_time=0.5)
        self.caption("A 在灵巧区内：末端不动，工具朝向转一整圈，手臂处处跟得上",
                     "A is dexterous: the tip stays put while the tool turns a full circle", wait=0)
        self.play(phi.animate.set_value(2 * PI), run_time=5.0, rate_func=linear)
        self.play(FadeOut(a), FadeOut(dA), run_time=0.4)
        phi.set_value(-1.6)
        b = always_redraw(lambda: arm(PB, phi.get_value()))
        dB = Dot(X(PB), color=YELLOW, radius=0.08)
        self.play(FadeIn(b), FadeIn(dB), run_time=0.5)
        self.caption("B 在外缘附近：只有工具大致指向外侧时才够得着，其余朝向都不行（红叉）",
                     "B is near the rim: only tool directions pointing roughly outwards work (red cross: unreachable)", wait=0)
        self.play(phi.animate.set_value(-1.6 + 2 * PI), run_time=6.0, rate_func=linear)
        self.wait(0.5)
        self.card([["工作空间", "Workspace"],
                   ["可达：至少一种朝向能到；灵巧：每一种朝向都能到", "reachable: some orientation; dexterous: every orientation"],
                   MathTex(r"|r - L_3| \ge |L_1 - L_2|,\qquad r \le L_1 + L_2 - L_3", font_size=40)])
