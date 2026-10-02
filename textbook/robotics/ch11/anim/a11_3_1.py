"""动画 11.3.1（配图 11.3.1）：把关节角长方形的左右两边、上下两边分别粘合，得到环面 T²；跨过边界的路径在环面上是连续的。"""
from manim import *
from wq_anim import *
import numpy as np

A = 0.7                 # 圆管半径（画面单位）；长方形两边长 2πA（θ₂ 方向）与 2π·2A（θ₁ 方向）
EL, AZ = np.radians(28), np.radians(-25)
SHIFT = np.array([0.0, -0.4, 0.0])


def scr(p):
    x, y, z = p
    X = x * np.cos(AZ) - y * np.sin(AZ)
    Y = (x * np.sin(AZ) + y * np.cos(AZ)) * np.sin(EL) + z * np.cos(EL)
    return np.array([X, Y, 0.0]) + SHIFT


def shape(u, v, a, b):
    """u = θ₁、v = θ₂（弧度）。a ∈ [0, 1]：沿 θ₂ 卷成圆管的程度；b ∈ [0, 1]：圆管沿 θ₁ 弯成圆环的程度。"""
    x0 = 2 * A * u
    if a < 1e-4:
        y, zc = A * v, -A
    else:
        r = A / a
        y, zc = r * np.sin(a * v), r * (1 - np.cos(a * v)) - A     # zc：相对圆管轴线的高度
    if b < 1e-4:
        return np.array([x0, y, zc + A])
    R = 2 * A / b
    ph = b * u
    return np.array([(R - zc) * np.sin(ph), y, R - (R - zc) * np.cos(ph) - 2 * A + A * 0])


def mesh(a, b):
    g = VGroup()
    us, vs = np.linspace(-np.pi, np.pi, 17), np.linspace(-np.pi, np.pi, 13)
    tt = np.linspace(-np.pi, np.pi, 50)
    for k, u in enumerate(us):
        col = RED if k in (0, len(us) - 1) else GREY_B
        g.add(VMobject(stroke_color=col, stroke_width=4 if col == RED else 1.5).set_points_as_corners([scr(shape(u, v, a, b)) for v in tt]))
    for k, v in enumerate(vs):
        col = BLUE if k in (0, len(vs) - 1) else GREY_B
        g.add(VMobject(stroke_color=col, stroke_width=4 if col == BLUE else 1.5).set_points_as_corners([scr(shape(u, v, a, b)) for u in tt]))
    # 一条跨过 θ₁ = ±180° 的路径：从 (150°, −60°) 到 (−120°, 60°) 沿最短方向
    s = np.linspace(0, 1, 60)
    th1 = np.radians(150) + s * np.radians(90)
    th1 = (th1 + np.pi) % (2 * np.pi) - np.pi
    th2 = np.radians(-60) + s * np.radians(120)
    pts = [scr(shape(p, q, a, b)) for p, q in zip(th1, th2)]
    cut = int(np.argmax(np.abs(np.diff(th1)) > np.pi)) + 1
    g.add(VMobject(stroke_color=GREEN, stroke_width=6).set_points_as_corners(pts[:cut]))
    g.add(VMobject(stroke_color=GREEN, stroke_width=6).set_points_as_corners(pts[cut:]))
    g.add(Dot(pts[0], color=BLUE_C, radius=0.09), Dot(pts[-1], color=GOLD, radius=0.09))
    return g


class Lesson(Base):
    def construct(self):
        self.title("11.3", "两个关节角组成环面", "Two joint angles make a torus")
        a, b = ValueTracker(0.0), ValueTracker(0.0)
        m = always_redraw(lambda: mesh(a.get_value(), b.get_value()))
        self.play(FadeIn(m), run_time=0.8)
        self.caption("关节角长方形：横向 θ₁，纵向 θ₂，各从 −180° 到 180°；绿线跨出了右边界",
                     "Joint-angle rectangle: θ₁ across, θ₂ up, each −180° to 180°; the green path leaves on the right", wait=1.5)
        self.caption("θ₂ = −180° 与 180° 是同一个构型：把上下两边（蓝）粘起来，卷成圆管",
                     "θ₂ = −180° and 180° are the same: glue top to bottom (blue) into a tube", wait=0)
        self.play(a.animate.set_value(1.0), run_time=4.0, rate_func=smooth)
        self.caption("θ₁ 也一样：把圆管两端（红）粘起来，得到环面",
                     "Same for θ₁: glue the tube's ends (red) and get a torus", wait=0)
        self.play(b.animate.set_value(1.0), run_time=4.5, rate_func=smooth)
        self.caption("在环面上，绿色路径是一条连续的短曲线：跨过 ±180° 并不是“跳”",
                     "On the torus the green path is one short continuous curve: crossing ±180° is no jump", wait=2.5)
        self.card([["平面 2R 臂的构型空间", "C-space of a planar 2R arm"],
                   MathTex(r"S^1 \times S^1 = T^2", font_size=56),
                   ["最短转角：Δθ = wrap(θ_b − θ_a)", "shortest turn: Δθ = wrap(θ_b − θ_a)"]])
