"""动画 19.3.1（配图 19.3.2）：麦克纳姆轮 AGV 的四种运动。
r = 0.075 m，l = 0.25 m，w = 0.20 m；辊子角：左前、右后 −45°，右前、左后 +45°。轮速按式 (19.3.5)：
θ̇ = H V_b，行 FL、FR、RL、RR，列 ω、v_x、v_y。每个车轮的转速用箭头画出，红色为向前、蓝色为向后。"""
from manim import *
from wq_anim import *
import numpy as np
import math

r, l, w = 0.075, 0.25, 0.20
k = l + w
H = np.array([[-k, 1, -1], [k, 1, 1], [-k, 1, 1], [k, 1, -1]]) / r
WHEELS = [(l, w, -1), (l, -w, 1), (-l, w, 1), (-l, -w, -1)]      # (x, y, tan γ)：FL、FR、RL、RR
S = 4.0                                                           # 1 m 画成 4 个单位
MOVES = [(np.array([0.0, 0.5, 0.0]), ["前进 0.5 m/s：四轮同速向前", "Forward 0.5 m/s: all four wheels forward"]),
         (np.array([0.0, 0.0, 0.3]), ["向左侧移 0.3 m/s：对角两轮向前，另两轮向后", "Sideways left 0.3 m/s: one diagonal forward, the other back"]),
         (np.array([0.0, 0.3, 0.3]), ["斜行：只有一条对角线上的两个轮子转", "Diagonal: only the wheels on one diagonal turn"]),
         (np.array([1.0, 0.0, 0.0]), ["原地逆时针转 1 rad/s：左侧向后，右侧向前", "Spin 1 rad/s anticlockwise: left side back, right side forward"])]


def chassis(q):
    x, y, f = q
    c = np.array([x, y, 0]) * S
    body = Rectangle(width=(2 * l + 0.12) * S, height=(2 * w + 0.02) * S, color=STEEL, fill_color=NAVY, fill_opacity=1, stroke_width=3)
    g = VGroup(body)
    for wx, wy, sg in WHEELS:
        yy = wy + (0.03 if wy > 0 else -0.03)
        wh = Rectangle(width=2 * r * S, height=0.05 * S, color=GREY_B, fill_color=GREY_D, fill_opacity=1, stroke_width=2).move_to([wx * S, yy * S, 0])
        g.add(wh)
        for t in np.linspace(-0.6, 0.6, 4):
            p = np.array([wx + t * r, yy, 0]) * S
            d = np.array([1, sg, 0]) * 0.035 * S         # 接地辊子轴线方向 (cos γ, sin γ) ∝ (1, tan γ)
            g.add(Line(p - d, p + d, color=WHITE, stroke_width=2))
    nose = Triangle(color=YELLOW, fill_opacity=1).scale(0.12).rotate(-PI / 2).move_to([(l + 0.03) * S, 0, 0])
    g.add(nose)
    g.rotate(f, about_point=ORIGIN).shift(c)
    return g


def speeds_view(q, th):
    x, y, f = q
    g = VGroup()
    Rm = np.array([[math.cos(f), -math.sin(f)], [math.sin(f), math.cos(f)]])
    for (wx, wy, sg), t in zip(WHEELS, th):
        yy = wy + (0.12 if wy > 0 else -0.12)
        p = Rm @ np.array([wx, yy]) + np.array([x, y])
        d = Rm @ np.array([1.0, 0.0])
        a = np.array([p[0], p[1], 0]) * S
        if abs(t) > 1e-6:
            e = a + np.array([d[0], d[1], 0]) * 0.07 * t
            g.add(Arrow(a, e, buff=0, color=RED if t > 0 else BLUE, stroke_width=5, max_tip_length_to_length_ratio=0.35))
        g.add(MathTex(("%.1f" % (t + 0.0)).replace("-0.0", "0.0"), font_size=26, color=RED if t > 0 else (BLUE if t < 0 else GREY_B)).move_to(a + np.array([0, 0.35 if wy > 0 else -0.35, 0])))
    return g


class Lesson(Base):
    def construct(self):
        self.title("19.3", "麦克纳姆轮 AGV 的四种运动", "Four motions of a mecanum AGV")
        q = np.array([-0.6, -0.25, 0.0])
        car = chassis(q)
        self.play(FadeIn(car), run_time=0.8)
        self.caption("四个麦克纳姆轮，接地辊子的轴线（白线）与轮平面成 ±45°", "Four mecanum wheels; the floor rollers (white) sit at ±45° to the wheel planes", wait=0.8)
        eq = MathTex(r"\dot\theta = H\,\mathcal V_b", font_size=44).move_to([4.6, 2.3, 0])
        self.play(Write(eq), run_time=0.6)
        for V, cap in MOVES:
            th = H @ V
            arr = speeds_view(q, th)
            self.play(FadeIn(arr), run_time=0.4)
            self.caption(cap[0], cap[1], wait=0)
            tk = ValueTracker(0.0)
            q0 = q.copy()

            def pose(t, q0=q0, V=V):
                wv, vx, vy = V
                f0 = q0[2]
                if abs(wv) < 1e-9:
                    c, s = math.cos(f0), math.sin(f0)
                    return np.array([q0[0] + t * (c * vx - s * vy), q0[1] + t * (s * vx + c * vy), f0])
                return np.array([q0[0], q0[1], f0 + wv * t])

            T_move = 1.3 if abs(V[0]) < 1e-9 else 1.57
            moving = always_redraw(lambda: VGroup(chassis(pose(tk.get_value())), speeds_view(pose(tk.get_value()), th)))
            self.add(moving)
            self.play(FadeOut(car), FadeOut(arr), run_time=0.1)
            self.play(tk.animate.set_value(T_move), run_time=2.6, rate_func=linear)
            q = pose(T_move)
            car = chassis(q)
            self.add(car)
            self.play(FadeOut(moving), run_time=0.1)
            self.wait(0.4)
            q = np.array([-0.6, -0.25, 0.0])
            self.play(Transform(car, chassis(q)), run_time=0.6)
        self.card([["瑞典轮的辊子在侧向“让开”，车可以任意横移", "The rollers give way sideways: the AGV can move in any direction"],
                   MathTex(r"\dot\theta = \frac{a^{\mathsf T}v_P}{r\cos\gamma}", font_size=44),
                   ["四个轮子三个自由度：前两轮之和等于后两轮之和", "Four wheels, three freedoms: front pair sum equals rear pair sum"]])
