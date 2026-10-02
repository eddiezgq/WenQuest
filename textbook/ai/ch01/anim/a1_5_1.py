"""动画 1.5.1（配图 1.5.1）：一张 224×224×3 的图片逐层穿过 AlexNet。每一层出现时显示输出尺寸、乘加次数和参数量，
右侧的累计条不断增长；最后对比卷积层与全连接层：运算集中在卷积层，参数集中在全连接层。
逐层数字按式 (1.5.1) 计算，与程序 1.5.1 相同。"""
from manim import *
from wq_anim import *
import numpy as np

CONV = [("conv1", 55, 55, 96, 11, 11, 3), ("conv2", 27, 27, 256, 5, 5, 48), ("conv3", 13, 13, 384, 3, 3, 256),
        ("conv4", 13, 13, 384, 3, 3, 192), ("conv5", 13, 13, 256, 3, 3, 192)]
FC = [("fc6", 9216, 4096), ("fc7", 4096, 4096), ("fc8", 4096, 1000)]


def layers():
    out = []
    for n, ho, wo, co, kh, kw, ci in CONV:
        out.append((n, f"{ho}×{wo}×{co}", ho * wo * co * kh * kw * ci, co * kh * kw * ci + co, True))
    for n, fi, fo in FC:
        out.append((n, f"{fo}", fi * fo, fi * fo + fo, False))
    return out


class Lesson(Base):
    def construct(self):
        self.title("1.5", "一次推理要做多少次乘加", "How many multiply–adds in one inference")
        L = layers()
        total_mac = sum(x[2] for x in L)
        total_par = sum(x[3] for x in L)
        img = Square(side_length=1.0, color=GREY_B, fill_color=BLUE_E, fill_opacity=0.7).move_to(LEFT * 6.0 + UP * 0.9)
        img_lab = zh("224×224×3", 18, GREY_A).next_to(img, DOWN, buff=0.15)
        self.play(FadeIn(img), FadeIn(img_lab))
        self.caption("输入：一张 224×224 的彩色图片", "Input: one 224×224 colour image")
        boxes = VGroup()
        x0 = -4.7
        for i, (n, shape, mac, par, conv) in enumerate(L):
            h = 1.6 - 0.12 * i if conv else 0.9
            b = Rectangle(width=0.62, height=h, color=BLUE if conv else GOLD, fill_opacity=0.35, stroke_width=2)
            b.move_to(RIGHT * (x0 + 0.92 * i) + UP * 0.9)
            t = zh(n, 16, WHITE).next_to(b, UP, buff=0.12)
            s = zh(shape, 13, GREY_A).next_to(b, DOWN, buff=0.12)
            boxes.add(VGroup(b, t, s))
        # cumulative bar
        bar_frame = Rectangle(width=9.0, height=0.36, color=GREY_B, stroke_width=1.5).move_to(DOWN * 1.6 + LEFT * 0.4)
        self.play(Create(bar_frame))
        acc = 0
        segs = VGroup()
        mac_txt = VGroup()
        for i, (n, shape, mac, par, conv) in enumerate(L):
            self.play(FadeIn(boxes[i], shift=RIGHT * 0.2), run_time=0.45)
            w = 9.0 * mac / total_mac
            seg = Rectangle(width=max(w, 0.02), height=0.34, stroke_width=0, fill_color=BLUE if conv else GOLD, fill_opacity=0.9)
            seg.move_to(bar_frame.get_left() + RIGHT * (9.0 * acc / total_mac + w / 2))
            acc += mac
            new_txt = VGroup(zh("累计乘加", 22, GREY_A), zh("%.0f 百万" % (acc / 1e6), 30, YELLOW),
                             en("%.0f million" % (acc / 1e6), 20)).arrange(RIGHT, buff=0.25).next_to(bar_frame, DOWN, buff=0.3)
            info = VGroup(zh("%s：%.1f 百万次乘加，%.2f 百万个参数" % (n, mac / 1e6, par / 1e6), 22, WHITE)).to_edge(RIGHT, buff=0.5).shift(UP * 2.6)
            anims = [GrowFromEdge(seg, LEFT), FadeIn(info)]
            if len(mac_txt):
                anims += [FadeOut(mac_txt[0]), FadeIn(new_txt)]
            else:
                anims += [FadeIn(new_txt)]
            self.play(*anims, run_time=0.6 if i > 1 else 0.9)
            segs.add(seg)
            mac_txt = VGroup(new_txt)
            self.wait(0.35 if i > 1 else 0.8)
            self.play(FadeOut(info), run_time=0.25)
        self.caption("一张图共约 %.0f 百万次乘加，即约 %.2f GFLOP" % (total_mac / 1e6, 2 * total_mac / 1e9),
                     "About %.0f million multiply–adds per image, i.e. %.2f GFLOP" % (total_mac / 1e6, 2 * total_mac / 1e9))
        conv_mac = sum(x[2] for x in L if x[4]) / total_mac
        fc_par = sum(x[3] for x in L if not x[4]) / total_par
        note = VGroup(bi(["卷积层：%.0f%% 的乘加" % (100 * conv_mac), "conv layers: %.0f%% of multiply–adds" % (100 * conv_mac)], 26, BLUE),
                      bi(["全连接层：%.0f%% 的参数" % (100 * fc_par), "fc layers: %.0f%% of parameters" % (100 * fc_par)], 26, GOLD)
                      ).arrange(DOWN, buff=0.3, aligned_edge=LEFT).to_edge(RIGHT, buff=0.5).shift(UP * 2.3)
        self.play(FadeIn(note))
        self.caption("运算多的地方和数据多的地方不在一处", "Where the arithmetic is and where the data is are different places", wait=2.0)
        self.card([["AlexNet 一次推理", "One AlexNet inference"],
                   MathTex(r"\text{MAC} = H_{\rm out}W_{\rm out}C_{\rm out}\times K_hK_wC_{\rm in}", font_size=40),
                   MathTex(r"%.0f \times 10^{6}\ \text{MAC} \approx %.2f\ \text{GFLOP}" % (total_mac / 1e6, 2 * total_mac / 1e9), font_size=40)])
