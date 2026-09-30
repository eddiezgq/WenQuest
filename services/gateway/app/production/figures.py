"""插图 (round 4, step 2): the illustrator's figures, rendered by programs so text, numbers and formulas are exact.

Four kinds, chosen by the lecturer per figure:
  scene   — schematic with formulas, frames, arms, vectors: Manim code in the house parts (same checker as the
            animations), rendered as a still by the animator service (POST /still)
  graph   — block diagram / flow / process / classification tree: the illustrator gives nodes and edges (JSON),
            we write the Graphviz file ourselves (no code from the model runs here)
  chart   — data plot: series given as numbers (JSON), drawn with matplotlib
  drawing — a drawing from the parts and robot library (the course's copy), converted to PNG

Every figure is a PNG (for the slides and the lecture notes) and, for graph/chart/drawing, also an SVG.
Text follows the course's language setting: zh, en, or both (Chinese line, English line).
"""
from __future__ import annotations

import base64
import io
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import httpx

FONT = "Noto Sans CJK SC"
INK, ACCENT, SOFT, LINE = "#1f2a33", "#2d6fb3", "#eaf2fa", "#8a9aa8"
COLORS = ["#2d6fb3", "#e8913a", "#2e9e6a", "#c0392b", "#7d5ba6", "#6b7b88"]
SHAPES = {"box": "box", "round": "box", "diamond": "diamond", "circle": "ellipse", "note": "note", "cylinder": "cylinder"}


class FigureError(Exception):
    pass


def text_of(pair, lang: str) -> str:
    """zh / en / both from a [zh, en] pair (or a plain string)."""
    if isinstance(pair, str):
        return pair
    zh, en = (list(pair) + ["", ""])[:2] if isinstance(pair, (list, tuple)) else (str(pair or ""), "")
    zh, en = str(zh or "").strip(), str(en or "").strip()
    if lang == "en":
        return en or zh
    if lang == "zh":
        return zh or en
    return zh if (not en or en == zh) else (f"{zh}\n{en}" if zh else en)


# --- graph (Graphviz) -------------------------------------------------------------------------------------------

def _q(s: str) -> str:
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def graph_dot(spec: dict, lang: str) -> str:
    rank = {"LR": "LR", "TB": "TB", "RL": "RL", "BT": "BT"}.get(str(spec.get("direction") or "LR").upper(), "LR")
    nodes = [n for n in spec.get("nodes") or [] if isinstance(n, dict) and n.get("id")][:40]
    ids = {str(n["id"]) for n in nodes}
    groups: dict[str, list[dict]] = {}
    for n in nodes:
        groups.setdefault(str(n.get("group") or ""), []).append(n)
    out = [f"digraph G {{ rankdir={rank}; bgcolor=\"white\"; pad=0.25; nodesep=0.45; ranksep=0.55;",
           f'node [fontname={_q(FONT)}, fontsize=13, color={_q(LINE)}, fontcolor={_q(INK)}, style="filled,rounded", '
           f'fillcolor={_q(SOFT)}, penwidth=1.3, margin="0.18,0.08"];',
           f'edge [fontname={_q(FONT)}, fontsize=11, color={_q(LINE)}, fontcolor="#51606c", penwidth=1.3, arrowsize=0.8];']
    for gi, (g, members) in enumerate(groups.items()):
        if g:
            out.append(f"subgraph cluster_{gi} {{ label={_q(text_of(members[0].get('group_label') or g, lang))}; "
                       f'fontname={_q(FONT)}; fontsize=12; color="#c7d3dd"; style="rounded,dashed";')
        for i, n in enumerate(members):
            shape = SHAPES.get(str(n.get("shape") or "round"), "box")
            fill = COLORS[int(n.get("color") or 0) % len(COLORS)] if n.get("emphasis") else SOFT
            font = "white" if n.get("emphasis") else INK
            style = '"filled,rounded"' if shape == "box" else '"filled"'
            out.append(f"{_q('n_' + str(n['id']))} [label={_q(text_of(n.get('label'), lang))}, shape={shape}, style={style}, "
                       f"fillcolor={_q(fill)}, fontcolor={_q(font)}];")
        if g:
            out.append("}")
    for e in (spec.get("edges") or [])[:80]:
        if not isinstance(e, dict) or str(e.get("from")) not in ids or str(e.get("to")) not in ids:
            continue
        lab = text_of(e.get("label"), lang) if e.get("label") else ""
        style = "dashed" if e.get("dashed") else "solid"
        out.append(f"{_q('n_' + str(e['from']))} -> {_q('n_' + str(e['to']))} [label={_q(lab)}, style={style}];")
    out.append("}")
    return "\n".join(out)


def render_graph(spec: dict, lang: str, dest: Path) -> dict:
    if not (spec.get("nodes") or []):
        raise FigureError("graph has no nodes")
    if not shutil.which("dot"):
        raise FigureError("Graphviz (dot) is not installed on the server")
    dot = graph_dot(spec, lang)
    svg = subprocess.run(["dot", "-Tsvg"], input=dot.encode(), capture_output=True, timeout=60)
    png = subprocess.run(["dot", "-Tpng", "-Gdpi=170"], input=dot.encode(), capture_output=True, timeout=60)
    if svg.returncode or png.returncode:
        raise FigureError((svg.stderr or png.stderr).decode(errors="replace")[:400])
    dest.with_suffix(".svg").write_bytes(svg.stdout)
    dest.with_suffix(".png").write_bytes(png.stdout)
    return {"png": dest.with_suffix(".png").name, "svg": dest.with_suffix(".svg").name}


_FONT_NAME = ""


def _cjk_font() -> str:
    """Register the Chinese font file with matplotlib (it does not find .ttc collections by family name)."""
    global _FONT_NAME
    if _FONT_NAME:
        return _FONT_NAME
    from matplotlib import font_manager
    name = "DejaVu Sans"
    try:
        path = subprocess.run(["fc-match", "-f", "%{file}", f"{FONT}:lang=zh-cn"], capture_output=True, text=True, timeout=10).stdout.strip()
        if path:
            font_manager.fontManager.addfont(path)
            name = font_manager.FontProperties(fname=path).get_name()
    except Exception:
        pass
    _FONT_NAME = name
    return name


# --- chart (matplotlib) -----------------------------------------------------------------------------------------

def render_chart(spec: dict, lang: str, dest: Path) -> dict:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.sans-serif": [_cjk_font(), "DejaVu Sans"], "axes.unicode_minus": False, "font.size": 11,
                         "svg.fonttype": "none"})
    series = [s for s in spec.get("series") or [] if isinstance(s, dict) and s.get("y")][:6]
    if not series:
        raise FigureError("chart has no data")
    kind = str(spec.get("type") or "line")
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=170)
    for i, s in enumerate(series):
        y = [float(v) for v in s["y"]][:2000]
        x = [float(v) for v in (s.get("x") or range(len(y)))][: len(y)] if kind != "bar" else list(range(len(y)))
        name = text_of(s.get("name"), lang) if s.get("name") else None
        c = COLORS[i % len(COLORS)]
        if kind == "bar":
            w = 0.8 / len(series)
            ax.bar([v + i * w - 0.4 + w / 2 for v in x], y, width=w, color=c, label=name)
        elif kind == "scatter":
            ax.scatter(x, y, s=18, color=c, label=name)
        else:
            ax.plot(x, y, color=c, lw=2, label=name)
    if kind == "bar" and spec.get("categories"):
        ax.set_xticks(range(len(spec["categories"])), [text_of(c, lang) for c in spec["categories"]])
    for ref in (spec.get("lines") or [])[:6]:     # limits, targets (e.g. tolerance lines)
        if isinstance(ref, dict) and ref.get("y") is not None:
            ax.axhline(float(ref["y"]), color="#c0392b", lw=1.2, ls="--")
            if ref.get("label"):
                ax.annotate(text_of(ref["label"], lang).replace("\n", " "), (1, float(ref["y"])), xycoords=("axes fraction", "data"),
                            ha="right", va="bottom", fontsize=9, color="#c0392b")
    ax.set_xlabel(text_of(spec.get("x_label") or "", lang).replace("\n", " / "))
    ax.set_ylabel(text_of(spec.get("y_label") or "", lang).replace("\n", " / "))
    ax.grid(True, color="#e3e8ec", lw=0.8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    if any(s.get("name") for s in series):
        ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(dest.with_suffix(".png"))
    fig.savefig(dest.with_suffix(".svg"))
    plt.close(fig)
    return {"png": dest.with_suffix(".png").name, "svg": dest.with_suffix(".svg").name}


# --- drawing (library SVG) --------------------------------------------------------------------------------------

def render_drawing(svg_path: Path, dest: Path) -> dict:
    if not svg_path.exists():
        raise FigureError("the library entry has no drawing")
    if not shutil.which("rsvg-convert"):
        raise FigureError("rsvg-convert is not installed on the server")
    shutil.copyfile(svg_path, dest.with_suffix(".svg"))
    r = subprocess.run(["rsvg-convert", "-z", "2.2", "-b", "white", "-o", str(dest.with_suffix(".png")), str(svg_path)],
                       capture_output=True, timeout=60)
    if r.returncode:
        raise FigureError(r.stderr.decode(errors="replace")[:300])
    return {"png": dest.with_suffix(".png").name, "svg": dest.with_suffix(".svg").name}


# --- scene (Manim still via the animator) -------------------------------------------------------------------------

async def render_scene(url: str, code: str, dest: Path, timeout: float = 240.0) -> dict:
    try:
        async with httpx.AsyncClient(timeout=timeout, trust_env=False) as c:
            r = await c.post(url.rstrip("/") + "/still", json={"code": code, "width": 1600, "height": 900})
    except httpx.HTTPError as e:
        raise FigureError(f"renderer unreachable: {type(e).__name__}") from e
    d = r.json() if r.status_code == 200 else {"ok": False, "error": f"renderer answered {r.status_code}"}
    if not d.get("ok"):
        raise FigureError(str(d.get("error") or "render failed")[:3000])
    dest.with_suffix(".png").write_bytes(base64.b64decode(d["png"]))
    return {"png": dest.with_suffix(".png").name}


def png_ok(path: Path) -> bool:
    """A real, non-blank picture."""
    try:
        from PIL import Image, ImageStat
        with Image.open(path) as im:
            im = im.convert("L").resize((200, 120))
            return ImageStat.Stat(im).stddev[0] > 4
    except Exception:
        return False
