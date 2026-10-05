"""图 3.1.1（模块式 PLC 的组成与背板总线），图 3.2.1（一体式、模块式与分布式 I/O 三种结构）。"""
from bookout import figure, T, style
from _draw03 import _box, _l, frame, INK, MUTED, ACCENT, GREEN, WARM, SOFT, LINE


def modules():
    plt = style()
    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    _l(ax, [0.0, 10.4], [0.5, 0.5], color=MUTED, lw=6)                  # DIN rail
    ax.text(10.45, 0.5, T("导轨", "DIN rail"), va="center", fontsize=8.5, color=MUTED)
    mods = [("PS", T("电源\n24 V DC", "power\n24 V DC"), 1.1, "#e8eef5"), ("CPU", T("CPU\n存储器", "CPU\nmemory"), 1.6, "#dbe7f4"),
            ("DI", T("数字量\n输入 16", "digital\ninputs 16"), 1.1, "#e7f3e9"), ("DO", T("数字量\n输出 16", "digital\noutputs 16"), 1.1, "#fbeedd"),
            ("AI", T("模拟量\n输入 4", "analog\ninputs 4"), 1.1, "#e7f3e9"), ("AQ", T("模拟量\n输出 2", "analog\noutputs 2"), 1.1, "#fbeedd"),
            ("CP", T("通信\n模块", "comm.\nmodule"), 1.1, "#efe9f6")]
    x = 0.3
    xs = []
    for name, sub, w, c in mods:
        _box(ax, x, 0.8, w, 2.9, "", fc=c, ec=INK)
        ax.text(x + w / 2, 3.35, name, ha="center", fontsize=10.5, fontweight="bold", family="monospace")
        ax.text(x + w / 2, 2.5, sub, ha="center", va="center", fontsize=8.4, linespacing=1.2)
        for k in range(6 if name in ("DI", "DO") else 3):                  # terminals
            ax.add_patch(__import__("matplotlib").patches.Circle((x + 0.25 + (k % 3) * 0.3, 1.25 + (k // 3) * 0.32), 0.07, fc="white", ec=MUTED, lw=0.8, zorder=5))
        xs.append((x, w))
        x += w + 0.12
    xb0, xb1 = xs[0][0] + 0.2, xs[-1][0] + xs[-1][1] - 0.2
    _l(ax, [xb0, xb1], [0.95, 0.95], color=ACCENT, lw=3)
    ax.text((xb0 + xb1) / 2, 0.15, T("背板总线：CPU 经它读写各模块，电源经它给模块的电子电路供电", "backplane bus: the CPU reads and writes every module through it; it also powers their electronics"),
            ha="center", fontsize=8.6, color=ACCENT)
    ax.text(xs[2][0] + xs[2][1] / 2, 4.05, T("按钮、传感器", "sensors"), ha="center", fontsize=8.0, color=GREEN)
    ax.text(xs[3][0] + xs[3][1] / 2, 4.3, T("接触器、阀、灯", "contactors, valves"), ha="center", fontsize=8.0, color=WARM)
    ax.text(xs[6][0] + xs[6][1] / 2, 4.05, T("网络", "network"), ha="center", fontsize=8.4, color="#7a5ea8")
    frame(ax, (-0.2, 11.4), (-0.1, 4.6))
    ax.set_aspect("auto")
    return fig


def architectures():
    plt = style()
    fig, axs = plt.subplots(1, 3, figsize=(11.5, 4.2))
    a, b, c = axs
    # (a) compact
    _box(a, 0.8, 1.2, 3.4, 2.2, "", fc="#dbe7f4")
    a.text(2.5, 2.9, T("一体式 PLC", "compact PLC"), ha="center", fontsize=9.5, fontweight="bold")
    a.text(2.5, 2.2, T("电源、CPU、14 入 10 出\n装在一个外壳里", "power, CPU, 14 in / 10 out\nin one housing"), ha="center", va="center", fontsize=8.4)
    _box(a, 4.4, 1.2, 0.8, 2.2, T("扩\n展", "ex-\npan."), fc="#e7f3e9", fs=8.4)
    a.text(2.9, 0.6, T("小型设备：几十到几百点", "small machines: up to a few hundred points"), ha="center", fontsize=8.2, color=MUTED)
    frame(a, (0.4, 5.6), (0.2, 4.0)); a.set_aspect("auto")
    a.set_title(T("（a）一体式", "(a) compact"), fontsize=10)
    # (b) modular, central
    x = 0.4
    for nm, c0 in (("PS", "#e8eef5"), ("CPU", "#dbe7f4"), ("DI", "#e7f3e9"), ("DI", "#e7f3e9"), ("DO", "#fbeedd"), ("DO", "#fbeedd"), ("AI", "#e7f3e9"), ("CP", "#efe9f6")):
        _box(b, x, 1.2, 0.6, 2.2, nm, fc=c0, fs=7.8)
        x += 0.66
    b.text(3.0, 0.6, T("中大型设备：模块按需组合", "larger machines: modules as needed"), ha="center", fontsize=8.2, color=MUTED)
    frame(b, (0.2, 5.8), (0.2, 4.0)); b.set_aspect("auto")
    b.set_title(T("（b）模块式", "(b) modular"), fontsize=10)
    # (c) distributed I/O
    _box(c, 0.3, 2.6, 1.6, 1.0, T("控制柜\nCPU", "cabinet\nCPU"), fc="#dbe7f4", fs=8.4)
    _l(c, [1.9, 5.6], [3.1, 3.1], color=ACCENT, lw=2)
    c.text(3.7, 3.25, T("现场总线 / 工业以太网", "fieldbus / industrial Ethernet"), ha="center", fontsize=8.2, color=ACCENT)
    for k, x0 in enumerate((2.2, 3.4, 4.6)):
        _l(c, [x0 + 0.45, x0 + 0.45], [3.1, 2.3], color=ACCENT, lw=1.5)
        _box(c, x0, 1.3, 0.9, 1.0, T("远程\nI/O", "remote\nI/O"), fc="#e7f3e9", fs=8)
        for j in range(3):
            _l(c, [x0 + 0.2 + j * 0.25, x0 + 0.2 + j * 0.25], [1.3, 0.9], color=MUTED, lw=0.8)
    c.text(3.4, 0.5, T("I/O 装在设备旁边，到传感器的导线变短", "I/O next to the machine; short sensor cables"), ha="center", fontsize=8.2, color=MUTED)
    frame(c, (0.1, 5.8), (0.2, 4.0)); c.set_aspect("auto")
    c.set_title(T("（c）分布式 I/O", "(c) distributed I/O"), fontsize=10)
    return fig


figure(modules(), "fig3_1_1")
figure(architectures(), "fig3_2_1")
