"""动画 8.1.2（配图 8.1.3）：在平面 2R 臂逆运动学目标函数的等高线上，梯度下降（α = 3）沿狭长山谷来回折返，
牛顿法用二次模型一步步“跳”向极小点，4 步就到。"""
from manim import *
from wq_anim import *
import numpy as np
import math

L1, L2 = 0.425, 0.392
PD = np.array([0.5, 0.4])
C1, C2, S = 0.0, 80.0, 0.2           # 画面中心对应 θ = (0°, 80°)，1° 画成 0.2 个单位
OFF = np.array([-2.6, -0.1, 0])


def tip(t):
    return np.array([L1 * math.cos(t[0]) + L2 * math.cos(t[0] + t[1]), L1 * math.sin(t[0]) + L2 * math.sin(t[0] + t[1])])


def jac(t):
    s1, s12 = math.sin(t[0]), math.sin(t[0] + t[1])
    c1, c12 = math.cos(t[0]), math.cos(t[0] + t[1])
    return np.array([[-L1 * s1 - L2 * s12, -L2 * s12], [L1 * c1 + L2 * c12, L2 * c12]])


def f(t):
    r = tip(t) - PD
    return 0.5 * float(r @ r)


def grad(t):
    return jac(t).T @ (tip(t) - PD)


def hess(t):
    J, r = jac(t), tip(t) - PD
    e = tip(t)
    e2 = e - np.array([L1 * math.cos(t[0]), L1 * math.sin(t[0])])    # 关节 2 到末端
    H = J.T @ J
    H[0, 0] += -r @ e
    H[0, 1] += -r @ e2
    H[1, 0] += -r @ e2
    H[1, 1] += -r @ e2
    return H


def sci(e):
    m, x = ("%.1e" % e).split("e")
    return r"%s\times 10^{%d}" % (m, int(x))


def scr(t):
    return OFF + S * np.array([math.degrees(t[0]) - C1, math.degrees(t[1]) - C2, 0])


def path_gd(alpha, n):
    t = np.array([0.0, math.radians(90)])
    out = [t.copy()]
    for _ in range(n):
        t = t - alpha * grad(t)
        out.append(t.copy())
    return out


def path_newton(n):
    t = np.array([0.0, math.radians(90)])
    out = [t.copy()]
    for _ in range(n):
        t = t - np.linalg.solve(hess(t), grad(t))
        out.append(t.copy())
    return out


class Lesson(Base):
    def construct(self):
        self.title("8.1", "梯度下降与牛顿法的迭代路径", "Iteration paths of gradient descent and Newton's method")
        box = Rectangle(width=S * 24, height=S * 28, color=GREY_D, stroke_width=1).move_to(OFF)
        cont = VGroup()
        for lv in (2e-5, 8e-5, 2.5e-4, 7e-4, 1.6e-3, 3e-3):
            cont.add(ImplicitFunction(lambda x, y, lv=lv: f(np.radians([(x - OFF[0]) / S + C1, (y - OFF[1]) / S + C2])) - lv,
                                      x_range=[box.get_left()[0], box.get_right()[0]], y_range=[box.get_bottom()[1], box.get_top()[1]],
                                      color=GREY_B, stroke_width=2, min_depth=6, max_quads=4000))
        ax_lab = VGroup(MathTex(r"\theta_1", font_size=30, color=MUTED).next_to(box.get_corner(DR), RIGHT, buff=0.1),
                        MathTex(r"\theta_2", font_size=30, color=MUTED).next_to(box, LEFT, buff=0.1))
        self.play(Create(cont), FadeIn(box), FadeIn(ax_lab), run_time=2)
        c2 = (PD @ PD - L1 * L1 - L2 * L2) / (2 * L1 * L2)          # 解析逆解（余弦定理），作为“真值”
        t2 = math.acos(c2)
        ts = np.array([math.atan2(PD[1], PD[0]) - math.atan2(L2 * math.sin(t2), L1 + L2 * math.cos(t2)), t2])
        star = Star(n=5, outer_radius=0.16, color=RED, fill_opacity=1).move_to(scr(ts))
        start = Dot(scr(np.array([0.0, math.radians(90)])), color=WHITE, radius=0.07)
        slab = MathTex(r"\theta_0", font_size=30).next_to(start, UR, buff=0.05)
        self.play(FadeIn(star), FadeIn(start), Write(slab))
        self.caption("f(θ) = ½‖p(θ) − p_d‖² 的等高线：一条斜着的狭长山谷", "Level curves of f(θ) = ½‖p(θ) − p_d‖²: a long, tilted valley")

        info = VGroup(bi(["梯度下降 α = 3", "gradient descent α = 3"], 24, ORANGE).move_to(np.array([3.4, 2.4, 0])),
                      bi(["牛顿法", "Newton's method"], 24, BLUE_C).move_to(np.array([3.4, 0.9, 0])))
        self.play(FadeIn(info[0]))
        gd = path_gd(3.0, 40)
        self.caption("梯度下降：每一步沿 −∇f，垂直于等高线，在谷底两侧来回折返", "Gradient descent steps along −∇f, across the valley, zig-zagging", wait=0)
        segs = VGroup()
        for k in range(14):
            seg = Line(scr(gd[k]), scr(gd[k + 1]), color=ORANGE, stroke_width=4)
            segs.add(seg)
            self.play(Create(seg), run_time=0.28)
        cnt = bi(["共需 83 步", "83 steps in all"], 22, ORANGE).next_to(info[0], DOWN, buff=0.15)
        self.play(FadeIn(cnt))
        self.caption("到 10⁻⁸ 的精度要 83 步：每步误差只缩小到约 85%", "83 steps to 10⁻⁸: the error shrinks only to about 85% per step")
        self.play(FadeIn(info[1]))
        nw = path_newton(4)
        self.caption("牛顿法：用二次模型代替 f，直接跳到模型的最低点", "Newton's method jumps to the minimum of the quadratic model", wait=0)
        for k in range(4):
            seg = Arrow(scr(nw[k]), scr(nw[k + 1]), buff=0, color=BLUE_C, stroke_width=6, max_tip_length_to_length_ratio=0.12)
            self.play(GrowArrow(seg), run_time=0.8)
            self.add(Dot(scr(nw[k + 1]), color=BLUE_C, radius=0.06))
        err = [float(np.linalg.norm(t - ts)) for t in nw]
        tab = VGroup(*[MathTex(r"k=%d:\ \|\theta_k-\theta^*\|=%s" % (k, sci(e)), font_size=26)
                       for k, e in enumerate(err)]).arrange(DOWN, aligned_edge=LEFT, buff=0.12).next_to(info[1], DOWN, buff=0.25)
        self.play(LaggedStart(*[FadeIn(m) for m in tab], lag_ratio=0.3), run_time=2)
        self.caption("误差的指数每步约翻一倍：二次收敛", "The exponent of the error roughly doubles each step: quadratic convergence")
        self.wait(1)
        self.card([["两种方法", "Two methods"],
                   MathTex(r"\theta_{k+1} = \theta_k - \alpha\,\nabla f(\theta_k)", font_size=42),
                   MathTex(r"\theta_{k+1} = \theta_k - \nabla^2 f(\theta_k)^{-1}\,\nabla f(\theta_k)", font_size=42),
                   ["梯度下降线性收敛，牛顿法在极小点附近二次收敛", "gradient descent converges linearly; Newton's method quadratically near the minimum"]])
