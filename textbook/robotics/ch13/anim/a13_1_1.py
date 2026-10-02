"""动画 13.1.1（配图 13.1.1）：标准 DH 的一步变换由四个基本运动组成。
坐标系 {i−1} 依次：绕 z 转 θ_i、沿 z 移 d_i、沿新的 x 移 a_i、绕 x 转 α_i，到达 {i}。几何与图 13.1.1(a) 相同。"""
from manim import *
from wq_anim import *
import numpy as np

TH, D, A, AL = np.radians(55), 0.5, 0.75, np.radians(45)
O2 = np.array([-1.2, -1.4, 0])
SC = 3.4
AZ, EL = np.radians(-62), np.radians(18)


def P(p):
    """与图 13.1.1 相同的视角（方位角 −62°，仰角 18°）的正投影。"""
    x, y, z = (float(v) for v in p)
    sx = -np.sin(AZ) * x + np.cos(AZ) * y
    sy = -np.cos(AZ) * np.sin(EL) * x - np.sin(AZ) * np.sin(EL) * y + np.cos(EL) * z
    return O2 + SC * np.array([sx, sy, 0])


def Rz(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]])


def Rx(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[1.0, 0, 0], [0, c, -s], [0, s, c]])


def pose(f1, f2, f3, f4):
    """四个运动各完成 f1…f4（0 到 1）时坐标系的 (R, o)。"""
    R = Rz(TH * f1)
    o = np.array([0, 0, D * f2])
    o = o + R @ np.array([A * f3, 0, 0])
    R = R @ Rx(AL * f4)
    return R, o


def frame_mob(R, o, length=0.45):
    g = VGroup()
    for k, col in enumerate((RED, GREEN, BLUE)):
        g.add(Arrow(P(o), P(o + R[:, k] * length), buff=0, color=col, stroke_width=6, max_tip_length_to_length_ratio=0.25))
    g.add(Dot(P(o), radius=0.06, color=WHITE))
    return g


class Lesson(Base):
    def construct(self):
        self.title("13.1", "标准 DH：四个基本运动", "Standard DH: four elementary motions")
        zi = Rz(TH) @ Rx(AL) @ np.array([0, 0, 1.0])
        oi = np.array([A * np.cos(TH), A * np.sin(TH), D])
        axis_i = Line(P([0, 0, -0.3]), P([0, 0, 1.05]), color=GREY_B, stroke_width=5)
        axis_n = Line(P(oi - 0.55 * zi), P(oi + 0.6 * zi), color=GREY_B, stroke_width=5)
        lab_i = zh("轴 i", 24, GREY_B).next_to(axis_i.get_end(), UP, buff=0.1)
        lab_n = zh("轴 i+1", 24, GREY_B).next_to(axis_n.get_end(), UP, buff=0.1)
        normal = DashedLine(P([0, 0, D]), P(oi), color=YELLOW, stroke_width=4)
        lab_N = MathTex("N_i", color=YELLOW, font_size=32).next_to(normal.get_center(), UP, buff=0.12)
        self.play(Create(axis_i), Create(axis_n), FadeIn(lab_i), FadeIn(lab_n))
        self.play(Create(normal), FadeIn(lab_N))
        ghost = frame_mob(*pose(0, 0, 0, 0)).set_opacity(0.35)
        self.add(ghost)
        f = [ValueTracker(0.0) for _ in range(4)]
        moving = always_redraw(lambda: frame_mob(*pose(*[x.get_value() for x in f])))
        self.add(moving)
        self.caption("目标：把坐标系 {i−1}（在轴 i 上）搬到 {i}（在轴 i+1 上）",
                     "Goal: carry frame {i-1} (on axis i) to frame {i} (on axis i+1)")
        steps = [("① 绕 z 轴转 θᵢ：x 轴转到与公垂线 Nᵢ 平行", "1. Rotate θᵢ about z: x becomes parallel to Nᵢ"),
                 ("② 沿 z 轴移 dᵢ：原点到达 Nᵢ 在轴 i 上的垂足", "2. Slide dᵢ along z: the origin reaches the foot of Nᵢ"),
                 ("③ 沿新的 x 轴移 aᵢ：原点沿 Nᵢ 到达轴 i+1", "3. Slide aᵢ along the new x: along Nᵢ to axis i+1"),
                 ("④ 绕 x 轴转 αᵢ：z 轴转到轴 i+1 上", "4. Rotate αᵢ about x: z now lies along axis i+1")]
        for k, (z_txt, e_txt) in enumerate(steps):
            self.caption(z_txt, e_txt, wait=0)
            self.play(f[k].animate.set_value(1.0), run_time=2.2)
            self.wait(0.6)
        self.caption("每一步都绕（沿）当前坐标系的轴进行，所以依次右乘",
                     "Each motion is about the current axes, so the factors multiply on the right", wait=1.5)
        self.card([["标准 DH 的一步变换", "One standard-DH step"],
                   MathTex(r"T_{i-1,i}=\mathrm{Rot}(\hat z,\theta_i)\,\mathrm{Trans}(\hat z,d_i)\,\mathrm{Trans}(\hat x,a_i)\,\mathrm{Rot}(\hat x,\alpha_i)", font_size=38),
                   ["改进 DH 把次序换成：先绕（沿）x，再绕（沿）z", "Modified DH takes x first, then z"]])
