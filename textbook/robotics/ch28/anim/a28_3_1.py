"""动画 28.3.1（配图 28.3.1）：四旋翼的推力、转动与配平。数值与算例 28.3.1～28.3.4 相同。
(1) 动量理论：旋翼把空气向下加速，盘面处的诱导速度 v_i = 5.0 m/s，远处 2v_i；推力 f = 2ρA v_i²。
(2) 横滚：一侧两个旋翼加力、另一侧减力，m_x = 2.34 N·m，I_xx = 0.0367 kg·m²，角加速度约 64 rad/s²；
    偏航只靠反扭矩，力臂 c_τ = 2 cm，角加速度只有约 4.3 rad/s²。
(3) 前飞：阻力随速度的平方增大（10 m/s 时约 2.5 N），机身低头，推力的水平分量平衡阻力，10 m/s 约 11°。"""
from manim import *
from wq_anim import *
import numpy as np
import math

VI = 5.0
AX, AZ = 64.0, 4.3
D10 = 2.52
W = 13.0


class Lesson(Base):
    def construct(self):
        self.title("28.3", "四旋翼：推力、转动与配平", "Quadrotor: thrust, rotation and trim")
        # (1) 动量理论
        disk = Line([-2.0, 0.6, 0], [2.0, 0.6, 0], color=STEEL, stroke_width=8)
        self.play(Create(disk), run_time=0.5)
        tube = VGroup(
            CubicBezier([-2.6, 2.3, 0], [-2.2, 1.4, 0], [-2.0, 1.0, 0], [-2.0, 0.6, 0]),
            CubicBezier([-2.0, 0.6, 0], [-1.9, -0.6, 0], [-1.45, -1.3, 0], [-1.42, -2.4, 0]),
            CubicBezier([2.6, 2.3, 0], [2.2, 1.4, 0], [2.0, 1.0, 0], [2.0, 0.6, 0]),
            CubicBezier([2.0, 0.6, 0], [1.9, -0.6, 0], [1.45, -1.3, 0], [1.42, -2.4, 0])).set_color(GREY_B).set_stroke(width=2)
        self.play(Create(tube), run_time=1.0)
        dots = VGroup(*[Dot([x, 2.2, 0], radius=0.05, color=BLUE_B) for x in np.linspace(-1.8, 1.8, 7)])
        self.add(dots)
        self.play(dots.animate.shift(DOWN * 1.6), run_time=1.2, rate_func=rate_functions.ease_in_quad)
        self.play(dots.animate.shift(DOWN * 2.9).scale(0.72), run_time=0.8, rate_func=linear)
        self.add(vec([2.6, 0.6, 0], [2.6, -0.4, 0], BLUE, r"v_i", RIGHT, 32),
                 vec([2.6, -1.6, 0], [2.6, -3.6, 0], BLUE, r"2v_i", RIGHT, 32),
                 vec([0, 0.7, 0], [0, 2.2, 0], C_F, r"f", LEFT, 34))
        self.add(MathTex(r"f = 2\rho A v_i^2,\qquad P = f v_i", font_size=40).move_to([4.4, 2.0, 0]),
                 zh("X2 悬停：v_i ≈ 5.0 m/s", 26, YELLOW).move_to([4.6, 1.1, 0]))
        self.caption("旋翼把空气向下加速：推力等于空气动量的变化率，旋翼越大、诱导速度越低越省功率",
                     "The rotor accelerates air downward: thrust equals the rate of change of the air's momentum", wait=2.5)
        self.clear_stage()
        # (2) 横滚与偏航
        ang = ValueTracker(0.0)

        def quad():
            g = VGroup()
            arm = Line([-1.8, 0, 0], [1.8, 0, 0], color=GREY_B, stroke_width=6)
            body = RoundedRectangle(width=0.8, height=0.35, corner_radius=0.1, color=STEEL, fill_color=NAVY, fill_opacity=1)
            pl = Line([-2.3, 0.2, 0], [-1.3, 0.2, 0], color=WHITE, stroke_width=4)
            pr = Line([1.3, 0.2, 0], [2.3, 0.2, 0], color=WHITE, stroke_width=4)
            fl = Arrow([-1.8, 0.25, 0], [-1.8, 2.0, 0], buff=0, color=C_F, stroke_width=6)
            fr = Arrow([1.8, 0.25, 0], [1.8, 0.9, 0], buff=0, color=C_F, stroke_width=6)
            g.add(arm, body, pl, pr, fl, fr)
            g.rotate(ang.get_value(), about_point=ORIGIN).shift(LEFT * 2.5 + DOWN * 0.6)
            return g
        q = always_redraw(quad)
        self.add(q, bi(["后视：左边两个旋翼加力、右边减力", "rear view: left rotors up, right rotors down"], 24).move_to([-2.5, 2.1, 0]))
        rd = always_redraw(lambda: zh(f"横滚角 {math.degrees(ang.get_value()):.0f}°", 26, YELLOW).move_to([-2.5, -2.3, 0]))
        self.add(rd)
        self.add(MathTex(r"\dot\omega_x \approx \frac{m_x}{I_{xx}} = \frac{2.34}{0.0367} \approx 64\ \mathrm{rad/s^2}", font_size=34).move_to([3.4, 1.4, 0]),
                 MathTex(r"\dot\omega_z \approx \frac{2c_\tau f}{I_{zz}} \approx 4.3\ \mathrm{rad/s^2}", font_size=34).move_to([3.4, 0.2, 0]),
                 bi(["偏航只靠反扭矩，力臂只有 2 cm", "yaw relies on reaction torque: a 2 cm lever arm"], 22, MUTED).move_to([3.4, -0.9, 0]))
        self.play(ang.animate.set_value(-0.35), run_time=1.0, rate_func=rate_functions.ease_in_quad)
        self.caption("横滚：力矩除以惯量就是角加速度；欧拉方程还要加上陀螺项 ω × I ω",
                     "Roll: torque divided by inertia gives the angular acceleration; Euler's equation adds the gyroscopic term ω × Iω", wait=2.5)
        self.clear_stage()
        # (3) 前飞配平
        v = ValueTracker(0.0)
        gnd = Line([-6.5, -2.6, 0], [6.5, -2.6, 0], color=GREY_B)
        self.add(gnd)

        def fwd():
            vv = v.get_value()
            D = D10 * (vv / 10) ** 2
            th = math.atan2(D, W)
            c = np.array([-1.5, 0.0, 0])
            g = VGroup()
            g.add(Line(c + np.array([-1.3 * math.cos(th), 1.3 * math.sin(th), 0]), c + np.array([1.3 * math.cos(th), -1.3 * math.sin(th), 0]),
                       color=STEEL, stroke_width=8))
            k = 0.16
            f = math.hypot(D, W)
            g.add(Arrow(c, c + k * f * np.array([math.sin(th), math.cos(th), 0]), buff=0, color=C_F, stroke_width=6))
            g.add(Arrow(c, c + k * W * DOWN, buff=0, color=WHITE, stroke_width=6))
            if D > 0.05:
                g.add(Arrow(c, c + 0.5 * k * 10 * D * LEFT, buff=0, color=RED, stroke_width=6))
            g.add(VGroup(zh(f"v = {vv:.1f} m/s", 28), zh(f"阻力 {D:.2f} N", 26, RED), zh(f"低头 {math.degrees(th):.1f}°", 28, YELLOW))
                  .arrange(DOWN, aligned_edge=LEFT).move_to([3.6, 0.8, 0]))
            return g
        self.add(always_redraw(fwd), bi(["推力", "thrust"], 22, C_F).move_to([-0.2, 2.5, 0]), bi(["重力", "weight"], 22).move_to([-0.8, -2.2, 0]),
                 bi(["阻力（放大 5 倍画）", "drag (drawn 5×)"], 22, RED).move_to([-4.8, 0.6, 0]))
        self.play(v.animate.set_value(10.0), run_time=3.0, rate_func=linear)
        self.wait(0.5)
        self.play(v.animate.set_value(15.0), run_time=1.5, rate_func=linear)
        self.caption("阻力随速度的平方增大：机身要低头，让推力的水平分量平衡阻力；逆风悬停也是这样",
                     "Drag grows with the square of speed: the body pitches down so the thrust's horizontal part balances it, as when hovering in a headwind", wait=2.5)
        self.card([["四旋翼动力学", "Quadrotor dynamics"],
                   MathTex(r"f_i = k_f\Omega_i^2,\qquad f = 2\rho A v_i^2", font_size=40),
                   MathTex(r"m_b = I_b\dot\omega_b + \omega_b \times I_b\omega_b", font_size=42),
                   MathTex(r"f\sin\theta = D,\qquad f\cos\theta = m\mathfrak g - F_{a,z}", font_size=40),
                   ["从轨迹到旋翼转速，每一步都是代数运算", "From trajectory to rotor speeds, every step is algebra"]])
