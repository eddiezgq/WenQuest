"""动画 29.4.1（配图 29.4.1）：延迟让伺服失稳；用机器人厂的数据随机化。
(1) 单关节 PD：测量值比真实位置晚 T，力矩按“过去的位置”推，推过了头；T 小于临界延迟 T* = φ_m/ω_c 时振荡衰减，大于它时越来越大。
    WQ-CR5 的腕关节 J6（带标准负载）T* ≈ 1.9 ms。
(2) 关节测试台的空载摩擦力矩散布（WQJ-L 名义 1.2 N·m、σ 0.15），抽出一台台“现场”的机器人；控制器 B（模型前馈 + 25 rad/s）24 台都稳，
    控制器 C（80 rad/s）延迟大的一半振荡（与算例 29.4.2 一致）。"""
from manim import *
from wq_anim import *
import numpy as np
import math


def pd_delay(T, n=600, h=0.002, wn=6.0, z=0.6):
    """归一化的单关节：θ̈ = −wn² θ(t − T) − 2 z wn θ̇(t − T)，从 θ = 1 出发（示意的时间尺度）"""
    d = int(round(T / h))
    x, v = 1.0, 0.0
    hist = [(1.0, 0.0)] * (d + 1)
    out = []
    for k in range(n):
        xd, vd = hist[0]
        a = -wn * wn * xd - 2 * z * wn * vd
        v += h * a
        x += h * v
        hist.append((x, v))
        hist.pop(0)
        out.append((k * h, x))
    return out


class Lesson(Base):
    def construct(self):
        self.title("29.4", "仿真里好好的，到了现场就抖", "Fine in simulation, shaking in the field")
        ax = Axes(x_range=[0, 1.2, 0.2], y_range=[-2.0, 2.0, 1], x_length=8.5, y_length=3.8, tips=False,
                  axis_config=dict(color=GREY_B, include_numbers=False)).move_to([-1.0, -0.2, 0])
        self.play(Create(ax), run_time=0.6)
        self.add(zh("关节角偏差", 20, MUTED).next_to(ax, LEFT, buff=0.1).shift(UP * 1.5), zh("时间", 20, MUTED).next_to(ax, DOWN, buff=0.1))
        for T, col, lab in ((0.0, GREEN, "没有延迟"), (0.08, YELLOW, "延迟小于 T*：衰减"), (0.22, RED, "延迟大于 T*：发散")):
            pts = pd_delay(T)
            path = VMobject(color=col, stroke_width=3).set_points_as_corners([ax.c2p(t * 0.6, max(min(x, 1.95), -1.95)) for t, x in pts if t * 0.6 <= 1.2])
            l = zh(lab, 24, col).to_corner(UR, buff=0.5).shift(DOWN * (0.9 + 0.45 * [0.0, 0.08, 0.22].index(T)))
            self.play(Create(path), FadeIn(l), run_time=1.6)
        f = MathTex(r"T^* = \varphi_m/\omega_c", font_size=40, color=YELLOW).to_corner(UR, buff=0.5).shift(DOWN * 2.4)
        self.play(Write(f), run_time=0.8)
        self.caption("测量值晚到一点，力矩就按“过去的位置”推，推过了头；WQ-CR5 的手腕 T* 只有约 1.9 ms",
                     "A late measurement makes the torque push for where the joint was; the WQ-CR5 wrist tolerates only about 1.9 ms", wait=2.0)
        self.clear_stage()
        # (2) 随机化
        ax2 = Axes(x_range=[0.6, 1.8, 0.2], y_range=[0, 1, 1], x_length=6, y_length=2.4, tips=False,
                   axis_config=dict(color=GREY_B, include_numbers=True, font_size=18)).move_to([-3.0, 0.6, 0])
        self.play(Create(ax2), run_time=0.5)
        bell = ax2.plot(lambda x: math.exp(-0.5 * ((x - 1.2) / 0.15) ** 2), x_range=[0.6, 1.8], color=BLUE)
        self.play(Create(bell), run_time=0.8)
        self.add(zh("关节测试台：WQJ-L 空载摩擦力矩 / (N·m)", 20, MUTED).next_to(ax2, DOWN, buff=0.15))
        rng = np.random.default_rng(2029)
        grid = VGroup()
        self.add(zh("B：模型前馈 + 25 rad/s", 24, GREEN).move_to([3.4, 2.2, 0]), zh("C：模型前馈 + 80 rad/s", 24, RED).move_to([3.4, -0.6, 0]))
        for k in range(24):
            fr = rng.normal(1.2, 0.15)
            dl = rng.uniform(0, 3)
            p = Dot(ax2.c2p(min(max(fr, 0.62), 1.78), 0.08), color=WHITE, radius=0.05)
            b = Square(0.28, color=GREEN, fill_opacity=0.8).move_to([1.6 + 0.36 * (k % 8), 1.6 - 0.36 * (k // 8), 0])
            c = Square(0.28, color=(RED if dl > 1.27 else GREEN), fill_opacity=0.8).move_to([1.6 + 0.36 * (k % 8), -1.2 - 0.36 * (k // 8), 0])
            grid.add(p, b, c)
            self.play(FadeIn(p), FadeIn(b), FadeIn(c), run_time=0.12)
        self.caption("按测试台的散布和延迟、负载的范围抽 24 台：B 全都稳；名义上最好的 C，延迟大的一半在抖",
                     "Draw 24 robots from the test-bench spread, delays and loads: B is always stable; C, best on paper, shakes in half", wait=2.0)
        self.card([["仿真与现实", "Simulation and reality"],
                   ["把延迟、控制周期照实放进回路", "Put the delays and the control period into the loop"],
                   MathTex(r"T^* = \varphi_m/\omega_c", font_size=40),
                   ["随机化的范围用数据定：关节测试台、用户的负载", "Set the randomisation from data: test bench, customer loads"]])
