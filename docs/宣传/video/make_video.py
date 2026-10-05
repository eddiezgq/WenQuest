"""Assemble the WenQuest promo video (docs/宣传/2026-10_推介幻灯片与演示视频.md, section 二).

Inputs (all in the work dir, made by the other scripts here):
  tts/sNN_MM.wav + tts/durations.json      tts.py          (narration, Kokoro 云夏, local)
  lab_*.mp4, site.mp4                      record.py       (labs and the official site, recorded frame by frame)
  anim/aX_Y_Z.mp4                          render_anims.sh (Manim, 1080p)
  st_*.png, pr_*.png, zh41.png, en41d.png  capture_pages.py and the platform captures (see README.md)
  docs/lab12_1-*.png                       the lab guide / report template (Word → PDF → PNG)
Output: <work>/问渠演示视频.mp4, .srt, and a contact sheet.

Every frame is drawn here in Python (Pillow) and piped to ffmpeg: stills get a slow pan/zoom, recordings play,
shots cross-fade, segment labels sit lower left, subtitles are burned in bottom centre, timed from the TTS clips.
Usage: python3 make_video.py <work dir> [--preview N]   (--preview: every Nth frame only, for a quick look)
"""
from __future__ import annotations

import json
import math
import os
import re
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
W = sys.argv[1]
PREVIEW = int(sys.argv[sys.argv.index("--preview") + 1]) if "--preview" in sys.argv else 0
SCR = os.path.dirname(W.rstrip("/"))                 # the scratchpad (older platform screenshots)
SHOTS_DIR = f"{REPO}/docs/截图"
FACT = f"{REPO}/factory/digital/docs/截图"
OUT = f"{W}/问渠演示视频.mp4"

FPS = 30
WIDTH, HEIGHT = 1920, 1080
FD = 0.6                 # cross-fade between shots (s)
GAP = 0.7                # pause after each sentence (s)
RATE = 24000             # Kokoro sample rate

# ---------- look ----------
NAVY, NAVY2, INK = (10, 26, 51), (19, 49, 92), (8, 16, 30)
AMBER, PALE, WHITE = (242, 183, 5), (160, 184, 217), (255, 255, 255)
FONT_DIR = "/usr/share/fonts/opentype/noto"


def font(size, weight="Regular"):
    return ImageFont.truetype(f"{FONT_DIR}/NotoSansCJK-{weight}.ttc", size, index=2)   # index 2 = Noto Sans CJK SC


def ease(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def backdrop():
    """Dark-blue diagonal gradient with a faint dot grid — the background of every card."""
    y, x = np.mgrid[0:HEIGHT, 0:WIDTH].astype(np.float32)
    u = np.clip((x / WIDTH * 0.6 + y / HEIGHT * 0.4), 0, 1)[..., None]
    img = (np.array(NAVY, np.float32) * (1 - u) + np.array(NAVY2, np.float32) * u)
    dots = ((x % 48 < 2) & (y % 48 < 2))[..., None]
    img = np.where(dots, img + 14, img)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


BACK = backdrop()


# ---------- shots ----------
class Shot:
    label = None

    def frame(self, t: float, dur: float) -> Image.Image:
        raise NotImplementedError

    def close(self):
        pass


def load(path):
    return Image.open(path).convert("RGB")


class Still(Shot):
    """Ken Burns over a (possibly tall) screenshot: the view rectangle moves from a to b.
    A rectangle is (cx, cy, w) in source pixels; its height is w·9/16. Rectangles are clamped to the image."""

    def __init__(self, path, a, b, label=None, img=None):
        self.img = img if img is not None else load(path)
        self.a, self.b, self.label = a, b, label
        sw = max(a[2], b[2])
        self.k = min(1.0, 1.12 * WIDTH / sw)          # pre-shrink so the widest view is ≤ 1.12× output (no aliasing)
        if self.k < 1.0:
            self.img = self.img.resize((round(self.img.width * self.k), round(self.img.height * self.k)), Image.LANCZOS)

    def rect(self, r):
        cx, cy, w = (v * self.k for v in r)
        w = min(w, self.img.width, self.img.height * 16 / 9)
        h = w * 9 / 16
        cx = min(max(cx, w / 2), self.img.width - w / 2)
        cy = min(max(cy, h / 2), self.img.height - h / 2)
        return cx, cy, w

    def frame(self, t, dur):
        u = ease(t / max(dur, 0.01))
        (ax, ay, aw), (bx, by, bw) = self.rect(self.a), self.rect(self.b)
        cx, cy, w = ax + (bx - ax) * u, ay + (by - ay) * u, aw + (bw - aw) * u
        s = w / WIDTH
        x0, y0 = cx - w / 2, cy - w * 9 / 16 / 2
        return self.img.transform((WIDTH, HEIGHT), Image.AFFINE, (s, 0, x0, 0, s, y0), resample=Image.BILINEAR)


def compose(parts, bg=None, shadow=True, radius=18):
    """parts: [(image, (x, y))] pasted on the dark backdrop with a soft shadow and rounded corners."""
    canvas = (bg or BACK).copy().convert("RGBA")
    for im, (x, y) in parts:
        im = im.convert("RGBA")
        mask = Image.new("L", im.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius, fill=255)
        if shadow:
            sh = Image.new("RGBA", (im.width + 80, im.height + 80), (0, 0, 0, 0))
            ImageDraw.Draw(sh).rounded_rectangle([40, 52, im.width + 40, im.height + 52], radius, fill=(0, 0, 0, 120))
            sh = sh.filter(ImageFilter.GaussianBlur(18))
            canvas.alpha_composite(sh, (x - 40, y - 40))
        canvas.paste(im, (x, y), mask)
    return canvas.convert("RGB")


def Panel(path, box, label=None, zoom=1.05, maxw=1700, maxh=860, maxs=2.0):
    """A crop of a screenshot shown as a card on the backdrop (used where the rest of the page is not for show)."""
    im = load(path).crop(box)
    s = min(maxw / im.width, maxh / im.height, maxs)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    img = compose([(im, ((WIDTH - im.width) // 2, (HEIGHT - im.height) // 2 - 30))])
    return Still(None, (960, 540, 1920), (960, 515, 1920 / zoom), label, img=img)


def Pages(paths, titles, label=None):
    """Document pages side by side (the lab guide and report template)."""
    ims = []
    for p in paths:
        im = load(p)
        s = 820 / im.height
        ims.append(im.resize((round(im.width * s), 820), Image.LANCZOS))
    gap = 90
    tw = sum(i.width for i in ims) + gap * (len(ims) - 1)
    x, parts = (WIDTH - tw) // 2, []
    for im in ims:
        parts.append((im, (x, 150)))
        x += im.width + gap
    img = compose(parts)
    d = ImageDraw.Draw(img)
    for (im, (x, y)), title in zip(parts, titles):
        f = font(34, "Medium")
        d.text((x + im.width / 2, y - 52), title, font=f, fill=WHITE, anchor="mm")
    return Still(None, (960, 540, 1920), (960, 520, 1800), label, img=img)


def Grid(paths, names, label=None):
    """Last frames of six recorded labs, 3 × 2."""
    tw, th, gx, gy = 560, 315, 40, 80
    x0 = (WIDTH - (3 * tw + 2 * gx)) // 2
    y0 = 120
    parts = []
    for i, p in enumerate(paths):
        im = load(p).resize((tw, th), Image.LANCZOS)
        parts.append((im, (x0 + (i % 3) * (tw + gx), y0 + (i // 3) * (th + gy))))
    img = compose(parts, radius=12)
    d = ImageDraw.Draw(img)
    f = font(28, "Medium")
    for (im, (x, y)), n in zip(parts, names):
        d.text((x + tw / 2, y + th + 30), n, font=f, fill=PALE, anchor="mm")
    return Still(None, (960, 540, 1920), (960, 520, 1780), label, img=img)


class Video(Shot):
    """A recording. mode: 'full' (fills the frame), 'anim' (a Manim clip shown at 84 % on its own dark background so its
    built-in bilingual captions stay clear of our subtitles), 'embed' (inside a screenshot, at a given box)."""

    def __init__(self, path, start=0.0, mode="full", label=None, bg=None, box=None, zoom=None):
        self.path, self.start, self.mode, self.label = path, start, mode, label
        self.proc, self.n, self.last = None, -1, None
        if mode == "anim":
            self.size = (round(WIDTH * 0.84) // 2 * 2, round(HEIGHT * 0.84) // 2 * 2)
            self.pos = ((WIDTH - self.size[0]) // 2, 22)
            self.bg = Image.new("RGB", (WIDTH, HEIGHT), (15, 17, 21))
        elif mode == "embed":
            self.bg = load(bg)
            x, y, w, h = box
            self.size, self.pos = (round(w) // 2 * 2, round(h) // 2 * 2), (round(x), round(y))
        else:
            self.size, self.pos, self.bg = (WIDTH, HEIGHT), (0, 0), None
        self.zoom = zoom

    def _open(self):
        w, h = self.size
        self.proc = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{self.start:.3f}", "-i", self.path,
                                      "-vf", f"fps={FPS},scale={w}:{h}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                     stdout=subprocess.PIPE)

    def frame(self, t, dur):
        if self.proc is None:
            self._open()
        want = int(round(t * FPS))
        w, h = self.size
        while self.n < want:
            buf = self.proc.stdout.read(w * h * 3)
            if len(buf) < w * h * 3:
                break                                   # clip ended: hold its last frame
            self.last = Image.frombuffer("RGB", (w, h), buf)
            self.n += 1
        im = self.last if self.last is not None else Image.new("RGB", (w, h))
        if self.bg is not None:
            out = self.bg.copy()
            out.paste(im, self.pos)
            im = out
        if self.zoom:
            z = 1 + (self.zoom - 1) * ease(t / max(dur, 0.01))
            s = 1 / z
            im = im.transform((WIDTH, HEIGHT), Image.AFFINE, (s, 0, WIDTH * (1 - s) / 2, 0, s, HEIGHT * (1 - s) / 2),
                              resample=Image.BICUBIC)
        return im

    def close(self):
        if self.proc:
            self.proc.kill()
            self.proc = None


class Phone(Shot):
    """The phone edition: the mobile page scrolling inside a phone outline over the dimmed desktop page."""

    def __init__(self, path, bg, scroll, label=None):
        self.label = label
        sw, sh = 430, 932
        im = load(path)
        self.page = im.resize((sw, round(im.height * sw / im.width)), Image.LANCZOS)
        self.sw, self.sh, self.scroll = sw, sh, scroll
        b = load(bg).filter(ImageFilter.GaussianBlur(6))
        b = Image.blend(b, Image.new("RGB", b.size, INK), 0.62)
        self.x, self.y = (WIDTH - sw) // 2, (HEIGHT - sh) // 2 - 20
        frame = b.convert("RGBA")
        sh_ = Image.new("RGBA", (sw + 160, sh + 160), (0, 0, 0, 0))
        ImageDraw.Draw(sh_).rounded_rectangle([60, 70, sw + 100, sh + 110], 70, fill=(0, 0, 0, 150))
        frame.alpha_composite(sh_.filter(ImageFilter.GaussianBlur(20)), (self.x - 80, self.y - 80))
        ImageDraw.Draw(frame).rounded_rectangle([self.x - 18, self.y - 18, self.x + sw + 18, self.y + sh + 18], 62,
                                                fill=(22, 24, 30), outline=(90, 98, 112), width=3)
        self.base = frame.convert("RGB")
        self.mask = Image.new("L", (sw, sh), 0)
        ImageDraw.Draw(self.mask).rounded_rectangle([0, 0, sw - 1, sh - 1], 46, fill=255)

    def frame(self, t, dur):
        y = int(self.scroll * ease(t / max(dur, 0.01)))
        y = min(y, self.page.height - self.sh)
        out = self.base.copy()
        out.paste(self.page.crop((0, y, self.sw, y + self.sh)), (self.x, self.y), self.mask)
        return out


# ---------- title cards ----------
class Card(Shot):
    """Elements fade in one after another (and rise a little); the whole card zooms in very slowly."""

    def __init__(self, items, zoom=1.035, label=None):
        self.items, self.zoom, self.label = items, zoom, label     # items: [(appear_s, RGBA layer or callable(t))]

    def frame(self, t, dur):
        done = all(t - at >= 0.6 and not callable(L) for at, L in self.items) or \
            all(t - at >= 1.6 for at, L in self.items)
        if done and getattr(self, "_still", None) is not None:
            im = self._still
        else:
            im = BACK.copy().convert("RGBA")
            for at, layer in self.items:
                a = ease((t - at) / 0.6)
                if a <= 0:
                    continue
                L = layer(t - at) if callable(layer) else layer
                box = L.getbbox()
                if not box:
                    continue
                L = L.crop(box)
                if a < 1:
                    L.putalpha(L.getchannel("A").point(lambda v, a=a: int(v * a)))
                im.alpha_composite(L, (box[0], box[1] + int(round(18 * (1 - a)))))
            im = im.convert("RGB")
            if done:
                self._still = im
        z = 1 + (self.zoom - 1) * (t / max(dur, 0.01))
        s = 1 / z
        return im.transform((WIDTH, HEIGHT), Image.AFFINE, (s, 0, WIDTH * (1 - s) / 2, 0, s, HEIGHT * (1 - s) / 2),
                            resample=Image.BILINEAR)


def layer():
    return Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))


def text_layer(xy, s, size, weight="Regular", fill=WHITE, anchor="mm"):
    L = layer()
    ImageDraw.Draw(L).text(xy, s, font=font(size, weight), fill=fill, anchor=anchor)
    return L


def bar_layer(box, fill=AMBER):
    L = layer()
    ImageDraw.Draw(L).rounded_rectangle(box, 3, fill=fill)
    return L


def card_open():
    L = layer()
    d = ImageDraw.Draw(L)
    f1, f2 = font(150, "Bold"), font(92, "Light")
    w1 = d.textlength("问渠", font=f1)
    w2 = d.textlength("  WenQuest", font=f2)
    x = (WIDTH - w1 - w2) / 2
    d.text((x, 470), "问渠", font=f1, fill=WHITE, anchor="ls")
    d.text((x + w1, 470), "  WenQuest", font=f2, fill=PALE, anchor="ls")
    return Card([(0.2, L), (0.9, bar_layer((900, 520, 1020, 526))),
                 (1.1, text_layer((960, 610), "AI 原生的智慧教学平台", 70, "Medium")),
                 (1.8, text_layer((960, 720), "教材 · 课程 · 动画 · 虚拟实验 · 课程管理", 36, "Regular", PALE))])


def chips_layer(words, y, hi=()):
    """Rounded chips in a row, each its own layer so they can appear one by one."""
    f = font(46, "Medium")
    d0 = ImageDraw.Draw(layer())
    ws = [d0.textlength(w, font=f) + 80 for w in words]
    gap = 30
    x = (WIDTH - sum(ws) - gap * (len(ws) - 1)) / 2
    out = []
    for w, word in zip(ws, words):
        L = layer()
        d = ImageDraw.Draw(L)
        amber = word in hi
        d.rounded_rectangle([x, y - 50, x + w, y + 50], 50, fill=(242, 183, 5, 255) if amber else (255, 255, 255, 28),
                            outline=None if amber else (160, 184, 217, 160), width=2)
        d.text((x + w / 2, y), word, font=f, fill=INK if amber else WHITE, anchor="mm")
        out.append(L)
        chips_layer.last_cx = x + w / 2
        x += w + gap
    return out


def card_course():
    chips = chips_layer(["内容", "课件", "视频", "作业", "测验", "考试", "实验"], 560, hi=("实验",))
    items = [(0.2, text_layer((960, 330), "一门完整的课", 92, "Bold")), (0.5, bar_layer((900, 400, 1020, 406)))]
    times = [2.6, 3.2, 3.8, 4.35, 4.9, 5.5, 7.6]          # follows “内容、课件、视频、作业、测验和考试，理工科还要有实验”
    items += [(t, c) for t, c in zip(times, chips)]
    items += [(7.4, text_layer((chips_layer.last_cx, 640), "理工科", 28, "Regular", AMBER))]
    return Card(items)


def card_rows(title, rows, sub=None):
    items = [(0.2, text_layer((960, 250), title, 80, "Bold")), (0.5, bar_layer((900, 312, 1020, 318)))]
    y = 440
    for i, (k, v) in enumerate(rows):
        L = layer()
        d = ImageDraw.Draw(L)
        d.ellipse([430, y - 34, 498, y + 34], fill=AMBER)
        d.text((464, y), str(i + 1), font=font(38, "Bold"), fill=INK, anchor="mm")
        d.text((540, y - 4), k, font=font(48, "Medium"), fill=WHITE, anchor="lm")
        if v:
            d.text((540, y + 46), v, font=font(30), fill=PALE, anchor="lm")
        items.append((1.0 + 1.3 * i, L))
        y += 150
    if sub:
        items.append((1.0 + 1.3 * len(rows), text_layer((960, 930), sub, 30, "Regular", PALE)))
    return Card(items)


NUMBERS = [  # section 三 of the doc (2026-10-04)
    (8, "", "本教材", "规划 410 章"),
    (447, "", "节已写成", "48 章"),
    (160, "", "段 Manim 动画", "中英字幕"),
    (149, "", "个浏览器实验", "不用安装软件"),
    (390, "", "份指导书与报告模板", "Word"),
    (667, "", "个算例程序", "书中数字由程序算出"),
    (5000, "+", "条中英术语", "统一术语表"),
    (13, "", "章英文版", "《机器人学》"),
]


def fmt(n):
    return f"{n:,}"


def card_numbers():
    items = [(0.2, text_layer((960, 170), "已经做出来的", 70, "Bold")), (0.4, bar_layer((900, 222, 1020, 228)))]
    cw, ch = 400, 300
    x0, y0 = (WIDTH - 4 * cw) // 2, 300
    for i, (n, plus, unit, note) in enumerate(NUMBERS):
        cx, cy = x0 + (i % 4) * cw + cw // 2, y0 + (i // 4) * ch

        def draw(t, n=n, plus=plus, unit=unit, note=note, cx=cx, cy=cy):
            v = round(n * ease(t / 1.4))
            L = layer()
            d = ImageDraw.Draw(L)
            d.text((cx, cy + 70), fmt(v) + plus, font=font(96, "Bold"), fill=AMBER, anchor="ms")
            d.text((cx, cy + 128), unit, font=font(36, "Medium"), fill=WHITE, anchor="ms")
            d.text((cx, cy + 176), note, font=font(26), fill=PALE, anchor="ms")
            return L
        items.append((0.6 + 0.18 * i, draw))
    return Card(items, zoom=1.02)


def card_close():
    items = [(0.2, text_layer((960, 330), "一起建一门示范课", 100, "Bold")),
             (0.5, bar_layer((900, 400, 1020, 406))),
             (0.9, text_layer((960, 480), "确定试点学院和 3–5 门课 · 签协议 · 一个月内开课", 38, "Regular", PALE)),
             (1.6, text_layer((960, 640), "8 本教材 · 447 节 · 160 段动画 · 149 个浏览器实验 · 390 份指导书与报告模板 · 667 个算例程序",
                              30, "Regular", WHITE)),
             (2.2, text_layer((960, 820), "问渠 WenQuest", 56, "Bold")),
             (2.4, text_layer((960, 900), "wenquestrobotics.com", 44, "Medium", AMBER))]
    return Card(items, zoom=1.025)


# ---------- the storyboard ----------
P = W
LAB_NAMES = ["UR5e 正运动学", "Go2 四足", "梯度下降", "电桥测力", "PLC 压装工位", "GPU 线程束"]


def end_frame(name):
    """Last frame of a recorded lab, as a still (for the grid)."""
    out = f"{W}/end_{name}.png"
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(f"{W}/{name}.mp4"):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.2", "-i", f"{W}/{name}.mp4", "-frames:v", "1", out], check=True)
    return out


def storyboard():
    """Per segment: lead (s), tail (s), min slot per sentence (s), shots [(sentence index, offset s, shot factory)].
    A shot starts at its sentence's start + offset (the first shot of a segment at the segment start)."""
    return [
        dict(id=1, label=None, lead=3.0, tail=2.0, mins=[4.4, 5.4, 6.4], shots=[
            (0, -9, card_open),
            (1, 0, lambda: Video(f"{P}/site.mp4", 0.5, label="官网 · wenquestrobotics.com"))]),
        dict(id=2, lead=1.4, tail=1.6, mins=[8.6, 3.4, 4.0, 3.6, 6.2], shots=[
            (0, -9, card_course),
            (2, 0, lambda: Still(f"{P}/pr_courses.png", (960, 540, 1920), (1360, 330, 1150), "学习平台 · 仪表盘")),
            (3, 0, lambda: Still(f"{P}/pr_studio2.png", (620, 560, 1500), (1300, 420, 1250), "AI 建课 · 了解要求"))]),
        dict(id=3, lead=1.2, tail=1.4, mins=[2.2, 6.2, 6.4, 6.6, 10.6, 6.0, 5.6], shots=[
            (0, -9, lambda: Still(f"{P}/st_book_toc.png", (960, 540, 1920), (760, 470, 1450), "教材 · 机器人学")),
            (2, 0, lambda: Still(f"{P}/st_book_121.png", (620, 760, 1150), (620, 1420, 1150), "教材 · 每章三道审核")),
            (3, 0, lambda: Still(f"{P}/st_book_41.png", (1190, 560, 1340), (1190, 1900, 1340), "教材 · 4.1 节")),
            (4, 0, lambda: Still(f"{P}/st_book_121.png", (1190, 430, 1340), (1190, 2760, 1340), "教材 · 12.1 节")),
            (5, 0, lambda: Phone(f"{P}/st_phone_121.png", f"{P}/zh41.png", 1500, "教材 · 手机阅读")),
            (6, 0, lambda: Still(f"{P}/zh41.png", (960, 540, 1920), (960, 520, 1840), "教材 · 中文")),
            (6, 1.7, lambda: Still(f"{P}/en41d.png", (960, 520, 1840), (1000, 470, 1660), "教材 · English"))]),
        dict(id=4, lead=1.2, tail=1.4, mins=[3.2, 6.2, 10.8, 10.4, 10.4, 7.4], shots=[
            (0, -9, lambda: Video(f"{P}/anim/a12_2_1.mp4", 3.5, "anim", "动画 · 12.2 指数积公式")),
            (2, 0, lambda: Video(f"{P}/anim/a4_2_1.mp4", 1.6, "anim", "动画 · 4.2 转动的次序")),
            (3, 0, lambda: Video(f"{P}/anim/a6_1_1.mp4", 12.6, "anim", "动画 · 6.1 螺旋运动")),
            (4, 0, lambda: Video(f"{P}/anim/a7_2_1.mp4", 7.6, "anim", "动画 · 7.2 欧拉法误差")),
            (5, 0, lambda: Video(f"{P}/anim/a4_2_1.mp4", 6.0, "embed", "动画 · 在书页里播放", bg=f"{P}/st_book_42.png",
                                 box=(646.7, 199.8, 1093.3, 615.0)))]),
        dict(id=5, lead=1.2, tail=1.4, mins=[2.2, 7.4, 13.2, 9.0, 9.4, 8.6, 10.6], shots=[
            (0, -9, lambda: Video(f"{P}/lab_ur5e.mp4", 0.0, label="虚拟实验 · UR5e（12.1）")),
            (3, 0, lambda: Video(f"{P}/lab_go2.mp4", 0.0, label="虚拟实验 · Go2 四足（1.6）")),
            (4, 0, lambda: Video(f"{P}/lab_gd.mp4", 0.0, label="虚拟实验 · 梯度下降（8.1）")),
            (5, 0, lambda: Video(f"{P}/lab_circuit.mp4", 0.0, label="虚拟实验 · 电桥测力（39.2）")),
            (6, 0, lambda: Grid([end_frame(n) for n in ("lab_ur5e", "lab_go2", "lab_gd", "lab_circuit", "lab_plc", "lab_gpu")],
                                LAB_NAMES, "虚拟实验")),
            (6, 4.6, lambda: Pages([f"{P}/docs/lab12_1-guide-1.png", f"{P}/docs/lab12_1-report-1.png"],
                                   ["实验指导书", "实验报告模板"], "实验 12.1 · Word 文档"))]),
        dict(id=6, lead=1.2, tail=1.4, mins=[4.6, 8.4, 8.4, 8.2], shots=[
            (0, -9, lambda: Video(f"{P}/lab_linalg.mp4", 0.0, label="线性代数 · 演示台")),
            (1, 0, lambda: Video(f"{P}/lab_plc.mp4", 0.0, label="PLC · 压装工位（15.3）")),
            (2, 0, lambda: Video(f"{P}/lab_micro.mp4", 0.0, label="微电子 · CMOS 反相器")),
            (3, 0, lambda: Video(f"{P}/lab_gpu.mp4", 0.0, label="人工智能 · GPU 执行模拟器"))]),
        dict(id=7, lead=1.2, tail=1.4, mins=[2.0, 6.0, 7.6, 9.4, 9.0, 6.0], shots=[
            (0, -9, lambda: Panel(f"{SHOTS_DIR}/1-资料自动分类.png", (196, 62, 1084, 472), "AI 建课 · 上传资料")),
            (2, 0, lambda: Still(f"{SHOTS_DIR}/1-资料自动分类.png", (640, 900, 1060), (640, 1500, 1060), "AI 建课 · 自动分类")),
            (3, 0, lambda: Panel(f"{P}/pr_studio1.png", (130, 90, 1462, 372), "AI 教授团队")),
            (3, 4.4, lambda: Still(f"{SHOTS_DIR}/2-按资料生成大纲.png", (640, 400, 1100), (640, 640, 1100), "AI 建课 · 课程大纲")),
            (4, 0, lambda: Still(f"{SHOTS_DIR}/5-双语课件1.png", (1334, 750, 2668), (700, 400, 1400), "AI 生成 · 中英双语课件")),
            (4, 4.6, lambda: Still(f"{SHOTS_DIR}/6-双语课件2.png", (1334, 750, 2400), (1900, 1080, 1400), "AI 生成 · 中英双语课件")),
            (5, 0, lambda: Still(f"{SHOTS_DIR}/2-按资料生成大纲.png", (640, 3078, 1100), (840, 3157, 1000), "AI 建课 · 老师确认"))]),
        dict(id=8, lead=1.2, tail=1.4, mins=[4.6, 6.4, 5.4, 3.6], shots=[
            (0, -9, lambda: Panel(f"{SCR}/rev_committee.png", (460, 192, 1362, 506), "课程委员会 · AI 预审")),
            (2, 0, lambda: Panel(f"{SCR}/rev_committee.png", (460, 586, 1362, 950), "课程委员会 · 批准或退回"))]),
        dict(id=9, lead=1.2, tail=1.4, mins=[11.6, 4.2, 13.4], shots=[
            (0, -9, lambda: Still(f"{P}/pr_course.png", (960, 520, 1840), (700, 420, 1300), "学习平台 · 课程页")),
            (1, 0, lambda: Still(f"{FACT}/1-首页看板.png", (720, 405, 1440), (720, 520, 1150), "数字工厂 · 总览")),
            (2, 0, lambda: Still(f"{FACT}/2-订单与计划.png", (720, 500, 1440), (760, 420, 1200), "数字工厂 · 订单与计划")),
            (2, 2.6, lambda: Still(f"{FACT}/3-设计与工艺.png", (720, 405, 1440), (640, 470, 1150), "数字工厂 · 设计与工艺")),
            (2, 5.2, lambda: Still(f"{FACT}/4-车间终端.png", (720, 500, 1440), (760, 440, 1200), "数字工厂 · 车间终端")),
            (2, 7.6, lambda: Still(f"{FACT}/6-3D车间.png", (720, 500, 1440), (900, 480, 1100), "数字工厂 · 3D 车间")),
            (2, 10.4, lambda: Still(f"{FACT}/5-经营与成本.png", (720, 405, 1440), (720, 460, 1200), "数字工厂 · 经营与成本"))]),
        dict(id=10, lead=1.2, tail=7.4, mins=[4.4, 6.6, 8.2, 4.6], shots=[
            (0, -9, lambda: card_rows("合规与部署", [
                ("国内只调用已备案的大模型", "如 DeepSeek；Claude 只用于美国"),
                ("语音、动画、实验检查在本地运行", "开源模型部署在学校或平台自己的服务器上"),
                ("数据留在学校", "校内私有 · 云服务 · 混合，三种部署方式")])),
            (2, 0, card_numbers),
            (3, 0, card_close)]),
    ]


# ---------- narration, timeline, subtitles ----------
N = json.load(open(f"{HERE}/narration.json", encoding="utf-8"))
DUR = json.load(open(f"{W}/tts/durations.json", encoding="utf-8"))


def timeline():
    segs = storyboard()
    t = 0.0
    sentences, shots = [], []
    for seg, nseg in zip(segs, N["segments"]):
        assert seg["id"] == nseg["id"]
        seg_start = t
        t += seg["lead"]
        starts = []
        for j, s in enumerate(nseg["sentences"]):
            key = f"s{seg['id']:02d}_{j:02d}"
            d = DUR[key]["seconds"]
            assert DUR[key]["say"] == s.get("say", s["text"]), key
            slot = max(d + GAP, seg["mins"][j])
            starts.append(t)
            sentences.append(dict(key=key, text=s["text"], start=t, dur=d))
            t += slot
        t += seg["tail"]
        for j, off, make in seg["shots"]:
            st = seg_start if off == -9 else starts[j] + off
            shots.append([st, make])
        seg["start"], seg["end"] = seg_start, t
    total = t
    return segs, sentences, shots, total


def chunks(text, maxc=22):
    """Split a sentence into subtitle lines, wording unchanged: at ，；：。 first, at 、 only when a piece is still too
    long (nearest the middle); a line's trailing punctuation is dropped."""
    def split_long(p):
        if vlen(p) <= maxc:
            return [p]
        cuts = [m.end() for m in re.finditer("、", p[:-1])]
        if not cuts:
            return [p]
        c = min(cuts, key=lambda i: abs(vlen(p[:i]) - vlen(p) / 2))
        return split_long(p[:c]) + split_long(p[c:])
    parts = [q for p in re.findall(r"[^，：；。]+[，：；。]?", text) for q in split_long(p)]
    lines, cur = [], ""
    for p in parts:
        if cur and vlen(cur + p) > maxc:
            lines.append(cur)
            cur = p
        else:
            cur += p
    if cur:
        lines.append(cur)
    return [re.sub(r"[，、：；。]$", "", x) for x in lines]


def vlen(s):
    return sum(0.55 if ord(c) < 128 else 1 for c in s)


def subtitles(sentences):
    subs = []
    for s in sentences:
        ls = chunks(s["text"])
        tot = sum(vlen(x) for x in ls)
        t = s["start"]
        for x in ls:
            d = s["dur"] * vlen(x) / tot
            subs.append(dict(start=t, end=t + d + (0.25 if x == ls[-1] else 0.0), text=x))
            t += d
    return subs


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


SUB_FONT = font(46, "Medium")


def sub_image(text):
    """White text with a dark outline on a soft translucent band (readable over busy pages)."""
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    tw = int(d0.textlength(text, font=SUB_FONT))
    w, h = tw + 64, 76
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 14, fill=(8, 14, 26, 150))
    d.text((w / 2, h / 2 + 1), text, font=SUB_FONT, fill=WHITE, anchor="mm", stroke_width=4, stroke_fill=(8, 14, 26, 255))
    return im


LABEL_FONT = font(26, "Medium")


def label_image(text):
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    w = int(d0.textlength(text, font=LABEL_FONT)) + 44
    im = Image.new("RGBA", (w, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, 47], 8, fill=(10, 26, 51, 210))
    d.rectangle([0, 8, 5, 39], fill=AMBER)
    d.text((24, 24), text, font=LABEL_FONT, fill=WHITE, anchor="lm")
    return im


# ---------- audio ----------
def read_wav(p):
    with wave.open(p) as w:
        return np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float32) / 32768


def music(total):
    """A quiet synthesized pad (four slow chords, soft attack, detuned sines through a gentle low-pass)."""
    n = int(total * RATE)
    t = np.arange(n) / RATE
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)  # noqa: E731
    chords = [[48, 55, 59, 62, 64], [45, 52, 55, 59, 60], [41, 48, 52, 55, 57], [43, 50, 52, 57, 59]]   # Cmaj9 Am9 Fmaj9 G6/9
    L = 8.0
    out = np.zeros(n, np.float32)
    k = 0
    while k * L < total + L:
        t0 = k * L - 1.5
        i0, i1 = max(0, int(t0 * RATE)), min(n, int((t0 + L + 3.0) * RATE))
        if i0 < i1:
            tt = t[i0:i1] - t0
            env = np.minimum(1, tt / 2.8) * np.minimum(1, np.maximum(0, (L + 3.0 - tt) / 3.0))
            sig = np.zeros_like(tt)
            for m in chords[k % 4]:
                f = hz(m)
                sig += np.sin(2 * np.pi * f * tt) + 0.6 * np.sin(2 * np.pi * (f * 1.003) * tt + 1.3) + 0.15 * np.sin(4 * np.pi * f * tt)
            out[i0:i1] += (sig * env).astype(np.float32)
        k += 1
    trem = 1 + 0.08 * np.sin(2 * np.pi * 0.11 * t)
    out *= trem.astype(np.float32)
    from scipy.signal import lfilter
    a = np.exp(-2 * np.pi * 900 / RATE)                 # one-pole low-pass
    y = lfilter([1 - a], [1, -a], out).astype(np.float32)
    y /= np.max(np.abs(y)) + 1e-9
    fade = np.minimum(1, t / 3.0) * np.minimum(1, np.maximum(0, (total - t) / 4.0))
    return (y * fade).astype(np.float32)


def build_audio(sentences, total):
    n = int((total + 0.5) * RATE)
    voice = np.zeros(n, np.float32)
    active = np.zeros(n, np.float32)
    for s in sentences:
        x = read_wav(f"{W}/tts/{s['key']}.wav")
        i = int(round(s["start"] * RATE))
        voice[i:i + len(x)] += x[: n - i]
        active[i:i + len(x)] = 1
    v_rms = np.sqrt(np.mean(voice[active > 0] ** 2))
    voice *= 0.1 / v_rms                                 # speech at about −20 dBFS RMS
    m = music(total + 0.5)[:n]
    k = int(0.4 * RATE)                                  # smooth ducking envelope
    duck = np.convolve(active, np.ones(k) / k, mode="same")
    m_gain = 10 ** (-21 / 20) * (1 - 0.45 * np.clip(duck * 1.5, 0, 1))
    mix = voice + m * m_gain / (np.sqrt(np.mean(m ** 2)) + 1e-9) * 0.1
    raw = f"{W}/mix.wav"
    with wave.open(raw, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes((np.clip(mix, -1, 1) * 32767).astype("<i2").tobytes())
    # two-pass loudness normalisation to −16 LUFS, true peak −1.5 dB
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", raw, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    js = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    af = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}:"
          f"measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true,aresample=48000")
    out = f"{W}/mix_norm.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", af, "-ar", "48000", "-ac", "2", out], check=True)
    return out


# ---------- render ----------
def main():
    segs, sentences, shots, total = timeline()
    subs = subtitles(sentences)
    print(f"total {total:.1f} s, {len(shots)} shots, {len(sentences)} sentences, {len(subs)} subtitle lines", flush=True)
    for seg in segs:
        print(f"  segment {seg['id']:2d}: {seg['start']:6.1f} – {seg['end']:6.1f}  ({seg['end'] - seg['start']:.1f} s)")
    with open(OUT.replace(".mp4", ".srt"), "w", encoding="utf-8") as f:
        for i, s in enumerate(subs, 1):
            f.write(f"{i}\n{srt_time(s['start'])} --> {srt_time(s['end'])}\n{s['text']}\n\n")
    json.dump(dict(total=total, segments=[{k: v for k, v in s.items() if k in ("id", "start", "end")} for s in segs],
                   sentences=sentences), open(f"{W}/timeline.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    audio = None if PREVIEW else build_audio(sentences, total)
    sub_imgs = [sub_image(s["text"]) for s in subs]
    label_cache = {}

    nframes = int(round(total * FPS))
    starts = [s[0] for s in shots]
    live = {}                                   # shot index -> Shot object (created lazily, closed when done)

    def get(k):
        if k not in live:
            live[k] = shots[k][1]()
        return live[k]

    vf_out = OUT if not PREVIEW else f"{W}/preview.mp4"
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}",
           "-r", str(FPS if not PREVIEW else FPS / PREVIEW), "-i", "-"]
    if audio:
        cmd += ["-i", audio, "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            "-shortest" if audio else "-an", vf_out]
    enc = subprocess.Popen([c for c in cmd if c], stdin=subprocess.PIPE)
    step = PREVIEW or 1
    for f in range(0, nframes, step):
        t = f / FPS
        k = max(i for i, s in enumerate(starts) if s <= t + 1e-9)
        end_k = starts[k + 1] if k + 1 < len(starts) else total
        cur = get(k)
        img = cur.frame(t - starts[k], end_k - starts[k] + FD)
        a_lab = 1.0
        if k > 0 and t - starts[k] < FD:
            prev = get(k - 1)
            a = ease((t - starts[k]) / FD)
            pimg = prev.frame(t - starts[k - 1], starts[k] - starts[k - 1] + FD)
            img = Image.blend(pimg, img, a)
            same = prev.label == cur.label
            a_lab = 1.0 if same else a
        for i in list(live):                     # close shots that are finished
            if i < k - 1:
                live.pop(i).close()
        img = img.convert("RGBA")
        lab = cur.label
        if lab:
            if lab not in label_cache:
                label_cache[lab] = label_image(lab)
            L = label_cache[lab]
            a = a_lab
            if a < 1:
                L = L.copy()
                L.putalpha(L.getchannel("A").point(lambda v, a=a: int(v * a)))
            img.alpha_composite(L, (40, HEIGHT - 48 - 40))
        for s, im in zip(subs, sub_imgs):
            if s["start"] - 0.1 <= t <= s["end"] + 0.1:
                a = min(1.0, (t - s["start"] + 0.1) / 0.15, (s["end"] + 0.1 - t) / 0.15)
                if a < 1:
                    im = im.copy()
                    im.putalpha(im.getchannel("A").point(lambda v, a=a: int(v * a)))
                img.alpha_composite(im, ((WIDTH - im.width) // 2, HEIGHT - 116))
        img = img.convert("RGB")
        fin = min(1.0, t / 0.8, (total - t) / 1.5)          # fade in from / out to black
        if fin < 1:
            img = Image.blend(Image.new("RGB", img.size), img, max(0.0, fin))
        enc.stdin.write(img.tobytes())
        if f % (FPS * 10) < step:
            print(f"  {t:6.1f} / {total:.1f} s", flush=True)
    enc.stdin.close()
    enc.wait()
    for s in live.values():
        s.close()
    print("wrote", vf_out)


if __name__ == "__main__":
    main()
