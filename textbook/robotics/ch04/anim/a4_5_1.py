"""动画 4.5.1（配图 4.5.1）：万向支架的中环逐渐转到 90°，内环轴逐渐与外环轴重合；此后转外环与转内环效果相同。"""
from manim import *
from wq_anim import *
import numpy as np
import math

O = np.array([0.0, -0.5, 0])
SC = 2.2


def ring(a, b, r, color, width=7):
    pts = [proj3(r * (math.cos(t) * a + math.sin(t) * b), O, SC) for t in np.linspace(0, 2 * math.pi, 100)]
    return VMobject(color=color, stroke_width=width).set_points_smoothly(pts)


def gimbal(theta_deg, psi=25, phi=30):
    Ro = rot_z(psi)
    y_o, z = Ro[:, 1], np.array([0, 0, 1.0])
    Rm = Ro @ rot_y(-theta_deg)
    x_m = Rm[:, 0]
    z_i = (Rm @ rot_x(phi))[:, 2]
    g = VGroup(ring(y_o, z, 1.0, BLUE), ring(x_m, y_o, 0.8, GREEN), ring(x_m, z_i, 0.6, RED))
    for v, L, col in ((z, 1.3, BLUE), (y_o, 1.15, GREEN), (x_m, 0.95, RED)):
        g.add(DashedLine(proj3(-L * v, O, SC), proj3(L * v, O, SC), color=col, stroke_width=3))
    return g


class Lesson(Base):
    def construct(self):
        self.title("4.5", "万向节锁", "Gimbal lock")
        th = ValueTracker(30.0)
        g = always_redraw(lambda: gimbal(th.get_value()))
        legend = VGroup(zh("外环轴", 22, BLUE), zh("中环轴", 22, GREEN), zh("内环轴", 22, RED)).arrange(DOWN, aligned_edge=LEFT).to_corner(UR, buff=0.8).shift(DOWN * 0.6)
        self.add(g, legend)
        self.caption("三环万向支架：三根转轴各不相同，平台可以朝向任何方向", "Three gimbals: three different axes, any orientation is reachable")
        readout_ = always_redraw(lambda: zh("中环转角 %d°" % round(th.get_value()), 28, YELLOW).to_corner(UL, buff=0.6).shift(DOWN * 1.0))
        self.add(readout_)
        self.caption("中环逐渐转向 90°……", "The middle gimbal turns towards 90°...", wait=0)
        self.play(th.animate.set_value(90), run_time=4, rate_func=smooth)
        self.caption("内环轴与外环轴重合：转外环和转内环效果相同，失去一个自由度", "Inner and outer axes coincide: one degree of freedom is lost")
        self.wait(2)
        self.card([["万向节锁", "Gimbal lock"],
                   ["欧拉角在中间角为 ±90° 时（ZYX）只确定 ψ − φ", "ZYX angles at ±90° pitch only fix ψ − φ"],
                   ["计算内部用旋转矩阵或四元数", "compute with rotation matrices or quaternions"]])
