"""动画 4.7.1（配图 4.7.1）：同一个工具从 R0 = I 转到 R1（ZYX 欧拉角 90°, 45°, 90°），
左边按欧拉角插值，右边按球面线性插值（Slerp），同时开始、同时结束；z 轴指向的轨迹画在球面上。"""
from manim import *
from wq_anim import *
import numpy as np
import math

SC = 1.9


def q_of(R):
    q0 = 0.5 * math.sqrt(max(0.0, 1 + np.trace(R)))
    return np.array([q0, (R[2, 1] - R[1, 2]) / (4 * q0), (R[0, 2] - R[2, 0]) / (4 * q0), (R[1, 0] - R[0, 1]) / (4 * q0)])


def R_of(q):
    q0, q1, q2, q3 = q / np.linalg.norm(q)
    return np.array([[1 - 2 * (q2 * q2 + q3 * q3), 2 * (q1 * q2 - q0 * q3), 2 * (q1 * q3 + q0 * q2)],
                     [2 * (q1 * q2 + q0 * q3), 1 - 2 * (q1 * q1 + q3 * q3), 2 * (q2 * q3 - q0 * q1)],
                     [2 * (q1 * q3 - q0 * q2), 2 * (q2 * q3 + q0 * q1), 1 - 2 * (q1 * q1 + q2 * q2)]])


QA, QB = q_of(np.eye(3)), q_of(rot_z(90) @ rot_y(45) @ rot_x(90))
OM = math.acos(min(1.0, float(QA @ QB)))


def euler(t):
    return rot_z(90 * t) @ rot_y(45 * t) @ rot_x(90 * t)


def slerp(t):
    return R_of((math.sin((1 - t) * OM) * QA + math.sin(t * OM) * QB) / math.sin(OM))


def sphere(o):
    g = VGroup(Circle(radius=SC, color=GREY_D, stroke_width=2).move_to(o))
    for lat in (-0.5, 0, 0.5):
        pts = [proj3(np.array([math.cos(a) * math.cos(lat), math.sin(a) * math.cos(lat), math.sin(lat)]), o, SC)
               for a in np.linspace(0, 2 * math.pi, 80)]
        g.add(VMobject(color=GREY_D, stroke_width=1.5).set_points_smoothly(pts))
    return g


class Lesson(Base):
    def construct(self):
        self.title("4.7", "姿态插值：欧拉角插值与 Slerp", "Orientation interpolation: Euler angles vs Slerp")
        oL, oR = np.array([-3.4, -0.5, 0]), np.array([3.4, -0.5, 0])
        self.add(sphere(oL), sphere(oR), zh("欧拉角插值", 26, RED).move_to(oL + UP * 2.7),
                 zh("球面线性插值（Slerp）", 26, ORANGE).move_to(oR + UP * 2.7))
        t = ValueTracker(0.0)
        frames = always_redraw(lambda: VGroup(frame3(oL, euler(t.get_value()), length=SC, scale=1.0),
                                              frame3(oR, slerp(t.get_value()), length=SC, scale=1.0)))
        trails = always_redraw(lambda: VGroup(
            VMobject(color=RED, stroke_width=6).set_points_smoothly(
                [proj3(euler(s)[:, 2], oL, SC) for s in np.linspace(0, max(t.get_value(), 0.01), 60)]),
            VMobject(color=ORANGE, stroke_width=6).set_points_smoothly(
                [proj3(slerp(s)[:, 2], oR, SC) for s in np.linspace(0, max(t.get_value(), 0.01), 60)])))
        self.add(trails, frames)
        self.caption("两个工具同时出发、同时到达，起点和终点姿态相同", "Same start, same end, same duration", wait=1)
        self.play(t.animate.set_value(1.0), run_time=6, rate_func=linear)
        self.caption("欧拉角插值多转了一成多，而且忽快忽慢；Slerp 绕一根轴匀速转过", "Euler angles: ~11% longer and uneven; Slerp: one axis, constant speed")
        self.wait(1.5)
        self.card([["球面线性插值", "Spherical linear interpolation"],
                   MathTex(r"\mathrm{slerp}(q_A,q_B;t)=\frac{\sin((1-t)\Omega)}{\sin\Omega}q_A+\frac{\sin(t\Omega)}{\sin\Omega}q_B", font_size=36),
                   ["最短路径、匀速；先检查 q_A·q_B 的正负号", "shortest and uniform; check the sign of q_A·q_B first"]])
