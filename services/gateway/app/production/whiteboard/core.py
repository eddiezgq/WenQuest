"""问渠白板讲课（第 35 轮）的核心：一节课的讲稿 + 画板 → 播放数据（手绘动画）、网页、Excalidraw 画板文件。
网关（AI 生成、编辑器接口）和 tools/whiteboard/wb.py（本机出片）都用这一份。

lesson.json：
  title、audio（课目录里的录音文件）、segments（讲稿分段 [{t0, t1, zh}]，时间来自录音）、
  boards（画板 [{title: {zh, en}, elements: [...]}]）。每个元素的 at = 在第几段讲稿时画。
  元素：text {x, y, s, text, font: zh|en, c, align}；box {x, y（中心）, w, h, zh, en, c, s}；
        rect / ellipse {x, y（左上）, w, h, c, fill}；arrow / line {pts: [[x, y], …], c, w}；
        icon {name, x, y（中心）, size, c, w}（图标见 icons.py）；path {d, c, w}。
"""
import base64
import glob
import hashlib
import html as _html
import json
import math
import os
import subprocess
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
from .icons import ICONS  # noqa: E402

W, H = 1920, 1080
INK, MUTED = "#1d2329", "#5f6b76"
COLORS = {"ink": INK, "muted": MUTED, "gold": "#c98a00", "red": "#c2410c", "blue": "#1f6f9f", "green": "#2e7d4f"}


class Font:
    """霞鹜文楷（中文手写楷体）按字切片的 woff2 合成一张字表；英文先用 Caveat 手写体。"""

    def __init__(self, files):
        self.map = {}
        for f in files:
            ft = TTFont(f)
            for cp in ft.getBestCmap():
                self.map.setdefault(cp, ft)

    def glyphs(self, s, x, y, size, align="left"):
        out, fs = [], []
        for ch in s:
            f = self.map.get(ord(ch)) or self.map.get(ord("?"))
            fs.append(f)
        ks = [size / f["head"].unitsPerEm for f in fs]
        ws = [f["hmtx"][f.getBestCmap().get(ord(ch), ".notdef") if ord(ch) in f.getBestCmap() else ".notdef"][0] * k
              for ch, f, k in zip(s, fs, ks)]
        x0 = x - (sum(ws) / 2 if align == "center" else sum(ws) if align == "right" else 0)
        for ch, f, k, w in zip(s, fs, ks, ws):
            if not ch.isspace() and ord(ch) in f.getBestCmap():
                gs = f.getGlyphSet()
                pen = SVGPathPen(gs)
                gs[f.getBestCmap()[ord(ch)]].draw(TransformPen(pen, (k, 0, 0, -k, x0, y)))
                d = pen.getCommands()
                if d:
                    out.append(d)
            x0 += w
        return out, sum(ws)


WENKAI = sorted(glob.glob(str(HERE / "fonts" / "lxgwwenkai-bold-subset-*.woff2")))
_fonts = {}


def _font(kind):
    """Loaded on first use (about 100 font slices)."""
    if kind not in _fonts:
        greek = [str(HERE / "fonts" / "noto-sans-greek-500-italic.woff2")]   # τ θ ω π Δ … (not in the handwriting fonts)
        _fonts[kind] = (Font(WENKAI + greek) if kind == "zh"
                        else Font([str(HERE / "fonts" / "caveat-latin-700-normal.woff2")] + greek + WENKAI))
    return _fonts[kind]


class _Lazy:
    def __init__(self, kind):
        self.kind = kind

    def __getattr__(self, name):
        return getattr(_font(self.kind), name)


ZH, EN = _Lazy("zh"), _Lazy("en")


def missing_chars(text: str) -> str:
    """Characters no font can draw (they would be left out)."""
    m = _font("zh").map
    return "".join(sorted({ch for ch in text if not ch.isspace() and ord(ch) not in m}))


def color(c):
    return COLORS.get(c or "ink", c or INK)


def seed(*parts):
    return int(hashlib.md5(repr(parts).encode()).hexdigest()[:7], 16)


def expand(el):
    """box → rect + 中英文字；其余原样。"""
    if el["t"] != "box":
        return [el]
    c, s = el.get("c", "ink"), el.get("s", 40)
    x, y, w, h = el["x"], el["y"], el["w"], el["h"]
    out = [{"t": "rect", "x": x - w / 2, "y": y - h / 2, "w": w, "h": h, "c": c, "at": el["at"], "fill": el.get("fill"), "sw": el.get("sw", 3)}]
    if el.get("en"):
        out.append({"t": "text", "x": x, "y": y + s * 0.12, "s": s, "text": el["zh"], "font": "zh", "c": c, "align": "center", "at": el["at"]})
        out.append({"t": "text", "x": x, "y": y + s * 0.12 + s * 0.85, "s": max(22, s * 0.62), "text": el["en"], "font": "en", "c": "muted", "align": "center", "at": el["at"]})
    else:
        out.append({"t": "text", "x": x, "y": y + s * 0.36, "s": s, "text": el["zh"], "font": "zh", "c": c, "align": "center", "at": el["at"]})
    if el.get("id"):
        for o in out:
            o["id"] = el["id"]
    return out


def arrow_head(pts, size=22):
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    a = math.atan2(y2 - y1, x2 - x1)
    return [[[x2 + size * math.cos(a + s), y2 + size * math.sin(a + s)], [x2, y2]] for s in (2.6, -2.6)]


def compile_lesson(L, resolve_media=None):
    """resolve_media(src) → {kind: video | page, url | html, hash}: where a media frame's lab, animation or video comes from."""
    segs = L["segments"]
    items, ex = [], []
    moves, media = [], []
    boards = []
    for bi, b in enumerate(L["boards"]):
        ox, oy = bi * 2200, (bi % 2) * 260
        boards.append({"ox": ox, "oy": oy})
        els = []
        first = b.get("title_at", min(e["at"] for e in b["elements"]))
        if b.get("title"):
            els.append({"t": "text", "x": 110, "y": 112, "s": 60, "text": b["title"]["zh"], "font": "zh", "c": "ink", "at": first})
            if b["title"].get("en"):
                els.append({"t": "text", "x": 114, "y": 162, "s": 40, "text": b["title"]["en"], "font": "en", "c": "muted", "at": first})
        for e in b["elements"]:
            els.extend(expand(e))
        for n, e in enumerate(els):
            if e["t"] == "move":      # 画的东西活起来：rotate / shift / spin / flow / pulse 编号为 targets 的元素
                moves.append({"b": bi, "at": e["at"], "kind": e.get("kind", "rotate"), "targets": list(e.get("targets") or []),
                              **{k: e[k] for k in ("pivot", "to", "dx", "dy", "rpm", "speed", "dur", "delay", "until") if k in e}})
                continue
            if e["t"] == "media":     # 虚拟实验、动画、数字工厂视频：先画框，框里再播放
                src = (resolve_media or (lambda s_: None))(e.get("src", ""))
                if src:
                    media.append(dict(src, b=bi, x=e["x"], y=e["y"], w=e["w"], h=e["h"], item=len(items),
                                      **{k: e[k] for k in ("from", "play", "zoom") if k in e}))
                e = dict(e, t="rect", c=e.get("c", "muted"), sw=e.get("sw", 3.4))
            it = {"b": bi, "at": e["at"], **({"eid": str(e["id"])} if e.get("id") else {})}
            c = color(e.get("c"))
            w = e.get("sw") or (e.get("w", 3.2) if e["t"] in ("arrow", "line", "path") else 3.2)
            t = e["t"]
            if t == "text":
                f = ZH if e.get("font", "zh") == "zh" else EN
                gl, width = f.glyphs(e["text"], e["x"], e["y"], e.get("s", 40), e.get("align", "left"))
                it.update(k="path", paths=[{"d": d, "c": c, "w": 1.3, "f": 1} for d in gl], weight=max(0.35, 0.16 * len(gl)))
            elif t in ("rect", "ellipse"):
                it.update(k="rough", shape={"type": t, "x": e["x"], "y": e["y"], "w": e["w"], "h": e["h"]},
                          opts={"stroke": c, "strokeWidth": w, "seed": seed(bi, n),
                                **({"fill": color(e["fill"]), "fillStyle": "hachure", "hachureGap": 9, "fillWeight": 1.6} if e.get("fill") else {})},
                          weight=0.75 if not e.get("fill") else 1.3)
            elif t in ("arrow", "line"):
                pts = e["pts"]
                it.update(k="rough", shape={"type": "line", "pts": pts}, opts={"stroke": c, "strokeWidth": w, "seed": seed(bi, n), "roughness": 0.8},
                          weight=0.45)
                if t == "arrow":
                    items.append(it)
                    h = arrow_head(pts, e.get("head", 22))
                    it = {"b": bi, "at": e["at"], "k": "rough", "shape": {"type": "line", "pts": [h[0][0], pts[-1], h[1][0]]},
                          "opts": {"stroke": c, "strokeWidth": w, "seed": seed(bi, n, "h"), "roughness": 0.6}, "weight": 0.2,
                          **({"eid": str(e["id"])} if e.get("id") else {})}
            elif t == "icon":
                k = e.get("size", 200) / 200
                x0, y0 = e["x"] - 100 * k, e["y"] - 100 * k
                paths = [{"d": scale_path(d, k, x0, y0), "c": c, "w": e.get("w", 3.4)} for d in ICONS[e["name"]]]
                it.update(k="path", paths=paths, weight=0.35 + 0.22 * len(paths))
            elif t == "path":
                it.update(k="path", paths=[{"d": e["d"], "c": c, "w": w}], weight=0.5)
            else:
                raise SystemExit(f"unknown element type {t!r}")
            items.append(it)
            ex.append((bi, ox, oy, e))
    data = schedule(items, boards, L["segments"], L.get("duration", 0))
    add_moves_and_media(data, moves, media, segs)
    return data, ex


def add_moves_and_media(data, moves, media, segs):
    """Times for the moves (from their segment) and the media frames (once the frame is drawn)."""
    leave = {}
    for k in data["cam"]:                    # when the camera leaves each board
        for b, bd in enumerate(data["boards"]):
            if [bd["ox"], bd["oy"]] == k["a"] and b not in leave:
                leave[b] = k["t0"]
    out = []
    for m in moves:
        s = segs[min(m["at"], len(segs) - 1)]
        drawn = max([it["start"] + it["dur"] for it in data["items"] if it.get("eid") in m["targets"] and it["b"] == m["b"]] or [0])
        start = max(s["t0"] + 0.25 + m.pop("delay", 0), drawn + 0.3)   # a thing moves only once it is drawn
        dur = m.pop("dur", max(0.8, min(2.5, s["t1"] - s["t0"])))
        until = m.pop("until", None)
        end = segs[min(until, len(segs) - 1)]["t1"] if isinstance(until, int) else leave.get(m["b"], data["total"])
        out.append(dict(m, start=round(start, 3), dur=round(dur, 3), end=round(end, 3)))
    together = {}                            # moves of one segment that change a pose start together
    for m in out:
        if m["kind"] in ("rotate", "shift"):
            together[(m["b"], m["at"])] = max(together.get((m["b"], m["at"]), 0), m["start"])
    for m in out:
        if m["kind"] in ("rotate", "shift"):
            m["start"] = together[(m["b"], m["at"])]
    data["moves"] = out
    for md in media:
        it = data["items"][md.pop("item")]
        md["start"] = round(it["start"] + it["dur"] + 0.1, 3)
    data["media"] = media



def schedule(items, boards, segs, duration=0):
    """Give every stroke a start and a length from the words it belongs to (item["at"] = segment index)."""
    cam, starts = [], {}
    order = sorted(range(len(items)), key=lambda i: (items[i]["at"], i))
    by_seg = {}
    for i in order:
        by_seg.setdefault(items[i]["at"], []).append(i)
    board_first = {}
    for s in sorted(by_seg):
        for i in by_seg[s]:
            board_first.setdefault(items[i]["b"], s)
    # Each segment's strokes start with its words and may run on into the next second of the next segment; a board
    # change pans the camera after the previous board is finished.
    segs_with = sorted(by_seg)
    last_board, cursor = 0, 0.0
    for n_, s in enumerate(segs_with):
        idx = by_seg[s]
        b = items[idx[0]]["b"]
        t0 = segs[s]["t0"]
        if b != last_board:
            pan0 = max(cursor + 0.2, t0 - 0.3)
            a, z = boards[last_board], boards[b]
            cam.append({"t0": round(pan0, 3), "t1": round(pan0 + 0.8, 3), "a": [a["ox"], a["oy"]], "b": [z["ox"], z["oy"]]})
            cursor = pan0 + 0.9
            last_board = b
        start = max(t0 + 0.05, cursor)
        nxt = segs_with[n_ + 1] if n_ + 1 < len(segs_with) else None
        if nxt is None:
            deadline = segs[s]["t1"] + 1.5
        elif items[by_seg[nxt][0]]["b"] != b:
            deadline = segs[nxt]["t0"] - 0.4          # finish before the camera moves on
        else:
            deadline = segs[nxt]["t0"] + 1.2          # may spill a little into the next words
        natural = sum(items[i]["weight"] for i in idx)
        k = min(1.0, max(0.25, deadline - start) / natural) if natural else 1
        t = start
        for i in idx:
            d = items[i]["weight"] * k
            items[i]["start"], items[i]["dur"] = round(t, 3), round(max(0.12, d * 0.9), 3)
            t += d
        cursor = t
    for it in items:
        it.pop("weight", None)
    total = round(max(segs[-1]["t1"] + 2.0, duration or 0), 2)
    return {"W": W, "H": H, "boards": boards, "items": items, "cam": cam, "total": total,
            "captions": [{"t0": s["t0"], "t1": s["t1"], "zh": s["zh"]} for s in segs]}


def scale_path(d, k, x0, y0):
    """把 200×200 图标坐标里的路径换算到画板坐标（只处理绝对坐标的 M L C Q A Z）。"""
    import re
    toks = re.findall(r"[MLCQAZHV]|-?\d+(?:\.\d+)?", d)
    out, cmd, nums = [], None, []

    def flush():
        if cmd is None:
            return
        if cmd == "A":
            for j in range(0, len(nums), 7):
                rx, ry, rot, la, sw, x, y = nums[j:j + 7]
                out.append(f"A{rx * k:.1f},{ry * k:.1f} {rot:g} {int(la)} {int(sw)} {x * k + x0:.1f},{y * k + y0:.1f}")
        elif cmd == "H":
            out.append("H" + " ".join(f"{v * k + x0:.1f}" for v in nums))
        elif cmd == "V":
            out.append("V" + " ".join(f"{v * k + y0:.1f}" for v in nums))
        elif cmd == "Z":
            out.append("Z")
        else:
            out.append(cmd + " ".join(f"{nums[j] * k + x0:.1f},{nums[j + 1] * k + y0:.1f}" for j in range(0, len(nums), 2)))

    for tk in toks:
        if tk.isalpha():
            flush()
            cmd, nums = tk, []
        else:
            nums.append(float(tk))
    flush()
    return " ".join(out)


# ---------------- Excalidraw ----------------
def sample_path(d, step=6.0):
    """Points along an SVG path (absolute M L H V Q C A Z — what icons.py and the scaler write), one list per subpath."""
    import re as _re
    toks = _re.findall(r"[MLHVQCAZ]|-?\d+(?:\.\d+)?", d)
    out, cur, pos, start, i, cmd = [], [], (0.0, 0.0), (0.0, 0.0), 0, None

    def take(n):
        nonlocal i
        v = [float(t) for t in toks[i:i + n]]
        i += n
        return v

    def line_to(p):
        n = max(1, int(math.dist(pos, p) / step))
        cur.extend((pos[0] + (p[0] - pos[0]) * k / n, pos[1] + (p[1] - pos[1]) * k / n) for k in range(1, n + 1))

    def curve(f, length_guess):
        n = max(4, int(length_guess / step))
        cur.extend(f(k / n) for k in range(1, n + 1))

    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]
            i += 1
            if cmd == "Z":
                line_to(start)
                pos = start
                continue
        if cmd == "M":
            if len(cur) > 1:
                out.append(cur)
            pos = start = tuple(take(2))
            cur = [pos]
            cmd = "L"
        elif cmd == "L":
            p = tuple(take(2)); line_to(p); pos = p
        elif cmd == "H":
            p = (take(1)[0], pos[1]); line_to(p); pos = p
        elif cmd == "V":
            p = (pos[0], take(1)[0]); line_to(p); pos = p
        elif cmd == "Q":
            c1x, c1y, x, y = take(4); p0 = pos
            curve(lambda t: ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c1x + t * t * x, (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c1y + t * t * y),
                  math.dist(p0, (c1x, c1y)) + math.dist((c1x, c1y), (x, y)))
            pos = (x, y)
        elif cmd == "C":
            c1x, c1y, c2x, c2y, x, y = take(6); p0 = pos
            curve(lambda t: ((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * c1x + 3 * (1 - t) * t * t * c2x + t ** 3 * x,
                             (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * c1y + 3 * (1 - t) * t * t * c2y + t ** 3 * y),
                  math.dist(p0, (c1x, c1y)) + math.dist((c1x, c1y), (c2x, c2y)) + math.dist((c2x, c2y), (x, y)))
            pos = (x, y)
        elif cmd == "A":
            rx, ry, rot, large, sweep, x, y = take(7)
            pts = _arc(pos, rx, ry, rot, int(large), int(sweep), (x, y))
            curve(lambda t: pts[min(len(pts) - 1, int(t * (len(pts) - 1)))], (rx + ry) * 3)
            pos = (x, y)
        else:
            i += 1
    if len(cur) > 1:
        out.append(cur)
    return out


def _arc(p0, rx, ry, rot, large, sweep, p1, n=48):
    """SVG elliptical arc → points (the endpoint-to-centre conversion of the SVG spec)."""
    if rx == 0 or ry == 0 or p0 == p1:
        return [p0, p1]
    phi = math.radians(rot)
    cp, sp = math.cos(phi), math.sin(phi)
    dx, dy = (p0[0] - p1[0]) / 2, (p0[1] - p1[1]) / 2
    x1, y1 = cp * dx + sp * dy, -sp * dx + cp * dy
    lam = x1 * x1 / (rx * rx) + y1 * y1 / (ry * ry)
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1 * y1 - ry * ry * x1 * x1
    den = rx * rx * y1 * y1 + ry * ry * x1 * x1
    co = math.sqrt(max(0.0, num / den)) * (-1 if large == sweep else 1)
    cxp, cyp = co * rx * y1 / ry, -co * ry * x1 / rx
    cx = cp * cxp - sp * cyp + (p0[0] + p1[0]) / 2
    cy = sp * cxp + cp * cyp + (p0[1] + p1[1]) / 2
    a0 = math.atan2((y1 - cyp) / ry, (x1 - cxp) / rx)
    a1 = math.atan2((-y1 - cyp) / ry, (-x1 - cxp) / rx)
    da = a1 - a0
    if sweep and da < 0:
        da += 2 * math.pi
    elif not sweep and da > 0:
        da -= 2 * math.pi
    return [(cx + rx * math.cos(a0 + da * k / n) * cp - ry * math.sin(a0 + da * k / n) * sp,
             cy + rx * math.cos(a0 + da * k / n) * sp + ry * math.sin(a0 + da * k / n) * cp) for k in range(n + 1)]
def excalidraw(L, ex, prefix=""):
    """Expanded lesson elements (from compile_lesson) → an Excalidraw scene (frames = boards). Elements keep their
    id as customData.wq_id (moves find them by it); a media frame keeps its source as customData.wq_media."""
    els = []
    base = {"angle": 0, "backgroundColor": "transparent", "fillStyle": "hachure", "strokeWidth": 2, "strokeStyle": "solid",
            "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None, "roundness": None, "version": 1, "versionNonce": 1,
            "isDeleted": False, "boundElements": None, "updated": 1, "link": None, "locked": False}
    for bi, b in enumerate(L["boards"]):
        els.append(dict(base, id=f"{prefix}frame{bi}", type="frame", x=bi * 2200, y=(bi % 2) * 260, width=W, height=H, seed=seed("f", bi),
                        name=(b.get("title") or {}).get("zh", f"画板 {bi + 1}"), strokeColor="#bbb"))
    for n, (bi, ox, oy, e) in enumerate(ex):
        cd = {"wq_at": e["at"]}
        if e.get("id"):
            cd["wq_id"] = str(e["id"])
        if e.get("src"):
            cd["wq_media"] = {k: e[k] for k in ("src", "label", "from", "play", "zoom") if k in e}
        common = dict(base, id=f"{prefix}e{n}", seed=seed(prefix, "e", n), frameId=f"{prefix}frame{bi}", strokeColor=color(e.get("c")),
                      customData=cd)
        t = e["t"]
        if t == "text":
            s = e.get("s", 40)
            width = sum(s * (1.0 if ord(ch) > 0x2e80 else 0.55) for ch in e["text"])   # close to Excalidraw's own fonts
            align = e.get("align", "left")
            x = e["x"] - (width / 2 if align == "center" else width if align == "right" else 0)
            common["customData"] = dict(cd, wq_ax=e["x"], wq_x=x, wq_font=e.get("font", "zh"))
            els.append(dict(common, type="text", x=ox + x, y=oy + e["y"] - s, width=width, height=s * 1.25, text=e["text"],
                            originalText=e["text"], fontSize=s, fontFamily=5, textAlign=e.get("align", "left"),
                            verticalAlign="top", containerId=None, lineHeight=1.25, autoResize=True))
        elif t in ("rect", "ellipse"):
            els.append(dict(common, type="rectangle" if t == "rect" else "ellipse", x=ox + e["x"], y=oy + e["y"], width=e["w"], height=e["h"],
                            backgroundColor=color(e["fill"]) if e.get("fill") else "transparent"))
        elif t in ("arrow", "line"):
            p0 = e["pts"][0]
            pts = [[p[0] - p0[0], p[1] - p0[1]] for p in e["pts"]]
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            els.append(dict(common, type=t, x=ox + p0[0], y=oy + p0[1], width=max(xs) - min(xs), height=max(ys) - min(ys), points=pts,
                            lastCommittedPoint=None, startBinding=None, endBinding=None, startArrowhead=None,
                            endArrowhead="arrow" if t == "arrow" else None))
        elif t in ("icon", "path"):
            if t == "icon":
                k = e.get("size", 200) / 200
                ds = [scale_path(d, k, e["x"] - 100 * k, e["y"] - 100 * k) for d in ICONS[e["name"]]]
            else:
                ds = [e["d"]]
            gid = f"{prefix}g{n}"
            for m, d in enumerate(ds):
                for pts in sample_path(d):
                    x0, y0 = pts[0]
                    rel = [[p[0] - x0, p[1] - y0] for p in pts]
                    xs, ys = [p[0] for p in rel], [p[1] for p in rel]
                    els.append(dict(common, id=f"{prefix}e{n}_{m}_{len(els)}", type="freedraw", x=ox + x0, y=oy + y0, width=max(xs) - min(xs),
                                    height=max(ys) - min(ys), points=rel, pressures=[], simulatePressure=True, lastCommittedPoint=None,
                                    groupIds=[gid]))
    return {"type": "excalidraw", "version": 2, "source": "https://learn.wenquestrobotics.com", "elements": els,
            "appState": {"viewBackgroundColor": "#fdfcf8", "gridSize": None}, "files": {}}


# ---------------- from an Excalidraw scene (第 2 步：老师在编辑器里改过的画板) ----------------
def freedraw_d(pts, x, y):
    if not pts:
        return ""
    P = [(x + p[0], y + p[1]) for p in pts]
    if len(P) < 3:
        return "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in P)
    d = [f"M{P[0][0]:.1f},{P[0][1]:.1f}"]
    for i in range(1, len(P) - 1):
        mx, my = (P[i][0] + P[i + 1][0]) / 2, (P[i][1] + P[i + 1][1]) / 2
        d.append(f"Q{P[i][0]:.1f},{P[i][1]:.1f} {mx:.1f},{my:.1f}")
    d.append(f"L{P[-1][0]:.1f},{P[-1][1]:.1f}")
    return " ".join(d)


def compile_scene(scene, segs, duration=0, moves=None, resolve_media=None):
    """Excalidraw scene (frames = boards, customData.wq_at = segment index) → player data.
    moves: [{frame (frame id), at, kind, targets (wq_id), …}]; a rectangle with customData.wq_media is a media frame,
    resolve_media(src) says where its lab, animation or video comes from."""
    live = [e for e in scene["elements"] if not e.get("isDeleted")]
    frames = [e for e in live if e["type"] == "frame"]
    if not frames:
        frames = [{"id": "_all", "x": 0, "y": 0, "width": W, "height": H}]
    fidx = {f["id"]: i for i, f in enumerate(frames)}
    boards = [{"ox": f["x"], "oy": f["y"]} for f in frames]

    def board_of(e):
        if e.get("frameId") in fidx:
            return fidx[e["frameId"]]
        cx, cy = e["x"] + e.get("width", 0) / 2, e["y"] + e.get("height", 0) / 2
        return min(range(len(frames)), key=lambda i: (frames[i]["x"] + W / 2 - cx) ** 2 + (frames[i]["y"] + H / 2 - cy) ** 2)

    items, at, last_group = [], 0, None
    media = []
    nseg = len(segs)
    for e in live:
        if e["type"] == "frame":
            continue
        cd = e.get("customData") or {}
        if isinstance(cd.get("wq_at"), int):
            at = max(0, min(nseg - 1, cd["wq_at"]))
        bi = board_of(e)
        ox, oy = boards[bi]["ox"], boards[bi]["oy"]
        x, y = e["x"] - ox, e["y"] - oy
        c = e.get("strokeColor") or INK
        sw = max(1.6, (e.get("strokeWidth") or 2) * 1.6)
        opts = {"stroke": c, "strokeWidth": sw, "seed": e.get("seed", 1) % 2147483647,
                "roughness": max(0.4, min(2.2, (e.get("roughness", 1) or 0.5) * 1.1))}
        bg = e.get("backgroundColor")
        if bg and bg != "transparent":
            opts.update(fill=bg, fillStyle=e.get("fillStyle") or "hachure", hachureGap=9, fillWeight=1.6)
        t = e["type"]
        it = {"b": bi, "at": at, "eid": str(cd.get("wq_id") or e["id"])}
        if t == "rectangle" and isinstance(cd.get("wq_media"), dict):
            wm = cd["wq_media"]
            src = (resolve_media or (lambda s_: None))(str(wm.get("src", "")))
            if src:
                media.append(dict(src, b=bi, x=x, y=y, w=e["width"], h=e["height"], item=len(items),
                                  **{k: wm[k] for k in ("from", "play", "zoom") if k in wm}))
        if t in ("rectangle", "ellipse"):
            it.update(k="rough", shape={"type": "rect" if t == "rectangle" else "ellipse", "x": x, "y": y, "w": e["width"], "h": e["height"]},
                      opts=opts, weight=0.75 if "fill" not in opts else 1.3)
        elif t == "diamond":
            w_, h_ = e["width"], e["height"]
            it.update(k="rough", shape={"type": "line", "pts": [[x + w_ / 2, y], [x + w_, y + h_ / 2], [x + w_ / 2, y + h_], [x, y + h_ / 2], [x + w_ / 2, y]]},
                      opts=opts, weight=0.8)
        elif t in ("arrow", "line"):
            pts = [[x + p[0], y + p[1]] for p in e.get("points") or []]
            if len(pts) < 2:
                continue
            it.update(k="rough", shape={"type": "line", "pts": pts}, opts=dict(opts, roughness=min(opts["roughness"], 0.9)), weight=0.45)
            items.append(it)
            for end, tip, prev in (("endArrowhead", pts[-1], pts[-2]), ("startArrowhead", pts[0], pts[1])):
                if e.get(end):
                    h = arrow_head([prev, tip], 10 + sw * 3)
                    items.append({"b": bi, "at": at, "k": "rough", "shape": {"type": "line", "pts": [h[0][0], tip, h[1][0]]},
                                  "opts": dict(opts, roughness=0.6, seed=opts["seed"] + 1), "weight": 0.2, "eid": it["eid"]})
            continue
        elif t == "text":
            s_ = e.get("fontSize", 36)
            lh = s_ * (e.get("lineHeight") or 1.25)
            align = e.get("textAlign", "left")
            if isinstance(cd.get("wq_ax"), (int, float)) and isinstance(cd.get("wq_x"), (int, float)):
                ax = cd["wq_ax"] + (x - cd["wq_x"])     # our anchor, moved as far as the teacher moved the text
            else:
                ax = x + (e["width"] / 2 if align == "center" else e["width"] if align == "right" else 0)
            if cd.get("wq_font") in ("zh", "en"):
                f = ZH if cd["wq_font"] == "zh" else EN
            else:
                f = ZH if any(ord(ch) > 0x2e80 for ch in e.get("text", "")) else EN
            paths = []
            for li, line in enumerate((e.get("text") or "").split("\n")):
                gl, _ = f.glyphs(line, ax, y + li * lh + s_ * 0.92, s_, align)
                paths += [{"d": d, "c": c, "w": 1.3, "f": 1} for d in gl]
            if not paths:
                continue
            it.update(k="path", paths=paths, weight=max(0.35, 0.16 * len(paths)))
        elif t == "freedraw":
            d = freedraw_d(e.get("points") or [], x, y)
            if not d:
                continue
            g = (e.get("groupIds") or [None])[0]
            path = {"d": d, "c": c, "w": max(2.2, (e.get("strokeWidth") or 2) * 1.7)}
            if g and last_group == g and items and items[-1].get("group") == g and items[-1]["b"] == bi:
                items[-1]["paths"].append(path)
                items[-1]["weight"] += 0.22
                continue
            it.update(k="path", paths=[path], weight=0.57, group=g)
        else:
            continue   # images and embeds: later
        last_group = (e.get("groupIds") or [None])[0] if t == "freedraw" else None
        items.append(it)
    for it in items:
        it.pop("group", None)
    data = schedule(items, boards, segs, duration)
    mv = []
    for m in moves or []:
        if m.get("frame") in fidx:
            mv.append({**{k: v for k, v in m.items() if k != "frame"}, "b": fidx[m["frame"]],
                       "at": max(0, min(nseg - 1, int(m.get("at", 0))))})
    add_moves_and_media(data, mv, media, segs)
    return data




# ---------------- page ----------------
PEN = """<g id="pen" transform="translate(2300,1500)"><g transform="rotate(-38)">
<path d="M0,0 L-7,-20 L7,-20 Z" fill="#1d2329"/><rect x="-11" y="-46" width="22" height="26" rx="3" fill="#3a4550"/>
<rect x="-15" y="-250" width="30" height="206" rx="9" fill="#c98a00"/><rect x="-15" y="-250" width="9" height="206" rx="4" fill="#e3a91a"/>
<rect x="-16" y="-110" width="32" height="10" fill="#1d2329" opacity=".85"/><rect x="-13" y="-268" width="26" height="22" rx="7" fill="#1d2329"/></g>
<ellipse cx="8" cy="6" rx="30" ry="8" fill="#000" opacity=".06"/></g>"""


HAND_DIR = Path(os.environ.get("WQ_WB_HAND_DIR", str(HERE / "hand")))


def pen_svg(hand_dir=None):
    """The hand holding a marker (hand.webp + hand.json: where the tip is), drawn marker when there is no photo."""
    d = Path(hand_dir) if hand_dir else HAND_DIR
    img, meta = d / "hand.webp", d / "hand.json"
    if not (img.exists() and meta.exists()):
        return PEN
    m = json.loads(meta.read_text())
    k = m.get("scale", 1)
    b64 = base64.b64encode(img.read_bytes()).decode()
    return (f'<g id="pen" transform="translate(2300,1500)"><image href="data:image/webp;base64,{b64}" '
            f'x="{-m["tip_x"] * k:.1f}" y="{-m["tip_y"] * k:.1f}" width="{m["width"] * k:.1f}" height="{m["height"] * k:.1f}"/></g>')


def lesson_scene(L, prefix=""):
    """An AI-made lesson (boards of elements) → (Excalidraw scene, moves): the form the platform keeps and edits."""
    _, ex = compile_lesson(L)
    scene = excalidraw(L, ex, prefix)
    moves = []
    for bi, b in enumerate(L["boards"]):
        for e in b["elements"]:
            if e["t"] == "move":
                moves.append({"frame": f"{prefix}frame{bi}", "at": e["at"], "kind": e.get("kind", "rotate"),
                              "targets": [str(x) for x in e.get("targets") or []],
                              **{k: e[k] for k in ("pivot", "to", "dx", "dy", "rpm", "speed", "dur", "delay", "until") if k in e}})
    return scene, moves


def page(data, title, audio_b64=None, audio_type="audio/mp4", render=False, hand_dir=None, audio_url=None, seek_from=None):
    """The lesson as one web page. audio_url instead of audio_b64 links the narration; seek_from (render pages for the
    frame-by-frame recorder) adds window.SEEK(t) = draw the moment seek_from + t, and window.READY."""
    rough_js = (HERE / "rough.js").read_text()
    player = (HERE / "player.js").read_text()
    ui = "" if render else (HERE / "ui.html").read_text()
    # "</" inside the data (an embedded lab page has </script>) would end the script tag early
    data_js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    src = audio_url or (f"data:{audio_type};base64,{audio_b64}" if audio_b64 else "")
    audio = "" if render or not src else f'<audio id="aud" preload="auto" src="{_html.escape(src)}"></audio>'
    seek = "" if seek_from is None else (f"<script>window.SEEK=async function(t){{WB.seek({float(seek_from)}+t);await WB.settle();}};"
                                         "window.READY=true;</script>")
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_html.escape(str(title))}</title><style>
html,body{{margin:0;background:#fdfcf8;{'overflow:hidden' if render else ''}}}
#stage{{position:relative;width:100%;max-width:{'1920px' if render else '1280px'};margin:0 auto;aspect-ratio:16/9;background:#fdfcf8;overflow:hidden}}
#cv{{position:absolute;inset:0;width:100%;height:100%}}
</style></head><body>
<div id="stage"><svg id="cv" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet">
<defs><filter id="paper"><feTurbulence baseFrequency="0.9" numOctaves="2" seed="3"/><feColorMatrix values="0 0 0 0 0.96 0 0 0 0 0.95 0 0 0 0 0.92 0 0 0 0.07 0"/></filter></defs>
<rect width="{W}" height="{H}" fill="#fdfcf8"/><rect width="{W}" height="{H}" filter="url(#paper)"/>
<g id="worldwrap"></g>{pen_svg(hand_dir)}</svg></div>
{audio}{ui}
<script>{rough_js}</script><script>{player}</script>
<script>const DATA={data_js};
WB.init(document.getElementById('worldwrap'),DATA);if(window.UI)UI(DATA);</script>{seek}
</body></html>"""
