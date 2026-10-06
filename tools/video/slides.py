"""课件画面（第 22 轮）：用 Manim 按讲稿画一个镜头（片头、幻灯、程序、作业、结尾、封面），时间点由配音决定。

由 make.py 调用：  manim -qh slides.py Shot  （环境变量 WQ_SHOT_SPEC 指向镜头说明 JSON）
JSON：{kind, lang, total, steps: [秒, …], part, head, items, …}。steps[i] 是第 i 项出现的时刻，total 是镜头总长。
风格与教材动画一致（services/animator/wq_anim.py）：深色底、黄色小标题、白字、LaTeX 公式。
"""
from __future__ import annotations

import json
import os
import re

from manim import *  # noqa: F401,F403

BG = "#0f1419"
INK = "#e6edf3"
MUTED = "#9aa7b2"
ACCENT = "#f2c14e"
TEAL = "#2ea8a0"
CJK = "Noto Sans CJK SC"
MONO = "DejaVu Sans Mono"
config.background_color = BG

SPEC = json.loads(open(os.environ["WQ_SHOT_SPEC"], encoding="utf-8").read()) if os.environ.get("WQ_SHOT_SPEC") else {}
LANG = SPEC.get("lang", "zh")
TOP, BOTTOM = 3.55, -2.55          # content area (subtitles live below BOTTOM)
XL, XR = -6.6, 6.6


def T(s, size=30, color=INK, weight=NORMAL, font=CJK):
    return Text(str(s), font=font, font_size=size, color=color, weight=weight)


def _cw(ch: str, size: float) -> float:
    """Estimated advance of one character in manim units (CJK and full-width punctuation are 1 em)."""
    em = size / 48 * 0.667          # Text(font_size=48) ≈ 0.667 units per em
    if "\u2e80" <= ch <= "\u9fff" or "\uff00" <= ch <= "\uffef" or ch in "“”‘’、。，；：？！（）《》":
        return em
    return em * (0.32 if ch == " " else 0.56)


def rich(text: str, size=30, width=12.0, color=INK, line_gap=0.2):
    """Text with inline $math$, wrapped to width (manim units). Returns a left-aligned VGroup of lines.
    Plain runs are set as whole Text objects (so CJK punctuation keeps its full width); only line breaks split them."""
    tokens = [p for p in re.split(r"(\$[^$]+\$)", text) if p]
    lines, cur, x = [], [], 0.0
    gap = 0.1 * size / 30

    def flush():
        nonlocal cur, x
        if cur:
            lines.append(cur)
        cur, x = [], 0.0

    for tok in tokens:
        if tok.startswith("$") and tok.endswith("$") and len(tok) > 1:
            m = MathTex(tok[1:-1], font_size=size * 1.12, color=color)
            if cur and x + gap + m.width > width:
                flush()
            cur.append(m)
            x += (gap if len(cur) > 1 else 0) + m.width
            continue
        rest = tok
        while rest:
            room = width - x - (gap if cur else 0)
            used, n, last_break = 0.0, 0, -1
            for i, ch in enumerate(rest):
                w = _cw(ch, size)
                if used + w > room:
                    break
                used += w
                n = i + 1
                if ch == " " or "\u2e80" <= ch <= "\u9fff" or ch in "，。；：、？！":
                    last_break = i + 1
            if n < len(rest):           # does not all fit: break at a word boundary (Latin) or anywhere (CJK)
                if last_break > 0 and not ("\u2e80" <= rest[n - 1] <= "\u9fff"):
                    n = last_break
                while n < len(rest) and rest[n] in "，。；：、？！）”,.;:?!)":
                    n -= 1                # keep closing punctuation off the start of the next line
                if n <= 0:
                    if cur:
                        flush()
                        continue
                    n = max(1, len(rest))
            piece, rest = rest[:n], rest[n:].lstrip(" ")
            if piece.strip():
                cur.append(T(piece.strip(), size, color))
                x += (gap if len(cur) > 1 else 0) + cur[-1].width
            if rest:
                flush()
    flush()
    rows = []
    for ln in lines:
        g = VGroup(*ln).arrange(RIGHT, buff=gap, aligned_edge=ORIGIN)
        for m in ln:
            if isinstance(m, MathTex):
                m.align_to(g, ORIGIN)
        rows.append(g)
    return VGroup(*rows).arrange(DOWN, aligned_edge=LEFT, buff=line_gap)


def fit(m, w=None, h=None):
    if w and m.width > w:
        m.scale_to_fit_width(w)
    if h and m.height > h:
        m.scale_to_fit_height(h)
    return m


def header(part, head):
    p = T(part, 24, ACCENT, BOLD) if part else None
    h = fit(T(head, 40, WHITE, BOLD), 12.8)
    g = VGroup(*(x for x in (p, h) if x)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
    g.to_corner(UL, buff=0.45)
    rule = Line([XL, 0, 0], [XR, 0, 0], stroke_width=1.5, color=MUTED).next_to(g, DOWN, buff=0.18)
    rule.set_x(0)
    return VGroup(g, rule)


class Shot(Scene):
    def at(self, t):
        """Wait until scene time t (seconds)."""
        now = self.renderer.time
        if t > now + 1 / 60:
            self.wait(t - now)

    def construct(self):
        k = SPEC.get("kind")
        getattr(self, "do_" + k)()
        self.at(SPEC["total"])

    # ---------------------------------------------------------------- 片头
    def do_title(self):
        s = SPEC
        brand = T("问渠 WenQuest" if LANG == "zh" else "WenQuest", 30, TEAL, BOLD).to_corner(UL, buff=0.5)
        course = T(s["course"], 34, MUTED)
        chap = T(s["chapter"], 30, MUTED)
        title = fit(T(s["title"], 64, WHITE, BOLD), 12.5)
        no = T(s["no"], 34, ACCENT, BOLD)
        g = VGroup(course, chap, no, title).arrange(DOWN, buff=0.32).move_to([0, 0.4, 0])
        line = Line([-4, 0, 0], [4, 0, 0], color=ACCENT, stroke_width=3).next_to(title, DOWN, buff=0.35)
        note = T(s.get("voice_note", ""), 20, MUTED).to_corner(DR, buff=0.4) if s.get("voice_note") else VMobject()
        self.play(FadeIn(brand), FadeIn(course, shift=DOWN * 0.2), FadeIn(chap, shift=DOWN * 0.2), run_time=0.8)
        self.play(FadeIn(no), Write(title), Create(line), FadeIn(note), run_time=1.6)

    # ---------------------------------------------------------------- 幻灯
    def make_item(self, it, width):
        if "tex" in it:
            return fit(MathTex(it["tex"], font_size=it.get("size", 42), color=WHITE), width, 2.4)
        if "text" in it:
            return rich(it["text"], it.get("size", 32), width)
        if "img" in it:
            im = ImageMobject(it["img"])
            im.scale_to_fit_width(it.get("width", 6.6))
            card = RoundedRectangle(corner_radius=0.12, width=im.width + 0.3, height=im.height + 0.3,
                                    fill_color=WHITE, fill_opacity=1, stroke_width=0)
            return Group(card, im.move_to(card))
        raise ValueError(f"unknown item {it}")

    def do_slide(self):
        s = SPEC
        hd = header(s.get("part"), s.get("head", ""))
        self.play(FadeIn(hd, shift=DOWN * 0.15), run_time=0.6)
        items = s["items"]
        has_img = any("img" in it for it in items)
        colw = 6.1 if has_img else 12.6
        mobs = [self.make_item(it, colw) for it in items]
        left = [m for it, m in zip(items, mobs) if "img" not in it]
        right = [m for it, m in zip(items, mobs) if "img" in it]
        top = hd.get_bottom()[1] - 0.45
        y = top
        for m in left:
            cx = 0 if (isinstance(m, MathTex) and not has_img) else XL + m.width / 2
            m.move_to([cx, y - m.height / 2, 0])
            y -= m.height + 0.42
        if y < BOTTOM:      # too tall: shrink the left column to fit
            g = Group(*left)
            g.scale((top - BOTTOM) / (top - y), about_point=[XL, top, 0])
        if right:
            rg = Group(*right).arrange(DOWN, buff=0.3)
            rg.scale_to_fit_width(6.9)
            fit(rg, 6.9, top - BOTTOM)
            rg.move_to([XR - rg.width / 2, top - rg.height / 2, 0])
        steps = s["steps"]
        for i, m in enumerate(mobs):
            if i < len(steps):
                self.at(steps[i])
            anim = Write(m) if isinstance(m, MathTex) else FadeIn(m, shift=UP * 0.12)
            self.play(anim, run_time=1.2 if isinstance(m, MathTex) else 0.5)

    # ---------------------------------------------------------------- 程序
    def do_code(self):
        s = SPEC
        hd = header(s.get("part"), s.get("head", ""))
        self.play(FadeIn(hd, shift=DOWN * 0.15), run_time=0.6)
        code = Code(code_string=s["source"], language="python", formatter_style="monokai", background="rectangle",
                    add_line_numbers=False, paragraph_config={"font": MONO, "font_size": 24})
        top = hd.get_bottom()[1] - 0.35
        fit(code, 12.8, 3.6)
        code.move_to([0, top - code.height / 2, 0])
        res_head = T("运行结果" if LANG == "zh" else "Output", 24, ACCENT, BOLD)
        res = VGroup(*[T(x, 24, INK, font=MONO) for x in s["result"]]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        rg = VGroup(res_head, res).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        box = SurroundingRectangle(rg, color=TEAL, buff=0.2, corner_radius=0.08, stroke_width=2)
        out = VGroup(box, rg)
        fit(out, 12.8, max(0.8, code.get_bottom()[1] - 0.25 - BOTTOM))
        out.next_to(code, DOWN, buff=0.25).set_x(XL + out.width / 2 + 0.05)
        steps = s["steps"]
        self.at(steps[0] if steps else 0.8)
        self.play(FadeIn(code, shift=UP * 0.1), run_time=0.7)
        if len(steps) > 1:
            self.at(steps[1])
        self.play(FadeIn(out, shift=UP * 0.1), run_time=0.6)

    # ---------------------------------------------------------------- 作业
    def do_homework(self):
        s = SPEC
        hd = header(s.get("part"), s.get("head", ""))
        self.play(FadeIn(hd, shift=DOWN * 0.15), run_time=0.6)
        rows = []
        for no, kind, text in s["items"]:
            tag = T(f"{no}", 26, ACCENT, BOLD)
            kd = T(kind, 22, BG, BOLD)
            chip = VGroup(RoundedRectangle(corner_radius=0.1, width=kd.width + 0.3, height=kd.height + 0.18, fill_color=TEAL,
                                           fill_opacity=1, stroke_width=0), kd)
            kd.move_to(chip[0])
            body = rich(text, 26, 10.2)
            head = VGroup(tag, chip).arrange(RIGHT, buff=0.2)
            row = VGroup(head, body).arrange(RIGHT, aligned_edge=UP, buff=0.3)
            rows.append(row)
        foot = T(s["foot"], 26, MUTED)
        top = hd.get_bottom()[1] - 0.4
        g = VGroup(*rows).arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        fit(g, 13.0, top - BOTTOM - 0.7)
        g.move_to([XL + g.width / 2, top - g.height / 2, 0])
        foot.next_to(g, DOWN, buff=0.35).set_x(XL + foot.width / 2)
        steps = s["steps"]
        for i, r in enumerate(rows):
            if i < len(steps):
                self.at(steps[i])
            self.play(FadeIn(r, shift=UP * 0.1), run_time=0.5)
        self.at(steps[-1] + 2.0 if steps else 1.0)
        self.play(FadeIn(foot), run_time=0.5)

    # ---------------------------------------------------------------- 结尾
    def do_outro(self):
        s = SPEC
        head = T(s["head"], 40, WHITE, BOLD).to_edge(UP, buff=0.6)
        self.play(FadeIn(head), run_time=0.6)
        pts = [rich(p, 32, 12.2) for p in s["points"]]
        nums = [T(f"{i + 1}", 32, ACCENT, BOLD) for i in range(len(pts))]
        rows = [VGroup(n, p).arrange(RIGHT, aligned_edge=UP, buff=0.35) for n, p in zip(nums, pts)]
        g = VGroup(*rows).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit(g, 12.4, 3.4)
        g.next_to(head, DOWN, buff=0.55).set_x(0)
        steps = s["steps"]
        for i, r in enumerate(rows):
            if i < len(steps):
                self.at(steps[i])
            self.play(FadeIn(r, shift=UP * 0.1), run_time=0.5)
        cta = VGroup(T(s["cta"], 34, TEAL, BOLD), T(s.get("cta2", ""), 26, MUTED)).arrange(DOWN, buff=0.15)
        cta.next_to(g, DOWN, buff=0.6)
        if cta.get_bottom()[1] < BOTTOM:
            cta.shift(UP * (BOTTOM - cta.get_bottom()[1]))
        self.at(s.get("cta_at", self.renderer.time + 0.5))
        box = SurroundingRectangle(cta, color=TEAL, buff=0.25, corner_radius=0.12)
        self.play(Create(box), FadeIn(cta), run_time=0.8)

    # ---------------------------------------------------------------- 封面（静帧）
    def do_cover(self):
        s = SPEC
        brand = T("问渠 WenQuest" if LANG == "zh" else "WenQuest", 34, TEAL, BOLD).to_corner(UL, buff=0.5)
        course = T(s["course"], 40, MUTED).next_to(brand, DOWN, aligned_edge=LEFT, buff=0.3)
        title = fit(T(s["title"], 80, WHITE, BOLD), 13)
        no = T(s["no"], 40, ACCENT, BOLD)
        g = VGroup(no, title).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to([0, -0.3, 0]).to_edge(LEFT, buff=0.7)
        f = MathTex(s.get("formula", ""), font_size=110, color=ACCENT) if s.get("formula") else VMobject()
        f.to_edge(DOWN, buff=0.8).to_edge(RIGHT, buff=0.8)
        self.add(brand, course, g, f)
