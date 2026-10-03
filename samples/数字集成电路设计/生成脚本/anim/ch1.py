"""数字集成电路设计 第 1 章动画（Manim Community，3Blue1Brown 风格，R3）。
数值来自 ../model.py（与浏览器实验同一组参数）。
渲染：manim -r 1920,1080 --fps 30 ch1.py SwitchPath
"""
import sys
from pathlib import Path
import numpy as np
from manim import *

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import model as M  # noqa: E402

CJK = "Noto Sans CJK SC"
config.background_color = "#0f1419"
BLUE_ = "#58a6ff"; GREEN_ = "#56d364"; ORANGE_ = "#ffa657"; RED_ = "#ff7b72"; VIOLET_ = "#d2a8ff"; MUTED = "#8d9ba5"

EN = {
    "MOSFET 开关与 CMOS 反相器": "MOSFET switches and the CMOS inverter",
    "电压传输特性与噪声容限": "Voltage transfer characteristic and noise margins",
    "尺寸与对称": "Sizing and symmetry",
    "传播延时与反相器链": "Propagation delay and the inverter chain",
    "功耗：每次翻转的能量": "Power: the energy of every transition",
    "输入为 0：PMOS 导通，电容经 PMOS 充电到 VDD": "Input 0: the PMOS is on and charges the load capacitor to VDD",
    "输入为 1：NMOS 导通，电容经 NMOS 放电到地": "Input 1: the NMOS is on and discharges the capacitor to ground",
    "稳态时总有一个管子截止：电源到地没有直流通路": "In steady state one transistor is always off: no DC path from VDD to ground",
    "只有翻转的瞬间才有电流——这就是 CMOS 省电的原因": "Current flows only while switching: that is why CMOS saves power",
    "缓慢增大输入，逐点画出输出": "Raise the input slowly and plot the output point by point",
    "两个管子同时饱和的地方，曲线几乎竖直：开关阈值 VM": "Where both transistors saturate the curve is almost vertical: the threshold VM",
    "斜率为 −1 的两点定出 VIL、VIH": "The two points with slope −1 define VIL and VIH",
    "输入干扰小于噪声容限，输出仍是正确的逻辑值": "Noise smaller than the margin still gives the correct logic output",
    "Wp = Wn 时，PMOS 弱，阈值偏低": "With Wp = Wn the PMOS is weaker and the threshold sits low",
    "加宽 PMOS 到 r = 2.25 倍：VM 回到 VDD / 2": "Widen the PMOS to r = 2.25 times: VM moves to VDD / 2",
    "波形上看：上升和下降变得一样快": "In the waveform: rising and falling edges now match",
    "代价：PMOS 更大，输入电容也更大": "The cost: a larger PMOS and a larger input capacitance",
    "最小反相器直接驱动 10 pF：RC 很大，边沿很慢": "A minimum inverter driving 10 pF directly: huge RC, very slow edge",
    "插入逐级放大的反相器链，每级只驱动约 4 倍于自己的负载": "Insert a chain that grows stage by stage; each drives about 4 times its own load",
    "每级都很快，总延时从几十纳秒降到不到 0.3 纳秒": "Each stage is fast; total delay drops from tens of ns to under 0.3 ns",
    "充电：电源送出 CV²，一半存在电容里，一半在 PMOS 上变成热": "Charging: the supply delivers CV², half stored, half burnt in the PMOS",
    "放电：电容里的 ½CV² 在 NMOS 上变成热": "Discharging: the stored ½CV² is burnt in the NMOS",
    "每秒翻转 αfN 次：P = αCV²fN": "αfN transitions per second: P = αCV²fN",
    "电压从 1.8 V 降到 1.2 V：功耗降到 44%": "Lower the supply from 1.8 V to 1.2 V: power drops to 44%",
    "静态时总有一个管子截止，没有直流功耗": "One transistor is always off in steady state: no static power",
    "线性区 NMOS 相当于电阻 Ron": "In the linear region the NMOS acts as a resistor Ron",
    "VM 由两管强弱之比决定": "VM is set by the strength ratio of the two transistors",
    "噪声容限 NML = VIL − VOL，NMH = VOH − VIH": "Noise margins NML = VIL − VOL, NMH = VOH − VIH",
    "对称尺寸：上升下降一样快": "Symmetric sizing: equal rise and fall",
    "最优级数：每级扇出约 4": "Optimum number of stages: fan-out about 4 per stage",
    "降压最省电，但门会变慢": "Lowering VDD saves most power, but slows the gates",
}


def en(s, size=20, color="#9aa7b2"):
    return Text(s, font="DejaVu Sans", font_size=size * 0.92, color=color)


def zh(s, size=30, color=WHITE, weight=NORMAL):
    return Text(s, font=CJK, font_size=size, color=color, weight=weight)


class Base(Scene):
    def title(self, no, text):
        head = VGroup(zh(no, 26, YELLOW), zh(text, 34, WHITE, BOLD)).arrange(RIGHT, buff=0.3)
        t = VGroup(head, en(EN.get(text, ""), 20)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        t.to_corner(UL, buff=0.4)
        self.play(FadeIn(t, shift=DOWN * 0.2), run_time=0.8)
        self._cap = None
        return t

    def caption(self, text, wait=0.0):
        new = VGroup(zh(text, 26, "#e6edf3"), en(EN.get(text, ""), 19)).arrange(DOWN, buff=0.08)
        bg = BackgroundRectangle(new, color="#0f1419", fill_opacity=0.85, buff=0.15)
        g = VGroup(bg, new).to_edge(DOWN, buff=0.25)
        if self._cap is None:
            self.play(FadeIn(g, shift=UP * 0.15), run_time=0.6)
        else:
            self.play(FadeOut(self._cap, shift=UP * 0.15), FadeIn(g, shift=UP * 0.15), run_time=0.6)
        self._cap = g
        self.wait(max(wait, 2.0))  # 每条字幕至少留 2 秒阅读时间

    def card(self, lines, wait=4.0):
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
        full = []
        for m in lines:
            full.append(m)
            src = getattr(m, "text", None) or getattr(m, "original_text", None)
            if isinstance(m, Text) and src in EN:
                full.append(en(EN[src], 22))
        body = VGroup(*full).arrange(DOWN, buff=0.3)
        box = SurroundingRectangle(body, color=YELLOW, buff=0.45, corner_radius=0.15, stroke_width=2)
        self.play(Create(box), LaggedStart(*[Write(m) for m in full], lag_ratio=0.35), run_time=2.2)
        self.wait(wait)


def switch(top, bot, closed, color):
    """开关符号：闭合为直线，断开为斜线。"""
    a, b = np.array(top), np.array(bot)
    mid1, mid2 = a + (b - a) * 0.3, a + (b - a) * 0.7
    blade = Line(mid1, mid2 if closed else mid2 + RIGHT * 0.45, color=color, stroke_width=6)
    return VGroup(Line(a, mid1, color=color, stroke_width=5), blade, Line(mid2, b, color=color, stroke_width=5))


# ---------------------------------------------------------------------------------- 1.1
class SwitchPath(Base):
    def construct(self):
        self.title("1.1", "MOSFET 开关与 CMOS 反相器")
        x = -1.0
        vdd = Line([x - 1, 2.3, 0], [x + 1, 2.3, 0], color=MUTED); gnd = Line([x - 1, -2.3, 0], [x + 1, -2.3, 0], color=MUTED)
        lv = zh("VDD", 24, MUTED).next_to(vdd, RIGHT); lg = zh("GND", 24, MUTED).next_to(gnd, RIGHT)
        out = Dot([x, 0, 0], color=WHITE)
        wire = Line([x, 0, 0], [x + 3.0, 0, 0], color=WHITE)
        cap_top = Line([x + 2.6, 0, 0], [x + 3.4, 0, 0], color=WHITE).shift(DOWN * 0.6)
        cap_bot = cap_top.copy().shift(DOWN * 0.25)
        cap = VGroup(Line([x + 3.0, 0, 0], [x + 3.0, -0.6, 0], color=WHITE), cap_top, cap_bot,
                     Line([x + 3.0, -0.85, 0], [x + 3.0, -2.3, 0], color=WHITE), Line([x + 2.6, -2.3, 0], [x + 3.4, -2.3, 0], color=MUTED))
        lc = zh("C", 26).next_to(cap_top, RIGHT)
        self.play(Create(vdd), Create(gnd), FadeIn(lv, lg), Create(wire), Create(cap), FadeIn(lc, out))

        def stage(vin):
            p = switch([x, 2.3, 0], [x, 0, 0], vin == 0, GREEN_ if vin == 0 else MUTED)
            n = switch([x, 0, 0], [x, -2.3, 0], vin == 1, GREEN_ if vin == 1 else MUTED)
            lp = zh("PMOS", 24, GREEN_ if vin == 0 else MUTED).next_to(p, LEFT, buff=0.3)
            ln = zh("NMOS", 24, GREEN_ if vin == 1 else MUTED).next_to(n, LEFT, buff=0.3)
            li = zh(f"输入 = {vin}", 28, YELLOW).move_to([-5.2, 0, 0])
            return VGroup(p, n, lp, ln, li)

        s0 = stage(0)
        self.play(FadeIn(s0))
        self.caption("输入为 0：PMOS 导通，电容经 PMOS 充电到 VDD")
        path = VMobject().set_points_as_corners([[x, 2.3, 0], [x, 0, 0], [x + 3.0, 0, 0], [x + 3.0, -0.6, 0]])
        dots = VGroup(*[Dot(radius=0.07, color=ORANGE_) for _ in range(6)])
        for i, d in enumerate(dots):
            d.move_to(path.point_from_proportion(i / 6))
        self.play(LaggedStart(*[MoveAlongPath(d, path, rate_func=linear) for d in dots], lag_ratio=0.15), run_time=2.5)
        vlab = zh("1.8 V", 26, ORANGE_).next_to(out, UR, buff=0.15)
        self.play(FadeOut(dots), FadeIn(vlab)); self.wait(0.8)

        s1 = stage(1)
        self.play(ReplacementTransform(s0, s1))
        self.caption("输入为 1：NMOS 导通，电容经 NMOS 放电到地")
        path2 = VMobject().set_points_as_corners([[x + 3.0, -0.6, 0], [x + 3.0, 0, 0], [x, 0, 0], [x, -2.3, 0]])
        dots = VGroup(*[Dot(radius=0.07, color=ORANGE_) for _ in range(6)])
        for i, d in enumerate(dots):
            d.move_to(path2.point_from_proportion(i / 6))
        self.play(LaggedStart(*[MoveAlongPath(d, path2, rate_func=linear) for d in dots], lag_ratio=0.15), run_time=2.5)
        v0 = zh("0 V", 26, ORANGE_).next_to(out, UR, buff=0.15)
        self.play(FadeOut(dots), Transform(vlab, v0)); self.wait(0.6)

        self.caption("稳态时总有一个管子截止：电源到地没有直流通路")
        cross = Cross(Line([x, 2.3, 0], [x, -2.3, 0]), stroke_color=RED_, stroke_width=5).scale(0.25).move_to([x + 0.7, 1.15, 0])
        self.play(Create(cross), run_time=0.8); self.wait(1.5)
        self.caption("只有翻转的瞬间才有电流——这就是 CMOS 省电的原因", wait=2.5)
        ron = 0.2 / 1e-3
        self.card([zh("静态时总有一个管子截止，没有直流功耗", 30), zh("线性区 NMOS 相当于电阻 Ron", 30),
                   MathTex(r"R_{on}\approx\frac{1}{k_n'\frac{W}{L}(V_{DD}-V_{T})}", font_size=46)])


# ---------------------------------------------------------------------------------- 1.2
class VtcSweep(Base):
    def construct(self):
        self.title("1.2", "电压传输特性与噪声容限")
        ax = Axes(x_range=[0, 1.8, 0.3], y_range=[0, 1.8, 0.3], x_length=6.0, y_length=4.0, tips=False,
                  axis_config={"color": MUTED, "include_numbers": True, "font_size": 22, "decimal_number_config": {"num_decimal_places": 1}}).shift(LEFT * 1.6 + UP * 0.35)
        xl = MathTex("V_{in}", font_size=30).next_to(ax.x_axis, DOWN, buff=0.35).align_to(ax.x_axis, RIGHT)
        yl = MathTex("V_{out}", font_size=30).next_to(ax.y_axis, UP, buff=0.1)
        self.play(Create(ax), FadeIn(xl, yl))
        Wn, Wp = M.Wmin, M.Wmin * (M.kn / M.kp)
        vs = np.linspace(0, M.VDD, 361); vo = np.array([M.vout(v, Wn, Wp) for v in vs])
        t = ValueTracker(0)
        curve = always_redraw(lambda: ax.plot_line_graph(vs[: max(2, int(t.get_value() * 360) + 1)], vo[: max(2, int(t.get_value() * 360) + 1)],
                                                         add_vertex_dots=False, line_color=BLUE_, stroke_width=5))
        dot = always_redraw(lambda: Dot(ax.c2p(vs[int(t.get_value() * 360)], vo[int(t.get_value() * 360)]), color=ORANGE_, radius=0.09))

        def regions():
            i = int(t.get_value() * 360); v, o = vs[i], vo[i]
            name = {"off": "截止", "lin": "线性", "sat": "饱和"}
            def reg(vgs, vds, vt): return "off" if vgs <= vt else ("lin" if vds < vgs - vt else "sat")
            rn, rp = reg(v, o, M.VTn), reg(M.VDD - v, M.VDD - o, M.VTp)
            g = VGroup(zh(f"NMOS：{name[rn]}", 28, GREEN_), zh(f"PMOS：{name[rp]}", 28, VIOLET_),
                       MathTex(rf"V_{{in}}={v:.2f}\,\mathrm{{V}}", font_size=34)).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
            return g.move_to([4.4, 1.0, 0])
        reg_label = always_redraw(regions)
        self.add(curve, dot, reg_label)
        self.caption("缓慢增大输入，逐点画出输出")
        self.play(t.animate.set_value(0.49), run_time=4, rate_func=linear)
        self.caption("两个管子同时饱和的地方，曲线几乎竖直：开关阈值 VM")
        self.play(t.animate.set_value(1), run_time=4, rate_func=linear)
        vm = M.vm(Wn, Wp)
        vmdot = Dot(ax.c2p(vm, vm), color=RED_); vml = MathTex(rf"V_M={vm:.2f}", font_size=30, color=RED_).next_to(vmdot, RIGHT)
        diag = DashedLine(ax.c2p(0, 0), ax.c2p(1.8, 1.8), color=MUTED)
        self.play(Create(diag), FadeIn(vmdot, vml)); self.wait(0.6)
        self.remove(reg_label)
        nm = M.noise_margins(Wn, Wp)
        self.caption("斜率为 −1 的两点定出 VIL、VIH")
        lines = VGroup()
        for vx, lab, col in ((nm["VIL"], "V_{IL}", GREEN_), (nm["VIH"], "V_{IH}", VIOLET_)):
            yo = M.vout(vx, Wn, Wp)
            tang = Line(ax.c2p(vx - 0.25, yo + 0.25), ax.c2p(vx + 0.25, yo - 0.25), color=col, stroke_width=4)
            vl = DashedLine(ax.c2p(vx, 0), ax.c2p(vx, yo), color=col)
            tl = MathTex(lab, font_size=28, color=col).next_to(ax.c2p(vx, yo), UR, buff=0.12)
            lines.add(tang, vl, tl)
        self.play(LaggedStart(*[Create(m) for m in lines], lag_ratio=0.2), run_time=2.5)
        self.caption("输入干扰小于噪声容限，输出仍是正确的逻辑值")
        band = Rectangle(width=ax.c2p(nm["VIL"], 0)[0] - ax.c2p(0, 0)[0], height=4.0, fill_color=YELLOW, fill_opacity=0.15, stroke_width=0).move_to(ax.c2p(nm["VIL"] / 2, 0.9))
        nml = MathTex(rf"NM_L={nm['NML']:.2f}\,\mathrm{{V}}", font_size=34, color=YELLOW).move_to([4.4, 0.4, 0])
        nmh = MathTex(rf"NM_H={nm['NMH']:.2f}\,\mathrm{{V}}", font_size=34, color=YELLOW).next_to(nml, DOWN)
        self.play(FadeIn(band), Write(nml), Write(nmh), run_time=1.5); self.wait(2.5)
        self.card([zh("VM 由两管强弱之比决定", 30), zh("噪声容限 NML = VIL − VOL，NMH = VOH − VIH", 30),
                   MathTex(r"V_M=\frac{V_{Tn}+r\,(V_{DD}-|V_{Tp}|)}{1+r},\quad r=\sqrt{\frac{k_p'W_p}{k_n'W_n}}", font_size=40)])


# ---------------------------------------------------------------------------------- 1.3
class Sizing(Base):
    def construct(self):
        self.title("1.3", "尺寸与对称")
        r = M.kn / M.kp
        ax = Axes(x_range=[0, 1.8, 0.3], y_range=[0, 1.8, 0.3], x_length=4.6, y_length=3.6, tips=False,
                  axis_config={"color": MUTED, "include_numbers": True, "font_size": 20, "decimal_number_config": {"num_decimal_places": 1}}).move_to([-3.6, 0.1, 0])
        ratio = ValueTracker(1.0)
        vs = np.linspace(0, M.VDD, 181)
        vtc = always_redraw(lambda: ax.plot_line_graph(vs, [M.vout(v, M.Wmin, ratio.get_value() * M.Wmin) for v in vs], add_vertex_dots=False, line_color=BLUE_, stroke_width=5))
        vmd = always_redraw(lambda: Dot(ax.c2p(M.vm(M.Wmin, ratio.get_value() * M.Wmin), M.vm(M.Wmin, ratio.get_value() * M.Wmin)), color=RED_))
        half = DashedLine(ax.c2p(0.9, 0), ax.c2p(0.9, 1.8), color=MUTED)
        # 右边：输入方波与输出波形
        ax2 = Axes(x_range=[0, 2, 0.5], y_range=[0, 1.8, 0.9], x_length=5.2, y_length=3.0, tips=False, axis_config={"color": MUTED}).move_to([3.2, 0.1, 0])

        def wave():
            p = ratio.get_value(); Wn, Wp = M.Wmin, p * M.Wmin
            CL = 4 * M.cin(Wn, Wp) + (Wn + Wp) * M.Cd
            tf, tr = M.req_n(Wn) * CL, M.req_p(Wp) * CL
            T = 1.0; scale = 0.14 / (M.req_n(M.Wmin) * (4 * M.cin(M.Wmin, M.Wmin * r) + M.Wmin * (1 + r) * M.Cd))
            ts = np.linspace(0, 2, 400); v = M.VDD; out = []
            for i, tt in enumerate(ts):
                hi = (tt % T) < T / 2; dt = ts[1] - ts[0]
                if i: v = v * np.exp(-dt / (tf * scale)) if hi else M.VDD - (M.VDD - v) * np.exp(-dt / (tr * scale))
                out.append(v)
            return ax2.plot_line_graph(ts, out, add_vertex_dots=False, line_color=ORANGE_, stroke_width=4)
        vin = ax2.plot_line_graph([0, 0.5, 0.5, 1, 1, 1.5, 1.5, 2], [1.8, 1.8, 0, 0, 1.8, 1.8, 0, 0], add_vertex_dots=False, line_color=MUTED, stroke_width=2)
        w = always_redraw(wave)
        lab = always_redraw(lambda: MathTex(rf"W_p/W_n={ratio.get_value():.2f}", font_size=36).move_to([0, 2.55, 0]))
        self.play(Create(ax), Create(ax2), Create(half), FadeIn(vin))
        self.add(vtc, vmd, w, lab)
        self.caption("Wp = Wn 时，PMOS 弱，阈值偏低", wait=2.0)
        self.caption("加宽 PMOS 到 r = 2.25 倍：VM 回到 VDD / 2")
        self.play(ratio.animate.set_value(r), run_time=6, rate_func=smooth)
        self.wait(2.5)
        self.caption("波形上看：上升和下降变得一样快", wait=2.5)
        a = M.fo4(M.Wmin, M.Wmin); b = M.fo4(M.Wmin, r * M.Wmin)
        tbl = VGroup(MathTex(rf"W_p/W_n=1:\ t_{{PHL}}={a[0]*1e12:.0f},\ t_{{PLH}}={a[1]*1e12:.0f}\ \mathrm{{ps}}", font_size=30),
                     MathTex(rf"W_p/W_n=2.25:\ t_{{PHL}}=t_{{PLH}}={b[0]*1e12:.0f}\ \mathrm{{ps}}", font_size=30)).arrange(DOWN, aligned_edge=LEFT).move_to([0, -2.0, 0])
        self.play(Write(tbl), run_time=1.5)
        self.caption("代价：PMOS 更大，输入电容也更大", wait=2.5)
        self.card([zh("对称尺寸：上升下降一样快", 30), MathTex(r"\frac{W_p}{W_n}=r=\frac{k_n'}{k_p'}\approx 2.25", font_size=44),
                   MathTex(r"t_p=0.69\,R_{eq}\,C_L,\quad R_{eq}\approx\frac{3}{4}\frac{V_{DD}}{I_{DSAT}}", font_size=40)])


# ---------------------------------------------------------------------------------- 1.4
def inv(size, color=BLUE_):
    tri = Polygon([-0.6 * size, size, 0], [-0.6 * size, -size, 0], [0.7 * size, 0, 0], color=color, stroke_width=4)
    bub = Circle(radius=0.08 + 0.04 * size, color=color, stroke_width=4).next_to(tri, RIGHT, buff=0)
    return VGroup(tri, bub)


class Chain(Base):
    def construct(self):
        self.title("1.4", "传播延时与反相器链")
        r = M.kn / M.kp; CL = 10e-12
        one = inv(0.25).move_to([-4.5, 1.2, 0])
        load = Rectangle(width=0.4, height=1.4, fill_color=ORANGE_, fill_opacity=0.8, stroke_width=0).move_to([4.8, 1.2, 0])
        ll = MathTex(r"C_L=10\,\mathrm{pF}", font_size=30, color=ORANGE_).next_to(load, UP)
        wire = Line(one.get_right(), load.get_left(), color=MUTED)
        self.play(FadeIn(one), Create(wire), FadeIn(load, ll))
        self.caption("最小反相器直接驱动 10 pF：RC 很大，边沿很慢")
        ax = Axes(x_range=[0, 1, 0.25], y_range=[0, 1.8, 0.9], x_length=8, y_length=2.2, tips=False, axis_config={"color": MUTED}).move_to([0, -1.4, 0])
        t1 = M.chain_delay(1, CL, r)
        slow = ax.plot(lambda x: 1.8 * (1 - np.exp(-x * 1.2)), x_range=[0, 1], color=RED_, stroke_width=4)
        tl = MathTex(rf"t\approx{t1*1e9:.0f}\,\mathrm{{ns}}", font_size=34, color=RED_).next_to(ax, RIGHT, buff=0.2).shift(UP * 0.5)
        self.play(Create(ax), Create(slow, run_time=3, rate_func=linear), Write(tl)); self.wait(0.8)
        self.caption("插入逐级放大的反相器链，每级只驱动约 4 倍于自己的负载")
        N = 6; f = (CL / M.cin(M.Wmin, r * M.Wmin)) ** (1 / N)
        stages = VGroup(*[inv(0.18 + 0.12 * i) for i in range(N)]).arrange(RIGHT, buff=0.35).move_to([0, 1.2, 0])
        labels = VGroup(*[MathTex(rf"\times{f**i:.0f}" if f ** i >= 10 else rf"\times{f**i:.1f}", font_size=22, color=MUTED).next_to(s, DOWN, buff=0.15) for i, s in enumerate(stages)])
        self.play(FadeOut(wire), ReplacementTransform(one, stages[0]), LaggedStart(*[GrowFromCenter(s) for s in stages[1:]], lag_ratio=0.2), FadeIn(labels), load.animate.move_to([stages.get_right()[0] + 0.6, 1.2, 0]), ll.animate.next_to([stages.get_right()[0] + 0.6, 1.9, 0], UP, buff=0.05), run_time=2.5)
        for s in stages:
            self.play(s.animate.set_color(GREEN_), run_time=0.4)
        self.wait(1.5)
        tN = M.chain_delay(N, CL, r)
        fast = ax.plot(lambda x: 1.8 * (1 - np.exp(-x * 60)), x_range=[0, 1], color=GREEN_, stroke_width=4)
        self.play(Create(fast), run_time=1.0)
        self.caption("每级都很快，总延时从几十纳秒降到不到 0.3 纳秒")
        tf_ = VGroup(zh("6 级", 28, GREEN_), MathTex(rf"t\approx{tN*1e12:.0f}\,\mathrm{{ps}}", font_size=34, color=GREEN_)).arrange(RIGHT, buff=0.15).next_to(tl, DOWN, buff=0.3)
        self.play(Write(tf_)); self.wait(2.5)
        self.card([zh("最优级数：每级扇出约 4", 30), MathTex(r"N\approx\frac{\ln F}{\ln 4},\quad F=\frac{C_L}{C_{in}}", font_size=44),
                   MathTex(rf"F\approx{CL / M.cin(M.Wmin, r * M.Wmin):.0f}\ \Rightarrow\ N\approx 6", font_size=40)])


# ---------------------------------------------------------------------------------- 1.5
class Power(Base):
    def construct(self):
        self.title("1.5", "功耗：每次翻转的能量")
        supply = VGroup(Rectangle(width=1.6, height=0.9, color=BLUE_), zh("电源", 26, BLUE_)).move_to([-4.6, 1.2, 0])
        pm = VGroup(Rectangle(width=1.4, height=0.8, color=VIOLET_), zh("PMOS", 24, VIOLET_)).move_to([-1.6, 1.2, 0])
        capb = VGroup(Rectangle(width=1.2, height=2.0, color=WHITE), zh("C", 28)).move_to([1.4, 1.0, 0])
        nm = VGroup(Rectangle(width=1.4, height=0.8, color=GREEN_), zh("NMOS", 24, GREEN_)).move_to([4.4, 1.2, 0])
        arrows = VGroup(Arrow(supply.get_right(), pm.get_left(), color=MUTED), Arrow(pm.get_right(), capb.get_left(), color=MUTED), Arrow(capb.get_right(), nm.get_left(), color=MUTED))
        self.play(FadeIn(supply, pm, capb, nm), Create(arrows))
        fill = Rectangle(width=1.1, height=0.01, fill_color=ORANGE_, fill_opacity=0.8, stroke_width=0).align_to(capb[0], DOWN).shift(UP * 0.05)
        self.add(fill)
        self.caption("充电：电源送出 CV²，一半存在电容里，一半在 PMOS 上变成热")
        heat1 = VGroup(MathTex(r"\tfrac12 CV^2", font_size=32, color=RED_), zh("热", 26, RED_)).arrange(RIGHT, buff=0.12).next_to(pm, DOWN)
        store = MathTex(r"\tfrac12 CV^2", font_size=32, color=ORANGE_).next_to(capb, DOWN)
        draw = MathTex(r"CV^2", font_size=32, color=BLUE_).next_to(supply, DOWN)
        self.play(fill.animate.stretch_to_fit_height(1.8, about_edge=DOWN), Write(draw), Write(heat1), Write(store), run_time=2.5)
        self.wait(0.8)
        self.caption("放电：电容里的 ½CV² 在 NMOS 上变成热")
        heat2 = VGroup(MathTex(r"\tfrac12 CV^2", font_size=32, color=RED_), zh("热", 26, RED_)).arrange(RIGHT, buff=0.12).next_to(nm, DOWN)
        self.play(fill.animate.stretch_to_fit_height(0.01, about_edge=DOWN), Write(heat2), FadeOut(store), run_time=2.5)
        self.wait(0.6)
        self.caption("每秒翻转 αfN 次：P = αCV²fN")
        q = M.P["problems"]["p15"]
        p1 = M.dyn_power(q["N"], q["alpha"], q["Cgate"], M.VDD, q["f"]); p2 = M.dyn_power(q["N"], q["alpha"], q["Cgate"], q["Vlow"], q["f"])
        eq = MathTex(rf"P=0.1\times 5\,\mathrm{{fF}}\times(1.8\,\mathrm{{V}})^2\times 100\,\mathrm{{MHz}}\times 10^4={p1*1e3:.2f}\,\mathrm{{mW}}", font_size=34).move_to([0, -1.1, 0])
        self.play(Write(eq), run_time=2.0); self.wait(1.5)
        self.caption("电压从 1.8 V 降到 1.2 V：功耗降到 44%")
        base = [-2.5, -2.4, 0]
        b1 = Rectangle(width=1.0, height=2.0 * 0.6, fill_color=BLUE_, fill_opacity=0.8, stroke_width=0)
        b1.move_to(base, aligned_edge=DOWN)
        b2 = Rectangle(width=1.0, height=2.0 * 0.6, fill_color=GREEN_, fill_opacity=0.8, stroke_width=0)
        b2.move_to([base[0] + 1.6, base[1], 0], aligned_edge=DOWN)
        self.play(FadeOut(eq), FadeIn(b1, b2))
        l1 = MathTex(rf"1.8\,\mathrm{{V}}:\ {p1*1e3:.2f}\,\mathrm{{mW}}", font_size=28).next_to(b1, LEFT)
        self.play(b2.animate.stretch_to_fit_height(1.2 * (p2 / p1), about_edge=DOWN), FadeIn(l1), run_time=2)
        l2 = MathTex(rf"1.2\,\mathrm{{V}}:\ {p2*1e3:.2f}\,\mathrm{{mW}}", font_size=28).next_to(b2, RIGHT)
        self.play(FadeIn(l2)); self.wait(2.5)
        self.card([zh("降压最省电，但门会变慢", 30), MathTex(r"P_{dyn}=\alpha\,C\,V_{DD}^2\,f\,N", font_size=48),
                   MathTex(r"E_{\mathrm{transition}}=C V_{DD}^2", font_size=40)])
