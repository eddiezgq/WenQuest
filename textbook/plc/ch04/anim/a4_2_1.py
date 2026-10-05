"""动画 4.2.1（配图 4.2.1）：循环扫描逐步播放。按钮 S1 在第 1 次扫描执行程序时按下：输入映像还是 0，程序看不到；
第 2 次扫描读输入时 S1 的 1 进入输入映像，程序把输出映像里的 H1 置 1，写输出时指示灯才亮。"""
from manim import *
from wq_anim import *

Y = 0.3


def cell(x, label, zh, en_lab):
    box = RoundedRectangle(width=2.1, height=1.5, corner_radius=0.1, color=MUTED).move_to([x, Y, 0])
    t = Text(zh, font=CJK, font_size=20, color=INK).move_to([x, Y + 1.05, 0])
    v = Text(label, font=LATIN, font_size=26, color=INK).move_to([x, Y, 0])
    return box, t, v


def bit(x, val, name):
    return Text(f"{name} = {val}", font=LATIN, font_size=24, color=GREEN if val else INK).move_to([x, Y, 0])


class Lesson(Base):
    def construct(self):
        self.title("4.2", "循环扫描：读输入、执行程序、写输出", "The scan cycle: read inputs, execute, write outputs")
        # field (left), input image, program, output image, field (right)
        xs = [-5.4, -2.7, 0.0, 2.7, 5.4]
        s1 = Circle(radius=0.32, color=INK).move_to([xs[0], Y, 0])
        s1_lab = Text("S1", font=LATIN, font_size=22, color=INK).move_to([xs[0], Y + 0.7, 0])
        lamp = Circle(radius=0.32, color=INK).move_to([xs[4], Y, 0])
        lamp_lab = Text("H1", font=LATIN, font_size=22, color=INK).move_to([xs[4], Y + 0.7, 0])
        b1, t1, _ = cell(xs[1], "", "输入映像", "")
        b2, t2, _ = cell(xs[2], "", "程序", "")
        b3, t3, _ = cell(xs[3], "", "输出映像", "")
        prog = Text("H1 := S1;", font=LATIN, font_size=24, color=INK).move_to([xs[2], Y, 0])
        ii = bit(xs[1], 0, "S1"); oi = bit(xs[3], 0, "H1")
        self.play(FadeIn(VGroup(s1, s1_lab, lamp, lamp_lab, b1, t1, b2, t2, b3, t3, prog, ii, oi)))
        phase = Text("", font=CJK, font_size=24).move_to([0, -2.0, 0])
        scan_t = Text("", font=CJK, font_size=22, color=MUTED).move_to([4.6, 2.6, 0])

        def set_phase(zh, scan):
            p = Text(zh, font=CJK, font_size=24, color=STEEL).move_to([0, -2.0, 0])
            s = Text(f"第 {scan} 次扫描", font=CJK, font_size=22, color=MUTED).move_to([4.6, 2.6, 0])
            self.play(Transform(phase, p), Transform(scan_t, s), run_time=0.4)

        def hi(box):
            return box.animate.set_stroke(STEEL, width=6)

        def lo(box):
            return box.animate.set_stroke(MUTED, width=4)

        self.add(phase, scan_t)
        # scan 1: read 0
        set_phase("① 读输入：把端子的状态抄进输入映像", 1)
        arrow = Arrow([xs[0] + 0.4, Y, 0], [xs[1] - 1.1, Y, 0], color=GREEN, buff=0)
        self.play(GrowArrow(arrow), hi(b1)); self.play(FadeOut(arrow), lo(b1))
        set_phase("② 执行程序：只看输入映像，不看端子", 1)
        self.play(hi(b2))
        self.play(s1.animate.set_fill(GREEN, opacity=0.9), run_time=0.5)
        note = Text("S1 此刻按下，程序却看不到", font=CJK, font_size=20, color=RED).move_to([xs[0] + 0.6, Y - 1.3, 0])
        self.play(FadeIn(note))
        self.caption("按钮在执行程序时按下：输入映像里还是 0，这次扫描当它没按", "Pressed while the program runs: the input image still says 0")
        self.play(lo(b2), FadeOut(note))
        set_phase("③ 写输出：把输出映像送到端子", 1)
        self.play(hi(b3)); self.play(lo(b3))
        set_phase("④ 通信与诊断，然后从头再来", 1)
        self.wait(0.6)
        # scan 2
        set_phase("① 读输入：S1 的 1 进入输入映像", 2)
        arrow = Arrow([xs[0] + 0.4, Y, 0], [xs[1] - 1.1, Y, 0], color=GREEN, buff=0)
        self.play(GrowArrow(arrow), hi(b1), Transform(ii, bit(xs[1], 1, "S1"))); self.play(FadeOut(arrow), lo(b1))
        set_phase("② 执行程序：H1 := S1，输出映像里的 H1 变成 1", 2)
        self.play(hi(b2)); self.play(Transform(oi, bit(xs[3], 1, "H1")), lo(b2))
        self.caption("程序算出的结果先写进输出映像，端子这时还没变", "The result goes into the output image; the terminal has not changed yet")
        set_phase("③ 写输出：H1 的端子接通，指示灯亮", 2)
        arrow = Arrow([xs[3] + 1.1, Y, 0], [xs[4] - 0.4, Y, 0], color=ORANGE, buff=0)
        self.play(GrowArrow(arrow), hi(b3)); self.play(lamp.animate.set_fill(YELLOW, opacity=0.9), FadeOut(arrow), lo(b3))
        self.caption("从按下到灯亮，经过了一到两个扫描周期", "From press to lamp: one to two scan cycles")
        self.card([["每次扫描：读输入 → 执行程序 → 写输出 → 通信与诊断", "Every scan: read → execute → write → communicate"],
                   ["程序只看输入映像：扫描中途的变化要等下一次", "The program sees only the input image"],
                   ["输出在写输出时才到端子", "Outputs reach the terminals only when written"],
                   ["响应时间最长约两个扫描周期，再加滤波和输出延迟", "Response: up to about two scans, plus filter and output delay"]])
