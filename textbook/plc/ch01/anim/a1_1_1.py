"""动画 1.1.1（配图 1.1.1）：继电器柜改成 PLC 柜——同一条输送线，接线怎样变少，修改怎样变快。"""
from manim import *
from wq_anim import *


def contact(x, y, name, nc=False, color=INK):
    g = VGroup(Line([x, y, 0], [x + 0.25, y, 0], color=color), Line([x + 0.25, y - 0.2, 0], [x + 0.25, y + 0.2, 0], color=color),
               Line([x + 0.5, y - 0.2, 0], [x + 0.5, y + 0.2, 0], color=color), Line([x + 0.5, y, 0], [x + 0.75, y, 0], color=color))
    if nc:
        g.add(Line([x + 0.18, y - 0.26, 0], [x + 0.57, y + 0.26, 0], color=color))
    g.add(Text(name, font=LATIN, font_size=14, color=color).move_to([x + 0.37, y + 0.38, 0]))
    return g


def coil(x, y, name, color=INK):
    return VGroup(Circle(radius=0.22, color=color).move_to([x + 0.22, y, 0]),
                  Text(name, font=LATIN, font_size=14, color=color).move_to([x + 0.22, y + 0.42, 0]))


def rung(y, items, out, x0=-6.6, x1=-0.3):
    g, x = VGroup(), x0
    for name, nc in items:
        g.add(Line([x, y, 0], [x + 0.2, y, 0], color=INK))
        g.add(contact(x + 0.2, y, name, nc))
        x += 0.85
    g.add(Line([x, y, 0], [x1 - 0.44, y, 0], color=INK))
    g.add(coil(x1 - 0.44, y, out))
    return g


class Lesson(Base):
    def construct(self):
        self.title("1.1", "继电器控制与 PLC 控制", "Relay control and PLC control")
        rails = VGroup(Line([-6.6, 2.0, 0], [-6.6, -2.5, 0], color=INK, stroke_width=4), Line([-0.3, 2.0, 0], [-0.3, -2.5, 0], color=INK, stroke_width=4))
        r1 = rung(1.4, [("S0", 1), ("S2", 1), ("F1", 1), ("S1", 0), ("B2", 1), ("KA2", 1)], "KM1")
        r2 = rung(0.1, [("KM1", 0), ("B2", 1)], "KT1")
        r3 = rung(-1.1, [("KT1", 0), ("S1", 1)], "KA2")
        hdr = Text("继电器控制", font=CJK, font_size=22, color=INK).move_to([-3.45, 2.4, 0])
        self.play(FadeIn(hdr), Create(rails))
        self.play(Create(r1), run_time=1.6)
        self.caption("启动、停止、急停、过载、到末端：触点串成一行，逻辑就是接线", "Start, stop, e-stop, overload, end: contacts in series; the logic is the wiring")
        self.play(Create(r2), Create(r3), run_time=1.6)
        self.caption("卡料报警要再加一个时间继电器 KT1 和一个中间继电器 KA2", "The jam alarm needs a timer relay KT1 and an auxiliary relay KA2")
        relay = VGroup(rails, r1, r2, r3, hdr)

        # the PLC on the right: devices on terminals, the logic in a program
        plc = RoundedRectangle(width=3.0, height=3.9, corner_radius=0.15, color=INK, fill_color=STEEL, fill_opacity=0.12).move_to([3.6, -0.15, 0])
        ptitle = Text("PLC", font=LATIN, font_size=22, color=INK).move_to([3.6, 1.45, 0])
        ins = ["S1", "S2", "S0", "F1", "B1", "B2"]
        outs = ["KM1", "H1", "H2"]
        wires = VGroup()
        for i, n in enumerate(ins):
            y = 1.2 - i * 0.48
            wires.add(Line([1.3, y, 0], [2.1, y, 0], color=GREEN), Text(n, font=LATIN, font_size=15, color=INK).move_to([1.0, y, 0]))
        for i, n in enumerate(outs):
            y = 0.9 - i * 0.7
            wires.add(Line([5.1, y, 0], [5.8, y, 0], color=BLUE), Text(n, font=LATIN, font_size=15, color=INK).move_to([6.25, y, 0]))
        code = Text("KM1_Run :=\n (S1_Start OR KM1_Run)\n AND S2_Stop AND S0_EStop\n AND F1_Overload\n AND NOT B2_End\n AND NOT jammed;",
                    font="DejaVu Sans Mono", font_size=12, color=INK, line_spacing=0.8).move_to([3.6, -0.3, 0])
        hdr2 = Text("PLC 控制", font=CJK, font_size=22, color=INK).move_to([3.6, 2.4, 0])
        self.play(FadeIn(hdr2), Create(plc), FadeIn(ptitle))
        self.play(LaggedStart(*[Create(w) for w in wires], lag_ratio=0.08), run_time=1.6)
        self.caption("按钮、开关接到输入端子，接触器、指示灯接到输出端子：接线只说明“谁接在哪里”", "Buttons and switches on input terminals, contactor and lamps on outputs: the wiring only says what goes where")
        self.play(Write(code), run_time=2)
        self.caption("逻辑写在程序里，自锁就是“OR KM1_Run”这几个字", "The logic is in the program: the seal-in is just 'OR KM1_Run'")

        # a change request: stop 0.5 s after the bar reaches the end
        req = Text("新要求：到末端后再走 0.5 s 再停", font=CJK, font_size=20, color=ORANGE).move_to([3.6, -2.5, 0])
        self.play(FadeIn(req))
        kt2 = rung(-2.25, [("B2", 0)], "KT2")
        cross = Cross(r1[9], stroke_color=RED, stroke_width=4)
        self.play(Create(cross), Create(kt2), run_time=1.5)
        self.caption("继电器柜：加一个时间继电器 KT2，拆线、接线、查线——停产一两天", "Relay cabinet: add a timer relay, unwire, rewire, check: a day or two of downtime")
        code2 = Text("KM1_Run :=\n (S1_Start OR KM1_Run)\n AND S2_Stop AND S0_EStop\n AND F1_Overload\n AND NOT tEnd.Q\n AND NOT jammed;",
                     font="DejaVu Sans Mono", font_size=12, color=INK, line_spacing=0.8).move_to(code)
        self.play(Transform(code, code2), run_time=1.2)
        dl = Text("下载 ✓", font=CJK, font_size=18, color=GREEN).next_to(plc, RIGHT, buff=0.15).shift(DOWN * 1.4)
        self.play(FadeIn(dl, shift=UP * 0.2))
        self.caption("PLC：加一个定时器、改一行程序、下载——几分钟，一根线不动", "PLC: add a timer, change a line, download: minutes, not one wire touched")
        self.card([["继电器控制：逻辑在接线里，改逻辑要改线", "Relay control: the logic is the wiring; change the logic, change the wires"],
                   ["PLC 控制：逻辑在程序里，改逻辑只要改程序", "PLC control: the logic is the program; change the logic, change the program"]])
