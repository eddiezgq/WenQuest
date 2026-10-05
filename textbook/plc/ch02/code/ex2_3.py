"""图 2.3.1、2.3.2、2.3.4、2.3.6：经典继电器控制电路（点动与自锁；正反转；星三角启动；顺序启动与多地控制）。"""
from bookout import figure, style, T
from _draw02 import (control, frame, group, motor, phase_lines, rails3, _l, _lab, dot, P, MUTED, INK, ACCENT, coil, contact)

PB = {"act": "push"}
TH = {"act": "thermal"}


def jog_seal():
    """图 2.3.1：（a）点动；（b）自锁（长动）；（c）点动与自锁两用。"""
    plt = style()
    fig, axs = plt.subplots(1, 3, figsize=(11.5, 5.0), gridspec_kw={"width_ratios": [3.0, 3.6, 6.2]})
    a = [("NC", "F1", TH), ("NO", "S1", PB), ("COIL", "KM1")]
    b = [("NC", "F1", TH), ("NC", "S2", PB), ("PAR", [[("NO", "S1", PB)], [("NO", "KM1")]], 1.0), ("COIL", "KM1")]
    # (c) jog button S3 is a compound button: its NO contact starts the motor, its NC contact breaks the seal-in path
    c = [("NC", "F1", TH), ("NC", "S2", PB), ("PAR", [[("NO", "S1", PB), ("WIRE", "")], [("NO", "S3", PB), ("WIRE", "")], [("NC", "S3", PB), ("NO", "KM1")]], 1.9),
         ("COIL", "KM1")]
    for ax, cols, title, w in ((axs[0], [a], T("（a）点动", "(a) jog"), 2.4), (axs[1], [b], T("（b）自锁（长动）", "(b) seal-in"), 3.0),
                               (axs[2], [c], T("（c）点动与自锁两用", "(c) jog and run"), 5.6)):
        xs, bot = control(ax, cols, top=0, x0=0.0, numbers=False, xs=[1.25])
        frame(ax, (-0.6, w), (bot - 0.6, 0.6))
        ax.set_title(title, fontsize=10.5)
    return fig


def reversing():
    """图 2.3.2：电动机正反转。左：主电路（KM2 把 L1、L3 对调）；右：控制电路（按钮互锁 + 接触器互锁）。"""
    plt = style()
    fig, (am, ac) = plt.subplots(1, 2, figsize=(11, 6.6), gridspec_kw={"width_ratios": [1, 1.45]})
    x = 0.6
    rails3(am, x, 0)
    phase_lines(am, x, 0, -0.35)
    group(am, x, -0.35, "CB", "Q1")
    G = 1.55
    # split to KM1 (straight) and KM2 (L1 and L3 swapped)
    ys = [-1.6, -1.75, -1.9]
    for i in range(3):
        xi = x + i * P
        _l(am, [xi, xi], [-1.35, -2.3])
        _l(am, [xi, x + G + i * P], [ys[i], ys[i]])
        _l(am, [x + G + i * P, x + G + i * P], [ys[i], -2.3])
        dot(am, xi, ys[i])
    group(am, x, -2.3, "KM", "KM1")
    group(am, x + G, -2.3, "KM", "KM2", label_side=1)
    yb = [-3.75, -3.9, -4.05]
    for i in range(3):
        xi = x + i * P
        _l(am, [xi, xi], [-3.3, -4.4])
        j = 2 - i                       # KM2 pole i goes to motor lead 2 − i: L1 ↔ L3
        xg = x + G + i * P
        _l(am, [xg, xg], [-3.3, yb[j]])
        _l(am, [xg, x + j * P], [yb[j], yb[j]])
        dot(am, x + j * P, yb[j])
    group(am, x, -4.4, "OL", "F1")
    for i, n in enumerate(("U", "V", "W")):
        am.text(x + i * P + 0.06, -5.55, n, fontsize=7.4, color=MUTED, family="monospace")
    phase_lines(am, x, -5.4, -5.7)
    motor(am, x, -5.7, "M1")
    am.text(x + G + P, -4.55, T("KM2 把 L1、L3\n两相对调", "KM2 swaps\nL1 and L3"), ha="center", va="top", fontsize=8.2, color=MUTED)
    frame(am, (-0.9, 3.4), (-7.4, 0.5))
    am.set_title(T("主电路", "Main circuit"), fontsize=10.5)

    fwd = [("PAR", [[("NO", "S1", PB)], [("NO", "KM1")]], 1.2), ("NC", "S3", PB), ("NC", "KM2"), ("COIL", "KM1")]
    rev = [("PAR", [[("NO", "S3", PB)], [("NO", "KM2")]], 1.2), ("NC", "S1", PB), ("NC", "KM1"), ("COIL", "KM2")]
    cols = [[("NC", "F1", TH), ("NC", "S2", PB), ("PAR", [fwd, rev], 2.9)]]
    xs, bot = control(ac, cols, top=0, x0=0.0, numbers=False, xs=[1.3])
    ac.text(1.3, bot - 0.35, T("正转", "forward"), ha="center", va="top", fontsize=8.6, color=MUTED)
    ac.text(4.2, bot - 0.35, T("反转", "reverse"), ha="center", va="top", fontsize=8.6, color=MUTED)
    ac.annotate(T("按钮互锁", "button interlock"), xy=(1.55, -4.1), xytext=(2.0, -3.75), fontsize=8.2, color=ACCENT, va="center",
                arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.8))
    ac.annotate(T("接触器互锁\n（常闭辅助触点）", "contactor interlock\n(NC auxiliary contact)"), xy=(1.55, -5.1), xytext=(2.0, -5.3),
                fontsize=8.2, color=ACCENT, arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.8))
    frame(ac, (-0.9, 5.4), (bot - 0.9, 0.5))
    ac.set_title(T("控制电路", "Control circuit"), fontsize=10.5)
    return fig


def stardelta():
    """图 2.3.4：星三角启动。左：主电路；右：控制电路（KT1 为通电延时时间继电器）。"""
    plt = style()
    from matplotlib.patches import Rectangle
    fig, (am, ac) = plt.subplots(1, 2, figsize=(11.5, 7.0), gridspec_kw={"width_ratios": [4.9, 9.4]})
    x = 0.6
    rails3(am, x, 0)
    phase_lines(am, x, 0, -0.3)
    group(am, x, -0.3, "CB", "Q1")
    group(am, x, -1.3, "KM", "KM1")
    yt = [-2.45, -2.6, -2.75]          # taps for the delta connection (to U1, V1, W1)
    group(am, x, -2.9, "OL", "F1")
    for i in range(3):
        _l(am, [x + i * P] * 2, [-2.3, -2.9])
        dot(am, x + i * P, yt[i])
    # motor: three windings U1–U2, V1–V2, W1–W2
    wy0, wy1 = -4.2, -5.4
    for i, (a, b) in enumerate((("U1", "U2"), ("V1", "V2"), ("W1", "W2"))):
        xi = x + i * P
        _l(am, [xi, xi], [-3.9, wy0])
        am.add_patch(Rectangle((xi - 0.08, wy1 + 0.15), 0.16, wy0 - wy1 - 0.3, fc="white", ec=INK, lw=1.2, zorder=3))
        am.text(xi + 0.1, wy0 - 0.05, a, fontsize=6.8, family="monospace", color=MUTED, va="top")
        am.text(xi + 0.1, wy1 + 0.1, b, fontsize=6.8, family="monospace", color=MUTED, va="bottom")
        _l(am, [xi, xi], [wy1 + 0.15, wy1])
        _l(am, [xi, xi], [wy0, wy0 - 0.15])
    am.add_patch(Rectangle((x - 0.3, wy1 - 0.05), 2 * P + 0.6, wy0 - wy1 + 0.1, fill=False, ec=MUTED, lw=0.8, ls=(0, (3, 2))))
    am.text(x - 0.38, (wy0 + wy1) / 2, "M1\n3~", ha="right", va="center", fontsize=8.4)
    # star contactor KM2 under U2 V2 W2, its lower ends joined (the star point)
    for i in range(3):
        _l(am, [x + i * P] * 2, [wy1, -5.8])
    group(am, x, -5.8, "KM", "KM2")
    _l(am, [x, x + 2 * P], [-6.8, -6.8])
    am.text(x + P, -6.95, T("星点", "star point"), ha="center", va="top", fontsize=7.8, color=MUTED)
    # delta contactor KM3: U2 → V1, V2 → W1, W2 → U1
    G = 1.45
    yd = [-5.55, -5.65, -5.75]
    for i in range(3):
        xi, xg = x + i * P, x + G + i * P
        _l(am, [xi, xg], [yd[i], yd[i]]); dot(am, xi, yd[i])
        _l(am, [xg, xg], [yd[i], -5.8])
    group(am, x + G, -5.8, "KM", "KM3", label_side=1)
    xr = x + G + 2 * P + 0.75
    for i in range(3):
        xg = x + G + i * P
        to = (i + 1) % 3                  # U2 → V1 line, V2 → W1, W2 → U1
        yb = -6.95 - 0.12 * i
        xo = xr + 0.15 * i
        _l(am, [xg, xg, xo, xo, x + to * P], [-6.8, yb, yb, yt[to], yt[to]])
    am.text(x + G + P, -7.4, T("KM3 接成三角形", "KM3 makes the delta"), ha="center", va="top", fontsize=8, color=MUTED)
    frame(am, (-0.9, 4.0), (-7.8, 0.5))
    am.set_title(T("主电路", "Main circuit"), fontsize=10.5)

    star = [("NC", "KT1", {"delay": "on"}), ("NC", "KM3"), ("COIL", "KM2")]
    timer = [("NC", "KM3"), ("COIL", "KT1", {"kind": "on"})]
    delta = [("PAR", [[("NO", "KT1", {"delay": "on"})], [("NO", "KM3")]], 1.35), ("NC", "KM2"), ("COIL", "KM3")]
    cols = [[("NC", "F1", TH), ("NC", "S2", PB), ("PAR", [[("PAR", [[("NO", "S1", PB)], [("NO", "KM1")]], 0.95), ("COIL", "KM1")]], 1.0),
            ]]
    # the main path and the three timed paths hang from the node after S1 / KM1
    from _draw02 import build
    top = 0.0
    xl = 0.0
    _l(ac, [xl, 8.4], [top, top], lw=1.6)
    _lab(ac, xl - 0.08, top, "L+", fs=9)
    xA = 1.2
    dot(ac, xA, top)
    y = build(ac, xA, top, [("NC", "F1", TH), ("NC", "S2", PB), ("PAR", [[("NO", "S1", PB)], [("NO", "KM1")]], 0.95)])
    node = y
    xs = [xA, xA + 1.9, xA + 3.6, xA + 5.3]
    _l(ac, [xA, xs[-1]], [node, node])
    for xx in xs[1:]:
        dot(ac, xx, node)
    ends = [build(ac, xs[0], node, [("WIRE", ""), ("WIRE", ""), ("COIL", "KM1")]), build(ac, xs[1], node, star),
            build(ac, xs[2], node, timer), build(ac, xs[3], node, delta)]
    bot = min(ends) - 0.3
    for xx, ye in zip(xs, ends):
        _l(ac, [xx, xx], [ye, bot]); dot(ac, xx, bot)
    _l(ac, [xl, 8.4], [bot, bot], lw=1.6)
    _lab(ac, xl - 0.08, bot, "M", fs=9)
    for xx, n in zip(xs, (T("主", "main"), T("星形", "star"), T("计时", "timer"), T("三角形", "delta"))):
        ac.text(xx, bot - 0.3, n, ha="center", va="top", fontsize=8.4, color=MUTED)
    frame(ac, (-0.8, 8.6), (bot - 0.8, 0.5))
    ac.set_title(T("控制电路", "Control circuit"), fontsize=10.5)
    return fig


def sequence_multi():
    """图 2.3.6：（a）顺序启动：M1 运转后 M2 才能启动；（b）两地控制：两处的停止按钮串联、启动按钮并联。"""
    plt = style()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 5.8))
    m1 = [("NC", "S2", PB), ("PAR", [[("NO", "S1", PB)], [("NO", "KM1")]], 0.95), ("NC", "F1", TH), ("COIL", "KM1")]
    m2 = [("NC", "S4", PB), ("PAR", [[("NO", "S3", PB)], [("NO", "KM2")]], 0.95), ("NO", "KM1"), ("NC", "F2", TH), ("COIL", "KM2")]
    xs, bot = control(a1, [m1, m2], top=0, x0=0.0, numbers=False, xs=[1.2, 3.6])
    a1.text(1.2, bot - 0.3, "M1", ha="center", va="top", fontsize=8.6, color=MUTED)
    a1.text(3.6, bot - 0.3, "M2", ha="center", va="top", fontsize=8.6, color=MUTED)
    a1.annotate(T("KM1 的常开辅助触点：\nM1 不转，M2 起不来", "KM1 NO auxiliary:\nno M2 without M1"), xy=(3.45, -3.9), xytext=(4.8, -2.6),
                fontsize=8.2, color=ACCENT, arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.8))
    frame(a1, (-0.7, 7.0), (bot - 0.8, 0.5))
    a1.set_title(T("（a）顺序启动", "(a) sequential start"), fontsize=10.5)
    two = [("NC", "F1", TH), ("NC", "S2A", PB), ("NC", "S2B", PB), ("PAR", [[("NO", "S1A", PB)], [("NO", "S1B", PB)], [("NO", "KM1")]], 1.9),
           ("COIL", "KM1")]
    xs, bot = control(a2, [two], top=0, x0=0.0, numbers=False, xs=[1.4])
    a2.annotate(T("停止按钮串联：\n哪一处按都停", "stops in series:\neither one stops"), xy=(1.55, -2.5), xytext=(3.6, -1.6),
                fontsize=8.2, color=ACCENT, arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.8))
    a2.annotate(T("启动按钮并联：\n哪一处按都启动", "starts in parallel:\neither one starts"), xy=(3.4, -4.0), xytext=(5.2, -5.0),
                fontsize=8.2, color=ACCENT, arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.8))
    frame(a2, (-0.7, 7.4), (bot - 0.8, 0.5))
    a2.set_title(T("（b）两地控制", "(b) control from two places"), fontsize=10.5)
    return fig


figure(jog_seal(), "fig2_3_1")
figure(reversing(), "fig2_3_2")
figure(stardelta(), "fig2_3_4")
figure(sequence_multi(), "fig2_3_6")
