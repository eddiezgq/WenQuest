"""动画 8.1.1（配图 8.1.1）：同一个数 0.1 在 FP32、BF16、FP16、FP8 E4M3、FP4 E2M1 里的位分配与舍入。
先在数轴上看 0.1 落在哪两个可表示数之间、就近舍入到哪一个（间隔随格式变粗）；再依次排出各格式的位：符号、指数、尾数，
旁边写出存进去的值与相对误差。最后对比 FP16 与 BF16：同样 16 位，一个精度高、一个范围大。数值由书中的舍入规则（_ch8.round_to）算出。"""
import math

from manim import *
from wq_anim import *

# (名称, 指数位, 尾数位, 存进去的值, 符号位, 指数字段, 尾数字段)：0.1 = 1.6 × 2^−4
ROWS = [("FP32", 8, 23, 0.10000000149011612, 0, 123, 5033165), ("BF16", 8, 7, 0.10009765625, 0, 123, 77),
        ("FP16", 5, 10, 0.0999755859375, 0, 11, 614), ("FP8 E4M3", 4, 3, 0.1015625, 0, 3, 5), ("FP4 E2M1", 2, 1, 0.0, 0, 0, 0)]


class Lesson(Base):
    def construct(self):
        self.title("8.1", "0.1 存进去还是 0.1 吗", "Is 0.1 still 0.1 once stored?")
        # 数轴：0.1 附近 FP16 与 E4M3 的可表示数
        line = NumberLine(x_range=[0.085, 0.115, 0.005], length=11, include_numbers=True, font_size=22,
                          decimal_number_config={"num_decimal_places": 3}).shift(UP * 1.2)
        self.play(Create(line))
        x = Dot(line.n2p(0.1), color=RED)
        self.play(FadeIn(x), FadeIn(zh("0.1", 24, RED).next_to(x, UP, buff=0.25)))
        self.caption("0.1 写成二进制是无限循环小数，只能存最接近的一个可表示数", "0.1 is a repeating binary fraction: only the nearest representable number can be stored")
        for name, step, col, y in (("FP16", 2 ** -14, BLUE, 0.6), ("FP8 E4M3", 2 ** -7, GREEN, 0.0)):
            ticks = VGroup(*[Line(line.n2p(k * step) + UP * 0.12, line.n2p(k * step) + DOWN * 0.12, color=col, stroke_width=3).shift(DOWN * (y + 0.6))
                             for k in range(math.ceil(0.085 / step), math.floor(0.115 / step) + 1)])
            lab = zh(name, 20, col).next_to(ticks, LEFT, buff=0.3)
            self.play(Create(ticks), FadeIn(lab), run_time=1.0)
        self.caption("蓝：FP16 的可表示数，间隔约 0.00006；绿：FP8 E4M3，间隔约 0.008。就近舍入，平分取偶",
                     "Blue: FP16 numbers, spacing ≈ 0.00006; green: FP8 E4M3, spacing ≈ 0.008. Round to nearest, ties to even")
        self.clear_stage()

        rows = VGroup()
        for name, e, m, v, s, ef, mf in ROWS:
            nb = 1 + e + m
            w = min(0.32, 9.0 / nb)
            cells = VGroup()
            bits = [s] + [(ef >> (e - 1 - i)) & 1 for i in range(e)] + [(mf >> (m - 1 - i)) & 1 for i in range(m)]
            for k, b in enumerate(bits):
                c = RED if k == 0 else BLUE if k <= e else GREEN
                sq = Square(w, stroke_width=1, color=GREY_B, fill_color=c, fill_opacity=0.55)
                cells.add(VGroup(sq, Text(str(b), font_size=int(w * 45), color=WHITE).move_to(sq)))
            cells.arrange(RIGHT, buff=0.02)
            err = abs(v - 0.1) / 0.1 * 100
            info = zh(f"{v:.10g}（误差 {err:.3g}%）" if v else "0（下溢：误差 100%）", 20, INK)
            rows.add(VGroup(zh(name, 20, YELLOW), cells, info).arrange(RIGHT, buff=0.3))
        rows.arrange(DOWN, buff=0.35, aligned_edge=LEFT).shift(UP * 0.3)
        fit(rows, 12.5)
        for r in rows:
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.8)
        self.caption("红：符号；蓝：指数；绿：尾数。尾数越短，0.1 存得越不准；FP4 的最小正数是 0.5，0.1 直接成了 0",
                     "Red: sign; blue: exponent; green: mantissa. Shorter mantissas store 0.1 less exactly; FP4's smallest positive is 0.5, so 0.1 becomes 0")
        self.caption("FP16 与 BF16 都是 16 位：FP16 尾数长、精度高，范围只到 65504；BF16 指数与 FP32 一样长，范围大、精度低",
                     "FP16 and BF16 are both 16 bits: FP16 has the longer mantissa and reaches only 65504; BF16 keeps FP32's exponent: wide range, low precision")
        self.card([["浮点格式", "Floating-point formats"],
                   MathTex(r"x = (-1)^s \times 1.f \times 2^{E - \text{bias}}", font_size=40),
                   ["指数位数决定范围，尾数位数决定精度", "Exponent bits set the range, mantissa bits the precision"],
                   ["相对精度约 2^−m：FP32 约 10⁻⁷，FP16 约 10⁻³，BF16 约 10⁻²", "Relative precision ≈ 2^−m: FP32 ≈ 10⁻⁷, FP16 ≈ 10⁻³, BF16 ≈ 10⁻²"]])
