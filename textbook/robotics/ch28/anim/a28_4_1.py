"""动画 28.4.1（配图 28.4.2）：浮动基座。数值与算例 28.4.3、28.4.5 相同（Go2 15.2 kg，示意的弹簧-阻尼腿只用来画图：
它从 0.3 m 落下的峰值力约为体重的 8.5 倍、下沉约 42 mm，与 MuJoCo 中 kp = 60 的结果 8.3 倍、43 mm 相近）。
(1) 落地：质心只能靠地面的力减速；地面的力在几十毫秒内升到体重的八九倍。
(2) 腾空：质心沿抛物线运动，腿怎么摆都改不了；对质心的角动量守恒。
(3) 摆腿翻身：大腿、小腿按方框转一圈，机身净转过约 1.7°（图中放大 5 倍），反着转则反向。"""
from manim import *
from wq_anim import *
import numpy as np
import math

M, G = 15.2, 9.81
K, ZETA = 22000.0, 0.4
H0 = 0.3


def drop_curve(dt=2e-4, T=0.55):
    """质心下落高度（相对着地点）与地面力：先自由落体 0.3 m，再压缩弹簧-阻尼腿。"""
    c = 2 * ZETA * math.sqrt(K * M)
    z, v, t = H0, 0.0, 0.0
    out = []
    while t < T:
        s = -z if z < 0 else 0.0
        sd = -v if z < 0 else 0.0
        F = max(K * s + c * sd, 0.0) if z < 0 else 0.0
        a = F / M - G
        v += a * dt
        z += v * dt
        t += dt
        out.append((t, z, F))
    return np.array(out)


def sq_point(sq, s):
    """方框路线上参数 s ∈ [0, 1) 处的点。"""
    k = min(int(s * 4), 3)
    r = s * 4 - k
    a, b = np.array(sq[k]), np.array(sq[k + 1])
    return a + (b - a) * r


class Lesson(Base):
    def construct(self):
        self.title("28.4", "浮动基座：只能靠地面的力", "Floating base: only the ground can push")
        data = drop_curve()
        gy = -2.4
        sc = 6.0
        self.add(Line([-6.5, gy, 0], [1.0, gy, 0], color=GREY_B, stroke_width=3))
        idx = ValueTracker(0)

        def dog():
            t, z, F = data[int(idx.get_value())]
            leg = 0.27 * sc * 0.6
            sink = max(-z, 0.0)
            by = gy + leg - sink * sc + max(z, 0) * sc
            g = VGroup()
            body = RoundedRectangle(width=3.0, height=0.5, corner_radius=0.15, color=STEEL, fill_color=NAVY, fill_opacity=1).move_to([-2.8, by + 0.25, 0])
            g.add(body)
            for x in (-3.9, -1.7):
                knee = [x - 0.25, (by + max(gy, by - leg)) / 2 + 0.1 * (1 + sink * 20), 0]
                foot = [x, max(gy, by - leg), 0]
                g.add(Line([x, by, 0], knee, color=GREY_B, stroke_width=6), Line(knee, foot, color=GREY_B, stroke_width=6),
                      Dot(foot, radius=0.08, color=GREY_B))
            g.add(Dot([-2.8, by + 0.25, 0], radius=0.1, color=YELLOW))
            if F > 1:
                L_ = F / (M * G) * 0.25
                for x in (-3.9, -1.7):
                    g.add(Arrow([x, gy - 0.05 - L_ / 2, 0], [x, gy - 0.05, 0], buff=0, color=GREEN, stroke_width=6) if L_ > 0.2 else VGroup())
            g.add(VGroup(zh(f"t = {t:.3f} s", 24, MUTED), zh(f"地面力 / 体重 = {F / (M * G):.1f}", 28, GREEN)).arrange(DOWN, aligned_edge=LEFT).move_to([3.8, 1.6, 0]))
            return g
        self.add(always_redraw(dog))
        # 地面力曲线
        ax = Axes(x_range=[0.2, 0.4, 0.05], y_range=[0, 10, 2], x_length=4.2, y_length=2.4, tips=False,
                  axis_config=dict(color=GREY_B, include_numbers=True, font_size=18)).move_to([3.9, -1.3, 0])
        self.add(ax, zh("地面力 / 体重", 18, MUTED).next_to(ax, UP, buff=0.05))
        sel = (data[:, 0] > 0.2) & (data[:, 0] < 0.4)
        curve = ax.plot_line_graph(data[sel, 0], data[sel, 2] / (M * G), add_vertex_dots=False, line_color=GREEN, stroke_width=3)
        self.play(idx.animate.set_value(int(0.235 / 2e-4)), run_time=1.6, rate_func=linear)
        self.play(idx.animate.set_value(len(data) - 1), Create(curve), run_time=4.0, rate_func=linear)
        self.caption("机身没有电机推着它：质心只能靠地面的力刹住，0.3 m 落下，力是体重的八九倍",
                     "Nothing drives the base: only the ground can stop the centre of mass; after a 0.3 m drop the force is eight or nine body weights", wait=2.5)
        self.clear_stage()
        # (2) 腾空：抛物线
        tt = np.linspace(0, 0.64, 60)
        x0, y0, vx, vy = -5.0, -1.5, 6.0, 3.1
        path = VMobject(color=YELLOW).set_points_smoothly([np.array([x0 + vx * t, y0 + vy * t - 0.5 * 9.81 * t * t, 0]) for t in tt])
        self.play(Create(path), run_time=1.5)
        k_ = ValueTracker(0.0)

        def flyer():
            t = k_.get_value()
            c = np.array([x0 + vx * t, y0 + vy * t - 0.5 * 9.81 * t * t, 0])
            sw = 0.8 * math.sin(2 * math.pi * t / 0.32)
            b = RoundedRectangle(width=1.6, height=0.3, corner_radius=0.1, color=STEEL, fill_color=NAVY, fill_opacity=1).move_to(c)
            legs = VGroup(*[Line(c + np.array([dx, 0, 0]), c + np.array([dx + 0.5 * math.sin(sw), -0.6 * math.cos(sw), 0]), color=GREY_B, stroke_width=5)
                            for dx in (-0.6, 0.6)])
            return VGroup(b, legs, Dot(c, radius=0.08, color=YELLOW))
        self.add(always_redraw(flyer))
        self.play(k_.animate.set_value(0.64), run_time=3.0, rate_func=linear)
        self.caption("腾空时没有地面的力：质心沿抛物线走，腿怎么摆都改不了；对质心的角动量守恒",
                     "In flight there is no ground force: the CoM follows a parabola whatever the legs do; the angular momentum about it is conserved", wait=2.5)
        self.clear_stage()
        # (3) 摆腿翻身
        ax2 = Axes(x_range=[0, 40, 10], y_range=[0, 40, 10], x_length=3.4, y_length=3.4, tips=False,
                   axis_config=dict(color=GREY_B, include_numbers=True, font_size=18)).move_to([-4.2, -0.2, 0])
        self.add(ax2, zh("大腿 / °", 18, MUTED).next_to(ax2, DOWN, buff=0.1), zh("小腿 / °", 18, MUTED).next_to(ax2, LEFT, buff=0.1).shift(UP))
        sq = [ax2.c2p(0, 0), ax2.c2p(34, 0), ax2.c2p(34, 34), ax2.c2p(0, 34), ax2.c2p(0, 0)]
        u = ValueTracker(0.0)
        dot = always_redraw(lambda: Dot(sq_point(sq, u.get_value() % 1.0), color=YELLOW))
        self.add(VMobject(color=BLUE).set_points_as_corners(sq), dot)

        def body():
            s = u.get_value()
            ph = s % 1.0
            th = 1.7 * s + 3.0 * math.sin(2 * math.pi * ph)           # 每圈净转 1.7°，中间来回摆
            b = RoundedRectangle(width=3.2, height=0.6, corner_radius=0.15, color=STEEL, fill_color=NAVY, fill_opacity=1).move_to([2.6, 0.2, 0])
            b.rotate(math.radians(5 * th), about_point=np.array([2.6, 0.2, 0]))
            return VGroup(b, zh(f"机身俯仰 {th:.1f}°（图中放大 5 倍）", 24, YELLOW).move_to([2.6, -1.6, 0]))
        self.add(always_redraw(body), DashedLine([0.6, 0.2, 0], [4.6, 0.2, 0], color=GREY_B))
        self.play(u.animate.set_value(3.0), run_time=6.0, rate_func=linear)
        self.caption("角动量为零是不可积的约束：腿按方框摆一圈，机身净转一个角度——猫就是这样在空中翻身的",
                     "Zero angular momentum is a non-integrable constraint: a loop of the legs leaves the body turned, which is how a cat rights itself", wait=2.5)
        self.card([["浮动基座", "Floating base"],
                   MathTex(r"M\dot\nu + h = S^{\mathsf T}\tau + \sum_i J_i^{\mathsf T}f_i", font_size=42),
                   MathTex(r"\frac{d}{dt}\begin{pmatrix}L_c\\ P\end{pmatrix} = \sum_i\begin{pmatrix}(p_i - c)\times f_i\\ f_i\end{pmatrix} + \begin{pmatrix}0\\ -m\mathfrak g\hat z\end{pmatrix}", font_size=36),
                   ["机身的 6 个自由度没有电机，只能靠接触力", "The base's six freedoms have no motors: only contact forces move it"]])
