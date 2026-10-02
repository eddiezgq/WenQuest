"""动画 18.4.1（配图 18.4.2）：一层一层叠加 σᵢuᵢvᵢᵀ，齿轮图像（48×64 像素的缩小版）从模糊的十字条纹逐渐变清楚；
右侧的奇异值柱状图同步点亮已经用到的层。图像由与 _img.py 相同的几何画法生成（不加噪声）。"""
from manim import *
from wq_anim import *
import numpy as np
import math


def gear(m=48, n=64, cell=2.5):
    A = np.zeros((m, n))
    cx, cy = 80.0, 60.0

    def inside(x, y):
        r = math.hypot(x - cx, y - cy)
        a = math.atan2(y - cy, x - cx)
        ph = (a * 18 / (2 * math.pi)) % 1.0
        if 0.18 < ph < 0.62:
            tooth = 1.0
        elif ph <= 0.18:
            tooth = max(0.0, 1 - abs(ph - 0.18) / 0.08)
        else:
            tooth = max(0.0, 1 - abs(ph - 0.62) / 0.08)
        return r <= 40 + 6 * min(1.0, tooth * 1.6), r, a

    for i in range(m):
        for j in range(n):
            x, y = (j + 0.5) * cell, (i + 0.5) * cell
            v = 0.80 + 0.14 * i / (m - 1)
            if inside(x - 4, y - 4)[0]:
                v -= 0.18
            ok, r, a = inside(x, y)
            if ok:
                v = 0.30 + 0.12 * math.cos(a - 0.8)
                if r < 15:
                    v = 0.62
                bolt = any(math.hypot(x - (cx + 26 * math.cos(q * math.pi / 2 + math.pi / 4)),
                                      y - (cy + 26 * math.sin(q * math.pi / 2 + math.pi / 4))) < 3.6 for q in range(4))
                key = abs(x - cx) < 2.2 and cy - 9.5 < y < cy
                if r < 7 or bolt or key:
                    v = 0.80 + 0.14 * i / (m - 1) - 0.18
            A[i, j] = v
    return A


class Lesson(Base):
    def construct(self):
        self.title("18.4", "一层一层叠出一张图", "Building an image layer by layer")
        G = gear()
        m, n = G.shape
        U, s, Vt = np.linalg.svd(G)
        h = 0.1
        corner = np.array([-6.5, 2.3, 0.0])
        cells = VGroup(*[Square(h * 1.04, stroke_width=0, fill_color=BLACK, fill_opacity=1).move_to(corner + np.array([(j + 0.5) * h, -(i + 0.5) * h, 0.0]))
                         for i in range(m) for j in range(n)])
        frame_ = SurroundingRectangle(cells, color=GREY_B, buff=0.02, stroke_width=1.5)
        self.play(FadeIn(cells), Create(frame_))
        nb = 10
        top = math.log10(s[0]) + 0.2
        bot = math.log10(s[nb - 1]) - 0.3
        base = np.array([1.3, -2.0, 0.0])
        bars = VGroup()
        for i in range(nb):
            hh = 3.4 * (math.log10(s[i]) - bot) / (top - bot)
            bars.add(Rectangle(width=0.36, height=hh, stroke_width=0, fill_color=GREY_C, fill_opacity=1)
                     .move_to(base + np.array([0.5 * i, hh / 2, 0.0])))
        lab = bi(["奇异值 σ₁…σ₁₀（对数坐标）", "σ1…σ10 (log scale)"], 22, GREY_A).next_to(bars, DOWN, buff=0.25)
        self.play(FadeIn(bars), FadeIn(lab))

        def show(k):
            Ak = (U[:, :k] * s[:k]) @ Vt[:k] if k < min(m, n) else G
            anims = []
            for i in range(m):
                for j in range(n):
                    v = min(1.0, max(0.0, float(Ak[i, j])))
                    anims.append(cells[i * n + j].animate.set_fill(rgb_to_color([v, v, v])))
            return anims

        kt = bi(["k = 1：只有十字形的明暗条纹", "k = 1: only a cross of bands"], 26, YELLOW).to_corner(UR, buff=0.5)
        self.play(*show(1), bars[0].animate.set_fill(YELLOW), FadeIn(kt), run_time=1.5)
        self.caption("第 1 层 σ₁u₁v₁ᵀ：一行的明暗乘一列的明暗", "Layer 1: a row profile times a column profile")
        for k in (2, 3, 5, 10, 20):
            t2 = bi(["k = %d" % k, "k = %d" % k], 30, YELLOW).move_to(kt)
            self.play(*show(k), *[bars[i].animate.set_fill(YELLOW) for i in range(min(k, nb))], FadeOut(kt), FadeIn(t2), run_time=1.2)
            kt = t2
            self.wait(0.4)
        self.caption("每加一层，误差减少的正是被加入的那个奇异值", "Each layer removes exactly its singular value from the error")
        t3 = bi(["全部 48 层：原图", "all 48 layers: the image"], 26, YELLOW).move_to(kt)
        self.play(*show(48), FadeOut(kt), FadeIn(t3), run_time=1.5)
        self.wait(1)
        self.card([["埃卡特–杨定理", "Eckart–Young theorem"],
                   MathTex(r"A_k=\sum_{i=1}^{k}\sigma_i\boldsymbol u_i\boldsymbol v_i^{\mathsf T},\qquad \lVert A-A_k\rVert_2=\sigma_{k+1}", font_size=42),
                   ["秩不超过 k 的矩阵中，A_k 离 A 最近", "Among rank-k matrices, A_k is nearest to A"]])
