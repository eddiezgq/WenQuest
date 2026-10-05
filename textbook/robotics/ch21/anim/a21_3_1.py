"""动画 21.3.1（配图 21.3.2）：从机尾看，X2 横移 2 m（算例 21.3.2）。
横滚角走对称梯形曲线：以 2 rad/s 转到 25°，保持 h = 0.3471 s（程序 21.3.1 求得），转到 −25°，保持 h，再转回 0；
侧向加速度 𝔤 tan φ。上方是侧向加速度上限相同（𝔤 tan 25°）、不必倾斜的假想全驱动飞行器，先加速后减速，用时 2√(d/a)。
放慢 4 倍播放；1 m 画成 3 个单位。"""
from manim import *
from wq_anim import *
import numpy as np
import math

G, D = 9.81, 2.0
PM, WM, H = math.radians(25), 2.0, 0.3471
TR = PM / WM
TU = 4 * TR + 2 * H
AC = G * math.tan(PM)
TI = 2 * math.sqrt(D / AC)
SC, SLOW = 3.0, 4.0


def phi_of(t):
    if t < TR:
        return WM * t
    if t < TR + H:
        return PM
    if t < 3 * TR + H:
        return PM - WM * (t - TR - H)
    if t < 3 * TR + 2 * H:
        return -PM
    if t < TU:
        return -PM + WM * (t - 3 * TR - 2 * H)
    return 0.0


# 预先积分 X2 的侧向位移（梯形法，步长 1 ms）
TS = np.arange(0, TU + 0.6, 0.001)
AA = np.array([G * math.tan(phi_of(t)) for t in TS])
VV = np.concatenate([[0], np.cumsum((AA[1:] + AA[:-1]) / 2 * 0.001)])
YY = np.concatenate([[0], np.cumsum((VV[1:] + VV[:-1]) / 2 * 0.001)])


def y_under(t):
    return float(np.interp(t, TS, YY))


def y_ideal(t):
    if t < TI / 2:
        return 0.5 * AC * t * t
    if t < TI:
        return D - 0.5 * AC * (TI - t) ** 2
    return D


def drone(c, ang, col, arrow_col):
    R = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
    g = VGroup()
    for sx in (-1, 1):
        e = R @ np.array([sx * 0.8, 0.0])
        g.add(Line(c, c + np.r_[e, 0], color=col, stroke_width=7))
        p1 = c + np.r_[R @ np.array([sx * 0.8 - 0.32, 0.1]), 0]
        p2 = c + np.r_[R @ np.array([sx * 0.8 + 0.32, 0.1]), 0]
        g.add(Line(p1, p2, color=col, stroke_width=5))
    g.add(Ellipse(width=0.5, height=0.3, color=col, fill_color=NAVY, fill_opacity=1).rotate(ang).move_to(c))
    zb = np.r_[R @ np.array([0.0, 1.0]), 0]
    g.add(Arrow(c, c + 1.1 * zb, buff=0, color=arrow_col, stroke_width=5, max_tip_length_to_length_ratio=0.2))
    return g


class Lesson(Base):
    def construct(self):
        self.title("21.3", "横移 2 m：欠驱动要先转身", "Sliding 2 m sideways: turn first, then move")
        x0 = -3.0
        lanes = (1.3, -1.2)
        for yl, txt in zip(lanes, ("假想全驱动\n（直接侧推）", "X2\n（倾斜推力）")):
            self.add(DashedLine([x0 - 0.5, yl - 0.55, 0], [x0 + SC * D + 0.5, yl - 0.55, 0], color=GREY_D, stroke_width=1.5))
            self.add(Text(txt, font=CJK, font_size=22, color=MUTED).move_to([-6.7, yl, 0], aligned_edge=LEFT))
            for k in (0, 1, 2):
                self.add(Text(f"{k} m", font=CJK, font_size=18, color=GREY_C).move_to([x0 + SC * k, yl - 0.8, 0]))
        tt = ValueTracker(0.0)

        def scene():
            t = tt.get_value()
            g = VGroup()
            g.add(drone(np.array([x0 + SC * y_ideal(t), lanes[0], 0]), 0.0, GREY_B, GREY_B))
            ph = phi_of(t)
            # 从机尾看：向右倾（φ > 0）时右侧下沉，屏幕上顺时针转
            g.add(drone(np.array([x0 + SC * y_under(t), lanes[1], 0]), -ph, STEEL, BLUE))
            info = VGroup(Text(f"t = {t:.2f} s", font=CJK, font_size=24, color=INK),
                          Text(f"横滚角 φ = {math.degrees(ph):+.1f}°".replace("-", "−"), font=CJK, font_size=24, color=YELLOW))
            info.arrange(DOWN, aligned_edge=LEFT, buff=0.1).to_corner(UR, buff=0.45).shift(DOWN * 0.5)
            g.add(info)
            if t >= TI - 1e-9:
                g.add(Text(f"到达 {TI:.2f} s", font=CJK, font_size=22, color=GREY_B).move_to([x0 + SC * D + 2.4, lanes[0] + 0.5, 0]))
            if t >= TU - 1e-9:
                g.add(Text(f"到达 {TU:.2f} s", font=CJK, font_size=22, color=STEEL).move_to([x0 + SC * D + 2.4, lanes[1] + 0.5, 0]))
            return g

        self.add(always_redraw(scene))
        self.caption("两者的侧向加速度上限相同：全驱动的能立即侧推，X2 要先把机身转到 25°",
                     "Same lateral-acceleration limit: the fully actuated craft pushes at once; X2 must first roll to 25°", wait=0.5)
        self.play(tt.animate.set_value(TR + H), run_time=SLOW * (TR + H), rate_func=linear)
        self.caption("中途要转过 50° 才能反过来减速：这段转动的时间就是欠驱动的代价",
                     "Midway X2 must roll through 50° before it can brake: that time is the price of underactuation", wait=0)
        self.play(tt.animate.set_value(3 * TR + H), run_time=SLOW * 2 * TR + 1.0, rate_func=linear)
        self.play(tt.animate.set_value(TU + 0.1), run_time=SLOW * (H + TR + 0.1), rate_func=linear)
        self.caption("X2 多用约 0.24 s（18%）。横滚转得越快，越接近全驱动的极限",
                     "X2 needs about 0.24 s (18%) more; the faster it rolls, the closer it gets to the limit", wait=2.5)
        self.card([["欠驱动：位置要通过姿态来带动", "Underactuated: position is driven through attitude"],
                   MathTex(r"x_b\cdot(\ddot p + \mathfrak g\hat z) = 0,\qquad y_b\cdot(\ddot p + \mathfrak g\hat z) = 0", font_size=40),
                   MathTex(r"\ddot y = \mathfrak g\tan\varphi,\qquad T_{\text{full}} = 2\sqrt{d/a}", font_size=40),
                   ["只能水平地悬停；要相机不倾斜，就得加云台", "It can hover only level; a gimbal keeps the camera steady"]])
