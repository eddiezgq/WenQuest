"""动画 21.4.1（配图 21.4.2）：数字工厂巡检的最小 snap 轨迹（算例 21.4.2）。
航点（本章坐标，示意值）与各段时长取程序 21.4.1 的结果：时间分配优化后、按倾角 ≤ 30° 缩放的最快轨迹，
六段时长 2.4725、1.5094、2.2584、1.5992、1.5789、2.9623 s。最小 snap 样条按定理 21.4.2 的线性方程组求解。
画面为车间俯视，1 m 画成 0.22 个单位；橙色箭头为水平加速度（推力倾斜的方向），1 m/s² 画成 0.3 个单位。按实际速度播放。"""
from manim import *
from wq_anim import *
import numpy as np
import math

WP = np.array([(7, 19, 1.0), (12, 19, 3.0), (17, 15, 3.5), (24, 19, 3.0), (31, 15, 3.0), (38, 15, 3.0), (38, 9.5, 1.0)])
TS = np.array([2.4725, 1.5094, 2.2584, 1.5992, 1.5789, 2.9623])
UNITS = {"ht-01": (17, 13, 5, 4), "grd-01": (31, 13, 4.5, 2.2), "qc-01": (38, 13, 4, 3), "cnc-l01-a": (17, 4, 4, 2.2),
         "cnc-l01-b": (24, 4, 4, 2.2), "saw-01": (10, 4, 4, 2.5), "key-01": (31, 4, 3, 2.2), "store-01": (3, 4, 4, 5),
         "vmc-01": (10, 22, 3.5, 3), "hmc-01": (17, 22, 4.5, 3.5), "hob-01": (24, 22, 3.5, 2.5), "asm-01": (31, 22, 5, 3),
         "test-01": (38, 22, 3.5, 2.5), "store-02": (45, 22, 4, 5)}
K = 4
SC = 0.22
ORG = np.array([-6.7, -3.3, 0])


def fact(n, r):
    out = 1.0
    for i in range(r):
        out *= n - i
    return out if r <= n else 0.0


def solve():
    M, N = len(TS), 2 * K
    A = np.zeros((N * M, N * M))
    B = np.zeros((N * M, 3))
    row = [0]

    def put(j, s, r):
        v = np.zeros(N * M)
        for n in range(r, N):
            v[j * N + n] = fact(n, r) * s ** (n - r) / TS[j] ** r
        return v

    def add(v, b=None):
        A[row[0]] = v
        if b is not None:
            B[row[0]] = b
        row[0] += 1

    add(put(0, 0.0, 0), WP[0])
    for r in range(1, K):
        add(put(0, 0.0, r))
    for j in range(M - 1):
        add(put(j, 1.0, 0), WP[j + 1])
        add(put(j + 1, 0.0, 0), WP[j + 1])
        for r in range(1, 2 * K - 1):
            add(put(j, 1.0, r) - put(j + 1, 0.0, r))
    add(put(M - 1, 1.0, 0), WP[-1])
    for r in range(1, K):
        add(put(M - 1, 1.0, r))
    return np.linalg.solve(A, B).reshape(M, N, 3)


CF = solve()
TT = np.cumsum(np.r_[0.0, TS])


def ev(t, r=0):
    j = int(np.clip(np.searchsorted(TT, t, side="right") - 1, 0, len(TS) - 1))
    s = (min(max(t, 0.0), TT[-1]) - TT[j]) / TS[j]
    return sum(CF[j, n] * fact(n, r) * s ** (n - r) for n in range(r, 2 * K)) / TS[j] ** r


def scr(p):
    return ORG + SC * np.array([p[0], p[1], 0])


class Lesson(Base):
    def construct(self):
        self.title("21.4", "给定航点，生成能飞的轨迹", "From waypoints to a flyable trajectory")
        floor = Rectangle(width=50 * SC, height=28 * SC, color=GREY_D, stroke_width=1.5).move_to(scr((25, 14)))
        aisles = VGroup(*[Rectangle(width=50 * SC, height=2 * SC, color=GREY_E, fill_color=GREY_E, fill_opacity=0.5, stroke_width=0)
                          .move_to(scr((25, 28 - y))) for y in (9.0, 18.5)])
        mach = VGroup()
        for k, (x, yf, w, d) in UNITS.items():
            hl = k in ("ht-01", "grd-01", "qc-01")
            mach.add(Rectangle(width=w * SC, height=d * SC, color=GREY_B, fill_color="#5a4a1e" if hl else "#2a3540", fill_opacity=1,
                               stroke_width=1).move_to(scr((x, 28 - yf))))
        self.play(FadeIn(floor), FadeIn(aisles), FadeIn(mach), run_time=1.0)
        dots = VGroup(*[Dot(scr(w), radius=0.07, color=RED) for w in WP])
        labs = VGroup(*[Text(f"W{i} {w[2]:g} m", font=CJK, font_size=16, color=RED_B).next_to(dots[i], UP, buff=0.05)
                        for i, w in enumerate(WP)])
        self.caption("巡检员在平面图上点了七个航点（旁注高度）", "Seven waypoints picked on the floor plan (heights noted)", wait=0)
        self.play(LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.15), FadeIn(labs), run_time=1.5)
        poly = VMobject(color=GREY_B, stroke_width=2).set_points_as_corners([scr(w) for w in WP])
        self.play(Create(poly), run_time=1.0)
        self.caption("折线在拐角处速度方向突变，要无穷大的加速度和倾角，飞不出来",
                     "A polyline turns its velocity instantly: infinite acceleration and tilt, not flyable", wait=0.6)
        tt = np.linspace(0, TT[-1], 600)
        path = VMobject(color=TEAL, stroke_width=4).set_points_smoothly([scr(ev(t)) for t in tt])
        self.caption("最小 snap 样条：每段 7 次多项式，航点处 1～6 阶导数连续，首尾与悬停衔接",
                     "Minimum-snap spline: degree 7 per segment, derivatives 1–6 continuous, starting and ending at hover", wait=0)
        self.play(Create(path), run_time=2.0)
        tk = ValueTracker(0.0)

        def drone():
            t = tk.get_value()
            p, v, a = ev(t), ev(t, 1), ev(t, 2)
            c = scr(p)
            g = VGroup(Circle(radius=0.13, color=WHITE, fill_color=STEEL, fill_opacity=1, stroke_width=2).move_to(c))
            ah = np.array([a[0], a[1], 0])
            if np.linalg.norm(ah) > 0.05:
                g.add(Arrow(c, c + 0.3 * ah, buff=0, color=ORANGE, stroke_width=5, max_tip_length_to_length_ratio=0.25))
            tilt = math.degrees(math.atan2(np.linalg.norm(a[:2]), a[2] + 9.81))
            info = VGroup(Text(f"t = {t:.1f} s", font=CJK, font_size=22, color=INK),
                          Text(f"速度 {np.linalg.norm(v):.2f} m/s，高度 {p[2]:.2f} m", font=CJK, font_size=22, color=INK),
                          Text(f"倾角 {tilt:.1f}°（限制 30°）", font=CJK, font_size=22, color=YELLOW))
            info.arrange(DOWN, aligned_edge=LEFT, buff=0.08).to_corner(UR, buff=0.4).shift(DOWN * 0.55)
            g.add(info)
            return g

        self.add(always_redraw(drone))
        self.caption("X2 沿轨迹飞行：橙色箭头是水平加速度，推力向它的方向倾斜；最大倾角恰为 30°",
                     "X2 flies the path; orange: horizontal acceleration, the thrust tilts that way; peak tilt is exactly 30°", wait=0)
        self.play(tk.animate.set_value(TT[-1]), run_time=TT[-1], rate_func=linear)
        self.caption("姿态、推力、角速度全部由轨迹的导数算出：四旋翼是微分平坦的",
                     "Attitude, thrust and body rates all follow from the path's derivatives: the quadrotor is flat", wait=1.5)
        self.card([["平坦输出：位置 p 与偏航角 ψ", "Flat outputs: position p and yaw ψ"],
                   MathTex(r"\min\int\|p^{(4)}\|^2\,\mathrm dt", font_size=46),
                   MathTex(r"z_b = \frac{\ddot p + \mathfrak g\hat z}{\|\ddot p + \mathfrak g\hat z\|},\qquad "
                           r"\omega_y = \frac{x_b\cdot\dddot p}{\|\ddot p + \mathfrak g\hat z\|}", font_size=40),
                   ["航点 → 光滑曲线 → 姿态、推力、角速度", "Waypoints → smooth curve → attitude, thrust, body rates"]])
