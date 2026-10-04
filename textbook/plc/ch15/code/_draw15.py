"""第 15 章的画图工具：状态转换图、时序图、设备简图（中英两版，文字一律写成 T(中文, English)）。"""
import math

from bookout import T, style

INK = "#1d2327"
MUTED = "#7a868d"
ACCENT = "#3a7dc9"
WARM = "#d98c3a"
RED = "#b5443b"
GREEN = "#2f8f5b"
SOFT = "#eef2f6"


def fam(text):
    """Signal names in a monospace font; anything with Chinese in the book's sans font (the monospace font has no Chinese)."""
    return "monospace" if all(ord(c) < 0x2E80 for c in text) else None


def state_diagram(states, edges, size=(9, 5.2), title=None, group=None):
    """states: {key: (x, y, label, kind)} kind: "" | "init" | "fault"; edges: [(a, b, label, bend)] bend in −1…1 (curvature).
    A self-loop is (a, a, label, side) with side "up"/"down"/"left"/"right"."""
    plt = style()
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
    fig, ax = plt.subplots(figsize=size)
    H = 0.74
    widths = {k: max(1.5, 0.15 * max(len(l) * (1.3 if l.isascii() else 1.9) for l in v[2].split("\n")) + 0.3) for k, v in states.items()}
    if group:      # a dashed box around the working states; edges from "*" leave its right edge
        gx0, gy0, gx1, gy1, glabel = group
        ax.add_patch(FancyBboxPatch((gx0, gy0), gx1 - gx0, gy1 - gy0, boxstyle="round,pad=0.02,rounding_size=0.3", fc="none", ec=MUTED, lw=1.0, ls=(0, (4, 3)), zorder=1))
        ax.text(gx0 + 0.15, gy1 - 0.2, glabel, fontsize=9, color=MUTED, va="top")
    for k, (x, y, label, kind) in states.items():
        W = widths[k]
        fc = {"init": "#e8f1fb", "fault": "#fbeceb"}.get(kind, "white")
        ec = {"fault": RED}.get(kind, INK)
        ax.add_patch(FancyBboxPatch((x - W / 2, y - H / 2), W, H, boxstyle="round,pad=0.02,rounding_size=0.22", fc=fc, ec=ec, lw=1.4, zorder=3))
        if kind == "init":
            ax.add_patch(FancyBboxPatch((x - W / 2 + 0.06, y - H / 2 + 0.06), W - 0.12, H - 0.12, boxstyle="round,pad=0.02,rounding_size=0.18", fc="none", ec=ec, lw=1.0, zorder=3))
        ax.text(x, y, label, ha="center", va="center", fontsize=10.5, zorder=4, color=ec)

    def border(p, q, W):   # where the line from p to q leaves the box around p
        dx, dy = q[0] - p[0], q[1] - p[1]
        if dx == 0 and dy == 0:
            return p
        s = min((W / 2 + 0.04) / abs(dx) if dx else 1e9, (H / 2 + 0.04) / abs(dy) if dy else 1e9)
        return (p[0] + dx * s, p[1] + dy * s)

    for a, b, label, bend in edges:
        if a == "*":
            pb = states[b][:2]
            s, e = (group[2], pb[1]), (pb[0] - widths[b] / 2 - 0.04, pb[1])
            ax.add_patch(FancyArrowPatch(s, e, arrowstyle="-|>", mutation_scale=12, lw=1.2, color=RED, zorder=2))
            ax.text((s[0] + e[0]) / 2, pb[1] + 0.22, label, ha="center", va="bottom", fontsize=8.6, color=RED)
            continue
        pa = states[a][:2]
        W = widths[a]
        if a == b:
            side = bend or "up"
            off = {"up": (0, 1), "down": (0, -1), "left": (-1, 0), "right": (1, 0)}[side]
            p1 = (pa[0] + off[0] * W / 2 + off[1] * 0.3, pa[1] + off[1] * H / 2 + off[0] * 0.15)
            p2 = (pa[0] + off[0] * W / 2 - off[1] * 0.3, pa[1] + off[1] * H / 2 - off[0] * 0.15)
            ax.add_patch(FancyArrowPatch(p1, p2, connectionstyle="arc3,rad=-1.6", arrowstyle="-|>", mutation_scale=11, lw=1.1, color=MUTED, zorder=2))
            ax.text(pa[0] + off[0] * (W / 2 + 0.55), pa[1] + off[1] * (H / 2 + 0.42), label, ha="center", va="center", fontsize=8.6, color=MUTED)
            continue
        pb = states[b][:2]
        s, e = border(pa, pb, widths[a]), border(pb, pa, widths[b])
        rad = bend if isinstance(bend, (int, float)) else 0.0
        ax.add_patch(FancyArrowPatch(s, e, connectionstyle=f"arc3,rad={rad}", arrowstyle="-|>", mutation_scale=12, lw=1.2, color=ACCENT, zorder=2))
        mx, my = (s[0] + e[0]) / 2, (s[1] + e[1]) / 2
        dx, dy = e[0] - s[0], e[1] - s[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L                    # left normal; arc3 bulges to the right of travel for rad > 0
        b = -rad * L * 0.5                          # how far the arc bulges from the chord (to the left for b > 0)
        k = b + (0.28 if b >= 0 else -0.28)
        ax.text(mx + nx * k, my + ny * k, label, ha="center", va="center", fontsize=8.6, color=INK,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9), zorder=5)
    xs = [v[0] for v in states.values()]
    ys = [v[1] for v in states.values()]
    ax.set_xlim(min(v[0] - widths[k] / 2 for k, v in states.items()) - 0.6, max(v[0] + widths[k] / 2 for k, v in states.items()) + 0.6)
    ax.set_ylim(min(ys) - 1.0, max(ys) + 1.0)
    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=11)
    return fig


def timing(trace, rows, t0=0.0, t1=None, size=(9, 5.6), marks=()):
    """rows: [(signal, label, kind)] kind "bool" | ("analog", unit, scale); marks: [(t_ms, text)] vertical dashed lines."""
    plt = style()
    t = [x / 1000 for x in trace["t"]]
    t1 = t1 if t1 is not None else t[-1]
    fig, ax = plt.subplots(figsize=size)
    n = len(rows)
    for i, (sig, label, kind) in enumerate(rows):
        y0 = (n - 1 - i) * 1.25
        v = trace["v"][trace["names"].index(sig)]
        if kind == "bool":
            ys = [y0 + (0.8 if x else 0) for x in v]
            ax.step(t, ys, where="post", color=ACCENT if label.startswith(("Y", "H", "K")) else GREEN, lw=1.5)
        else:
            _, unit, scale = kind
            ys = [y0 + min(1.0, max(0.0, (x or 0) / scale)) * 0.9 for x in v]
            ax.plot(t, ys, color=WARM, lw=1.5)
            ax.text(t1 + 0.05, y0 + 0.9, f"{scale:g} {unit}", fontsize=8, color=MUTED, va="center")
        ax.text(t0 - 0.08 * (t1 - t0), y0 + 0.35, label, ha="right", va="center", fontsize=9.5, family=fam(label), color=INK)
        ax.axhline(y0, color="#e3e9e7", lw=0.6, zorder=0)
    for tm, text in marks:
        ax.axvline(tm / 1000, color=MUTED, lw=0.8, ls=(0, (4, 3)))
        ax.text(tm / 1000, n * 1.25 - 0.1, text, ha="center", va="bottom", fontsize=8.5, color=MUTED)
    ax.set_xlim(t0, t1)
    ax.set_ylim(-0.3, n * 1.25 + 0.3)
    ax.set_yticks([])
    ax.set_xlabel(T("时间 / s", "time / s"))
    for s in ("left", "right", "top"):
        ax.spines[s].set_visible(False)
    return fig


def press_sketch():
    """压装工位简图：机架、压头气缸、夹紧气缸、工件与轴承、光幕、双手按钮，标出 I/O 代号。"""
    plt = style()
    from matplotlib.patches import Rectangle, FancyBboxPatch, Circle
    fig, ax = plt.subplots(figsize=(8.6, 6.0))
    R = lambda x, y, w, h, fc="white", ec=INK, lw=1.3, z=2: ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, zorder=z))
    R(-2.0, 0, 4.0, 1.0, fc="#d8dee4")                  # base
    R(-1.6, 1.0, 0.25, 4.2, fc="#c4ccd4"); R(1.35, 1.0, 0.25, 4.2, fc="#c4ccd4")     # columns
    R(-1.8, 5.2, 3.6, 0.5, fc="#c4ccd4")                # crown
    R(-0.35, 3.7, 0.7, 1.5, fc="#e9edf1")               # ram cylinder
    R(-0.08, 2.2, 0.16, 1.5, fc="#f6f8fa")              # rod
    R(-0.3, 1.75, 0.6, 0.12, fc="#afb8c1")              # bearing
    R(-0.8, 1.0, 1.6, 0.75, fc="#8c959f")               # workpiece (cover)
    R(-1.25, 1.1, 0.35, 0.4, fc=WARM); R(0.9, 1.1, 0.35, 0.4, fc=WARM)      # clamps
    for x in (-2.4, 2.4):
        R(x - 0.06, 1.0, 0.12, 3.4, fc="#ffd47a", ec=WARM)                    # light curtain
    for y in (4.9, 3.85):
        ax.add_patch(Circle((0.55, y), 0.07, fc=GREEN, ec=INK, zorder=3))
    ax.add_patch(Circle((-1.5, 1.6), 0.07, fc=GREEN, ec=INK, zorder=3)); ax.add_patch(Circle((1.5, 1.6), 0.07, fc=GREEN, ec=INK, zorder=3))
    ax.add_patch(Circle((0, 0.85), 0.07, fc=GREEN, ec=INK, zorder=3))
    for x, lab in ((-3.4, "S_Hand1"), (3.4, "S_Hand2")):
        ax.add_patch(FancyBboxPatch((x - 0.35, -0.9), 0.7, 0.45, boxstyle="round,pad=0.02", fc="#2da44e", ec=INK, zorder=3))
        ax.text(x, -1.25, lab, ha="center", fontsize=9, family="monospace")
    lab = lambda x, y, tx, ty, text: ax.annotate(text, (x, y), (tx, ty), fontsize=9, family=fam(text), color=INK,
                                               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8), va="center")
    lab(0.0, 4.4, 2.9, 5.6, T("压头气缸  Y_PressDown / Y_PressUp", "Ram cylinder  Y_PressDown / Y_PressUp"))
    lab(0.6, 4.9, 2.9, 4.9, "B_PressUp")
    lab(0.6, 3.85, 2.9, 4.3, "B_PressDown")
    lab(0.0, 1.8, 2.9, 3.6, T("轴承", "bearing"))
    lab(0.0, 2.7, 2.9, 3.05, T("压装力传感器  AI_Force", "Force sensor  AI_Force"))
    lab(1.1, 1.3, 2.9, 2.45, T("夹紧气缸  Y_Clamp", "Clamp cylinder  Y_Clamp"))
    lab(1.5, 1.6, 2.9, 1.9, "B_Clamped / B_Unclamped")
    lab(-0.5, 1.2, -4.6, 3.2, T("工件（减速器盖）", "workpiece (gearbox cover)"))
    lab(0.0, 0.85, -4.6, 0.55, "B_Part")
    lab(-2.4, 3.5, -4.6, 4.3, T("安全光幕  S_LC", "light curtain  S_LC"))
    ax.text(-4.6, -1.7, T("操作台：S_EStop 急停、S_Auto 方式、S_Reset 复位、\nS_Step 单步、点动按钮；H_Ready、H_OK、H_NOK、H_Fault 指示灯",
                         "Panel: S_EStop, S_Auto (mode), S_Reset, S_Step, jog\nbuttons; lamps H_Ready, H_OK, H_NOK, H_Fault"), fontsize=8.5, color=MUTED, va="top")
    ax.set_xlim(-4.8, 6.6); ax.set_ylim(-2.5, 6.2); ax.set_aspect("equal"); ax.axis("off")
    return fig
