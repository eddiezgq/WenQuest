"""动画 11.1.2（配图 11.1.2）：同一根轴、不同节距。h = 0 为转动关节，h 有限为螺旋副，h 越大螺旋线越直，极限为移动关节。"""
from manim import *
from wq_anim import *
import numpy as np

R0 = 0.42                                   # 点到轴的距离（画面单位）
TMAX = 2.5 * np.pi
SC = 1.45
CASES = [(-4.8, 0.0, r"h = 0", "转动关节", "revolute"),
         (-1.6, 0.08, r"h = 0.08", "螺旋副", "helical"),
         (1.6, 0.2, r"h = 0.2", "螺旋副（节距大）", "helical, larger pitch"),
         (4.8, None, r"h \to \infty", "移动关节", "prismatic")]


def point(x0, h, t):
    base = np.array([x0, -2.1, 0.0])
    if h is None:                            # 移动关节：不转，只沿轴走（每单位 θ 走 0.28）
        return proj3(np.array([R0, 0.0, 0.28 * t]), base, SC)
    return proj3(np.array([R0 * np.cos(t), R0 * np.sin(t), h * t]), base, SC)


class Lesson(Base):
    def construct(self):
        self.title("11.1", "同一根轴，不同的节距", "One axis, different pitches")
        th = ValueTracker(0.0)
        axes, labels, traces, dots = VGroup(), VGroup(), VGroup(), VGroup()
        for x0, h, tex, zt, et in CASES:
            base = np.array([x0, -2.1, 0.0])
            axes.add(DashedLine(proj3(np.array([0, 0, -0.3]), base, SC), proj3(np.array([0, 0, 2.4]), base, SC), color=GREY_B))
            axes.add(Arrow(proj3(np.array([0, 0, 2.2]), base, SC), proj3(np.array([0, 0, 2.6]), base, SC), buff=0, color=WHITE, stroke_width=4))
            labels.add(VGroup(MathTex(tex, font_size=34, color=YELLOW), zh(zt, 22), en(et, 15)).arrange(DOWN, buff=0.08)
                       .move_to(np.array([x0, 2.3, 0])))
            traces.add(TracedPath(lambda x0=x0, h=h: point(x0, h, th.get_value()), stroke_color=ORANGE, stroke_width=4))
            dots.add(always_redraw(lambda x0=x0, h=h: Dot(point(x0, h, th.get_value()), radius=0.08, color=ORANGE)))
        self.play(Create(axes), FadeIn(labels), run_time=1.2)
        self.add(traces, dots)
        self.caption("同一个转角 θ，节距 h 决定沿轴前进多少：hθ", "For the same turn θ the pitch h sets the advance hθ", wait=0)
        self.play(th.animate.set_value(TMAX), run_time=6.0, rate_func=linear)
        self.caption("h = 0：点走圆，关节只转不移；h 越大，螺旋线拉得越直",
                     "h = 0: a circle, turning only; larger h stretches the helix", wait=2.0)
        self.caption("h → ∞：只剩沿轴的平移，这就是移动关节", "h → ∞: only the slide along the axis remains, the prismatic joint", wait=2.0)
        self.card([["三种单自由度低副是同一种东西", "The three 1-DOF lower pairs are one thing"],
                   MathTex(r"\mathcal{S}=\begin{pmatrix}\hat\omega\\ -\hat\omega\times q + h\hat\omega\end{pmatrix}", font_size=46),
                   ["R：h = 0　　H：h 有限　　P：h → ∞", "R: h = 0    H: finite h    P: h → ∞"]])
