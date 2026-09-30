"""Lesson animations (A2): send a Manim scene to the renderer (services/animator) and keep the video.

The AI animator writes the scene; when its code keeps failing, `storyboard_code` builds a plain
animation from the storyboard (captions, question, concept points and the formula card) so every
lesson still has a video.
"""
from __future__ import annotations

import base64
from pathlib import Path

import httpx


class RenderError(Exception):
    def __init__(self, message: str, stage: str = "render"):
        super().__init__(message)
        self.stage = stage


async def render(url: str, code: str, timeout: float = 600.0) -> tuple:
    """(video, poster, seconds, key frames) or RenderError with the renderer's message (fed back to the animator)."""
    try:
        async with httpx.AsyncClient(timeout=timeout, trust_env=False) as c:
            r = await c.post(url.rstrip("/") + "/render", json={"code": code})
    except httpx.HTTPError as e:
        raise RenderError(f"renderer unreachable: {type(e).__name__}", "service") from e
    if r.status_code != 200:
        raise RenderError(f"renderer answered {r.status_code}", "service")
    d = r.json()
    if not d.get("ok"):
        raise RenderError(str(d.get("error") or "render failed")[:4000], str(d.get("stage") or "render"))
    return (base64.b64decode(d["video"]), base64.b64decode(d.get("poster") or ""), float(d.get("seconds") or 0),
            [base64.b64decode(f) for f in d.get("frames") or []])


def _s(x: str) -> str:
    return repr(str(x or ""))


def _wrap(t, width: int, lines: int) -> list[str]:
    """Up to `lines` lines of about `width` characters (words kept whole for English)."""
    t = " ".join(str(t or "").split())
    if not t:
        return []
    words = sum(ch.isascii() for ch in t) > 0.8 * len(t)
    out, cur = [], ""
    for w in (t.split(" ") if words else list(t)):
        sep = " " if (cur and words) else ""
        if len(cur) + len(sep) + len(w) > width and cur:
            out.append(cur)
            cur = w
        else:
            cur += sep + w
    out.append(cur)
    if len(out) > lines:
        out = out[:lines]
        out[-1] = out[-1][: width - 1] + "…"
    return out


def storyboard_code(spec: dict, no: str) -> str:
    """A safe, always-renderable scene from the lesson spec: the storyboard beats as captions over the
    lesson's own problem, the question, the concept points and a closing card. It draws no robot (a stock robot
    could belong to another subject); only this lesson's words and formulas appear."""
    a, c, p = spec["animation"], spec["concept"], spec["problem"]
    beats = a["beats"] or [a["question"]]
    lines = [
        "from wq_anim import *", "", "", "class Lesson(Base):", "    def construct(self):",
        f"        self.title({_s(no)}, {_s(a['title'][0] or spec['title'][0])}, {_s(a['title'][1] or spec['title'][1])})",
        f"        q = VGroup(zh({_s(p['title'][0])}, 32, YELLOW), en({_s(p['title'][1])}, 22)).arrange(DOWN, buff=0.12)",
        "        fit(q, 12).move_to([0, 1.5, 0])",
        "        self.play(Write(q))",
        "        body = VGroup(" + ", ".join([f"zh({_s(t)}, 24, GREY_B)" for t in _wrap(p['text'][0], 30, 2)]
                                    + [f"en({_s(t)}, 20)" for t in _wrap(p['text'][1], 70, 2)]) + ").arrange(DOWN, buff=0.1)",
        "        fit(body, 12).next_to(q, DOWN, buff=0.4)",
        "        self.play(FadeIn(body, shift=UP * 0.1))",
    ]
    for zh_b, en_b in beats[:8]:
        lines.append(f"        self.caption({_s(zh_b)}, {_s(en_b)}, wait=2.2)")
    lines += [
        "        self.clear_stage()",
        f"        ask = VGroup(zh({_s(a['question'][0])}, 32, YELLOW), en({_s(a['question'][1])}, 22)).arrange(DOWN, buff=0.1)",
        "        self.play(Write(fit(ask, 12).move_to(UP * 1.2)))",
        "        pts = VGroup(" + ", ".join(f"bi([{_s(z)}, {_s(e)}], 24)" for z, e in c["points"][:4]) + ").arrange(DOWN, buff=0.22, aligned_edge=LEFT)",
        "        fit(pts, 12).next_to(ask, DOWN, buff=0.45)",
        "        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in pts], lag_ratio=0.4), run_time=2.5)",
        "        self.wait(2.0)",
        "        self.card([" + ", ".join(
            [f"[{_s(c['title'][0])}, {_s(c['title'][1])}]"]
            + ([f"[{_s(c['formula'][0])}, {_s(c['formula'][1] if c['formula'][1] != c['formula'][0] else '')}]"] if c["formula"][0] else [])
            + [f"[{_s(z)}, {_s(e)}]" for z, e in (spec.get("summary") or [])[:2]]) + "])",
    ]
    return "\n".join(lines) + "\n"


def save(folder: Path, name: str, video: bytes, poster: bytes) -> tuple[Path, Path | None]:
    folder.mkdir(parents=True, exist_ok=True)
    v = folder / f"{name}.mp4"
    v.write_bytes(video)
    pp = None
    if poster:
        from io import BytesIO

        from PIL import Image
        try:  # only a real image becomes the slide's first frame
            Image.open(BytesIO(poster)).verify()
            pp = folder / f"{name}.png"
            pp.write_bytes(poster)
        except Exception:
            pp = None
    return v, pp
