"""动画 10.5.1（配图 10.5.3）：SCARA 涂胶的工具尖沿椭圆运动（算例 10.2.1 的参数化），四个画面同时显示
同一支速度箭头 v 与加速度箭头 a，分别在直角、柱面、球面、自然坐标的局部基上分解；箭头相同，分量各异。"""
from manim import *
from wq_anim import *
import numpy as np
import math

XC, YC, Z0 = 0.40, 0.05, 0.10
A, B = 0.12, 0.08
W = math.pi / 2
CAM = np.array([0.40, 0.05, 0.40])
K = 9.0                                        # 画面中 1 m 画成 9 个单位
CENTERS = [np.array([-3.4, 0.8, 0]), np.array([3.4, 0.8, 0]), np.array([-3.4, -1.45, 0]), np.array([3.4, -1.45, 0])]
NAMES = [("直角", "Cartesian"), ("柱面", "cylindrical"), ("球面", "spherical"), ("自然", "natural")]


def state(t):
    p = np.array([XC + A * math.cos(W * t), YC + B * math.sin(W * t), Z0])
    v = np.array([-A * W * math.sin(W * t), B * W * math.cos(W * t), 0.0])
    a = np.array([-A * W * W * math.cos(W * t), -B * W * W * math.sin(W * t), 0.0])
    return p, v, a


def basis(k, p, v, a):
    if k == 0:
        return [np.array([1.0, 0, 0]), np.array([0, 1.0, 0])], [r"e_x", r"e_y"]
    if k == 1:
        ph = math.atan2(p[1], p[0])
        return [np.array([math.cos(ph), math.sin(ph), 0]), np.array([-math.sin(ph), math.cos(ph), 0])], [r"e_\rho", r"e_\varphi"]
    if k == 2:
        d = p - CAM
        r = np.linalg.norm(d)
        th, ph = math.atan2(math.hypot(d[0], d[1]), d[2]), math.atan2(d[1], d[0])
        er = d / r
        et = np.array([math.cos(th) * math.cos(ph), math.cos(th) * math.sin(ph), -math.sin(th)])
        ep = np.array([-math.sin(ph), math.cos(ph), 0])
        return [er, et, ep], [r"e_r", r"e_\theta", r"e_\varphi"]
    et = v / np.linalg.norm(v)
    en = a - (a @ et) * et
    return [et, en / np.linalg.norm(en)], [r"e_t", r"e_n"]


def proj(k, q):
    c = CENTERS[k]
    dz = (q[2] - Z0) if k == 2 else 0.0
    return c + K * np.array([q[0] - XC - 0.25 * dz, q[1] - YC + 0.35 * dz, 0])


class Lesson(Base):
    def construct(self):
        self.title("10.5", "同一支箭头，四组分量", "One arrow, four sets of components")
        frames = VGroup()
        for k in range(4):
            pts = [proj(k, np.array([XC + A * math.cos(u), YC + B * math.sin(u), Z0])) for u in np.linspace(0, 2 * math.pi, 80)]
            frames.add(Polygon(*pts, color=GREY_B, stroke_width=2),
                       bi(NAMES[k], 22, YELLOW).next_to(CENTERS[k] + UP * 0.85 + LEFT * 1.6, UP, buff=0.05))
        frames.add(Square(0.2, color=GREY_B, fill_color=GREY_E, fill_opacity=1).move_to(proj(2, CAM)))
        frames.add(Arrow(proj(1, np.array([XC - A - 0.02, YC, Z0])), proj(1, np.array([XC - A - 0.11, YC - 0.012, Z0])), buff=0, color=GREY_B,
                         stroke_width=3), zh("指向关节 1 轴", 16, MUTED).move_to(proj(1, np.array([XC - A - 0.07, YC + 0.03, Z0]))))
        self.play(FadeIn(frames))
        t = ValueTracker(0.0)
        cols = [RED, GREEN, BLUE]

        def draw():
            p, v, a = state(t.get_value())
            g = VGroup()
            for k in range(4):
                P = proj(k, p)
                es, labs = basis(k, p, v, a)
                for i, (e, lab) in enumerate(zip(es, labs)):
                    tip = proj(k, p + 0.036 * e)
                    g.add(Arrow(P, tip, buff=0, color=cols[i], stroke_width=3, max_tip_length_to_length_ratio=0.25),
                          MathTex(lab, font_size=22, color=cols[i]).move_to(P + (tip - P) * 1.5))
                g.add(Arrow(P, proj(k, p + 0.6 * v), buff=0, color=C_V, stroke_width=5, max_tip_length_to_length_ratio=0.18),
                      Arrow(P, proj(k, p + 0.4 * a), buff=0, color=C_A, stroke_width=5, max_tip_length_to_length_ratio=0.18),
                      Dot(P, radius=0.05, color=WHITE))
                for j, (q, name, col) in enumerate(((v, "v", C_V), (a, "a", C_A))):
                    comps = [float(q @ e) + 0.0 for e in es]
                    txt = ",\\ ".join("%.3f" % (0.0 if abs(c) < 5e-4 else c) for c in comps)
                    g.add(MathTex(name + r":\ (" + txt + ")", font_size=21, color=col)
                          .move_to(CENTERS[k] + RIGHT * 1.95 + UP * (1.42 - 0.32 * j)))
            g.add(MathTex(r"|\boldsymbol v| = %.3f\ \mathrm{m/s}" % float(np.linalg.norm(v)), font_size=24, color=C_V).move_to(np.array([0, 0.95, 0])),
                  MathTex(r"|\boldsymbol a| = %.3f\ \mathrm{m/s^2}" % float(np.linalg.norm(a)), font_size=24, color=C_A).move_to(np.array([0, 0.6, 0])))
            return g

        dyn = always_redraw(draw)
        self.add(dyn)
        self.caption("橙：速度 v；红：加速度 a。四个画面里是同一支箭头", "Orange: velocity v; red: acceleration a. The same arrows in all four views", wait=0)
        self.play(t.animate.set_value(2.0), run_time=8, rate_func=linear)
        self.caption("局部基各不相同，读出的分量也不同；长度 |v|、|a| 却处处相等", "Different local bases give different components; the lengths |v|, |a| agree", wait=0)
        self.play(t.animate.set_value(4.0), run_time=8, rate_func=linear)
        self.card([["四种坐标，同一个矢量", "Four coordinates, one vector"],
                   MathTex(r"\boldsymbol v = \dot x\,\boldsymbol e_x + \dot y\,\boldsymbol e_y = \dot\rho\,\boldsymbol e_\rho + \rho\dot\varphi\,\boldsymbol e_\varphi = \dot s\,\boldsymbol e_t", font_size=40),
                   ["曲线坐标的局部基在转动：基矢量的导数 = 角速度 × 基矢量", "Curvilinear bases turn: rate of a basis vector = angular velocity × basis vector"]])
