"""科普短片（MinutePhysics 式）样片共用的简笔画：果蝇、火柴人、神经元网、文字、对话框等。画板坐标 1920×1080。"""
import math
import numpy as np

# ---------------------------------------------------------------- drawing helpers (board coordinates 1920×1080)
def fly(cx, cy, k, at, idp="fly", legs_id=None):
    """A cartoon fly facing left: red eyes, two wings, six legs."""
    E = []
    E.append({"t": "ellipse", "at": at, "id": idp, "x": cx - 40 * k, "y": cy - 32 * k, "w": 80 * k, "h": 64 * k, "c": "ink"})        # thorax
    E.append({"t": "ellipse", "at": at, "id": idp, "x": cx + 30 * k, "y": cy - 30 * k, "w": 120 * k, "h": 62 * k, "c": "ink", "fill": "gold"})  # abdomen
    E.append({"t": "ellipse", "at": at, "id": idp, "x": cx - 82 * k, "y": cy - 26 * k, "w": 50 * k, "h": 48 * k, "c": "ink"})       # head
    E.append({"t": "ellipse", "at": at, "id": idp, "x": cx - 86 * k, "y": cy - 24 * k, "w": 24 * k, "h": 28 * k, "c": "red", "fill": "red"})  # eye
    for side in (-1, 1):                                                                                                       # wings
        E.append({"t": "path", "at": at, "id": idp + "_wings", "c": "blue", "w": 3,
                  "d": f"M{cx},{cy - 26 * k} Q{cx + 40 * k},{cy - (150 if side < 0 else 120) * k} {cx + (150 if side < 0 else 120) * k},{cy - (110 if side < 0 else 70) * k} "
                       f"Q{cx + 70 * k},{cy - 30 * k} {cx},{cy - 26 * k}"})
    for i, dx in enumerate((-30, 0, 30)):                                                                                      # legs
        x0 = cx + dx * k
        pts = [[x0, cy + 26 * k], [x0 + (-40 + 30 * i) * k, cy + 70 * k], [x0 + (-60 + 40 * i) * k, cy + 110 * k]]
        E.append({"t": "line", "at": at, "id": (legs_id if (legs_id and i == 0) else idp), "pts": pts, "c": "ink", "w": 3})
    return E

def stick(cx, cy, k, at, idp=None, arms="down"):
    """A stick person standing at (cx, cy) = feet level."""
    h = 200 * k
    E = [{"t": "ellipse", "at": at, "x": cx - 26 * k, "y": cy - h - 52 * k, "w": 52 * k, "h": 52 * k, "c": "ink"},
         {"t": "line", "at": at, "pts": [[cx, cy - h], [cx, cy - 80 * k]], "c": "ink", "w": 3.4},
         {"t": "line", "at": at, "pts": [[cx, cy - 80 * k], [cx - 40 * k, cy]], "c": "ink", "w": 3.4},
         {"t": "line", "at": at, "pts": [[cx, cy - 80 * k], [cx + 40 * k, cy]], "c": "ink", "w": 3.4}]
    if arms == "up":
        E.append({"t": "line", "at": at, "pts": [[cx - 60 * k, cy - h - 40 * k], [cx, cy - h + 30 * k], [cx + 60 * k, cy - h - 40 * k]], "c": "ink", "w": 3.4})
    else:
        E.append({"t": "line", "at": at, "pts": [[cx - 55 * k, cy - h + 90 * k], [cx, cy - h + 30 * k], [cx + 55 * k, cy - h + 90 * k]], "c": "ink", "w": 3.4})
    if idp:
        for e in E:
            e["id"] = idp
    return E

def network(cx, cy, r, at, n=13, seed=3, idp="net", c="ink"):
    """A tangle of neurons: dots joined by wires (the wires can carry a flow)."""
    rng = np.random.default_rng(seed)
    pts = []
    for i in range(n):
        a, d = rng.uniform(0, 2 * math.pi), r * math.sqrt(rng.uniform(0.05, 1))
        pts.append((cx + d * math.cos(a), cy + 0.7 * d * math.sin(a)))
    E = []
    for i, (x, y) in enumerate(pts):
        near = sorted(range(n), key=lambda j: (pts[j][0] - x) ** 2 + (pts[j][1] - y) ** 2)[1:4]
        for j in near:
            if j > i or i not in [k for k in sorted(range(n), key=lambda q: (pts[q][0] - pts[j][0]) ** 2 + (pts[q][1] - pts[j][1]) ** 2)[1:4]]:
                E.append({"t": "line", "at": at, "id": idp + "_w", "pts": [[x, y], list(pts[j])], "c": "blue", "w": 2.4})
    for x, y in pts:
        E.append({"t": "ellipse", "at": at, "id": idp, "x": x - 11, "y": y - 11, "w": 22, "h": 22, "c": c, "fill": "gold"})
    return E

def txt(x, y, s, text, at, c="ink", align="center", font="zh", **kw):
    return {"t": "text", "at": at, "x": x, "y": y, "s": s, "text": text, "c": c, "align": align, "font": font, **kw}

def bubble(x, y, w, h, at, text, s=44, c="ink"):
    return [{"t": "path", "at": at, "c": c, "w": 3,
             "d": f"M{x + 30},{y} L{x + w - 30},{y} Q{x + w},{y} {x + w},{y + 30} L{x + w},{y + h - 30} Q{x + w},{y + h} {x + w - 30},{y + h} "
                  f"L{x + 90},{y + h} L{x + 40},{y + h + 50} L{x + 55},{y + h} L{x + 30},{y + h} Q{x},{y + h} {x},{y + h - 30} L{x},{y + 30} Q{x},{y} {x + 30},{y}"},
            txt(x + w / 2, y + h / 2 + s * 0.36, s, text, at, c=c)]



def cute_fly(cx, cy, k, at, idp="fly", moves=True, mood="happy"):
    """A cute fly seen from the front: round head, big eyes with pupils, a smile, blush, curly antennae, two wings and
    six little legs. Ids: <idp>_body, <idp>_wl / <idp>_wr (wings), <idp>_legs; target "<idp>*" moves the whole fly.
    moves=True adds buzzing wings and a little hover."""
    def P(d, c="ink", w=3.2, part="_body"):
        return {"t": "path", "at": at, "id": idp + part, "c": c, "w": w, "d": d}
    E = []
    # wings first (behind the body)
    for side, part in ((-1, "_wl"), (1, "_wr")):
        x0, y0 = cx + side * 40 * k, cy - 5 * k
        E.append(P(f"M{x0},{y0} Q{x0 + side * 150 * k},{y0 - 170 * k} {x0 + side * 190 * k},{y0 - 40 * k} Q{x0 + side * 140 * k},{y0 + 40 * k} {x0},{y0}",
                   c="blue", w=3, part=part))
        E.append(P(f"M{x0 + side * 20 * k},{y0 - 10 * k} Q{x0 + side * 100 * k},{y0 - 90 * k} {x0 + side * 150 * k},{y0 - 45 * k}", c="blue", w=2, part=part))
    E.append({"t": "ellipse", "at": at, "id": idp + "_body", "x": cx - 62 * k, "y": cy - 10 * k, "w": 124 * k, "h": 150 * k, "c": "ink", "fill": "gold"})
    for i in range(3):   # stripes
        y = cy + (40 + 30 * i) * k
        E.append(P(f"M{cx - 52 * k + 8 * i * k},{y} Q{cx},{y + 14 * k} {cx + 52 * k - 8 * i * k},{y}", w=3))
    E.append({"t": "ellipse", "at": at, "id": idp + "_body", "x": cx - 70 * k, "y": cy - 130 * k, "w": 140 * k, "h": 130 * k, "c": "ink"})   # head
    for side in (-1, 1):
        ex = cx + side * 34 * k
        E.append({"t": "ellipse", "at": at, "id": idp + "_body", "x": ex - 30 * k, "y": cy - 118 * k, "w": 60 * k, "h": 70 * k, "c": "red", "fill": "red"})
        E.append({"t": "ellipse", "at": at, "id": idp + "_body", "x": ex - 10 * k + side * 4 * k, "y": cy - 100 * k, "w": 20 * k, "h": 24 * k,
                  "c": "ink", "fill": "ink"})
        E.append(P(f"M{cx + side * 22 * k},{cy - 128 * k} Q{cx + side * 30 * k},{cy - 200 * k} {cx + side * 70 * k},{cy - 196 * k} "
                   f"Q{cx + side * 90 * k},{cy - 180 * k} {cx + side * 70 * k},{cy - 170 * k}", w=3))
        E.append({"t": "ellipse", "at": at, "id": idp + "_body", "x": cx + side * 52 * k - 11 * k, "y": cy - 42 * k, "w": 22 * k, "h": 12 * k,
                  "c": "red", "fill": "red"})
    if mood == "happy":
        E.append(P(f"M{cx - 20 * k},{cy - 34 * k} Q{cx},{cy - 18 * k} {cx + 20 * k},{cy - 34 * k}", w=3))
    elif mood == "drool":
        E.append(P(f"M{cx - 20 * k},{cy - 30 * k} Q{cx},{cy - 10 * k} {cx + 20 * k},{cy - 30 * k} Z", w=3))
        E.append(P(f"M{cx + 12 * k},{cy - 22 * k} Q{cx + 8 * k},{cy + 2 * k} {cx + 14 * k},{cy + 8 * k} Q{cx + 22 * k},{cy} {cx + 12 * k},{cy - 22 * k}", c="blue", w=2.4))
    else:  # "o": surprised
        E.append({"t": "ellipse", "at": at, "id": idp + "_body", "x": cx - 9 * k, "y": cy - 38 * k, "w": 18 * k, "h": 20 * k, "c": "ink"})
    for side in (-1, 1):
        for j in range(3):
            x0, y0 = cx + side * (40 + 6 * j) * k, cy + (40 + 32 * j) * k
            E.append({"t": "path", "at": at, "id": idp + "_legs", "c": "ink", "w": 3,
                      "d": f"M{x0},{y0} L{x0 + side * 46 * k},{y0 + 18 * k} L{x0 + side * 52 * k},{y0 + 48 * k}"})
    if moves:
        E += [{"t": "move", "at": at, "kind": "wiggle", "targets": [idp + "_wl"], "pivot": [cx - 40 * k, cy - 5 * k], "amp": 18, "hz": 5},
              {"t": "move", "at": at, "kind": "wiggle", "targets": [idp + "_wr"], "pivot": [cx + 40 * k, cy - 5 * k], "amp": -18, "hz": 5},
              {"t": "move", "at": at, "kind": "bob", "targets": [idp + "*"], "amp": 14 * k, "hz": 1.2}]
    return E
