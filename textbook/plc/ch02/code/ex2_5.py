"""图 2.5.1：从继电器电路到逻辑式。（a）电路图里的一条电流通路（竖着画）；（b）同一条通路横过来，就是梯形图的一级；
（c）写成逻辑式：串联是“与”，并联是“或”，常闭触点是“非”。"""
from bookout import figure, T, style
from _draw02 import build, frame, _l, _lab, dot, INK, MUTED, ACCENT, GREEN, SOFT, _box

PB = {"act": "push"}
TH = {"act": "thermal"}
ES = {"act": "estop"}


def ld_contact(ax, x, y, name, nc=False):
    _l(ax, [x, x + 0.25], [y, y]); _l(ax, [x + 0.55, x + 0.8], [y, y])
    _l(ax, [x + 0.25, x + 0.25], [y - 0.2, y + 0.2]); _l(ax, [x + 0.55, x + 0.55], [y - 0.2, y + 0.2])
    if nc:
        _l(ax, [x + 0.2, x + 0.6], [y - 0.24, y + 0.24], lw=1.0)
    ax.text(x + 0.4, y + 0.32, name, ha="center", va="bottom", fontsize=8.2, family="monospace")
    return x + 0.8


def ld_coil(ax, x, y, name):
    from matplotlib.patches import Arc
    _l(ax, [x, x + 0.22], [y, y]); _l(ax, [x + 0.58, x + 0.8], [y, y])
    ax.add_patch(Arc((x + 0.3, y), 0.24, 0.44, theta1=100, theta2=260, lw=1.25, color=INK))
    ax.add_patch(Arc((x + 0.5, y), 0.24, 0.44, theta1=-80, theta2=80, lw=1.25, color=INK))
    ax.text(x + 0.4, y + 0.32, name, ha="center", va="bottom", fontsize=8.2, family="monospace")
    return x + 0.8


def draw():
    plt = style()
    fig, (a, b) = plt.subplots(1, 2, figsize=(11.2, 5.6), gridspec_kw={"width_ratios": [2.2, 6.4]})
    x = 1.3
    _l(a, [0.2, 2.8], [0, 0], lw=1.6); _lab(a, 0.12, 0, "L+", fs=9)
    dot(a, x, 0)
    y = build(a, x, 0, [("NC", "S0", ES), ("NC", "S2", PB), ("NC", "F1", TH), ("PAR", [[("NO", "S1", PB)], [("NO", "KM1")]], 1.25), ("COIL", "KM1")])
    _l(a, [x, x], [y, y - 0.3]); _l(a, [0.2, 2.8], [y - 0.3, y - 0.3], lw=1.6); _lab(a, 0.12, y - 0.3, "M", fs=9); dot(a, x, y - 0.3)
    frame(a, (-0.4, 3.0), (y - 0.8, 0.6))
    a.set_title(T("（a）电路图：竖着画", "(a) circuit diagram: vertical"), fontsize=10.5)

    # (b) the same path as one rung of a ladder diagram, with the logic underneath
    y0 = 4.2
    _l(b, [0, 0], [y0 + 0.9, y0 - 1.6], lw=2); _l(b, [7.6, 7.6], [y0 + 0.9, y0 - 1.6], lw=2)
    xx = 0.0
    _l(b, [xx, xx + 0.3], [y0, y0]); xx += 0.3
    for nm in ("S0", "S2", "F1"):
        xx = ld_contact(b, xx, y0, nm, nc=True)
        _l(b, [xx, xx + 0.25], [y0, y0]); xx += 0.25
    xp = xx
    xx = ld_contact(b, xx, y0, "S1")
    ld_contact(b, xp, y0 - 1.0, "KM1")
    _l(b, [xp - 0.0, xp - 0.0], [y0, y0 - 1.0]); _l(b, [xx, xx], [y0, y0 - 1.0])
    dot(b, xp, y0); dot(b, xx, y0)
    _l(b, [xx, 6.6], [y0, y0])
    ld_coil(b, 6.6, y0, "KM1")
    b.text(3.8, y0 + 1.15, T("（b）同一条通路横过来：梯形图的一级（第 8 章）", "(b) the same path turned sideways: one rung of a ladder diagram (Ch. 8)"),
           ha="center", fontsize=10.5)
    # brackets: series = AND, parallel = OR, NC = NOT
    def brace(x0, x1, yb, text, color):
        _l(b, [x0, x0, x1, x1], [yb + 0.12, yb, yb, yb + 0.12], color=color, lw=1.0)
        b.text((x0 + x1) / 2, yb - 0.12, text, ha="center", va="top", fontsize=8.6, color=color)
    brace(0.3, xp - 0.25, y0 - 0.55, T("常闭触点串联：NOT … AND …", "NC contacts in series: NOT … AND …"), ACCENT)
    brace(xp, xx, y0 - 1.55, T("并联：OR", "parallel: OR"), GREEN)
    _box(b, 0.2, 0.15, 7.2, 1.25, "", fc=SOFT, ec=SOFT)
    b.text(3.8, 1.05, T("逻辑式（变量为 1 表示器件动作：按钮按下、热继电器脱扣、接触器吸合）", "logic (a variable is 1 when the device operates: button pressed, relay tripped, contactor closed)"), ha="center", fontsize=9, color=MUTED)
    b.text(3.8, 0.55, r"$\mathrm{KM1} = \overline{\mathrm{S0}}\cdot\overline{\mathrm{S2}}\cdot\overline{\mathrm{F1}}\cdot(\mathrm{S1} + \mathrm{KM1})$", ha="center", fontsize=13)
    frame(b, (-0.3, 7.9), (0.0, 5.6))
    return fig


figure(draw(), "fig2_5_1")
