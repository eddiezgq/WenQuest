"""动画 11.1.1（配图 11.1.1）：同样的动量变化，冲击时间越长，力越小。四足机器人（15 kg）从 0.30 m 高处落地，
落地前动量 36.4 kg·m/s。腿几乎不弯时，地面力是一个又高又窄的脉冲；屈腿缓冲时，是一个又低又宽的脉冲。
两块面积（冲量）相同。为了看清楚，这里把两种力都画成半个正弦形，并略去重力的冲量。"""
from manim import *
from wq_anim import *
import numpy as np

P0 = 15.0 * np.sqrt(2 * 9.81 * 0.30)             # kg·m/s


def pulse(T):
    """半正弦脉冲，面积为 P0：F(t) = (π P0 / 2T) sin(π t / T)。"""
    A = np.pi * P0 / (2 * T)
    return lambda t: A * np.sin(np.pi * t / T) if 0 <= t <= T else 0.0, A


class Lesson(Base):
    def construct(self):
        self.title("11.1", "同样的冲量，不一样的力", "Same impulse, different force")
        ax = Axes(x_range=[0, 0.16, 0.04], y_range=[0, 3000, 1000], x_length=8.0, y_length=4.0,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 20}).move_to(np.array([0.6, -0.1, 0]))
        xl = bi(["落地后的时间 t / s", "time after touchdown t / s"], size=18).next_to(ax, DOWN, buff=0.2)
        yl = bi(["地面力 F / N", "ground force F / N"], size=18).next_to(ax, UP, buff=0.1).shift(LEFT * 3.2)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl))
        f1, A1 = pulse(0.020)
        f2, A2 = pulse(0.12)
        hard = ax.plot(f1, x_range=[0, 0.16, 0.0005], color=RED, use_smoothing=False)
        soft = ax.plot(f2, x_range=[0, 0.16, 0.0005], color=BLUE, use_smoothing=False)
        self.caption("腿几乎不弯：0.02 s 内停下，峰值将近 3000 N", "Stiff legs: stopped in 0.02 s, a peak near 3000 N", wait=0)
        self.play(Create(hard), run_time=1.5)
        a1 = ax.get_area(hard, x_range=[0, 0.020], color=RED, opacity=0.35)
        self.play(FadeIn(a1))
        lab1 = bi([f"峰值 {A1:.0f} N", f"peak {A1:.0f} N"], size=20, color=RED).next_to(ax.c2p(0.02, A1), RIGHT, buff=0.2)
        self.play(FadeIn(lab1))
        self.caption("屈腿缓冲：0.12 s 内停下，峰值只有约 480 N", "Bending the legs: stopped in 0.12 s, a peak of only about 480 N", wait=0)
        self.play(Create(soft), run_time=2)
        a2 = ax.get_area(soft, x_range=[0, 0.12], color=BLUE, opacity=0.35)
        lab2 = bi([f"峰值 {A2:.0f} N", f"peak {A2:.0f} N"], size=20, color=BLUE).next_to(ax.c2p(0.09, A2), UP, buff=0.15)
        self.play(FadeIn(a2), FadeIn(lab2))
        eq = MathTex(r"\int F\,\mathrm dt = \Delta p = " + f"{P0:.1f}" + r"\ \mathrm{N\cdot s}", font_size=36, color=YELLOW).move_to(np.array([2.2, 1.6, 0]))
        self.caption("两块面积相等：动量的变化一样，冲量就一样；时间拉长 6 倍，力就小 6 倍", "The two areas are equal: same change of momentum, same impulse; six times longer means six times smaller force", wait=0)
        self.play(Write(eq))
        self.wait(2.5)
        self.card([["动量定理", "Impulse–momentum theorem"],
                   MathTex(r"\boldsymbol J = \int\boldsymbol F\,\mathrm dt = \Delta\boldsymbol p", font_size=46),
                   ["动量的变化一定时，作用时间越长，平均力越小", "for a given change of momentum, a longer contact means a smaller average force"],
                   ["屈腿落地、气囊、缓冲器都是这个道理", "bent knees, airbags and buffers all work this way"]])
