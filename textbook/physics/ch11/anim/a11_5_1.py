"""动画 11.5.1（配图 11.5.2）：在质心系里看碰撞。上：实验室参考系，m₁ = 1 kg 以 2.0 m/s 撞向静止的 m₂ = 3 kg（弹性碰撞），
质心（黄色）以 v_c = 0.5 m/s 匀速前进，碰撞前后不变；下：跟着质心走的参考系，两球相向而来（+1.5、−0.5 m/s），总动量为零，
碰后各自原速反弹。"""
from manim import *
from wq_anim import *
import numpy as np

M1, M2, V1 = 1.0, 3.0, 2.0
VC = M1 * V1 / (M1 + M2)
V1A, V2A = (M1 - M2) / (M1 + M2) * V1, 2 * M1 / (M1 + M2) * V1       # 弹性碰撞后（实验室系）
R1, R2 = 0.22, 0.32
X1, X2 = -2.6, 0.0                                                     # 初始位置（m，画面单位 1 m = 1.6）
S = 1.6
TC = (X2 - R2 / S - X1 - R1 / S) / V1                                  # 接触时刻


def pos(t):
    if t < TC:
        return X1 + V1 * t, X2
    return X1 + V1 * TC + V1A * (t - TC), X2 + V2A * (t - TC)


class Lesson(Base):
    def construct(self):
        self.title("11.5", "在质心系里看碰撞", "A collision seen from the centre of mass")
        t = ValueTracker(0.0)
        y_lab, y_cm = 1.2, -1.3
        tr_lab = Line(np.array([-6.8, y_lab - 0.4, 0]), np.array([6.8, y_lab - 0.4, 0]), color=GREY_D)
        tr_cm = Line(np.array([-6.8, y_cm - 0.4, 0]), np.array([6.8, y_cm - 0.4, 0]), color=GREY_D)
        lab_l = bi(["实验室参考系", "lab frame"], size=20).move_to(np.array([-5.4, y_lab + 0.8, 0]))
        cm_l = bi(["质心参考系", "centre-of-mass frame"], size=20).move_to(np.array([-5.4, y_cm + 0.8, 0]))
        self.play(Create(tr_lab), Create(tr_cm), FadeIn(lab_l), FadeIn(cm_l))

        def balls(frame):
            def make():
                tt = t.get_value(); a, b = pos(tt); xc = (M1 * a + M2 * b) / (M1 + M2)
                off = 0 if frame == "lab" else -xc
                y = y_lab if frame == "lab" else y_cm
                g = VGroup(Circle(radius=R1, color=BLUE, fill_opacity=0.9).move_to(np.array([S * (a + off) - 1.0 * (frame == "lab"), y, 0])),
                           Circle(radius=R2, color=RED, fill_opacity=0.9).move_to(np.array([S * (b + off) - 1.0 * (frame == "lab"), y, 0])),
                           Triangle(color=YELLOW, fill_opacity=1).scale(0.12).move_to(np.array([S * (xc + off) - 1.0 * (frame == "lab"), y - 0.55, 0])))
                return g
            return always_redraw(make)

        self.add(balls("lab"), balls("cm"))
        note = bi(["黄三角：质心", "yellow triangle: centre of mass"], size=18, color=YELLOW).move_to(np.array([4.6, 2.6, 0]))
        self.play(FadeIn(note))
        self.caption("实验室系：小球撞向静止的大球；质心匀速前进，碰撞前后都不变", "Lab frame: the small ball hits the big one at rest; the centre of mass moves steadily, before and after", wait=0)
        self.play(t.animate.set_value(TC), run_time=3, rate_func=linear)
        self.caption("质心系：两球相向而来，总动量为零；弹性碰撞后各自原速反弹", "CM frame: the balls approach with zero total momentum; elastically, each simply bounces back at its own speed", wait=0)
        self.play(t.animate.set_value(TC + 2.2), run_time=4, rate_func=linear)
        self.wait(1.0)
        self.card([["质心系", "The centre-of-mass frame"],
                   MathTex(r"v_\mathrm c = \frac{m_1v_1 + m_2v_2}{m_1 + m_2}, \qquad m_1u_1 + m_2u_2 = 0", font_size=40),
                   ["碰撞不改变质心的速度", "a collision does not change the velocity of the centre of mass"],
                   ["在质心系里，弹性碰撞只把速度反向，完全非弹性碰撞后两者都静止", "in the CM frame an elastic collision just reverses the velocities; a perfectly inelastic one leaves both at rest"]])
