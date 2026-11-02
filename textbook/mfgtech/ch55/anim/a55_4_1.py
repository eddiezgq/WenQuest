"""动画 55.4.1（配图 55.4.2）：热态塑性变形产生残余拉应力——表层一块被加热、想伸长而被里层压住（压应力），压应力超过高温下的屈服强度，
表层被压短；冷却时它要缩得比原来更短，被里层拉住，留下残余拉应力。应力读数按算例 55.4.1 的示意模型（20CrMnTi，加热到 500 ℃）。"""
from manim import *
from wq_anim import *
import numpy as np

E, NU, ALPHA, SY = 207000.0, 0.3, 11.9e-6, 835.0
K = E * ALPHA / (1 - NU)


def sy_t(t):
    return max(0.0, SY * (1 - (t - 20) / 880))


class Lesson(Base):
    def construct(self):
        self.title("55.4", "磨削热留下的残余拉应力", "Residual tension left by grinding heat")
        bulk = Rectangle(width=8, height=2.2, color=MUTED, fill_color="#3a3f46", fill_opacity=1).move_to(np.array([-1.5, -1.6, 0]))
        lab_b = zh("里层：冷，不变形", 24, MUTED).next_to(bulk, DOWN, buff=0.15)
        T = ValueTracker(20.0)
        state = {"plastic": 0.0, "peak": 20.0}

        def stress(t, cooling):
            if not cooling:
                return -min(K * (t - 20), sy_t(t))
            s_peak = -min(K * (state["peak"] - 20), sy_t(state["peak"]))
            return min(s_peak + K * (state["peak"] - t), sy_t(t))     # 碰到该温度下的屈服强度后沿 σs(T) 上升

        cooling = {"on": False}

        def layer():
            t = T.get_value()
            frac = (t - 20) / 480
            col = interpolate_color(ManimColor("#b0823e"), ManimColor(RED), min(1, max(0, frac)))
            s = stress(t, cooling["on"])
            w = 8 * (1 + s / 8000)
            return Rectangle(width=w, height=0.5, color=col, fill_color=col, fill_opacity=0.9).move_to(np.array([-1.5, -0.25, 0]))

        lay = always_redraw(layer)
        self.play(FadeIn(bulk), FadeIn(lab_b), FadeIn(lay))

        def read():
            t = T.get_value()
            s = stress(t, cooling["on"])
            c = RED if s > 0 else STEEL
            return VGroup(zh(f"表层温度 {t:4.0f} ℃", 28, ORANGE), zh(f"表层应力 {s:+5.0f} MPa", 30, c),
                          zh("（拉为正）", 20, MUTED)).arrange(DOWN, aligned_edge=LEFT).move_to(np.array([4.6, 0.6, 0]))

        rd = always_redraw(read)
        self.play(FadeIn(rd))
        self.caption("砂轮磨过，表层瞬间受热、想伸长——里层冷，把它压住：压应力", "The wheel heats the surface, which wants to grow; the cold bulk holds it: compression")
        self.play(T.animate.set_value(200), run_time=2)
        self.caption("温度越高，屈服强度越低：压应力碰到屈服强度，表层被压短（塑性变形）", "Hotter means weaker: the compression reaches yield and the layer is squeezed shorter")
        self.play(T.animate.set_value(500), run_time=2.5)
        state["peak"] = 500.0
        cooling["on"] = True
        self.caption("冷却：被压短的表层要缩得比原来更短，又被里层拉住", "Cooling: the shortened layer wants to shrink further and is pulled by the bulk")
        self.play(T.animate.set_value(20), run_time=3)
        self.caption("回到室温，表层留下残余拉应力——零件看上去完全正常", "Back at room temperature the surface is left in tension — the part looks perfectly normal")
        self.card([["磨削温度超过二三百摄氏度，表面就会留下可观的残余拉应力", "A few hundred degrees are enough to leave sizeable residual tension"],
                   ["拉应力降低疲劳强度、促进裂纹——要控制磨削温度", "Tension lowers fatigue strength and starts cracks: control the grinding temperature"]])
