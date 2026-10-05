"""动画 19.4.1（配图 19.4.1）：阿克曼转向。
牵引式 AGV：轴距 L = 1.2 m，前轮距 w = 0.8 m。内侧前轮的转角 δi 由 0 增到 35°，外侧前轮按阿克曼条件
cot δo − cot δi = w/L 转动，四条轴线始终交于后轴延长线上的瞬心；随后车绕瞬心转过一段，四个车轮各走各的圆；
最后改为两前轮平行转向，外侧前轮的速度方向与轮平面出现侧偏角。"""
from manim import *
from wq_anim import *
import numpy as np
import math

L, W = 1.2, 0.8
S = 1.5
O = np.array([-3.2, -1.45, 0])


def P(x, y):
    return O + S * np.array([x, y, 0])


def wheel(c, ang, color=GREY_B):
    return Rectangle(width=0.32 * S, height=0.12 * S, color=color, fill_color=GREY_D, fill_opacity=1, stroke_width=2).rotate(ang).move_to(c)


def outer(di):
    return math.atan(1 / (1 / math.tan(di) + W / L)) if di > 1e-6 else 0.0


def car(q, di, do, alpha=1.0):
    """车在位姿 q = (x, y, φ)（后轴中点）处，两前轮转角 di（左）、do（右）。"""
    x, y, f = q
    Rm = np.array([[math.cos(f), -math.sin(f)], [math.sin(f), math.cos(f)]])
    W_ = lambda px, py: P(*(Rm @ np.array([px, py]) + np.array([x, y])))
    body = Polygon(*[W_(px, py) for px, py in ((-0.3, -0.5), (1.5, -0.5), (1.5, 0.5), (-0.3, 0.5))],
                   color=STEEL, fill_color=NAVY, fill_opacity=0.7 * alpha, stroke_width=3, stroke_opacity=alpha)
    g = VGroup(body, wheel(W_(0, W / 2), f), wheel(W_(0, -W / 2), f),
               wheel(W_(L, W / 2), f + di, YELLOW), wheel(W_(L, -W / 2), f + do, YELLOW))
    return g


class Lesson(Base):
    def construct(self):
        self.title("19.4", "阿克曼转向", "Ackermann steering")
        d = ValueTracker(0.0)

        def scene():
            di = d.get_value()
            do = outer(di)
            g = VGroup(car((0, 0, 0), di, do))
            g.add(DashedLine(P(0, -0.7), P(0, 2.9), color=RED, dash_length=0.1))
            if di > 0.02:
                R = L / math.tan(di) + W / 2
                for (x, y), a in (((L, W / 2), di), ((L, -W / 2), do)):
                    g.add(DashedLine(P(x, y), P(0, R), color=RED, dash_length=0.1))
                g.add(DashedLine(P(L, 0), P(0, R), color=PURPLE_B, dash_length=0.06))
                g.add(Dot(P(0, R), radius=0.09, color=YELLOW))
            return g

        def readout():
            di = d.get_value()
            do = outer(di)
            R = L / math.tan(di) + W / 2 if di > 0.02 else float("inf")
            rows = VGroup(MathTex(r"\delta_i = %.1f^\circ" % math.degrees(di), font_size=34, color=YELLOW),
                          MathTex(r"\delta_o = %.1f^\circ" % math.degrees(do), font_size=34, color=YELLOW),
                          MathTex(r"R = %s" % ("%.2f\\ \\mathrm{m}" % R if R < 1e3 else r"\infty"), font_size=34))
            return rows.arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to([4.6, 0.8, 0])

        self.add(always_redraw(scene), always_redraw(readout))
        eq = MathTex(r"\cot\delta_o - \cot\delta_i = \frac{w}{L}", font_size=40).move_to([4.6, 2.4, 0])
        self.play(Write(eq), run_time=0.8)
        self.caption("方向盘转动：内侧前轮转得多，外侧转得少，四条轴线交于后轴线上一点",
                     "Turning the wheel: the inner wheel turns more, the outer less, and four axles meet on the rear-axle line", wait=0)
        self.play(d.animate.set_value(math.radians(35)), run_time=4.0, rate_func=smooth)
        self.caption("紫线：自行车模型的虚拟前轮，tan δ = L/R", "Purple: the bicycle model's virtual front wheel, tan δ = L/R", wait=1.0)
        # ---------- 绕瞬心转动，四个车轮各走一个圆
        di = math.radians(35)
        do = outer(di)
        R = L / math.tan(di) + W / 2
        self.clear_stage()
        self.add(eq)
        c = np.array([0, R])
        tracks = VGroup()
        for (x, y), col in (((0, W / 2), GREEN), ((0, -W / 2), GREEN), ((L, W / 2), YELLOW), ((L, -W / 2), YELLOW)):
            rr = math.hypot(x - c[0], y - c[1])
            a0 = math.atan2(y - c[1], x - c[0])
            tracks.add(ParametricFunction(lambda t, rr=rr, a0=a0: P(c[0] + rr * math.cos(a0 + t), c[1] + rr * math.sin(a0 + t)),
                                          t_range=[0, 1.1], color=col, stroke_width=3))
        th = ValueTracker(0.0)

        def moving():
            t = th.get_value()
            x, y = c[0] + R * math.sin(t), c[1] - R * math.cos(t)
            return car((x, y, t), di, do)

        mv = always_redraw(moving)
        self.add(mv, Dot(P(*c), radius=0.09, color=YELLOW))
        self.caption("车绕瞬心转动：每个车轮走自己的圆，后轮在前轮的内侧（内轮差）",
                     "The car turns about the ICR; each wheel runs its own circle, rear wheels inside the front ones", wait=0)
        self.play(th.animate.set_value(1.1), Create(tracks), run_time=4.0, rate_func=linear)
        self.wait(0.6)
        # ---------- 平行转向的侧偏角
        self.clear_stage()
        self.add(eq)
        di = math.radians(30)
        do = outer(di)
        R = L / math.tan(di) + W / 2
        par = car((0, 0, 0), di, di)
        pf = P(L, -W / 2)
        vdir = np.array([math.cos(do), math.sin(do), 0])
        wdir = np.array([math.cos(di), math.sin(di), 0])
        v_arrow = Arrow(pf, pf + 3.0 * vdir, buff=0, color=GREEN, stroke_width=5)
        w_line = DashedLine(pf, pf + 3.0 * wdir, color=YELLOW, dash_length=0.08)
        ang = Angle(Line(pf, pf + 3.0 * vdir), Line(pf, pf + 3.0 * wdir), radius=2.2, color=RED)
        lab = MathTex(r"%.1f^\circ" % math.degrees(di - do), font_size=40, color=RED).next_to(ang, RIGHT, buff=0.15)
        self.play(FadeIn(par), run_time=0.5)
        self.caption("两前轮都转 30°（平行转向）：外侧前轮的速度方向（绿）与轮平面（黄）差 7.4°，轮胎被拖着侧滑",
                     "Both front wheels at 30°: the outer wheel's velocity (green) and its plane (yellow) differ by 7.4°; the tyre is dragged", wait=0)
        self.play(GrowArrow(v_arrow), Create(w_line), Create(ang), Write(lab), run_time=1.5)
        self.wait(1.5)
        self.card([["阿克曼条件：四条轮轴线交于一点", "Ackermann condition: the four wheel axles meet at one point"],
                   MathTex(r"\cot\delta_o - \cot\delta_i = \frac{w}{L},\qquad \dot\varphi = \frac{v}{L}\tan\delta", font_size=42),
                   ["车不动就不能转向：汽车不能原地转", "No turning without moving: a car cannot spin on the spot"]])
