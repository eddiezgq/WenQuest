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


def cute_drone(cx, cy, k, at, idp="dr", mood="happy", moves=True):
    """A cute racing drone seen from the front: one big camera eye, two spinning rotors, little skids.
    Ids: <idp>_body, <idp>_eye, <idp>_bl0 / <idp>_bl1 (rotor blades); "<idp>*" moves the whole drone."""
    def P(d, c="ink", w=3.2, part="_body"):
        return {"t": "path", "at": at, "id": idp + part, "c": c, "w": w, "d": d}
    x0, y0, w, h = cx - 95 * k, cy - 50 * k, 190 * k, 100 * k
    E = [P(f"M{x0 + 30 * k},{y0} L{x0 + w - 30 * k},{y0} Q{x0 + w},{y0} {x0 + w},{y0 + 30 * k} L{x0 + w},{y0 + h - 30 * k} "
           f"Q{x0 + w},{y0 + h} {x0 + w - 30 * k},{y0 + h} L{x0 + 30 * k},{y0 + h} Q{x0},{y0 + h} {x0},{y0 + h - 30 * k} "
           f"L{x0},{y0 + 30 * k} Q{x0},{y0} {x0 + 30 * k},{y0} Z")]
    rot = []
    for i, side in enumerate((-1, 1)):
        hx, hy = cx + side * 175 * k, cy - 70 * k
        E.append(P(f"M{cx + side * 90 * k},{cy - 20 * k} L{hx},{hy}", w=4))
        E.append({"t": "ellipse", "at": at, "id": idp + "_body", "x": hx - 60 * k, "y": hy - 60 * k, "w": 120 * k, "h": 120 * k, "c": "muted"})
        E.append({"t": "line", "at": at, "id": f"{idp}_bl{i}", "pts": [[hx - 52 * k, hy], [hx + 52 * k, hy]], "c": "blue", "w": 5})
        rot.append((f"{idp}_bl{i}", hx, hy))
    # the one big camera eye
    E.append({"t": "ellipse", "at": at, "id": idp + "_eye", "x": cx - 30 * k, "y": cy - 40 * k, "w": 60 * k, "h": 60 * k, "c": "ink"})
    if mood == "o":
        E.append(P(f"M{cx - 14 * k},{cy - 24 * k} L{cx + 14 * k},{cy + 4 * k} M{cx + 14 * k},{cy - 24 * k} L{cx - 14 * k},{cy + 4 * k}", w=3, part="_eye"))
    else:
        E.append({"t": "ellipse", "at": at, "id": idp + "_eye", "x": cx - 12 * k, "y": cy - 22 * k, "w": 24 * k, "h": 24 * k, "c": "ink", "fill": "ink"})
    for side in (-1, 1):   # blush
        E.append({"t": "ellipse", "at": at, "id": idp + "_body", "x": cx + side * 58 * k - 10 * k, "y": cy + 10 * k, "w": 20 * k, "h": 10 * k, "c": "red", "fill": "red"})
    E.append(P(f"M{cx - 14 * k},{cy + 30 * k} Q{cx},{cy + 42 * k} {cx + 14 * k},{cy + 30 * k}" if mood == "happy" else
               f"M{cx - 8 * k},{cy + 34 * k} a8,8 0 1,0 16,0 a8,8 0 1,0 -16,0", w=3))
    E.append(P(f"M{cx - 60 * k},{y0 + h} L{cx - 75 * k},{y0 + h + 30 * k} L{cx - 30 * k},{y0 + h + 30 * k} "
               f"M{cx + 60 * k},{y0 + h} L{cx + 75 * k},{y0 + h + 30 * k} L{cx + 30 * k},{y0 + h + 30 * k}", w=3))
    if moves:
        E += [{"t": "move", "at": at, "kind": "spin", "targets": [b], "pivot": [hx, hy], "rpm": 240} for b, hx, hy in rot]
        E.append({"t": "move", "at": at, "kind": "bob", "targets": [idp + "*"], "amp": 12 * k, "hz": 1.3})
    return E


def cute_battery(cx, cy, k, at, idp="bat", level=0.6, mood="happy", sweat=False, moves=True, label=None):
    """A standing battery with a face; level 0–1 sets the charge (green, red when low). "<idp>*" moves it."""
    def P(d, c="ink", w=3.2, part="_b"):
        return {"t": "path", "at": at, "id": idp + part, "c": c, "w": w, "d": d}
    w, h = 150 * k, 240 * k
    x0, y0 = cx - w / 2, cy - h / 2
    c = "green" if level > 0.3 else "red"
    E = [{"t": "rect", "at": at, "id": idp + "_b", "x": x0 + 45 * k, "y": y0 - 22 * k, "w": 60 * k, "h": 22 * k, "c": "ink", "fill": "ink"},
         {"t": "rect", "at": at, "id": idp + "_b", "x": x0, "y": y0, "w": w, "h": h, "c": "ink"}]
    fh = max(6 * k, (h - 16 * k) * level)
    E.append({"t": "rect", "at": at, "id": idp + "_b", "x": x0 + 8 * k, "y": y0 + h - 8 * k - fh, "w": w - 16 * k, "h": fh, "c": c, "fill": c})
    for side in (-1, 1):
        E.append({"t": "ellipse", "at": at, "id": idp + "_b", "x": cx + side * 30 * k - 9 * k, "y": cy - 50 * k, "w": 18 * k, "h": 24 * k, "c": "ink", "fill": "ink"})
    mouth = {"happy": f"M{cx - 22 * k},{cy} Q{cx},{cy + 22 * k} {cx + 22 * k},{cy}",
             "tired": f"M{cx - 22 * k},{cy + 16 * k} Q{cx},{cy - 4 * k} {cx + 22 * k},{cy + 16 * k}"}[mood]
    E.append(P(mouth))
    if sweat:
        E.append(P(f"M{x0 + w + 14 * k},{y0 + 10 * k} Q{x0 + w + 34 * k},{y0 + 50 * k} {x0 + w + 14 * k},{y0 + 60 * k} "
                   f"Q{x0 + w - 6 * k},{y0 + 50 * k} {x0 + w + 14 * k},{y0 + 10 * k}", c="blue", w=3))
    if label:
        E.append(txt(cx, y0 + h + 60 * k, 48 * k, label, at, c=c, font="en", id=idp + "_b"))
    if moves:
        E.append({"t": "move", "at": at, "kind": "bob", "targets": [idp + "*"], "amp": 8 * k, "hz": 1.1})
    return E


def cute_bot(cx, cy, k, at, idp="bot", mood="happy", moves=True):
    """A cute warehouse humanoid standing with feet at (cx, cy): box head with two eyes, torso, bird-like legs.
    "<idp>*" moves the whole robot."""
    def P(d, c="ink", w=3.4, part="_b"):
        return {"t": "path", "at": at, "id": idp + part, "c": c, "w": w, "d": d}
    E = [{"t": "rect", "at": at, "id": idp + "_b", "x": cx - 70 * k, "y": cy - 420 * k, "w": 140 * k, "h": 90 * k, "c": "ink"},
         {"t": "rect", "at": at, "id": idp + "_b", "x": cx - 60 * k, "y": cy - 325 * k, "w": 120 * k, "h": 150 * k, "c": "ink", "fill": "gold"}]
    for side in (-1, 1):
        E.append({"t": "ellipse", "at": at, "id": idp + "_b", "x": cx + side * 32 * k - 13 * k, "y": cy - 398 * k, "w": 26 * k, "h": 30 * k, "c": "blue", "fill": "blue"})
        E.append(P(f"M{cx + side * 60 * k},{cy - 300 * k} L{cx + side * 100 * k},{cy - 230 * k} L{cx + side * 90 * k},{cy - 170 * k}"))
        E.append(P(f"M{cx + side * 30 * k},{cy - 175 * k} L{cx + side * 50 * k},{cy - 95 * k} L{cx + side * 20 * k},{cy - 20 * k} "
                   f"L{cx + side * 55 * k},{cy}"))
    E.append(P(f"M{cx - 22 * k},{cy - 360 * k} Q{cx},{cy - 344 * k} {cx + 22 * k},{cy - 360 * k}" if mood == "happy" else
               f"M{cx - 22 * k},{cy - 346 * k} Q{cx},{cy - 362 * k} {cx + 22 * k},{cy - 346 * k}"))
    if moves:
        E.append({"t": "move", "at": at, "kind": "bob", "targets": [idp + "*"], "amp": 8 * k, "hz": 1.0})
    return E


def car(cx, cy, k, at, idp="car", mood="happy", jets=None, moves=True):
    """小 R: a cute low sports car seen from the side, facing right; (cx, cy) = the middle of the road under it.
    Ids: <idp>_b (body), <idp>_w0 / <idp>_w1 (wheels; spin about wheel_hub), <idp>_jet (gas jets: jets = "down" | "back" | None).
    "<idp>*" moves the whole car."""
    def P(d, c="ink", w=3.6, part="_b", **kw):
        return {"t": "path", "at": at, "id": idp + part, "c": c, "w": w, "d": d, **kw}
    X = lambda v: cx + v * k   # noqa: E731
    Y = lambda v: cy - v * k   # noqa: E731
    E = []
    if jets == "down":
        for x in (-95, 95):
            E.append(P(f"M{X(x - 18)},{Y(18)} L{X(x + 18)},{Y(18)} L{X(x + 40)},{Y(-90)} L{X(x - 40)},{Y(-90)} Z", c="blue", w=3, part="_jet"))
    if jets == "back":
        E.append(P(f"M{X(-205)},{Y(60)} L{X(-205)},{Y(30)} L{X(-330)},{Y(10)} L{X(-330)},{Y(80)} Z", c="blue", w=3, part="_jet"))
    E.append(P(f"M{X(-210)},{Y(28)} L{X(-210)},{Y(70)} L{X(-120)},{Y(80)} L{X(-40)},{Y(128)} L{X(70)},{Y(128)} "
               f"L{X(150)},{Y(84)} L{X(215)},{Y(66)} L{X(222)},{Y(34)} L{X(200)},{Y(26)} Z"))
    E.append(P(f"M{X(-30)},{Y(118)} L{X(60)},{Y(118)} L{X(118)},{Y(86)} L{X(-80)},{Y(86)} Z", c="blue", w=3))   # windshield
    E.append({"t": "ellipse", "at": at, "id": idp + "_b", "x": X(22), "y": Y(112), "w": 14 * k, "h": 16 * k, "c": "ink", "fill": "ink"})
    E.append({"t": "ellipse", "at": at, "id": idp + "_b", "x": X(56), "y": Y(112), "w": 14 * k, "h": 16 * k, "c": "ink", "fill": "ink"})
    mouth = {"happy": f"M{X(150)},{Y(58)} Q{X(170)},{Y(46)} {X(190)},{Y(58)}", "o": f"M{X(162)},{Y(58)} a8,8 0 1,0 {16 * k},0 a8,8 0 1,0 {-16 * k},0",
             "worried": f"M{X(150)},{Y(48)} Q{X(170)},{Y(60)} {X(190)},{Y(48)}"}[mood]
    E.append(P(mouth, w=3))
    E.append({"t": "rect", "at": at, "id": idp + "_b", "x": X(-212), "y": Y(92), "w": 46 * k, "h": 12 * k, "c": "red", "fill": "red"})   # spoiler
    for i, x in enumerate((-130, 130)):   # wheels: <idp>_w0, <idp>_w1 (spin each about its own hub: wheel_hub(cx, cy, k, i))
        E.append({"t": "ellipse", "at": at, "id": f"{idp}_w{i}", "x": X(x - 34), "y": Y(62), "w": 68 * k, "h": 68 * k, "c": "ink"})
        E.append(P(f"M{X(x - 22)},{Y(28)} L{X(x + 22)},{Y(28)} M{X(x)},{Y(50)} L{X(x)},{Y(6)}", c="ink", w=3, part=f"_w{i}"))
    if moves:
        if jets:
            E.append({"t": "move", "at": at, "kind": "wiggle", "targets": [idp + "_jet"], "pivot": [cx, cy], "amp": 3, "hz": 8})
        E.append({"t": "move", "at": at, "kind": "bob", "targets": [idp + "*"], "amp": 6 * k, "hz": 1.6})
    return E


def wheel_hub(cx, cy, k, i):
    return [cx + (-130 if i == 0 else 130) * k, cy - 28 * k]


def car_drive(cx, cy, k, at, idp="car", rpm=90):
    """Spinning wheels for a car drawn with car()."""
    return [{"t": "move", "at": at, "kind": "spin", "targets": [f"{idp}_w{i}"], "pivot": wheel_hub(cx, cy, k, i), "rpm": rpm} for i in (0, 1)]


def cute_whale(cx, cy, k, at, idp="wh", mood="happy", moves=True, mouth_open=False):
    """A cute sperm whale facing left: big box-shaped head, small lower jaw, round eye, smile, tail on the right, a spout.
    (cx, cy) = middle of the body. Ids: <idp>_b (body), <idp>_jaw (lower jaw; rotate about jaw_hinge), <idp>_t (tail; wiggles),
    <idp>_sp (spout). "<idp>*" moves the whole whale. mouth_open draws the jaw dropped."""
    def P(d, c="ink", w=3.6, part="_b", **kw):
        return {"t": "path", "at": at, "id": idp + part, "c": c, "w": w, "d": d, **kw}
    X = lambda v: cx + v * k   # noqa: E731
    Y = lambda v: cy + v * k   # noqa: E731
    E = [P(f"M{X(-260)},{Y(-110)} Q{X(-270)},{Y(-150)} {X(-200)},{Y(-150)} L{X(40)},{Y(-140)} Q{X(170)},{Y(-120)} {X(250)},{Y(-30)} "
           f"Q{X(290)},{Y(10)} {X(320)},{Y(0)} L{X(320)},{Y(20)} Q{X(220)},{Y(90)} {X(40)},{Y(80)} L{X(-150)},{Y(40)} "
           f"Q{X(-262)},{Y(30)} {X(-262)},{Y(-40)} Z", c="ink", w=4, fill="blue"),
         {"t": "ellipse", "at": at, "id": idp + "_b", "x": X(-170), "y": Y(-60), "w": 30 * k, "h": 34 * k, "c": "ink", "fill": "ink"},
         {"t": "ellipse", "at": at, "id": idp + "_b", "x": X(-130), "y": Y(-10), "w": 34 * k, "h": 18 * k, "c": "red", "fill": "red"},
         P({"happy": f"M{X(-240)},{Y(0)} Q{X(-210)},{Y(18)} {X(-180)},{Y(4)}", "o": f"M{X(-235)},{Y(6)} a10,10 0 1,0 {20 * k},0 a10,10 0 1,0 {-20 * k},0",
            "worried": f"M{X(-240)},{Y(12)} Q{X(-210)},{Y(-4)} {X(-180)},{Y(12)}"}[mood], w=3)]
    rot = 22 if mouth_open else 0
    E.append(P(f"M{X(-240)},{Y(34)} L{X(-40)},{Y(64)} L{X(-40)},{Y(84)} L{X(-240)},{Y(52)} Z", c="ink", w=3.4, part="_jaw"))
    for i in range(5):
        E.append(P(f"M{X(-220 + 38 * i)},{Y(36 + 6 * i)} L{X(-212 + 38 * i)},{Y(22 + 6 * i)}", w=3, part="_jaw"))
    E.append(P(f"M{X(310)},{Y(10)} Q{X(360)},{Y(-60)} {X(420)},{Y(-80)} Q{X(390)},{Y(-10)} {X(330)},{Y(12)} "
               f"Q{X(390)},{Y(40)} {X(420)},{Y(100)} Q{X(350)},{Y(80)} {X(310)},{Y(18)} Z", c="ink", w=3.6, part="_t", fill="blue"))
    E.append(P(f"M{X(-220)},{Y(-150)} Q{X(-240)},{Y(-220)} {X(-280)},{Y(-240)} M{X(-220)},{Y(-150)} Q{X(-215)},{Y(-230)} {X(-220)},{Y(-260)} "
               f"M{X(-220)},{Y(-150)} Q{X(-195)},{Y(-220)} {X(-160)},{Y(-240)}", c="blue", w=3.4, part="_sp"))
    if rot:
        E.append({"t": "move", "at": at, "kind": "rotate", "targets": [idp + "_jaw"], "to": rot, "pivot": jaw_hinge(cx, cy, k), "dur": 0.3, "delay": 0})
    if moves:
        E += [{"t": "move", "at": at, "kind": "wiggle", "targets": [idp + "_t"], "pivot": [X(320), Y(10)], "amp": 10, "hz": 1.4},
              {"t": "move", "at": at, "kind": "pulse", "targets": [idp + "_sp"], "dur": 0.8},
              {"t": "move", "at": at, "kind": "bob", "targets": [idp + "*"], "amp": 10 * k, "hz": 0.7}]
    return E


def jaw_hinge(cx, cy, k):
    return [cx - 40 * k, cy + 74 * k]


def cute_guide(cx, cy, k, at, idp="gd", mood="happy", moves=True, sweat=False):
    """小导: a half-size reception robot (cute_bot proportions, feet at (cx, cy)) with a round screen belly, antenna with a
    blinking light (<idp>_ant, spins/pulses) and a waving arm (<idp>_arm, wiggles). "<idp>*" moves the whole robot."""
    def P(d, c="ink", w=3.4, part="_b", **kw):
        return {"t": "path", "at": at, "id": idp + part, "c": c, "w": w, "d": d, **kw}
    X = lambda v: cx + v * k   # noqa: E731
    Y = lambda v: cy - v * k   # noqa: E731
    E = [{"t": "rect", "at": at, "id": idp + "_b", "x": X(-80), "y": Y(400), "w": 160 * k, "h": 110 * k, "c": "ink"},
         {"t": "rect", "at": at, "id": idp + "_b", "x": X(-62), "y": Y(280), "w": 124 * k, "h": 170 * k, "c": "ink", "fill": "gold"},
         {"t": "rect", "at": at, "id": idp + "_b", "x": X(-40), "y": Y(250), "w": 80 * k, "h": 60 * k, "c": "ink"},
         P(f"M{X(-28)},{Y(220)} L{X(-12)},{Y(220)} M{X(-28)},{Y(205)} L{X(20)},{Y(205)}", c="blue", w=3)]
    for side in (-1, 1):
        E.append({"t": "ellipse", "at": at, "id": idp + "_b", "x": X(side * 34 - 14), "y": Y(375), "w": 28 * k, "h": 32 * k, "c": "blue", "fill": "blue"})
        E.append(P(f"M{X(side * 28)},{Y(110)} L{X(side * 36)},{Y(10)} L{X(side * 60)},{Y(0)}"))
    E.append({"t": "ellipse", "at": at, "id": idp + "_b", "x": X(-62), "y": Y(338), "w": 22 * k, "h": 12 * k, "c": "red", "fill": "red"})
    E.append({"t": "ellipse", "at": at, "id": idp + "_b", "x": X(40), "y": Y(338), "w": 22 * k, "h": 12 * k, "c": "red", "fill": "red"})
    E.append(P(f"M{X(-22)},{Y(330)} Q{X(0)},{Y(312)} {X(22)},{Y(330)}" if mood == "happy" else f"M{X(-22)},{Y(316)} Q{X(0)},{Y(332)} {X(22)},{Y(316)}"))
    E.append(P(f"M{X(-62)},{Y(260)} L{X(-110)},{Y(190)} L{X(-100)},{Y(130)}"))
    E.append(P(f"M{X(62)},{Y(260)} L{X(120)},{Y(320)} L{X(150)},{Y(380)}", part="_arm"))
    E.append(P(f"M{X(0)},{Y(400)} L{X(0)},{Y(450)}", part="_ant"))
    E.append({"t": "ellipse", "at": at, "id": idp + "_ant", "x": X(-14), "y": Y(478), "w": 28 * k, "h": 28 * k, "c": "red", "fill": "red"})
    if sweat:
        E.append(P(f"M{X(100)},{Y(420)} Q{X(120)},{Y(380)} {X(100)},{Y(370)} Q{X(80)},{Y(380)} {X(100)},{Y(420)}", c="blue", w=3))
    if moves:
        E += [{"t": "move", "at": at, "kind": "wiggle", "targets": [idp + "_arm"], "pivot": [X(62), Y(260)], "amp": 14, "hz": 2.2},
              {"t": "move", "at": at, "kind": "pulse", "targets": [idp + "_ant"], "dur": 0.6},
              {"t": "move", "at": at, "kind": "bob", "targets": [idp + "*"], "amp": 8 * k, "hz": 1.0}]
    return E
