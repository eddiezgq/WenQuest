"""图 3.3.1（三线制传感器与 PLC 数字量输入的四种组合，电流的流向），图 3.3.2（两线制与三线制传感器的接法）。

本书按电流方向区分输入：电流流入输入端子的（公共端接 M，配 PNP 传感器），电流从输入端子流出的（公共端接 L+，配 NPN 传感器）。
IEC 61131-2 和西门子把前者叫“漏型”（current sinking），三菱把前者叫“源型”，叫法正好相反（3.3.2 节）。"""
from bookout import figure, T, style
from _draw03 import _box, _l, _lab, frame, dot, INK, MUTED, ACCENT, GREEN, WARM, RED, SOFT


def arrow(ax, pts, color=RED):
    from matplotlib.patches import FancyArrowPatch
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=10, lw=1.6, color=color, zorder=6,
                                     shrinkA=0, shrinkB=0))


def diode_h(ax, x0, x1, y, forward=True):
    """an LED of the input optocoupler, horizontal, anode left if forward"""
    xm = (x0 + x1) / 2
    _l(ax, [x0, xm - 0.15], [y, y]); _l(ax, [xm + 0.15, x1], [y, y])
    a, k = (xm - 0.15, xm + 0.15) if forward else (xm + 0.15, xm - 0.15)
    ax.fill([a, a, k], [y - 0.15, y + 0.15, y], fc="white", ec=INK, lw=1.2, zorder=3)
    _l(ax, [k, k], [y - 0.15, y + 0.15], lw=1.4, z=4)


def panel(ax, pnp, into, title):
    """pnp: sensor type; into: input built for current flowing into its terminal (common to M)."""
    L, M = 4.0, 0.0
    _l(ax, [0, 7.2], [L, L], lw=1.6); _l(ax, [0, 7.2], [M, M], lw=1.6)
    _lab(ax, -0.08, L, "L+", fs=9); _lab(ax, -0.08, M, "M", fs=9)
    # sensor: brown to L+, blue to M, black = output; inside, the output transistor drawn as a switch
    _box(ax, 0.6, 1.2, 1.6, 1.6, "", fc=SOFT, ec=MUTED)
    ax.text(1.4, 3.05, T("PNP 传感器（已动作）", "PNP sensor (on)") if pnp else T("NPN 传感器（已动作）", "NPN sensor (on)"), ha="center", fontsize=8.4)
    _l(ax, [1.0, 1.0], [L, 2.8], color="#8a5a2b"); _l(ax, [1.0, 1.0], [1.2, M], color="#2f6db5")
    ax.text(0.92, 3.4, T("棕", "BN"), ha="right", fontsize=7, color="#8a5a2b"); ax.text(0.92, 0.6, T("蓝", "BU"), ha="right", fontsize=7, color="#2f6db5")
    # output switch: PNP between L+ (brown) and output; NPN between output and M (blue)
    if pnp:
        _l(ax, [1.0, 1.7], [2.6, 2.6]); _l(ax, [1.7, 1.95], [2.6, 2.15], lw=1.4); _l(ax, [1.95, 1.95], [2.0, 2.0])
        yo = 2.0
    else:
        _l(ax, [1.0, 1.7], [1.4, 1.4]); _l(ax, [1.7, 1.95], [1.4, 2.0], lw=1.4)
        yo = 2.0
    _l(ax, [1.95, 1.95], [yo, 2.0]); _l(ax, [1.95, 3.4], [2.0, 2.0])
    ax.text(2.6, 2.1, T("黑", "BK"), ha="center", fontsize=7, color=INK)
    # PLC input: terminal I0.0 → resistor → LED → common
    _box(ax, 3.4, 1.2, 3.2, 1.6, "", fc="#eef4fb", ec=MUTED)
    ax.text(5.0, 3.05, T("PLC 输入", "PLC input"), ha="center", fontsize=8.6)
    dot(ax, 3.4, 2.0); ax.text(3.45, 2.2, "I0.0", fontsize=7.6, family="monospace")
    ax.add_patch(__import__("matplotlib").patches.Rectangle((3.75, 1.88), 0.6, 0.24, fc="white", ec=INK, lw=1.1, zorder=3))
    _l(ax, [3.4, 3.75], [2.0, 2.0]); _l(ax, [4.35, 4.7], [2.0, 2.0])
    diode_h(ax, 4.7, 5.8, 2.0, forward=into)
    _l(ax, [5.8, 6.6], [2.0, 2.0]); dot(ax, 6.6, 2.0)
    ax.text(6.55, 2.2, T("公共端", "COM"), fontsize=7.6, ha="right")
    _l(ax, [6.6, 6.9, 6.9], [2.0, 2.0, M if into else L])
    ok = (pnp and into) or (not pnp and not into)
    if ok:
        if into:   # L+ → brown → switch → black → I0.0 → LED → COM → M
            arrow(ax, [(1.15, 3.7), (1.15, 2.75), (2.05, 2.15), (3.3, 2.15), (4.55, 2.15), (5.9, 2.15), (6.75, 2.15), (6.75, 0.6)])
        else:      # L+ → COM → LED → I0.0 → black → switch → blue → M
            arrow(ax, [(6.75, 3.7), (6.75, 1.85), (5.9, 1.85), (4.55, 1.85), (3.3, 1.85), (2.05, 1.85), (1.15, 1.25), (1.15, 0.3)])
        ax.text(3.6, -0.55, T("✓ 有电流，PLC 读到 1", "✓ current flows: the PLC reads 1"), ha="center", fontsize=9, color=GREEN)
    else:
        ax.text(3.6, -0.55, T("✗ 两端都接同一极，没有电流", "✗ both ends at the same pole: no current"), ha="center", fontsize=9, color=RED)
    ax.set_title(title, fontsize=9.6)
    frame(ax, (-0.6, 7.4), (-0.9, 4.3))
    ax.set_aspect("auto")


def wiring():
    plt = style()
    fig, axs = plt.subplots(2, 2, figsize=(11, 7.4))
    panel(axs[0][0], True, True, T("（a）PNP 传感器 + 电流流入型输入（公共端接 M）", "(a) PNP sensor, current-into input (COM to M)"))
    panel(axs[0][1], False, False, T("（b）NPN 传感器 + 电流流出型输入（公共端接 L+）", "(b) NPN sensor, current-out-of input (COM to L+)"))
    panel(axs[1][0], True, False, T("（c）PNP 传感器 + 电流流出型输入：错", "(c) PNP sensor, current-out-of input: wrong"))
    panel(axs[1][1], False, True, T("（d）NPN 传感器 + 电流流入型输入：错", "(d) NPN sensor, current-into input: wrong"))
    fig.tight_layout()
    return fig


def two_three():
    plt = style()
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.6))
    for ax, three in ((a, True), (b, False)):
        _l(ax, [0, 6], [3, 3], lw=1.6); _l(ax, [0, 6], [0, 0], lw=1.6)
        _lab(ax, -0.08, 3, "L+", fs=9); _lab(ax, -0.08, 0, "M", fs=9)
        _box(ax, 0.8, 1.0, 1.4, 1.0, T("传感器", "sensor"), fc=SOFT, ec=MUTED, fs=8.4)
        _box(ax, 3.8, 1.0, 1.4, 1.0, "I0.0", fc="#eef4fb", ec=MUTED, fs=8.4)
        _l(ax, [4.5, 4.5], [1.0, 0.0])
        if three:
            _l(ax, [1.1, 1.1], [3, 2.0], color="#8a5a2b"); _l(ax, [1.1, 1.1], [1.0, 0], color="#2f6db5"); _l(ax, [2.2, 3.8], [1.5, 1.5])
            ax.set_title(T("（a）三线制：电源两根 + 信号一根", "(a) three-wire: supply pair + signal"), fontsize=9.6)
            ax.text(3.0, 1.62, T("输出", "output"), ha="center", fontsize=7.6)
        else:
            _l(ax, [1.5, 1.5], [3, 2.0], color="#8a5a2b"); _l(ax, [2.2, 3.8], [1.5, 1.5])
            ax.set_title(T("（b）两线制：与输入串联，关断时仍有漏电流", "(b) two-wire: in series with the input; leaks when off"), fontsize=9.6)
            ax.text(3.0, 1.62, T("约 1 mA 漏电流", "≈1 mA leakage"), ha="center", fontsize=7.6, color=RED)
        frame(ax, (-0.6, 6.2), (-0.4, 3.4)); ax.set_aspect("auto")
    fig.tight_layout()
    return fig


figure(wiring(), "fig3_3_1")
figure(two_three(), "fig3_3_2")
