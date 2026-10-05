"""第 1 章的画图工具（中英两版，文字一律写成 T(中文, English)）。"""
from bookout import T, style

INK = "#1d2327"
MUTED = "#7a868d"
ACCENT = "#3a7dc9"
WARM = "#d98c3a"
RED = "#b5443b"
GREEN = "#2f8f5b"
SOFT = "#eef2f6"
LINE = "#c9d2d8"


def fam(text):
    """Signal names in a monospace font; anything with Chinese in the book's sans font (the monospace font has no Chinese)."""
    return "monospace" if all(ord(c) < 0x2E80 for c in text) else None


def _box(ax, x, y, w, h, text="", fc="white", ec=INK, fs=10, lw=1.2, color=None, r=0.08, weight=None, va="center"):
    from matplotlib.patches import FancyBboxPatch
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.0,rounding_size={r}", fc=fc, ec=ec, lw=lw, zorder=2))
    if text:
        ax.text(x + w / 2, y + h / 2 if va == "center" else y + h - 0.12, text, ha="center", va=va, fontsize=fs,
                color=color or ec, zorder=3, family=fam(text), fontweight=weight)


def _arrow(ax, a, b, color=INK, lw=1.2, style="-|>", ls="-"):
    from matplotlib.patches import FancyArrowPatch
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=11, lw=lw, color=color, linestyle=ls, zorder=1))


def timing(trace, rows, t0=0.0, t1=None, size=(9, 4.6), marks=()):
    """rows: [(signal, label)] (Boolean signals); marks: [(t_ms, text)] vertical dashed lines."""
    plt = style()
    t = [x / 1000 for x in trace["t"]]
    t1 = t1 if t1 is not None else t[-1]
    fig, ax = plt.subplots(figsize=size)
    n = len(rows)
    for i, (sig, label) in enumerate(rows):
        y0 = (n - 1 - i) * 1.25
        v = trace["v"][trace["names"].index(sig)]
        ys = [y0 + (0.8 if x else 0) for x in v]
        ax.step(t, ys, where="post", color=ACCENT if label.startswith(("KM", "H")) else GREEN, lw=1.5)
        ax.text(t0 - 0.02 * (t1 - t0), y0 + 0.35, label, ha="right", va="center", fontsize=9.5, family=fam(label), color=INK)
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


def cabinets():
    """图 1.1.1：同一条输送线，继电器控制与 PLC 控制。左：控制电路由触点、线圈、时间继电器连成，逻辑就是接线；
    右：按钮、开关接到 PLC 的输入，接触器和指示灯接到输出，逻辑在程序里。"""
    plt = style()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 5.2))
    for ax in (a1, a2):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        ax.axis("off")
    # ---- relay: two rails and three rungs of contacts and coils
    a1.set_title(T("继电器控制：逻辑在接线里", "Relay control: the logic is in the wiring"), fontsize=11.5)
    a1.plot([0.6, 0.6], [0.6, 7.2], color=INK, lw=2)
    a1.plot([9.4, 9.4], [0.6, 7.2], color=INK, lw=2)
    a1.text(0.6, 7.45, "L", ha="center", fontsize=10)
    a1.text(9.4, 7.45, "N", ha="center", fontsize=10)

    def contact(ax, x, y, name, nc=False, below=False):
        ax.plot([x, x + 0.25], [y, y], color=INK, lw=1.2)
        ax.plot([x + 0.25, x + 0.25], [y - 0.22, y + 0.22], color=INK, lw=1.2)
        ax.plot([x + 0.55, x + 0.55], [y - 0.22, y + 0.22], color=INK, lw=1.2)
        if nc:
            ax.plot([x + 0.18, x + 0.62], [y - 0.28, y + 0.28], color=INK, lw=1.0)
        ax.plot([x + 0.55, x + 0.8], [y, y], color=INK, lw=1.2)
        if below:
            ax.text(x + 0.4, y - 0.42, name, ha="center", va="top", fontsize=8.0, family="monospace")
        else:
            ax.text(x + 0.4, y + 0.38, name, ha="center", fontsize=8.5, family="monospace")
        return x + 0.8

    def coil(ax, x, y, name):
        from matplotlib.patches import Circle
        ax.add_patch(Circle((x + 0.3, y), 0.28, fc="white", ec=INK, lw=1.2, zorder=3))
        ax.text(x + 0.3, y + 0.45, name, ha="center", fontsize=8.5, family="monospace")
        return x + 0.6

    rungs = [(6.6, [("S0", 1), ("S2", 1), ("F1", 1), ("S1", 0), ("B2", 1), ("KA2", 1)], "KM1"),
             (5.35, [("KM1", 0), ("B2", 1)], "KT1"),
             (4.1, [("KT1", 0), ("S1", 1)], "KA2"),
             (2.2, [("KM1", 0)], "H1"),
             (1.2, [("KA2", 0)], "H2")]
    for y, cs, out in rungs:
        x = 0.6
        for name, nc in cs:
            a1.plot([x, x + 0.3], [y, y], color=INK, lw=1.2)
            x = contact(a1, x + 0.3, y, name, nc)
        a1.plot([x, 8.2], [y, y], color=INK, lw=1.2)
        xe = coil(a1, 8.2, y, out)
        a1.plot([xe, 9.4], [y, y], color=INK, lw=1.2)
    # seal-in branch around S1 (KM1 auxiliary contact) and around KT1 for KA2
    for (y, k, name) in ((6.6, 3, "KM1"), (4.1, 0, "KA2"), (1.2, 0, "F1")):          # around the k-th contact of the rung
        x0, x1 = 0.6 + k * 1.1 + 0.15, 0.6 + (k + 1) * 1.1 + 0.15
        a1.plot([x0, x0], [y, y - 0.6], color=INK, lw=1.2)
        a1.plot([x1, x1], [y, y - 0.6], color=INK, lw=1.2)
        a1.plot([x0, x0 + 0.15], [y - 0.6, y - 0.6], color=INK, lw=1.2)
        contact(a1, x0 + 0.15, y - 0.6, name, below=True)
        a1.plot([x0 + 0.95, x1], [y - 0.6, y - 0.6], color=INK, lw=1.2)
    a1.set_ylim(-0.7, 8)
    a1.text(5, -0.5, T("每个“与”是串联、每个“或”是并联、每个“记住”是一个继电器；改逻辑就要改接线",
                       "every AND is a series path, every OR a parallel one, every 'remember' a relay; changing the logic means rewiring"),
            ha="center", fontsize=8.6, color=MUTED, wrap=True)
    # ---- PLC: inputs on the left, outputs on the right, the program in the middle
    a2.set_title(T("PLC 控制：逻辑在程序里", "PLC control: the logic is in the program"), fontsize=11.5)
    _box(a2, 2.6, 1.0, 4.8, 6.0, "", fc=SOFT, ec=INK)
    a2.text(5.0, 6.6, "PLC", ha="center", fontsize=12, fontweight="bold")
    ins = ["S1_Start", "S2_Stop", "S0_EStop", "F1_Overload", "B1_Entry", "B2_End"]
    outs = ["KM1_Run", "H1_Run", "H2_Fault"]
    for i, n in enumerate(ins):
        y = 6.0 - i * 0.82
        a2.text(0.15, y, n, fontsize=8.5, va="center", family="monospace")
        a2.plot([1.75, 2.6], [y, y], color=GREEN, lw=1.3)
        a2.text(2.75, y, "%IX0." + str(i), fontsize=7.8, va="center", color=MUTED, family="monospace")
    for i, n in enumerate(outs):
        y = 5.4 - i * 1.2
        a2.plot([7.4, 8.1], [y, y], color=ACCENT, lw=1.3)
        a2.text(7.25, y, "%QX0." + str(i), fontsize=7.8, va="center", ha="right", color=MUTED, family="monospace")
        a2.text(8.2, y, n, fontsize=8.5, va="center", family="monospace")
    _box(a2, 3.7, 2.0, 2.65, 3.3, "", fc="white", ec=MUTED, lw=1.0)
    prog = "KM1_Run :=\n (S1_Start OR KM1_Run)\n AND S2_Stop\n AND S0_EStop\n AND F1_Overload\n AND NOT B2_End\n AND NOT jammed;"
    a2.text(3.8, 5.15, prog, fontsize=7.2, va="top", family="monospace")
    a2.text(5.0, 0.15, T("接线只有“谁接到哪个端子”；改逻辑只要改程序、下载",
                         "the wiring only says which device goes to which terminal; changing the logic means editing and downloading"),
            ha="center", fontsize=8.6, color=MUTED)
    fig.tight_layout()
    return fig


def timeline(events):
    """图 1.2.1：PLC 发展大事记。events: [(year, zh, en, lane, level)] lane 0 上、1 下；level 0/1/2 标签离轴的远近（错开相邻的标签）"""
    plt = style()
    fig, ax = plt.subplots(figsize=(12, 4.8))
    y0, y1 = min(e[0] for e in events) - 3, max(e[0] for e in events) + 4
    ax.plot([y0, y1], [0, 0], color=INK, lw=1.6)
    for yr in range((y0 // 10 + 1) * 10, y1 + 1, 10):
        ax.plot([yr, yr], [-0.08, 0.08], color=INK, lw=1)
        ax.text(yr, -0.32, str(yr), ha="center", fontsize=9, color=MUTED)
    for yr, zh, en, lane, level in events:
        up = lane == 0
        h = (1 if up else -1) * (0.75 + 1.05 * level)
        ax.plot([yr, yr], [0, h], color=LINE, lw=1)
        ax.plot([yr], [0], "o", color=ACCENT if up else WARM, ms=5, zorder=3)
        ax.text(yr, h + (0.06 if up else -0.06), f"{yr}\n" + T(zh, en), ha="center", va="bottom" if up else "top", fontsize=8.2,
                color=INK, linespacing=1.12)
    ax.set_xlim(y0, y1)
    ax.set_ylim(-4.6, 4.4)
    ax.axis("off")
    ax.text(y0, 4.2, T("上：控制器与产品", "above: controllers and products"), fontsize=8.6, color=ACCENT)
    ax.text(y0, -4.5, T("下：标准与组织", "below: standards and bodies"), fontsize=8.6, color=WARM)
    return fig


def structure():
    """图 1.3.1：PLC 的组成与扫描周期。左：电源、CPU 与存储器、输入模块、输出模块、通信接口；右：一个扫描周期的三步。"""
    plt = style()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.8), gridspec_kw={"width_ratios": [1.25, 1]})
    for ax in (a1, a2):
        ax.axis("off")
    a1.set_xlim(0, 10)
    a1.set_ylim(0, 7)
    _box(a1, 0.2, 5.2, 9.6, 1.4, "", fc=SOFT)
    mods = [(T("电源", "Power\nsupply"), 1.2), (T("CPU\n与存储器", "CPU and\nmemory"), 1.6), (T("数字量\n输入", "Digital\ninputs"), 1.3),
            (T("数字量\n输出", "Digital\noutputs"), 1.3), (T("模拟量\n输入输出", "Analog\nI/O"), 1.3), (T("通信", "Comms"), 1.2)]
    x = 0.45
    xs = {}
    for name, w in mods:
        _box(a1, x, 5.35, w, 1.1, name, fc="white", fs=8.8)
        xs[name] = x + w / 2
        x += w + 0.12
    a1.text(5, 6.85, T("一台模块式 PLC（装在控制柜的导轨上）", "A modular PLC (on a DIN rail in the cabinet)"), ha="center", fontsize=9.5, color=MUTED)
    names = [m[0] for m in mods]
    dev_in = [(T("按钮", "buttons"), 0.9), (T("光电开关", "photo sensors"), 2.15), (T("限位开关", "limit switches"), 3.4)]
    for t, xx in dev_in:
        _box(a1, xx - 0.58, 2.3, 1.16, 0.7, t, fc="#e9f5ee", ec=GREEN, fs=8.2)
        _arrow(a1, (xx, 3.0), (xs[names[2]], 5.3), color=GREEN)
    dev_out = [(T("接触器", "contactors"), 4.75), (T("电磁阀", "solenoid valves"), 6.0), (T("指示灯", "lamps"), 7.25)]
    for t, xx in dev_out:
        _box(a1, xx - 0.58, 2.3, 1.16, 0.7, t, fc="#e8f1fb", ec=ACCENT, fs=8.2)
        _arrow(a1, (xs[names[3]], 5.3), (xx, 3.0), color=ACCENT)
    _box(a1, 8.4, 3.4, 1.5, 0.8, T("编程电脑\n/ HMI", "PC / HMI"), fc="white", ec=MUTED, fs=8.4)
    _arrow(a1, (xs[names[5]], 5.3), (9.15, 4.2), color=MUTED, style="<|-|>")
    a1.text(2.15, 1.7, T("现场的输入设备", "field inputs"), ha="center", fontsize=8.8, color=GREEN)
    a1.text(6.0, 1.7, T("现场的执行元件", "field actuators"), ha="center", fontsize=8.8, color=ACCENT)
    # scan cycle
    import math
    a2.set_xlim(-3, 3)
    a2.set_ylim(-3, 3)
    a2.set_aspect("equal")
    steps = [(T("① 读输入\n（输入映像）", "① read inputs\n(input image)"), 90), (T("② 执行程序\n（从头到尾一遍）", "② run the program\n(top to bottom)"), -30),
             (T("③ 写输出\n（输出映像）", "③ write outputs\n(output image)"), 210)]
    for text, ang in steps:
        x, y = 1.75 * math.cos(math.radians(ang)), 1.75 * math.sin(math.radians(ang))
        _box(a2, x - 0.95, y - 0.45, 1.9, 0.9, text, fc="white", fs=8.6)
    R = 1.75
    for a, b in ((65, -5), (-55, -125), (185, 115)):            # clockwise arcs between the three steps
        import numpy as np
        th = np.radians(np.linspace(a, b, 40))
        xs_, ys_ = R * np.cos(th) * 1.32, R * np.sin(th) * 1.32
        a2.plot(xs_[:-1], ys_[:-1], color=MUTED, lw=1.2)
        _arrow(a2, (xs_[-3], ys_[-3]), (xs_[-1], ys_[-1]), color=MUTED)
    a2.text(0, 0.05, T("扫描周期\n周而复始", "the scan cycle,\nover and over"), ha="center", va="center", fontsize=9.5, color=INK)
    fig.tight_layout()
    return fig


def pyramid(levels):
    """图 1.4.1：自动化金字塔与 ISA-95 分层。levels: [(层号, 中文名, 英文名, 中文例子, 英文例子, 时间尺度)] 从下到上"""
    plt = style()
    from matplotlib.patches import Polygon
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    n = len(levels)
    for i, (lv, zh, en, ezh, een, scale) in enumerate(levels):
        y0, y1 = i, i + 1
        w0, w1 = 5 * (1 - i / (n + 0.6)), 5 * (1 - (i + 1) / (n + 0.6))
        fc = ["#e9f5ee", "#e8f1fb", "#eef2f6", "#fdf3e6", "#fbeceb"][i % 5]
        ax.add_patch(Polygon([(-w0, y0), (w0, y0), (w1, y1), (-w1, y1)], closed=True, fc=fc, ec=INK, lw=1.0))
        ax.text(0, i + 0.5, T(zh, en), ha="center", va="center", fontsize=10, fontweight="bold" if "PLC" in zh else None)
        ax.text(5.4, i + 0.62, f"ISA-95 {lv}", fontsize=8.5, color=MUTED, va="center")
        ax.text(5.4, i + 0.32, T(ezh, een), fontsize=8.6, va="center", color=INK)
        ax.text(-5.4, i + 0.5, scale, fontsize=8.5, va="center", ha="right", color=MUTED)
    ax.text(-5.4, n + 0.15, T("时间尺度", "time scale"), ha="right", fontsize=8.8, color=MUTED)
    ax.text(5.4, n + 0.15, T("问渠数字工厂里对应的部分", "in the WenQuest digital factory"), fontsize=8.8, color=MUTED)
    ax.set_xlim(-8.5, 11.5)
    ax.set_ylim(-0.2, n + 0.5)
    ax.axis("off")
    return fig


def lifecycle(phases):
    """图 1.6.1：一个自动化项目的过程。phases: [(中文, 英文, 交付物中文, 交付物英文, 行)]，按 V 形排：左边设计，右边验证"""
    plt = style()
    fig, ax = plt.subplots(figsize=(11, 5.0))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6)
    ax.axis("off")
    pos = {}
    for i, (zh, en, dzh, den, side, row) in enumerate(phases):
        x = {"L": 0.3 + row * 1.35, "R": 10.7 - row * 1.35 - 2.3, "B": 4.35}[side]
        y = 4.9 - row * 1.25 if side != "B" else 0.3
        _box(ax, x, y, 2.3, 0.85, "", fc="white" if side != "B" else SOFT)
        ax.text(x + 1.15, y + 0.58, T(zh, en), ha="center", fontsize=9.5, fontweight="bold")
        ax.text(x + 1.15, y + 0.22, T(dzh, den), ha="center", fontsize=7.8, color=MUTED)
        pos[i] = (x, y)
    order = sorted([i for i, p in enumerate(phases) if p[4] == "L"], key=lambda i: phases[i][5]) + \
        [i for i, p in enumerate(phases) if p[4] == "B"] + sorted([i for i, p in enumerate(phases) if p[4] == "R"], key=lambda i: -phases[i][5])
    for a, b in zip(order, order[1:]):
        (xa, ya), (xb, yb) = pos[a], pos[b]
        _arrow(ax, (xa + 1.15 + (0.6 if xb > xa else -0.6), ya + (0 if yb < ya else 0.85)), (xb + 1.15 + (-0.6 if xb > xa else 0.6), yb + (0.85 if yb < ya else 0)), color=MUTED)
    # verification pairs (dashed): each test checks the matching design document
    L = sorted([i for i, p in enumerate(phases) if p[4] == "L"], key=lambda i: phases[i][5])
    R = sorted([i for i, p in enumerate(phases) if p[4] == "R"], key=lambda i: phases[i][5])
    for a, b in zip(L, R):
        (xa, ya), (xb, yb) = pos[a], pos[b]
        ax.plot([xa + 2.3, xb], [ya + 0.42, yb + 0.42], color=ACCENT, lw=0.9, ls=(0, (4, 3)))
    ax.text(5.5, 5.75, T("虚线：右边的每一次测试和验收，检验左边对应的那份设计文件", "dashed: each test on the right checks the design document opposite"),
            ha="center", fontsize=8.8, color=ACCENT)
    return fig
