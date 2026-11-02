"""动画 7.1.1（配图 7.1.1）：SRAM 读操作。两条位线预充到 VDD；字线打开后，存 0 的一侧（BL）被单元慢慢拉低，
另一侧（BLB）不动；两者相差约 100 mV 时灵敏放大器使能（同时与位线隔开，位线不再继续放电），它的两个输出在几十皮秒内
分开成满幅。右边对比：如果等 BL 掉到 VDD/2，
要多花好几倍的时间。数值是 256 行 × 128 列阵列按 SKY130 仿真参数的估算。"""
from manim import *
from wq_anim import *
import numpy as np

# <数值>  由 _sync.py 从 textbook/dic/conventions/mos.py 写入，不要手改
VDD = 1.8
DV = 0.1
T_BL_PS = 71.34125773195875
T_SA_PS = 24.689999999999998
T_TOTAL_PS = 644.9073699113363
C_BL_FF = 100.97817599999999
I_READ_UA = 155.20000000000002
T_HALF_PS = 585.5693195876288
# </数值>

BLUE_ = "#58a6ff"
ORANGE_ = "#ffa657"
GREEN_ = "#56d364"
RED_ = "#ff7b72"


class Lesson(Base):
    def construct(self):
        self.title("7.1", "SRAM 读操作：位线放电与灵敏放大", "SRAM read: bit-line discharge and sense amplification")
        t_end = T_BL_PS + T_SA_PS + 60
        ax = Axes(x_range=[0, t_end, 20], y_range=[0, VDD + 0.1, 0.3], x_length=8.6, y_length=4.4,
                  axis_config={"color": MUTED, "include_ticks": False}).shift(DOWN * 0.45 + LEFT * 0.6)
        xl = Text("时间 / ps  time", font_size=18, color=MUTED).next_to(ax.x_axis, DOWN, buff=0.15).align_to(ax.x_axis, RIGHT)
        yl = Text("电压 / V  voltage", font_size=18, color=MUTED).next_to(ax.y_axis, UP, buff=0.1).align_to(ax.y_axis, LEFT)
        self.play(Create(ax), FadeIn(xl, yl))
        pre = DashedLine(ax.c2p(0, VDD), ax.c2p(t_end, VDD), color=MUTED, stroke_width=1.5)
        self.play(Create(pre))
        self.caption("位线 BL、BLB 先预充到 VDD", "Both bit lines are precharged to VDD", wait=0.8)

        t = ValueTracker(0.0)
        t_sa = T_BL_PS

        def bl(x):
            return VDD - DV * min(x, t_sa) / T_BL_PS

        def sa_lo(x):     # 灵敏放大器接 BL 一侧的输出：从 VDD − ΔV 被正反馈拉到 0
            k = (x - t_sa) / T_SA_PS
            return max(0.0, (VDD - DV) * np.exp(-2.2 * k * k))

        def blb(x):
            return VDD

        c_bl = always_redraw(lambda: ax.plot(bl, x_range=[0, max(0.5, t.get_value()), 0.5], color=RED_, stroke_width=4))
        c_blb = always_redraw(lambda: ax.plot(blb, x_range=[0, max(0.5, t.get_value()), 0.5], color=BLUE_, stroke_width=4))
        lab_bl = Text("BL（存 0 的一侧）", font_size=20, color=RED_).move_to(ax.c2p(t_end * 0.25, VDD - DV) + DOWN * 0.3)
        lab_sa = Text("灵敏放大器输出  SA out", font_size=20, color=GREEN_).move_to(ax.c2p(t_end * 0.82, 0.45))
        lab_blb = Text("BLB", font_size=20, color=BLUE_).move_to(ax.c2p(t_end * 0.9, VDD + 0.05) + UP * 0.25)
        self.add(c_bl, c_blb)
        self.caption("字线打开：单元以约 %.0f μA 拉 BL，位线电容约 %.0f fF" % (I_READ_UA, C_BL_FF),
                     "Word line on: the cell pulls BL with about %.0f μA into about %.0f fF" % (I_READ_UA, C_BL_FF), wait=0.2)
        self.play(t.animate.set_value(t_sa), run_time=3.0, rate_func=linear)
        brace = BraceBetweenPoints(ax.c2p(t_sa, VDD - DV), ax.c2p(t_sa, VDD), direction=RIGHT, color=ORANGE_)
        dv_t = Text("ΔV = %.0f mV，约 %.0f ps" % (DV * 1000, T_BL_PS), font_size=20, color=ORANGE_).next_to(brace, RIGHT, buff=0.1)
        self.play(FadeIn(brace, dv_t), FadeIn(lab_blb))
        self.caption("位线只掉了一点点，灵敏放大器就使能", "The bit line has moved only a little when the sense amp fires", wait=0.6)
        sae = DashedLine(ax.c2p(t_sa, 0), ax.c2p(t_sa, VDD + 0.05), color=GREEN_, stroke_width=2)
        sae_t = Text("灵敏放大器使能  SAE", font_size=18, color=GREEN_).next_to(sae, UP, buff=0.05)
        self.play(Create(sae), FadeIn(sae_t))
        c_sa = always_redraw(lambda: ax.plot(sa_lo, x_range=[t_sa, max(t_sa + 0.5, t.get_value()), 0.5], color=GREEN_, stroke_width=4))
        self.add(c_sa)
        self.play(t.animate.set_value(t_end), run_time=1.6, rate_func=linear)
        self.play(FadeIn(lab_bl, lab_sa))
        self.caption("位线不再放电；锁存器正反馈约 %.0f ps 把输出拉开成满幅" % T_SA_PS,
                     "The bit line stops; the latch's feedback reaches full swing in about %.0f ps" % T_SA_PS, wait=1.2)
        self.caption("若等 BL 掉到 VDD/2 再判断，要约 %.0f ps" % T_HALF_PS,
                     "Waiting for BL to fall to VDD/2 would take about %.0f ps" % T_HALF_PS, wait=1.5)
        self.card([["小摆幅 + 灵敏放大", "Small swing + sense amplifier"],
                   MathTex(r"t_{BL}=\frac{C_{BL}\,\Delta V}{I_{read}}", font_size=44),
                   ["ΔV 小 → 位线快、能量省（算例 7.1.2）", "Small ΔV → fast bit line, little energy (Example 7.1.2)"],
                   ["整个存取约 %.0f ps，译码占一半以上" % T_TOTAL_PS, "Whole access about %.0f ps, over half in the decoder" % T_TOTAL_PS]])
