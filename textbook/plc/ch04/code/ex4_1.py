"""图 4.1.1（循环扫描的各个阶段），图 4.2.1（输入在一次扫描中途变化：程序要到下一次扫描才看到，输出再晚一次扫描的末尾才变）。
扫描时间取 10 ms：读输入 0.5 ms，执行程序 8 ms，写输出 0.5 ms，通信与诊断 1 ms。"""
from bookout import figure, T, style
from _draw04 import _box, _l, frame, INK, MUTED, ACCENT, GREEN, WARM, RED, SOFT

PH = [(T("读输入", "read inputs"), 0.5, GREEN), (T("执行程序", "execute program"), 8.0, ACCENT), (T("写输出", "write outputs"), 0.5, WARM),
      (T("通信与诊断", "comm. & diagnostics"), 1.0, MUTED)]


def phases():
    import math
    from matplotlib.patches import Wedge
    plt = style()
    fig, ax = plt.subplots(figsize=(6.4, 6.0))
    a0 = 90.0
    total = sum(p[1] for p in PH)
    for name, ms, color in PH:
        span = 360 * ms / total
        ax.add_patch(Wedge((0, 0), 2.0, a0 - span, a0, width=0.55, fc=color, ec="white", lw=2, alpha=0.85))
        mid = math.radians(a0 - span / 2)
        r = 2.45 if span < 40 else 1.72
        ax.text(r * math.cos(mid), r * math.sin(mid), f"{name}\n{ms:g} ms", ha="center", va="center", fontsize=9,
                color=INK if span < 40 else "white")
        a0 -= span
    ax.text(0, 0.15, T("一个扫描周期", "one scan"), ha="center", fontsize=11, fontweight="bold")
    ax.text(0, -0.3, T(f"约 {total:g} ms，周而复始", f"about {total:g} ms, over and over"), ha="center", fontsize=9, color=MUTED)
    from matplotlib.patches import FancyArrowPatch
    ax.add_patch(FancyArrowPatch((2.15, 0.6), (2.15, -0.6), connectionstyle="arc3,rad=-0.4", arrowstyle="-|>", mutation_scale=14, color=INK, lw=1.2))
    frame(ax, (-3.3, 3.3), (-3.0, 3.0))
    return fig


def image():
    """phys input rises at t = 13 ms (during scan 2); image takes it at the start of scan 3 (t = 20); program sets the output image;
    the output terminal changes at the end of scan 3 (write-outputs phase, t ≈ 29)."""
    plt = style()
    fig, ax = plt.subplots(figsize=(9.6, 3.6))
    T0 = [0, 10, 20, 30, 40]
    for k, t in enumerate(T0[:-1]):
        x = t
        for name, ms, color in PH:
            ax.add_patch(__import__("matplotlib").patches.Rectangle((x, 4.2), ms, 0.5, fc=color, ec="white", alpha=0.8))
            x += ms
        ax.text(t + 5, 4.85, T(f"第 {k + 1} 次扫描", f"scan {k + 1}"), ha="center", fontsize=8.4)
    rows = [(T("实际输入", "physical input"), [(0, 0), (13, 1)], GREEN), (T("输入映像", "input image"), [(0, 0), (20.5, 1)], GREEN),
            (T("输出映像", "output image"), [(0, 0), (24, 1)], WARM), (T("实际输出", "physical output"), [(0, 0), (28.5, 1)], WARM)]
    for i, (name, steps, color) in enumerate(rows):
        y0 = 3.0 - i * 0.9
        xs, ys = [], []
        for j, (t, v) in enumerate(steps):
            t1 = steps[j + 1][0] if j + 1 < len(steps) else 40
            xs += [t, t1]; ys += [y0 + 0.5 * v, y0 + 0.5 * v]
        xs2, ys2 = [xs[0]], [ys[0]]
        for k in range(1, len(xs)):
            xs2 += [xs[k], xs[k]] if k % 2 == 0 else [xs[k]]
            ys2 += [ys[k - 1], ys[k]] if k % 2 == 0 else [ys[k]]
        ax.plot(xs2, ys2, color=color, lw=1.8)
        ax.text(-0.8, y0 + 0.25, name, ha="right", va="center", fontsize=8.8)
    ax.annotate(T("扫描中途变化：这次看不到", "changes mid-scan: not seen now"), xy=(13, 3.5), xytext=(2, 3.75), fontsize=8.2, color=RED,
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=0.8))
    ax.annotate("", xy=(28.5, 0.75), xytext=(13, 0.75), arrowprops=dict(arrowstyle="<->", color=RED, lw=1))
    ax.text(20.7, 0.82, T("约 15.5 ms：一到两个扫描周期", "≈15.5 ms: one to two scans"), ha="center", va="bottom", fontsize=8.4, color=RED)
    for t in T0:
        ax.axvline(t, color="#e3e9e7", lw=0.8, zorder=0)
    ax.set_xlim(-12, 40); ax.set_ylim(0.2, 5.1)
    ax.set_yticks([]); ax.set_xticks(T0)
    ax.set_xlabel(T("时间 / ms", "time / ms"), fontsize=9)
    for s in ("left", "right", "top"):
        ax.spines[s].set_visible(False)
    return fig


figure(phases(), "fig4_1_1")
figure(image(), "fig4_2_1")
