"""动画 2.3.1：路径努力的分摊。译码器路径（反相器 + 三输入与非门 + 反相器）的路径努力 F = G·B·H 固定，
三级的级努力乘积不变；级努力不均时总延时大，调到每级都等于 F^(1/3) 时最小。"""
from manim import *
from wq_anim import *
import numpy as np

# <数值>  由 _sync.py 从 textbook/dic/conventions/mos.py 写入，不要手改
R_SYM = 2.42816091954023
GAMMA = 1.576
TAU_PS = 9.069818404407263
R_N_K = 7.303465765004228
C_FO4_FF = 10.035598275862068
CINV_FF = 1.7997844827586205
G_NAND3 = 1.5834031852472759
P_NAND3 = 4.728
B_DEC = 4.0
H_DEC = 16.0
# </数值>

BLUE_ = "#58a6ff"
ORANGE_ = "#ffa657"
GREEN_ = "#56d364"
RED_ = "#ff7b72"


class Lesson(Base):
    def construct(self):
        self.title("2.3", "路径努力的分摊", "Sharing the path effort")
        F = G_NAND3 * B_DEC * H_DEC
        fopt = F ** (1 / 3)
        P = GAMMA + P_NAND3 + GAMMA
        eq = MathTex(rf"F=G\,B\,H={G_NAND3:.2f}\times{B_DEC:.0f}\times{H_DEC:.0f}\approx{F:.0f}", font_size=40).move_to([0, 2.4, 0])
        self.play(Write(eq))
        self.caption("译码器路径：反相器 → 三输入与非门 → 反相器", "Decoder path: inverter → NAND3 → inverter", wait=1.2)
        a = ValueTracker(0.0)                     # 0：不均匀的分摊；1：均匀
        uneven = [F / (2.0 * 10.0), 2.0, 10.0]    # 乘积 = F

        def efforts():
            t = a.get_value()
            # 在对数空间里插值，保持乘积不变
            return [np.exp((1 - t) * np.log(u) + t * np.log(fopt)) for u in uneven]

        base = -1.8
        names = [MathTex(n, font_size=30) for n in (r"\mathrm{INV}", r"\mathrm{NAND3}", r"\mathrm{INV}")]
        xs = [-3.0, 0.0, 3.0]
        for n, x in zip(names, xs):
            n.move_to([x, base - 0.4, 0])
        self.play(*[FadeIn(n) for n in names])

        def bars():
            fs = efforts()
            g = VGroup()
            for f, x in zip(fs, xs):
                h = 0.32 * f
                col = GREEN_ if a.get_value() > 0.98 else (RED_ if f == max(fs) else BLUE_)
                b = Rectangle(width=1.1, height=h, fill_color=col, fill_opacity=0.85, stroke_width=0).move_to([x, base + h / 2, 0])
                lab = MathTex(rf"f={f:.1f}", font_size=28).next_to(b, UP, buff=0.1)
                g.add(b, lab)
            return g

        br = always_redraw(bars)
        dl = always_redraw(lambda: MathTex(rf"D=\sum f_i+P={sum(efforts()):.1f}+{P:.1f}={sum(efforts()) + P:.1f}\,\tau",
                                           font_size=36).move_to([0, 1.6, 0]))
        self.add(br, dl)
        self.caption("级努力不均：乘积还是 F，总和却更大", "Uneven efforts: the product is still F, but the sum is larger", wait=2.0)
        self.caption("调尺寸，三级的乘积不变，把努力摊匀", "Resize: the product stays the same, the efforts even out", wait=0.2)
        self.play(a.animate.set_value(1.0), run_time=5, rate_func=smooth)
        self.wait(1.0)
        self.caption(f"每级都等于 F 的立方根 ≈ {fopt:.2f}：总延时最小", f"Each equal to the cube root of F ≈ {fopt:.2f}: minimum delay", wait=2.5)
        self.card([["逻辑努力", "Logical effort"],
                   MathTex(r"d=g\,h+p,\qquad F=G\,B\,H", font_size=40),
                   MathTex(r"D_{\min}=N\,F^{1/N}+\sum p_i", font_size=40),
                   ["每级努力相等时最快；级数约为 ln F / ln 4", "Fastest with equal stage efforts; N ≈ ln F / ln 4"]])
