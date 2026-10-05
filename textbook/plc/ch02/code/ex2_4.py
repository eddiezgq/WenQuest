"""图 2.4.1：同一段电路的三种图——（a）电路图（原理图），（b）接线图，（c）端子图（端子表）。

取上料输送线控制电路里“停止—启动—自锁—热继电器—KM1 线圈”这一条通路（图 2.1.1）。按钮 S1、S2 装在现场的按钮盒里，
KM1、F1 和端子排 X1 装在控制柜里。触点的端子号按 EN 50005 / IEC 60947：常开 13-14，常闭 11-12，线圈 A1-A2，
热继电器的常闭辅助触点 95-96。线号取电位号：同一个电位的导线用同一个号。"""
from bookout import figure, out, T, style
from _draw02 import (contact, coil, frame, _l, _lab, _box, dot, INK, MUTED, ACCENT, GREEN, WARM, SOFT, LINE, build)

PB = {"act": "push"}
TH = {"act": "thermal"}


def tn(ax, x, y, text, ha="left"):
    ax.text(x, y, text, ha=ha, va="center", fontsize=7, color=MUTED, family="monospace")


def draw():
    plt = style()
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(12.2, 6.2), gridspec_kw={"width_ratios": [2.3, 4.6, 3.0]})
    # (a) schematic with terminal and wire numbers
    x = 1.0
    _l(a, [0.2, 2.6], [0, 0], lw=1.6); _lab(a, 0.12, 0, "L+", fs=9)
    dot(a, x, 0)
    y = build(a, x, 0, [("NC", "S2", PB), ("PAR", [[("NO", "S1", PB)], [("NO", "KM1")]], 1.2), ("NC", "F1", TH), ("COIL", "KM1")])
    _l(a, [x, x], [y, y - 0.3]); _l(a, [0.2, 2.6], [y - 0.3, y - 0.3], lw=1.6); _lab(a, 0.12, y - 0.3, "M", fs=9); dot(a, x, y - 0.3)
    for yy, t1, t2 in ((0, "11", "12"), (-1.2, "13", "14"), (-2.4, "95", "96"), (-3.4, "A1", "A2")):
        tn(a, x + 0.07, yy - 0.15, t1); tn(a, x + 0.07, yy - 0.88, t2)
    tn(a, x + 1.27, -1.35, "13"); tn(a, x + 1.27, -2.08, "14")
    for yy, w in ((-0.1, "1"), (-1.1, "2"), (-2.3, "3"), (-3.4, "4"), (y - 0.18, "5")):
        a.text(x - 0.12, yy, w, ha="right", va="center", fontsize=7.6, color=ACCENT)
    frame(a, (-0.3, 2.8), (y - 0.9, 0.6))
    a.set_title(T("（a）电路图", "(a) circuit diagram"), fontsize=10.5)

    # (b) wiring diagram: button box in the field, cabinet with X1, KM1, F1; every wire carries its potential number
    _box(b, 0.3, 1.6, 2.1, 3.9, "", fc=SOFT, ec=MUTED)
    b.text(1.35, 5.7, T("按钮盒（现场）", "button box (field)"), ha="center", fontsize=8.8)
    _box(b, 3.0, 0.6, 5.6, 4.9, "", fc=SOFT, ec=MUTED)
    b.text(5.8, 5.7, T("控制柜", "control cabinet"), ha="center", fontsize=8.8)

    def term(x, y, text, side):
        dot(b, x, y)
        tn(b, x + (0.08 if side > 0 else -0.08), y + 0.13, text, ha="left" if side > 0 else "right")

    def path(pts, num, at=0):
        b.plot([p[0] for p in pts], [p[1] for p in pts], color=INK, lw=1.0, zorder=3)
        (x0, y0), (x1, y1) = pts[at], pts[at + 1]
        b.text((x0 + x1) / 2, (y0 + y1) / 2 + 0.09, num, fontsize=7.4, color=ACCENT, ha="center")

    _box(b, 0.5, 3.9, 1.1, 0.9, "S2", fc="white", fs=8.6); term(1.6, 4.6, "11", 1); term(1.6, 4.1, "12", 1)
    _box(b, 0.5, 2.2, 1.1, 0.9, "S1", fc="white", fs=8.6); term(1.6, 2.9, "13", 1); term(1.6, 2.4, "14", 1)
    for k, y in ((1, 4.6), (2, 3.9), (3, 3.2), (4, 2.5)):
        _box(b, 3.2, y - 0.2, 0.4, 0.4, str(k), fc="white", fs=7.6)
    b.text(3.4, 2.05, "X1", ha="center", va="top", fontsize=8.6, family="monospace")
    path([(1.6, 4.6), (3.2, 4.6)], "1")
    path([(1.6, 4.1), (1.95, 4.1), (1.95, 2.9), (1.6, 2.9)], "2", at=1)
    dot(b, 1.95, 3.9); path([(1.95, 3.9), (3.2, 3.9)], "2")
    path([(1.6, 2.4), (2.2, 2.4), (2.2, 3.2), (3.2, 3.2)], "3", at=2)
    b.text(2.75, 2.75, "W1", fontsize=7.6, color=MUTED, family="monospace")
    # cabinet
    _box(b, 6.0, 3.4, 1.4, 1.1, "KM1", fc="white", fs=8.6); term(6.0, 4.25, "13", -1); term(6.0, 3.65, "14", -1)
    term(7.4, 4.25, "A2", 1); term(7.4, 3.65, "A1", 1)
    _box(b, 6.0, 1.3, 1.4, 0.9, "F1", fc="white", fs=8.6); term(6.0, 1.75, "95", -1); term(7.4, 1.75, "96", 1)
    path([(3.6, 4.6), (4.3, 4.6)], "1"); b.text(4.35, 4.6, "L+", va="center", fontsize=7.6, family="monospace", color=MUTED)
    path([(3.6, 3.9), (4.7, 3.9), (4.7, 4.25), (6.0, 4.25)], "2", at=2)
    path([(3.6, 3.2), (5.0, 3.2), (5.0, 3.65), (6.0, 3.65)], "3", at=2)
    dot(b, 5.0, 3.2); path([(5.0, 3.2), (5.0, 1.75), (6.0, 1.75)], "3", at=1)
    path([(7.4, 1.75), (7.9, 1.75), (7.9, 3.65), (7.4, 3.65)], "4", at=1)
    path([(7.4, 4.25), (8.2, 4.25), (8.2, 1.0)], "5", at=1); b.text(8.2, 0.92, "M", ha="center", va="top", fontsize=7.6, family="monospace", color=MUTED)
    frame(b, (0.0, 8.8), (0.3, 6.1))
    b.set_title(T("（b）接线图", "(b) wiring diagram"), fontsize=10.5)

    # (c) terminal diagram as a table
    rows = [("X1:1", "L+（F3）", "S2:11", "W1-1"), ("X1:2", "KM1:13", "S2:12、S1:13", "W1-2"), ("X1:3", "KM1:14", "S1:14", "W1-3"),
            ("X1:4", T("备用", "spare"), "—", "W1-4")]
    head = [T("端子", "terminal"), T("柜内", "inside"), T("现场", "field"), T("电缆芯", "core")]
    cx = [0.1, 1.05, 2.2, 3.85]
    for j, h in enumerate(head):
        c.text(cx[j], 5.6, h, fontsize=8.6, fontweight="bold")
    for i, row in enumerate(rows):
        yy = 5.0 - i * 0.62
        for j, v in enumerate(row):
            c.text(cx[j], yy, v, fontsize=8.2, family="monospace" if all(ord(ch) < 0x2E80 for ch in v) else None)
        _l(c, [0.05, 4.6], [yy - 0.3, yy - 0.3], color="#dfe5e8", lw=0.7)
    c.text(0.1, 1.5, T("W1：按钮盒电缆，4 芯", "W1: button-box cable, 4 cores"), fontsize=8.2, color=MUTED)
    frame(c, (0.0, 4.8), (0.8, 6.2))
    c.set_aspect("auto")
    c.set_title(T("（c）端子图", "(c) terminal diagram"), fontsize=10.5)
    return fig


figure(draw(), "fig2_4_1")
