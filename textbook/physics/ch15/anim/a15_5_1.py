"""动画 15.5.1（配图 15.5.1）：牛顿大炮——从抛石头到绕地球转。在 200 km 高的“山顶”上水平发射炮弹（不计空气阻力和地球自转），
初速度 6.0、7.0、7.79、9.0、11.5 km/s（取自算例 15.5.1）。速度越大落得越远；7.79 km/s 时“落”的弯曲正好跟上地面的弯曲，
成了圆轨道；再大是椭圆；超过 11.0 km/s 就逃逸。轨道由数值积分得到；画面中山的高度夸大。"""
from manim import *
from wq_anim import *
import numpy as np

GM, R = 3.986004418e14, 6.371e6
R0 = R + 200e3
S = 1.3 / R                                                      # 画面单位 / m（地球半径画成 1.3）
C = np.array([-1.8, 0.55, 0])


def path(v0, tmax=60000.0, dt=5.0):
    x, y, vx, vy = 0.0, R0, v0, 0.0
    pts, t, ang, prev = [(x, y)], 0.0, 0.0, 0.0
    ax, ay = 0.0, -GM / R0 ** 2
    while t < tmax:
        vx += 0.5 * dt * ax; vy += 0.5 * dt * ay; x += dt * vx; y += dt * vy
        r3 = (x * x + y * y) ** 1.5; ax, ay = -GM * x / r3, -GM * y / r3
        vx += 0.5 * dt * ax; vy += 0.5 * dt * ay; t += dt; pts.append((x, y))
        cur = np.arctan2(x, y); ang += (cur - prev + np.pi) % (2 * np.pi) - np.pi; prev = cur
        if np.hypot(x, y) < R or np.hypot(x, y) > 3.2 * R or ang >= 2 * np.pi: break
    return np.array(pts)


SHOTS = [(6.0, GREY_B, r"6.0\ \mathrm{km/s}"), (7.0, GREEN, r"7.0\ \mathrm{km/s}"), (7.79, BLUE, r"7.79\ \mathrm{km/s}"), (9.0, RED, r"9.0\ \mathrm{km/s}"), (11.5, YELLOW, r"11.5\ \mathrm{km/s}")]
CAPS = [("速度小，炮弹很快落地", "Slow: the shell soon hits the ground"),
        ("快一些，落得更远：地面向下弯了", "Faster, it lands farther: the ground curves away beneath it"),
        ("7.79 km/s：下落的弯曲正好跟上地面的弯曲，成了圆轨道", "7.79 km/s: it falls exactly as fast as the ground curves away, a circular orbit"),
        ("再快：椭圆轨道，发射点成了近地点", "Faster still: an ellipse, with the launch point as perigee"),
        ("超过逃逸速度（这里约 11.0 km/s）：一去不回", "Beyond escape speed (about 11.0 km/s here): it never comes back")]


class Lesson(Base):
    def construct(self):
        self.title("15.5", "从抛石头到绕地球转", "From throwing a stone to orbiting the Earth")
        earth = Circle(radius=R * S, color=BLUE_E, fill_opacity=0.5, stroke_width=2).move_to(C)
        hill = Triangle(color=GREY_B, fill_opacity=0.8).scale(0.12).move_to(C + UP * (R * S + 0.06))
        self.play(FadeIn(earth), FadeIn(hill))
        legend = VGroup()
        for k, ((v, col, lab), cap) in enumerate(zip(SHOTS, CAPS)):
            P = path(v * 1000)
            pts = [C + np.array([p[0] * S, p[1] * S, 0]) for p in P[::max(1, len(P) // 300)]]
            curve = VMobject(color=col, stroke_width=4).set_points_smoothly(pts)
            self.caption(*cap, wait=0)
            self.play(Create(curve), run_time=2.2 if k < 2 else 3.0, rate_func=linear)
            legend.add(MathTex(lab, font_size=28, color=col))
            legend.arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(UR, buff=0.5).shift(DOWN * 0.6)
            self.add(legend)
            self.wait(0.8)
        self.card([["牛顿大炮", "Newton's cannon"],
                   MathTex(r"v_1 = \sqrt{\frac{GM}{r}} ,\qquad v_\mathrm{esc} = \sqrt{\frac{2GM}{r}}", font_size=44),
                   ["绕地球转的卫星一直在“下落”，只是总落不到地面", "an orbiting satellite is always falling, but never reaches the ground"],
                   ["地面附近：7.9 km/s 绕地球转，11.2 km/s 逃离地球", "near the ground: 7.9 km/s to orbit, 11.2 km/s to escape"]])
