"""动画 28.2.1（配图 28.2.2）：线性倒立摆与捕获点。数值与算例 28.2.2～28.2.4 相同（G1：质心高 0.692 m，ω₀ = 3.77 rad/s，
脚掌在踝关节前 125 mm、后 55 mm）。
(1) 被推到 0.3 m/s：捕获点 ξ = x + ẋ/ω₀ 在脚掌内，把零力矩点（压力中心）移到 ξ，质心停在它的正上方。
(2) 被推到 0.6 m/s：ξ 跑出脚尖，零力矩点最多到脚尖，质心越走越快；迈一步，把脚放到捕获点上，站住。
(3) 步行（俯视）：零力矩点在左右脚之间跳，质心平稳地左右摆，摆幅不到零力矩点的一半。"""
from manim import *
from wq_anim import *
import numpy as np
import math

G = 9.81
ZC = 0.692
W0 = math.sqrt(G / ZC)
TOE, HEEL = 0.125, -0.055
SC = 5.0                    # 图中 1 m 的长度


def sim(v0, step_at=None, T=1.6, dt=0.002):
    """质心 x、零力矩点 p、捕获点 ξ、脚的位置（踝关节）随时间；零力矩点取 ξ，限制在脚掌内。"""
    x, v, foot = 0.003, v0, 0.0
    out = []
    stepped = False
    for k in range(int(T / dt)):
        t = k * dt
        xi = x + v / W0
        if step_at is not None and not stepped and t >= step_at:
            foot = xi + 0.01 - 0.035          # 新脚掌的中部（踝前 35 mm）放到捕获点稍前
            stepped = True
        p = min(max(xi, foot + HEEL), foot + TOE)
        out.append((t, x, p, xi, foot))
        v += W0 * W0 * (x - p) * dt
        x += v * dt
    return np.array(out)


class Lesson(Base):
    def construct(self):
        self.title("28.2", "线性倒立摆与捕获点", "Linear inverted pendulum and capture point")
        gy = -2.0
        x0 = -2.5
        self.add(Line([-6.5, gy, 0], [6.5, gy, 0], color=GREY_B, stroke_width=3))
        X = lambda x: x0 + x * SC  # noqa: E731

        def scene_of(data, idx, show_step):
            t, x, p, xi, foot = data[int(idx.get_value())]
            g = VGroup()
            g.add(Rectangle(width=(TOE - HEEL) * SC, height=0.12, color=STEEL, fill_color=NAVY, fill_opacity=1)
                  .move_to([X(foot + (TOE + HEEL) / 2), gy + 0.06, 0]))
            if show_step and foot != 0.0:
                g.add(Rectangle(width=(TOE - HEEL) * SC, height=0.12, color=GREY_B, fill_opacity=0.2).move_to([X((TOE + HEEL) / 2), gy + 0.06, 0]))
            com = np.array([X(x), gy + ZC * SC, 0])
            g.add(Line([X(p), gy, 0], com, color=GREY_B, stroke_width=4))
            g.add(Dot(com, radius=0.22, color=YELLOW))
            g.add(Triangle(color=GREEN, fill_opacity=1).scale(0.12).move_to([X(p), gy - 0.2, 0]))
            g.add(Triangle(color=RED, fill_opacity=1).scale(0.12).rotate(PI).move_to([X(xi), gy + 0.35, 0]))
            g.add(zh(f"t = {t:.2f} s", 24, MUTED).move_to([4.6, 2.2, 0]))
            return g
        legend = VGroup(VGroup(Triangle(color=GREEN, fill_opacity=1).scale(0.1), bi(["零力矩点", "ZMP"], 20, GREEN)).arrange(RIGHT),
                        VGroup(Triangle(color=RED, fill_opacity=1).scale(0.1).rotate(PI), bi(["捕获点 ξ", "capture point ξ"], 20, RED)).arrange(RIGHT),
                        VGroup(Dot(color=YELLOW), bi(["质心", "centre of mass"], 20, YELLOW)).arrange(RIGHT)).arrange(DOWN, aligned_edge=LEFT).move_to([4.6, 0.9, 0])
        self.add(legend)
        d1 = sim(0.3)
        i1 = ValueTracker(0)
        s1 = always_redraw(lambda: scene_of(d1, i1, False))
        self.add(s1, bi(["被推到 0.3 m/s", "pushed to 0.3 m/s"], 26).move_to([4.6, -0.6, 0]))
        self.play(i1.animate.set_value(len(d1) - 1), run_time=3.0, rate_func=linear)
        self.caption("ξ = x + ẋ/ω₀ 在脚掌内：把压力中心移到捕获点，质心就停在它上方",
                     "ξ = x + ẋ/ω₀ lies inside the foot: move the centre of pressure there and the CoM stops above it", wait=2.0)
        self.clear_stage()
        self.add(Line([-6.5, gy, 0], [6.5, gy, 0], color=GREY_B, stroke_width=3), legend)
        d2 = sim(0.6, T=0.5)
        d3 = sim(0.6, step_at=0.18, T=1.6)
        i2 = ValueTracker(0)
        s2 = always_redraw(lambda: scene_of(d2, i2, False))
        lab = bi(["被推到 0.6 m/s：不迈步", "pushed to 0.6 m/s: no step"], 26).move_to([4.6, -0.6, 0])
        self.add(s2, lab)
        self.play(i2.animate.set_value(len(d2) - 1), run_time=2.0, rate_func=linear)
        self.caption("捕获点跑出了脚尖：压力中心最多到脚尖，质心越走越快，站着不动必倒",
                     "The capture point has left the toe: the CoP can go no further, the CoM speeds up and the robot falls", wait=1.5)
        self.play(FadeOut(s2), FadeOut(lab), run_time=0.3)
        i3 = ValueTracker(0)
        s3 = always_redraw(lambda: scene_of(d3, i3, True))
        lab2 = bi(["迈一步，踩到捕获点上", "step onto the capture point"], 26).move_to([4.6, -0.6, 0])
        self.add(s3, lab2)
        self.play(i3.animate.set_value(len(d3) - 1), run_time=4.0, rate_func=linear)
        self.caption("迈一步，把新的脚放到捕获点上：零力矩点追上了捕获点，质心停住",
                     "Take a step and put the new foot on the capture point: the ZMP catches it and the CoM stops", wait=2.0)
        self.clear_stage()
        # (3) 步行俯视
        yf, ts, td = 0.1185, 0.6, 0.1
        sx = 2.6
        tt = np.linspace(0, 6 * ts, 1200)

        def zmp_y(t):
            k = int(t // ts)
            tau = t - k * ts
            side = 1 if k % 2 == 0 else -1
            if tau < td:
                return -side * yf + (tau / td) * 2 * side * yf
            return side * yf
        py = np.array([zmp_y(t) for t in tt])
        # 有界解：周期 2T 的方波（含双脚支撑的斜坡）与核 (ω/2)e^{−ω|t|} 的卷积，在三个周期上近似
        dt = tt[1] - tt[0]
        ker_t = np.arange(-3, 3, dt)
        ker = W0 / 2 * np.exp(-W0 * np.abs(ker_t)) * dt
        ext = np.concatenate([py] * 3)
        yc = np.convolve(ext, ker, "same")[len(py):2 * len(py)]
        ax = Axes(x_range=[0, 3.6, 0.6], y_range=[-0.15, 0.15, 0.05], x_length=10, y_length=3.6, tips=False,
                  axis_config=dict(color=GREY_B, include_numbers=False)).move_to([0, -0.1, 0])
        self.add(ax, zh("时间", 22, MUTED).next_to(ax, DOWN, buff=0.1), zh("侧向位置 y", 22, MUTED).next_to(ax, LEFT).shift(UP * 1.5))
        zl = ax.plot_line_graph(tt, py, add_vertex_dots=False, line_color=BLUE, stroke_width=3)
        cl = ax.plot_line_graph(tt, yc, add_vertex_dots=False, line_color=YELLOW, stroke_width=4)
        self.play(Create(zl), run_time=2.0)
        self.play(Create(cl), run_time=2.5)
        self.add(bi(["零力矩点：左右脚之间跳", "ZMP: jumps between the feet"], 22, BLUE).move_to([3.8, 2.25, 0]),
                 bi(["质心：平稳地摆，幅度不到一半", "CoM: swings smoothly, less than half as far"], 22, YELLOW).move_to([-1.2, 2.25, 0]))
        self.caption("质心是零力矩点过去和将来的加权平均：规划质心要预见将来的脚步",
                     "The CoM is a weighted average of past and future ZMP: planning it means looking ahead to the next steps", wait=2.5)
        self.card([["线性倒立摆", "Linear inverted pendulum"],
                   MathTex(r"\ddot x_c = \omega_0^2(x_c - x_Z),\qquad \omega_0 = \sqrt{\mathfrak g/z_c}", font_size=42),
                   MathTex(r"\xi = x_c + \dot x_c/\omega_0,\qquad \dot\xi = \omega_0(\xi - x_Z)", font_size=42),
                   ["捕获点在脚掌内就站得住，在脚掌外就迈到捕获点", "Capture point inside the foot: stand; outside: step onto it"]])
