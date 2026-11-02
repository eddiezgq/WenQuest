"""动画 56.6.1（配图 56.6.1）：从图纸要求往前推加工方案链——SH-101 轴承位 IT6、Ra 0.8，渗碳淬火后加工。
最后一道选精磨（经济精度 IT6–7、Ra 0.1–0.8，能磨淬硬钢），它要求上一道到 IT9；淬火后车不动，所以 IT9 要在淬火前车出，
半精车只保证 IT10，选精车（IT7–8）；精车要求上一道到 IT11，粗车按经济精度只保证 IT13，不够，插入半精车（IT8–10）；半精车接在粗车（IT11–13）之后，
粗车接棒料（IT14）。数据取自数字工厂的加工方法表 std/route_methods.yaml（与 hub/route.py 的 chains 结果一致）。"""
from manim import *
from wq_anim import *
import numpy as np

STEPS = [("棒料", "bar", 14, 50.0), ("粗车", "rough turn", 13, 50.0), ("半精车", "semi-finish turn", 10, 6.3),
         ("精车", "finish turn", 8, 1.6), ("精磨", "finish grind", 6, 0.8)]
X = [-5.6, -3.2, -0.8, 1.6, 5.2]
HT_X = 3.4


class Lesson(Base):
    def construct(self):
        self.title("56.6", "由图纸要求倒推加工方案链", "Working a process chain back from the drawing")
        req = VGroup(zh("图纸：轴承位 Ø25 k6", 26, WHITE), zh("IT6、Ra 0.8，渗碳淬火后加工", 24, YELLOW)).arrange(DOWN, buff=0.12)
        req.move_to(np.array([4.3, 3.0, 0]))
        self.play(FadeIn(req))
        self.caption("从最后一道往前推：先选经济精度能满足图纸的最后一道方法", "Start from the last operation: its economic accuracy must cover the drawing")

        def node(i, color=STEEL):
            n, e, it, ra = STEPS[i]
            box = RoundedRectangle(width=1.9, height=1.1, corner_radius=0.12, color=color, stroke_width=3)
            box.move_to(np.array([X[i], 0.2, 0]))
            t = VGroup(zh(n, 26, WHITE), zh(f"IT{it}  Ra {ra:g}", 20, MUTED)).arrange(DOWN, buff=0.08).move_to(box)
            return VGroup(box, t)

        def need(i, text, color=YELLOW):
            return zh(text, 20, color).next_to(np.array([X[i], -0.5, 0]), DOWN, buff=0.25)

        g4 = node(4, GREEN)
        self.play(FadeIn(g4))
        n4 = need(4, "要求上一道 IT9")
        self.play(FadeIn(n4))
        self.caption("精磨：IT6–7、Ra 0.1–0.8，淬硬钢也能磨；它要求上一道到 IT9", "Finish grinding: IT6–7, Ra 0.1–0.8, works on hardened steel; needs IT9 before it")
        ht = Line(np.array([HT_X, -1.2, 0]), np.array([HT_X, 1.3, 0]), color=RED, stroke_width=8)
        htl = zh("渗碳淬火", 22, RED).next_to(ht, UP, buff=0.1)
        self.play(Create(ht), FadeIn(htl))
        nh = zh("淬火后车不动：IT9 要在淬火前车出", 20, RED).move_to(np.array([HT_X, -1.75, 0]))
        self.play(FadeIn(nh))
        self.caption("中间是渗碳淬火：淬火后车刀车不动，上一道必须是淬火前的车削，而且要到 IT9 以内", "Hardening sits in between: no turning after it, so the step before must be a turning step done to IT9 before hardening")
        g3 = node(3)
        self.play(FadeIn(g3))
        n3 = need(3, "要求上一道 IT11")
        self.play(FadeIn(n3))
        self.caption("半精车只保证 IT10，不够；精车 IT7–8，满足；它要求上一道到 IT11", "Semi-finish turning holds only IT10; finish turning (IT7–8) does; it needs IT11 before it")
        bad = node(1, RED).move_to(np.array([X[2], 0.2, 0]))
        self.play(FadeIn(bad))
        cross = zh("粗车只保证 IT13，不够（跳级）", 22, RED).next_to(bad, UP, buff=0.3)
        self.play(FadeIn(cross))
        self.caption("直接接粗车？粗车的经济精度只到 IT13，误差和缺陷层精车一刀切不掉", "Rough turning straight before? It only holds IT13 — finish turning cannot clean that up")
        g2 = node(2)
        self.play(FadeOut(bad), FadeOut(cross), FadeIn(g2))
        n2 = need(2, "要求上一道 IT13")
        self.play(FadeIn(n2))
        self.caption("插入半精车（IT8–10），它接在粗车之后", "Insert semi-finish turning (IT8–10), which follows rough turning")
        g1, g0 = node(1), node(0, MUTED)
        self.play(FadeIn(g1), FadeIn(g0))
        arrows = VGroup(*[Arrow(np.array([X[i] + 0.95, 0.2, 0]), np.array([X[i + 1] - 0.95, 0.2, 0]), buff=0.05, color=WHITE, stroke_width=3)
                          for i in range(4)])
        self.play(FadeOut(n4), FadeOut(nh), FadeOut(n3), FadeOut(n2), Create(arrows))
        self.caption("推到毛坯：粗车 → 半精车 → 精车 → 渗碳淬火 → 精磨", "Back to the blank: rough → semi-finish → finish turn → harden → finish grind")
        # 公差等级一步步降下来
        axis = Line(np.array([-6.2, -2.5, 0]), np.array([6.2, -2.5, 0]), color=MUTED)
        dots = VGroup(*[Dot(np.array([X[i], -2.5 + (14 - STEPS[i][2]) * 0.12, 0]), color=YELLOW) for i in range(5)])
        path = VMobject(color=YELLOW).set_points_as_corners([d.get_center() for d in dots])
        self.play(Create(axis), FadeIn(dots), Create(path))
        self.caption("每一道切掉上一道留下的误差：IT14 → 13 → 10 → 8 → 6", "Each step removes the previous step's error: IT14 → 13 → 10 → 8 → 6")
        self.card([["方案链从最后一道往前推，每一环的经济精度要接得上", "Work the chain backwards; every link's economic accuracy must connect"],
                   ["热处理后只能用能加工淬硬钢的方法；热处理后不再加工的表面会降一级", "After hardening only methods for hard steel; surfaces left after hardening lose a grade"]])
