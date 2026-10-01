"""动画 4.3.1（配图 4.3.1）：物体先按两步（绕 z 转 30°、再绕自身 x 转 45°）到达终止姿态；再找出转轴，绕它一步转到。"""
from manim import *
from wq_anim import *
import numpy as np
import math

O = np.array([0.0, -0.6, 0])
SC = 1.7


def axis_angle(w, t):
    w = np.asarray(w, float) / np.linalg.norm(w)
    K = np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def body(R, color=STEEL):
    """A small box with its own frame."""
    a, b, c = 0.55, 0.35, 0.2
    V = [np.array([x, y, z]) for x in (-a, a) for y in (-b, b) for z in (-c, c)]
    P = [proj3(R @ v, O, SC) for v in V]
    faces = [[0, 1, 3, 2], [4, 5, 7, 6], [0, 1, 5, 4], [2, 3, 7, 6], [0, 2, 6, 4], [1, 3, 7, 5]]
    box = VGroup(*[Polygon(*[P[i] for i in f], color=color, fill_color=NAVY, fill_opacity=0.25, stroke_width=2) for f in faces])
    return VGroup(box, frame3(O, R, length=1.0, scale=SC))


class Lesson(Base):
    def construct(self):
        self.title("4.3", "欧拉转动定理", "Euler's rotation theorem")
        R_end = rot_z(30) @ rot_x(45)
        ghost = body(R_end, GREY_B).set_opacity(0.25)
        b = body(np.eye(3))
        self.play(FadeIn(b))
        self.caption("目标姿态（灰色）：先绕 z 转 30°，再绕自身 x 轴转 45°", "Target (grey): 30° about z, then 45° about its own x")
        self.play(FadeIn(ghost))
        t = ValueTracker(0.0)
        b.add_updater(lambda m: m.become(body(rot_z(30 * t.get_value()))))
        self.play(t.animate.set_value(1), run_time=2)
        b.clear_updaters()
        t.set_value(0)
        b.add_updater(lambda m: m.become(body(rot_z(30) @ rot_x(45 * t.get_value()))))
        self.play(t.animate.set_value(1), run_time=2)
        b.clear_updaters()
        self.caption("两步到达。能否绕一根轴，一步转到？", "Two steps. Can one turn about a single axis do it?")
        self.play(FadeOut(b))
        vals, vecs = np.linalg.eig(R_end)
        w = np.real(vecs[:, int(np.argmin(abs(vals - 1)))])
        th = math.acos((np.trace(R_end) - 1) / 2)
        w = w / np.linalg.norm(w)
        if not np.allclose(axis_angle(w, th), R_end):
            w = -w
        axis = Line(proj3(-1.5 * w, O, SC), proj3(1.6 * w, O, SC), color=YELLOW, stroke_width=5)
        alab = MathTex(r"\hat\omega", color=YELLOW).next_to(proj3(1.6 * w, O, SC), UP, buff=0.1)
        self.play(Create(axis), Write(alab))
        self.caption("转轴是 R 的特征值为 1 的特征向量；转角由迹求出：53.65°", "Axis: eigenvector for eigenvalue 1; angle from the trace: 53.65°")
        b2 = body(np.eye(3))
        self.play(FadeIn(b2))
        t.set_value(0)
        b2.add_updater(lambda m: m.become(body(axis_angle(w, th * t.get_value()))))
        self.play(t.animate.set_value(1), run_time=3.5, rate_func=smooth)
        b2.clear_updaters()
        self.caption("绕这根轴一步转过 53.65°，与两步的结果完全重合", "One turn of 53.65° about this axis lands exactly on the target")
        self.wait(1.5)
        self.card([["欧拉转动定理（1775）", "Euler's rotation theorem (1775)"],
                   ["任何转动都是绕某一固定轴转过一个角度", "Every rotation is a turn about some fixed axis"],
                   MathTex(r"R\hat\omega=\hat\omega,\qquad \mathrm{tr}\,R=1+2\cos\theta", font_size=44)])
