"""第 2 章的画图工具（中英两版，文字一律写成 T(中文, English)）。

电气图按 GB/T 4728 / IEC 60617 的图形符号画：控制电路竖着画（上面一条电源线 L+，下面一条 M，直流 24 V；每一列是一条电流通路），
触点画成“开关刀”的样子，线圈是矩形，指示灯是圆里一个叉；主电路三根相线竖着往下走到电动机。
一个元件占一格（高 1），build() 按列表从上往下画一条通路，("PAR", [支路1, 支路2]) 画并联。
"""
from bookout import T, style

INK = "#1d2327"
MUTED = "#7a868d"
ACCENT = "#3a7dc9"
WARM = "#d98c3a"
RED = "#b5443b"
GREEN = "#2f8f5b"
SOFT = "#eef2f6"
LINE = "#c9d2d8"
LW = 1.25


def fam(text):
    return "monospace" if all(ord(c) < 0x2E80 for c in text) else None


def _box(ax, x, y, w, h, text="", fc="white", ec=INK, fs=9.5, lw=1.1, color=None, r=0.06, weight=None):
    from matplotlib.patches import FancyBboxPatch
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.0,rounding_size={r}", fc=fc, ec=ec, lw=lw, zorder=2))
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=color or ec, zorder=3, family=fam(text), fontweight=weight)


def _l(ax, xs, ys, color=INK, lw=LW, ls="-", z=2):
    ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="round", zorder=z)


def _lab(ax, x, y, text, ha="right", fs=8.6, color=INK, va="center"):
    ax.text(x, y, text, ha=ha, va=va, fontsize=fs, family=fam(text), color=color, zorder=4)


def dot(ax, x, y, color=INK):
    ax.plot([x], [y], "o", ms=3.4, color=color, zorder=6)


# ---------------------------------------------------------------- symbols (vertical, top terminal at y, bottom at y−1)
def actuator(ax, x, ym, kind, side=-1):
    """Operating device drawn beside a contact, joined by a dashed line (mechanical link)."""
    xa = x + side * 0.5
    _l(ax, [x + side * 0.1, xa], [ym, ym], lw=0.9, ls=(0, (2.5, 1.8)))
    if kind == "push":             # push-button: a bracket
        _l(ax, [xa, xa], [ym - 0.12, ym + 0.12], lw=1.0)
        _l(ax, [xa, xa - side * 0.07], [ym + 0.12, ym + 0.12], lw=1.0)
        _l(ax, [xa, xa - side * 0.07], [ym - 0.12, ym - 0.12], lw=1.0)
    elif kind == "estop":          # mushroom head
        from matplotlib.patches import Arc
        _l(ax, [xa, xa], [ym - 0.14, ym + 0.14], lw=1.0)
        ax.add_patch(Arc((xa, ym), 0.22, 0.3, theta1=90 if side < 0 else -90, theta2=270 if side < 0 else 90, lw=1.0, color=INK))
    elif kind == "thermal":        # thermal effect: a small square with a step
        from matplotlib.patches import Rectangle
        ax.add_patch(Rectangle((xa - 0.09, ym - 0.09), 0.18, 0.18, fill=False, lw=0.9, ec=INK))
        _l(ax, [xa - 0.06, xa - 0.06, xa + 0.06, xa + 0.06], [ym - 0.05, ym + 0.04, ym + 0.04, ym - 0.05], lw=0.8)
    elif kind == "limit":          # position switch: a small triangle
        _l(ax, [xa, xa - side * 0.0, xa], [ym - 0.1, ym, ym + 0.1], lw=1.0)
        _l(ax, [xa, xa + side * 0.12, xa], [ym - 0.1, ym, ym + 0.1], lw=1.0)


def contact(ax, x, y, name="", nc=False, act=None, delay=None, label_side=-1):
    """NO (blade leans left, open) or NC (blade crosses a stub to the right). delay: 'on' (closes late) / 'off'."""
    _l(ax, [x, x], [y, y - 0.3])
    _l(ax, [x, x], [y - 0.72, y - 1])
    if nc:
        _l(ax, [x, x + 0.28], [y - 0.3, y - 0.3])
        _l(ax, [x, x + 0.2], [y - 0.72, y - 0.2])
    else:
        _l(ax, [x, x - 0.24], [y - 0.72, y - 0.28])
    if delay:   # time-delay contact: a "parachute" arc to the right, joined to the blade
        from matplotlib.patches import Arc
        xb = x + (0.12 if nc else -0.12)
        _l(ax, [xb, x + 0.3], [y - 0.5, y - 0.5], lw=0.9)
        ax.add_patch(Arc((x + 0.38, y - 0.5), 0.16, 0.26, theta1=90 if delay == "on" else -90, theta2=270 if delay == "on" else 90,
                         lw=0.9, color=INK))
    if act:
        actuator(ax, x - (0.0 if not nc else -0.12) - 0.1, y - 0.5, act)
    if name:
        off = 0.72 if act else 0.32
        _lab(ax, x + label_side * off, y - 0.5, name, ha="right" if label_side < 0 else "left")


def coil(ax, x, y, name="", kind=None, label_side=-1):
    from matplotlib.patches import Rectangle
    _l(ax, [x, x], [y, y - 0.34])
    _l(ax, [x, x], [y - 0.66, y - 1])
    ax.add_patch(Rectangle((x - 0.2, y - 0.66), 0.4, 0.32, fill=True, fc="white", lw=LW, ec=INK, zorder=3))
    if kind == "on":                 # on-delay coil: a marked box beside it
        ax.add_patch(Rectangle((x - 0.36, y - 0.66), 0.16, 0.32, fill=True, fc="white", lw=1.0, ec=INK, zorder=3))
        _l(ax, [x - 0.36, x - 0.2], [y - 0.66, y - 0.34], lw=0.9, z=4)
        _l(ax, [x - 0.36, x - 0.2], [y - 0.34, y - 0.66], lw=0.9, z=4)
    if name:
        _lab(ax, x + label_side * (0.5 if kind else 0.28), y - 0.5, name, ha="right" if label_side < 0 else "left")


def lamp(ax, x, y, name="", label_side=-1):
    from matplotlib.patches import Circle
    _l(ax, [x, x], [y, y - 0.32])
    _l(ax, [x, x], [y - 0.68, y - 1])
    ax.add_patch(Circle((x, y - 0.5), 0.18, fc="white", ec=INK, lw=LW, zorder=3))
    d = 0.18 * 0.707
    _l(ax, [x - d, x + d], [y - 0.5 - d, y - 0.5 + d], lw=1.0, z=4)
    _l(ax, [x - d, x + d], [y - 0.5 + d, y - 0.5 - d], lw=1.0, z=4)
    if name:
        _lab(ax, x + label_side * 0.28, y - 0.5, name, ha="right" if label_side < 0 else "left")


def fuse(ax, x, y, name="", label_side=-1, h=1.0):
    from matplotlib.patches import Rectangle
    _l(ax, [x, x], [y, y - h])
    ax.add_patch(Rectangle((x - 0.08, y - 0.5 * h - 0.2), 0.16, 0.4, fc="white", ec=INK, lw=LW, zorder=3))
    _l(ax, [x, x], [y - 0.5 * h - 0.2, y - 0.5 * h + 0.2], lw=LW, z=4)
    if name:
        _lab(ax, x + label_side * 0.2, y - 0.5 * h, name, ha="right" if label_side < 0 else "left")


def wire(ax, x, y, h=1.0):
    _l(ax, [x, x], [y, y - h])


DRAW = {"NO": lambda ax, x, y, n, **k: contact(ax, x, y, n, **k), "NC": lambda ax, x, y, n, **k: contact(ax, x, y, n, nc=True, **k),
        "COIL": lambda ax, x, y, n, **k: coil(ax, x, y, n, **k), "LAMP": lambda ax, x, y, n, **k: lamp(ax, x, y, n, **k),
        "FUSE": lambda ax, x, y, n, **k: fuse(ax, x, y, n, **k), "WIRE": lambda ax, x, y, n, **k: wire(ax, x, y)}


def depth(items):
    d = 0
    for it in items:
        if it[0] == "PAR":
            d += max(depth(b) for b in it[1]) + 0.4
        else:
            d += 1
    return d


def build(ax, x, y, items, dx=1.3):
    """Draw a current path from (x, y) downwards; returns the y where it ends."""
    for it in items:
        if it[0] == "PAR":
            branches = it[1]
            bdx = it[2] if len(it) > 2 else dx
            h = max(depth(b) for b in branches)
            xs = [x + i * bdx for i in range(len(branches))]
            _l(ax, [x, xs[-1]], [y - 0.2, y - 0.2])
            _l(ax, [x, x], [y, y - 0.2])
            dot(ax, x, y - 0.2)
            for xb, b in zip(xs, branches):
                yb = y - 0.2
                if xb != x:
                    pass
                yb = build(ax, xb, yb, b, dx)
                _l(ax, [xb, xb], [yb, y - 0.2 - h])
            _l(ax, [x, xs[-1]], [y - 0.2 - h, y - 0.2 - h])
            dot(ax, x, y - 0.2 - h)
            _l(ax, [x, x], [y - 0.2 - h, y - 0.4 - h])
            y = y - 0.4 - h
        else:
            kind, name = it[0], it[1]
            kw = it[2] if len(it) > 2 else {}
            DRAW[kind](ax, x, y, name, **kw)
            y -= 1
    return y


def control(ax, cols, top=0.0, bottom=None, x0=0.0, rails=("L+", "M"), numbers=True, gap=1.55, notes=None, xs=None):
    """cols: list of item lists, one per current path. Returns the x positions used."""
    xs = xs or [x0 + 0.6 + i * gap for i in range(len(cols))]
    ends = []
    for x, items in zip(xs, cols):
        ends.append(build(ax, x, top, items))
    bottom = bottom if bottom is not None else min(ends) - 0.4
    for x, ye in zip(xs, ends):
        _l(ax, [x, x], [ye, bottom])
        dot(ax, x, top)
        dot(ax, x, bottom)
    xl, xr = x0, max(xs) + 0.5
    _l(ax, [xl, xr], [top, top], lw=1.6)
    _l(ax, [xl, xr], [bottom, bottom], lw=1.6)
    _lab(ax, xl - 0.08, top, rails[0], fs=9)
    _lab(ax, xl - 0.08, bottom, rails[1], fs=9)
    if numbers:
        for i, x in enumerate(xs):
            ax.text(x, bottom - 0.32, str(i + 1), ha="center", va="top", fontsize=7.8, color=MUTED)
    if notes:
        for x, n in zip(xs, notes):
            if n:
                ax.text(x, bottom - 0.68, n, ha="center", va="top", fontsize=7.6, color=MUTED, family=fam(n))
    return xs, bottom


# ---------------------------------------------------------------- main circuit pieces (three phases, spacing P)
P = 0.36


def phase_lines(ax, x, y0, y1, n=3):
    for i in range(n):
        _l(ax, [x + i * P, x + i * P], [y0, y1])


def group(ax, x, y, kind, name="", label_side=-1, h=1.0):
    """Three-pole device across the phases at x, x+P, x+2P, from y down to y−h."""
    if kind == "FUSE":
        for i in range(3):
            fuse(ax, x + i * P, y, h=h)
    elif kind in ("NO", "KM", "CB", "QS"):
        for i in range(3):
            xi = x + i * P
            _l(ax, [xi, xi], [y, y - 0.3]); _l(ax, [xi, xi], [y - 0.72, y - h])
            _l(ax, [xi, xi - 0.2], [y - 0.72, y - 0.3])
            if kind == "KM":   # contactor function: a small semicircle on the fixed contact (IEC 60617)
                from matplotlib.patches import Arc
                ax.add_patch(Arc((xi, y - 0.3), 0.12, 0.12, theta1=0, theta2=180, lw=1.0, color=INK))
            if kind == "CB":   # circuit breaker: a cross on the fixed contact
                _l(ax, [xi - 0.06, xi + 0.06], [y - 0.24, y - 0.36], lw=1.0); _l(ax, [xi - 0.06, xi + 0.06], [y - 0.36, y - 0.24], lw=1.0)
        _l(ax, [x - 0.12, x + 2 * P - 0.12], [y - 0.5, y - 0.5], lw=0.9, ls=(0, (2.5, 1.8)))
        if kind in ("CB", "QS"):
            actuator(ax, x - 0.02, y - 0.5, "thermal" if kind == "CB" else "push")
    elif kind == "OL":     # thermal elements of the overload relay
        from matplotlib.patches import Rectangle
        for i in range(3):
            xi = x + i * P
            _l(ax, [xi, xi], [y, y - h])
            ax.add_patch(Rectangle((xi - 0.09, y - 0.5 * h - 0.18), 0.18, 0.36, fc="white", ec=INK, lw=LW, zorder=3))
            _l(ax, [xi - 0.05, xi - 0.05, xi + 0.05, xi + 0.05], [y - 0.5 * h - 0.1, y - 0.5 * h + 0.06, y - 0.5 * h + 0.06, y - 0.5 * h - 0.1], lw=0.9, z=4)
    if name:
        xl = x - 0.62 if label_side < 0 else x + 2 * P + 0.25
        if kind in ("CB", "QS") and label_side < 0:
            xl = x - 0.75
        _lab(ax, xl, y - 0.5 * h, name, ha="right" if label_side < 0 else "left")


def motor(ax, x, y, name="M1", text="M\n3~", r=0.42):
    """Motor below the three phase lines ending at y; returns nothing."""
    from matplotlib.patches import Circle
    cx = x + P
    cy = y - 0.3 - r
    for i in range(3):
        xi = x + i * P
        _l(ax, [xi, xi, cx + (i - 1) * 0.22], [y, y - 0.15, cy + r * 0.86 if i != 1 else cy + r])
    ax.add_patch(Circle((cx, cy), r, fc="white", ec=INK, lw=LW, zorder=3))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=8.5, zorder=4, linespacing=0.95)
    _lab(ax, cx - r - 0.12, cy, name)
    return cy - r


def rails3(ax, x, y, names=("L1", "L2", "L3")):
    for i, n in enumerate(names):
        ax.text(x + i * P, y + 0.08, n, ha="center", va="bottom", fontsize=8, family="monospace")


def frame(ax, xlim, ylim):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")


# ---------------------------------------------------------------- timing diagrams in milliseconds
def timing_ms(ax, trace, rows, t0, t1, marks=(), title=None, zero=0.0, labels=True):
    """rows: [(signal, label, color)]; time axis in ms relative to `zero`."""
    t = [x - zero for x in trace["t"]]
    n = len(rows)
    for i, row in enumerate(rows):
        sig, label = row[0], row[1]
        color = row[2] if len(row) > 2 else ACCENT
        y0 = (n - 1 - i) * 1.2
        v = trace["v"][trace["names"].index(sig)]
        pts = [(tt, y0 + (0.75 if x else 0)) for tt, x in zip(t, v) if t0 - 5 <= tt <= t1 + 5]
        if pts:
            ax.step([p[0] for p in pts], [p[1] for p in pts], where="post", color=color, lw=1.5)
        if labels:
            ax.text(t0 - 0.02 * (t1 - t0), y0 + 0.35, label, ha="right", va="center", fontsize=8.6, family=fam(label), color=INK)
        ax.axhline(y0, color="#e3e9e7", lw=0.6, zorder=0)
    for tm, text in marks:
        ax.axvline(tm - zero, color=MUTED, lw=0.8, ls=(0, (4, 3)))
        if text:
            ax.text(tm - zero, n * 1.2 - 0.05, text, ha="center", va="bottom", fontsize=8, color=MUTED)
    ax.set_xlim(t0, t1)
    ax.set_ylim(-0.3, n * 1.2 + 0.35)
    ax.set_yticks([])
    ax.set_xlabel(T("时间 / ms", "time / ms"), fontsize=9)
    for s in ("left", "right", "top"):
        ax.spines[s].set_visible(False)
    if title:
        ax.set_title(title, fontsize=10)
