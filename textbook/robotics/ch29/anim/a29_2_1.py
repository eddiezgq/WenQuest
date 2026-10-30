"""动画 29.2.1（配图 29.2.1）：从机器人厂的物料清单到 MJCF。
(1) WQ-CR5 的大臂（连杆 2）：铝管 Ø90×3（约 0.89 kg）、下一个关节模组 WQJ-M（2.0 kg，在 0.4 m 处）、罩壳（0.3 kg），
    逐块装上，质心按质量加权移到 −0.326 m（示例值，与零件库 B-ARM-WQCR5 一致）；惯量用平行轴定理相加。
(2) 电机转子：100 W 电机的转子惯量 4×10⁻⁶ kg·m²，乘以减速比的平方 100² 变成 0.04 kg·m²，腕关节 J6 的等效惯量里它占八成多。
(3) 位置伺服：kp(u − θ) 把手臂拉向目标，重力把它往下拽，停在两者平衡的地方 θ = u − K_p⁻¹ g(θ)：带 5 kg 标准负载，TCP 下垂约 41 mm。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("29.2", "从物料清单到仿真模型", "From the bill of materials to a simulation model")
        sc = 9.0                                     # 图中 1 m 的长度
        o = np.array([4.0, -0.4, 0])                 # 大臂的关节 J2 在右，臂向左伸 0.4 m
        parts = [("铝管 Ø90×3", 0.885, -0.20, 0.045 * sc, 0.4 * sc, GREY_B),
                 ("关节模组 WQJ-M", 2.0, -0.40, 0.045 * sc, 0.095 * sc, BLUE),
                 ("罩壳与线缆", 0.30, -0.20, 0.04 * sc, 0.08 * sc, GREY_D)]
        self.add(Dot(o, color=YELLOW), zh("J2", 22, YELLOW).next_to(o, DOWN, buff=0.1))
        m_tot, mc = 0.0, 0.0
        com = always_redraw(lambda: VGroup())
        rd = VGroup()
        shapes = []
        for k, (name, m, x, r, L, col) in enumerate(parts):
            if k == 0:
                sh = RoundedRectangle(width=L, height=2 * r, corner_radius=r * 0.9, color=col, fill_color=col, fill_opacity=0.5).move_to(o + np.array([x * sc, 0, 0]))
            elif k == 1:
                sh = Circle(radius=r, color=col, fill_color=col, fill_opacity=0.8).move_to(o + np.array([x * sc, 0, 0]))
            else:
                sh = Rectangle(width=L, height=r, color=col, fill_color=col, fill_opacity=0.6).move_to(o + np.array([x * sc, 0.55, 0]))
            self.play(FadeIn(sh, shift=DOWN * 0.4), run_time=0.7)
            shapes.append(sh)
            m_tot += m
            mc += m * x
            line = zh(f"{name}：{m:.2f} kg，质心在 {x:.2f} m", 22).to_corner(UR, buff=0.4).shift(DOWN * (1.0 + 0.45 * k))
            self.play(FadeIn(line), run_time=0.4)
            rd.add(line)
            cx = mc / m_tot
            dot = Dot(o + np.array([cx * sc, -0.75, 0]), color=RED, radius=0.11)
            lab = zh(f"质心 {cx:.3f} m，共 {m_tot:.2f} kg", 22, RED).next_to(dot, DOWN, buff=0.1)
            if k == 0:
                cg = VGroup(dot, lab)
                self.play(FadeIn(cg), run_time=0.4)
            else:
                self.play(Transform(cg, VGroup(dot, lab)), run_time=0.6)
        self.caption("每块零件的质量、质心、惯量按平行轴定理相加，写成 MJCF 的 <inertial>：每个数都有来历",
                     "Mass, centre and inertia of every part add up by the parallel-axis theorem into the MJCF <inertial>", wait=2.0)
        self.clear_stage()
        # (2) 转子惯量
        rotor = Circle(radius=0.25, color=ORANGE, fill_opacity=0.8).move_to([-4.5, 0.3, 0])
        gear = Circle(radius=1.2, color=BLUE, stroke_width=6).move_to([-1.5, 0.3, 0])
        self.play(FadeIn(rotor), FadeIn(gear), run_time=0.6)
        self.add(zh("电机转子", 22, ORANGE).next_to(rotor, DOWN), zh("谐波减速器 i = 100", 22, BLUE).next_to(gear, DOWN))
        self.play(Rotate(rotor, 6 * TAU, run_time=2.0, rate_func=linear), Rotate(gear, 6 * TAU / 100 * 8, run_time=2.0, rate_func=linear))
        eq = VGroup(MathTex(r"J_{\mathrm{arm}} = k_r^2 J_m = 100^2 \times 4\times10^{-6} = 0.04\ \mathrm{kg\,m^2}", font_size=36),
                    zh("腕关节 J6 的等效惯量里，电机转子占八成多", 26, YELLOW)).arrange(DOWN).move_to([3.4, 1.0, 0])
        fit(eq, 5.8)
        self.play(Write(eq), run_time=1.5)
        self.caption("减速比 100 把转子的惯量放大一万倍：模型里漏了 armature，手腕就轻了几倍到上百倍",
                     "A ratio of 100 multiplies the rotor inertia by ten thousand: leave out the armature and the wrist is far too light", wait=2.0)
        self.clear_stage()
        # (3) 位置伺服的下垂
        base = np.array([-3.5, -1.8, 0])
        ang = ValueTracker(0.0)
        tgt = planar_arm(base, [70, -55], [2.4, 2.0], color=GREY_B)
        tgt.set_opacity(0.35)
        self.add(tgt, zh("目标", 22, MUTED).move_to(base + np.array([3.4, 1.9, 0])))
        live = always_redraw(lambda: planar_arm(base, [70 - 6 * ang.get_value(), -55 - 4 * ang.get_value()], [2.4, 2.0]))
        self.add(live)
        load = always_redraw(lambda: Square(0.35, color=ORANGE, fill_opacity=0.9).move_to(planar_fk(base, [70 - 6 * ang.get_value(), -55 - 4 * ang.get_value()], [2.4, 2.0])[-1] + DOWN * 0.25))
        self.add(load)
        txt = VGroup(MathTex(r"\tau = k_p(u - \theta) - k_v\dot\theta", font_size=38),
                     MathTex(r"\theta = u - K_p^{-1}g(\theta)", font_size=38, color=YELLOW),
                     zh("带 5 kg 标准负载：TCP 下垂约 41 mm", 24, RED)).arrange(DOWN, aligned_edge=LEFT).move_to([3.4, 0.8, 0])
        self.play(FadeIn(txt[0]), run_time=0.5)
        self.play(ang.animate.set_value(1.0), run_time=1.6, rate_func=rate_functions.ease_out_cubic)
        self.play(FadeIn(txt[1]), FadeIn(txt[2]), run_time=0.8)
        self.caption("位置伺服就是不带重力补偿的 PD：偏得越多，拉力越大，停在与重力平衡的地方",
                     "A position servo is PD without gravity compensation: it sags until the pull balances the weight", wait=2.0)
        self.card([["MJCF 的要点", "Key points of MJCF"],
                   ["嵌套的 body 就是运动链；关节写在子连杆里", "Nested bodies are the kinematic chain; joints live in the child"],
                   ["默认角度单位是度；armature = 转子惯量 × 减速比²", "Angles default to degrees; armature = rotor inertia × ratio²"],
                   MathTex(r"\theta = u - K_p^{-1}g(\theta)", font_size=40)])
