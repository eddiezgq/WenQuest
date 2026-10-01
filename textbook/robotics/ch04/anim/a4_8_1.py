"""动画 4.8.1（配图 4.8.1）：用一阶近似反复更新的坐标系逐渐“变形”——三根轴变长、夹角偏离 90°；正交化后恢复。
（为看得清楚，步长取得很大。）"""
from manim import *
from wq_anim import *
import numpy as np
import math

O = np.array([-2.6, -0.8, 0])
SC = 2.0


def skew(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])


def orth(M):
    U, _, Vt = np.linalg.svd(M)
    return U @ np.diag([1, 1, np.sign(np.linalg.det(U @ Vt))]) @ Vt


class Lesson(Base):
    def construct(self):
        self.title("4.8", "数值漂移与正交化", "Numerical drift and re-orthonormalization")
        w = np.array([0.3, -0.5, 0.8])
        dt = 0.12
        Rs = [np.eye(3)]
        for _ in range(40):
            Rs.append(Rs[-1] @ (np.eye(3) + skew(w) * dt))
        k = ValueTracker(0)

        def current():
            return Rs[int(round(k.get_value()))]

        def info():
            R = current()
            lens = np.linalg.norm(R, axis=0)
            dev = np.abs(R.T @ R - np.eye(3)).max()
            return VGroup(zh("三根轴的长度", 24, INK),
                          MathTex(r"%.3f,\ %.3f,\ %.3f" % tuple(lens), font_size=34),
                          zh("与正交的偏差", 24, INK),
                          MathTex(r"\max|R^{\mathsf T}R-I|=%.3f" % dev, font_size=34, color=YELLOW)).arrange(DOWN, buff=0.25).move_to(np.array([3.6, 0.2, 0]))

        fr = always_redraw(lambda: frame3(O, current(), length=1.0, scale=SC))
        ref = frame3(O, np.eye(3), length=1.0, scale=SC).set_opacity(0.2)
        txt = always_redraw(info)
        self.add(ref, fr, txt)
        self.caption("每一步右乘 I + [ω]Δt（一阶近似），一千次一秒", "Each step multiplies by I + [ω]Δt (first order)", wait=0.5)
        self.play(k.animate.set_value(40), run_time=6, rate_func=linear)
        self.caption("坐标轴变长了，矩阵已不是旋转矩阵", "The axes have grown: no longer a rotation matrix")
        Rfix = orth(Rs[-1])
        self.play(FadeOut(fr), FadeOut(txt), run_time=0.3)
        bad = frame3(O, Rs[-1], length=1.0, scale=SC)
        good = frame3(O, Rfix, length=1.0, scale=SC)
        self.add(bad)
        self.caption("奇异值分解正交化：换成最接近的旋转矩阵", "SVD: replace it by the nearest rotation matrix", wait=0)
        self.play(Transform(bad, good), run_time=2)
        lens = np.linalg.norm(Rfix, axis=0)
        self.play(FadeIn(VGroup(zh("正交化后", 24, INK), MathTex(r"%.3f,\ %.3f,\ %.3f" % tuple(lens), font_size=34, color=GREEN))
                             .arrange(DOWN, buff=0.25).move_to(np.array([3.6, 0.2, 0]))))
        self.wait(1.5)
        self.card([["定期正交化", "Re-orthonormalize regularly"],
                   MathTex(r"R=U\,\mathrm{diag}(1,1,\det UV^{\mathsf T})\,V^{\mathsf T}", font_size=42),
                   ["用四元数时，只需除以它的模", "with quaternions: just divide by the norm"]])
