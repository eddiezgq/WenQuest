"""动画 50.5.1（配图 50.5.1）：SH-301 从 Ø50 棒料到成品——每道工序切掉的材料用这道工序的颜色显示。

轴向尺寸按工厂数据（总长 167，轴段 Ø30/Ø35/Ø40/Ø35/Ø30）；直径方向放大 2 倍画出，余量看得清。
"""
from manim import *
from wq_anim import *
import numpy as np

SEGS = [(30, 40), (35, 12), (40, 60), (35, 25), (30, 30)]
ROUGH = {35: 36.5, 40: 41.5, 30: 31.5}         # 粗车后（工序尺寸；Ø30 段示意）
FINISH = {35: 35.3, 40: 40.3, 30: 30.0}        # 精车后：轴承位、齿轮位留磨量，Ø30 段精车到尺寸
SX, SY = 0.06, 0.12                            # mm → 画面单位：轴向、径向（径向放大 2 倍）
X0 = -167 * SX / 2


def profile(diams, color, opacity=1.0):
    """台阶轴的上半轮廓（以轴线为界，上下对称画一整块）"""
    g = VGroup()
    z = 0
    for (d0, L), d in zip(SEGS, diams):
        r = Rectangle(width=L * SX, height=d * SY, fill_color=color, fill_opacity=opacity, stroke_width=1.2, stroke_color=INK)
        r.move_to(np.array([X0 + (z + L / 2) * SX, 0, 0]))
        g.add(r)
        z += L
    return g


class Lesson(Base):
    def construct(self):
        self.title("50.5", "SH-301：从棒料到成品", "SH-301 from bar to finished part")
        axis = DashedLine(LEFT * 6, RIGHT * 6, color=MUTED, dash_length=0.15).shift(DOWN * 0.0)
        bar = Rectangle(width=182 * SX, height=50 * SY, fill_color="#8c8c8c", fill_opacity=1, stroke_color=INK, stroke_width=1.2)
        self.play(FadeIn(bar), Create(axis))
        self.caption("10 下料：Ø50 热轧圆钢，锯成 182 mm", "10 Sawing: a Ø50 hot-rolled bar cut to 182 mm")
        rough = profile([ROUGH[d] for d, _ in SEGS], "#d98c3a")
        self.caption("20 粗车：切掉大部分余量，轴承位、齿轮位各留精车余量", "20 Rough turning removes most of the stock, leaving some for finishing")
        self.play(Transform(bar, rough), run_time=2.5)
        heat = SurroundingRectangle(bar, color="#b5443b", buff=0.15)
        self.caption("30 调质：淬火 + 高温回火，得到 217–255 HB；工件会变形、表面会氧化", "30 Quench & temper to 217–255 HB; the part distorts and its skin oxidises")
        self.play(Create(heat), bar.animate.set_fill("#b5443b"), run_time=1.5)
        self.play(FadeOut(heat))
        fin = profile([FINISH[d] for d, _ in SEGS], "#3a7dc9")
        self.caption("40 精车：以两端中心孔定位，切掉变形和氧化层，轴承位、齿轮位留 0.3 mm 磨量", "40 Finish turning between centres removes distortion and scale, leaving 0.3 mm to grind")
        self.play(Transform(bar, fin), run_time=2)
        key = Rectangle(width=45 * SX, height=5 * SY, fill_color=BG, fill_opacity=1, stroke_color="#7b5fb3", stroke_width=2)
        key.move_to(np.array([X0 + (52 + 30) * SX, (40.3 / 2 - 2.5) * SY, 0]))
        self.caption("50 铣键槽：键槽 12N9，在磨削之前铣，毛刺不会碰伤磨好的表面", "50 Keyway 12N9 is milled before grinding, so burrs cannot spoil the ground seats")
        self.play(FadeIn(key), run_time=1.2)
        fin2 = profile([d for d, _ in SEGS], "#2f8f5b")
        self.caption("60 磨外圆：两处轴承位和齿轮位磨到 k6、Ra 0.8", "60 Grinding brings the bearing and gear seats to k6, Ra 0.8")
        self.play(Transform(bar, fin2), key.animate.set_stroke("#2f8f5b"), run_time=2)
        self.caption("70 检验：按检验模板量直径、键槽宽、粗糙度和硬度", "70 Inspection: diameters, keyway width, roughness, hardness")
        self.card([["从毛坯到成品：先粗后精，热处理在中间，键槽在磨削前", "Rough before finish, heat treatment between, keyway before grinding"],
                   ["毛坯 2.8 kg，成品约 1.24 kg：一半多变成了切屑", "Blank 2.8 kg, part about 1.24 kg: more than half becomes chips"]])
