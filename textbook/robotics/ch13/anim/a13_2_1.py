"""动画 13.2.1（配图 13.2.3）：为 UR5e 逐个建立连杆坐标系 {0}…{6}（零位）。
每一步说明相邻两轴的关系（相交、平行）和读出的 DH 参数；数据与程序 13.2.1、表 13.3.2 相同（零件库模型的尺寸）。"""
from manim import *
from wq_anim import *
import numpy as np

AZ, EL = np.radians(-35), np.radians(24)
SC = 8.5
# 零件库模型尺寸下的 DH 表 (a, α, d)，θ 偏置全为 0
TAB = [(0.0, np.pi / 2, 0.163), (-0.425, 0.0, 0.0), (-0.392, 0.0, 0.0), (0.0, np.pi / 2, 0.134), (0.0, -np.pi / 2, 0.1), (0.0, 0.0, 0.1)]
# 关节实物的中心（表 12.1.1）与法兰盘中心，用来画手臂
BODY = np.array([[0, 0, 0], [0, 0, 0.163], [0, -0.138, 0.163], [-0.425, -0.138, 0.163], [-0.425, -0.007, 0.163],
                 [-0.817, -0.007, 0.163], [-0.817, -0.134, 0.163], [-0.817, -0.134, 0.063], [-0.817, -0.234, 0.063]])


def proj(p):
    x, y, z = (float(v) for v in p)
    sx = -np.sin(AZ) * x + np.cos(AZ) * y
    sy = -np.cos(AZ) * np.sin(EL) * x - np.sin(AZ) * np.sin(EL) * y + np.cos(EL) * z
    return np.array([sx, sy, 0.0])


CENTER = proj([-0.42, -0.12, 0.09])
SHIFT = np.array([0.6, -0.25, 0.0])


def P(p):
    return SHIFT + SC * (proj(p) - CENTER)


def dh(a, al, d):
    ca, sa = np.cos(al), np.sin(al)
    return np.array([[1, 0, 0, a], [0, ca, -sa, 0], [0, sa, ca, d], [0, 0, 0, 1.0]])


FRAMES = [np.eye(4)]
for a, al, d in TAB:
    FRAMES.append(FRAMES[-1] @ dh(a, al, d))


def frame_mob(F, i, length=0.09):
    o = F[:3, 3]
    g = VGroup()
    for k, col in enumerate((RED, GREEN, BLUE)):
        g.add(Arrow(P(o), P(o + F[:3, k] * length), buff=0, color=col, stroke_width=5, max_tip_length_to_length_ratio=0.3))
    g.add(Dot(P(o), radius=0.05, color=WHITE))
    off = {0: DR, 1: RIGHT, 2: UR, 3: UR, 4: UL, 5: DOWN, 6: DL}[i]
    g.add(MathTex(r"\{%d\}" % i, color=YELLOW, font_size=30).next_to(P(o), off, buff=0.32))
    return g


class Lesson(Base):
    def construct(self):
        self.title("13.2", "逐个关节建立连杆坐标系：UR5e", "Building the link frames joint by joint: UR5e")
        body = VMobject(color=GREY_C, stroke_width=14, stroke_opacity=0.55).set_points_as_corners([P(p) for p in BODY])
        axes_pts = [((0, 0, 1), BODY[1]), ((0, -1, 0), BODY[2]), ((0, -1, 0), BODY[4]), ((0, -1, 0), BODY[5]),
                    ((0, 0, -1), BODY[6]), ((0, -1, 0), BODY[7])]
        lines = VGroup(*[DashedLine(P(np.array(q) - 0.14 * np.array(w)), P(np.array(q) + 0.14 * np.array(w)), color=GREY_B,
                                    stroke_width=2, dash_length=0.08) for w, q in axes_pts])
        self.play(Create(body), Create(lines), run_time=1.5)
        self.caption("零位的 UR5e：灰色是手臂，虚线是六根关节轴", "UR5e at home: grey arm, dashed lines are the six joint axes")
        steps = [
            ("{0}：z₀ 沿轴 1 竖直向上，原点在基座安装面中心", "{0}: z0 along axis 1, upward; origin at the centre of the base"),
            ("{1}：轴 1、2 相交 → a₁ = 0，原点在交点，d₁ = 0.163 m，α₁ = 90°", "{1}: axes 1, 2 intersect: a1 = 0, origin at the crossing, d1 = 0.163 m, α1 = 90°"),
            ("{2}：轴 2、3 平行 → 取 d₂ = 0；沿 x₂ 量得 a₂ = −0.425 m", "{2}: axes 2, 3 parallel: take d2 = 0; along x2, a2 = −0.425 m"),
            ("{3}：轴 3、4 平行 → d₃ = 0，a₃ = −0.392 m", "{3}: axes 3, 4 parallel: d3 = 0, a3 = −0.392 m"),
            ("{4}：轴 4、5 相交 → a₄ = 0，d₄ = 0.134 m，α₄ = 90°", "{4}: axes 4, 5 intersect: a4 = 0, d4 = 0.134 m, α4 = 90°"),
            ("{5}：轴 5、6 相交 → a₅ = 0，d₅ = 0.1 m，α₅ = −90°", "{5}: axes 5, 6 intersect: a5 = 0, d5 = 0.1 m, α5 = −90°"),
            ("{6}：原点在法兰盘中心，d₆ = 0.1 m，z₆ 沿法兰法线向外", "{6}: origin at the flange centre, d6 = 0.1 m, z6 along the flange normal"),
        ]
        prev = None
        for i, (z_txt, e_txt) in enumerate(steps):
            f = frame_mob(FRAMES[i], i)
            anims = [FadeIn(f, scale=0.6)]
            if prev is not None:
                o0, o1 = FRAMES[i - 1][:3, 3], FRAMES[i][:3, 3]
                z0 = FRAMES[i - 1][:3, 2]
                foot = o0 + ((o1 - o0) @ z0) * z0          # 先沿 z_{i−1} 走 d_i，再沿 x_i 走 a_i
                path = VGroup(Line(P(o0), P(foot), color=BLUE_B, stroke_width=4), Line(P(foot), P(o1), color=YELLOW, stroke_width=4))
                anims.append(Create(path))
            self.caption(z_txt, e_txt, wait=0)
            self.play(*anims, run_time=1.2)
            self.wait(1.4)
            prev = f
        self.caption("{1}、{2}、{3} 的原点都在 y = 0 的平面内：坐标系由轴线决定，不必在关节实物的中心",
                     "Origins of {1}, {2}, {3} lie in the plane y = 0: frames follow the axis lines, not the joint housings", wait=2)
        self.card([["UR5e 的 DH 参数（零件库尺寸）", "UR5e DH parameters (library model)"],
                   MathTex(r"d_1 = 0.163,\ a_2 = -0.425,\ a_3 = -0.392,\ d_4 = 0.134,\ d_5 = d_6 = 0.1\ (\mathrm{m})", font_size=34),
                   MathTex(r"\alpha = (90^\circ,\ 0,\ 0,\ 90^\circ,\ -90^\circ,\ 0)", font_size=34),
                   ["厂商手册中每个长度与此相差不到 1 mm（13.3 节）", "Each length in the maker's table differs by less than 1 mm (Section 13.3)"]])
