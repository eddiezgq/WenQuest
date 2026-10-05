"""图 3.5.1：两线制 4–20 mA 液位计接到 PLC 的模拟量输入（左），电流、模拟量的数与液位的对应（右）。
本书实验台的约定：4 mA ↔ 0，20 mA ↔ 27648，低于 4 mA 为负数（3.5 节、程序 3.5.1）。"""
from bookout import figure, out, T, style
from _draw03 import _box, _l, _lab, frame, dot, INK, MUTED, ACCENT, GREEN, WARM, RED, SOFT


def draw():
    plt = style()
    fig, (a, b) = plt.subplots(1, 2, figsize=(10.8, 4.0), gridspec_kw={"width_ratios": [1.1, 1]})
    _l(a, [0, 6.4], [3.4, 3.4], lw=1.6); _l(a, [0, 6.4], [0.2, 0.2], lw=1.6)
    _lab(a, -0.08, 3.4, "L+", fs=9); _lab(a, -0.08, 0.2, "M", fs=9)
    _box(a, 0.7, 1.3, 1.8, 1.2, T("液位计\n（两线制变送器）", "level transmitter\n(two-wire)"), fc=SOFT, ec=MUTED, fs=8.2)
    _l(a, [1.6, 1.6], [3.4, 2.5]); _l(a, [1.6, 1.6], [1.3, 0.9]); _l(a, [1.6, 3.6], [0.9, 0.9], z=6); _l(a, [3.6, 4.0], [0.9, 0.9], z=6)
    _box(a, 3.6, 0.6, 2.4, 2.4, "", fc="#eef4fb", ec=MUTED)
    a.text(4.8, 3.15, T("PLC 模拟量输入", "PLC analog input"), ha="center", fontsize=8.4)
    a.add_patch(__import__("matplotlib").patches.Rectangle((4.3, 1.3), 0.3, 0.8, fc="white", ec=INK, lw=1.1, zorder=5))
    _l(a, [4.0, 4.45, 4.45], [0.9, 0.9, 1.3]); _l(a, [4.45, 4.45, 5.5, 5.5], [2.1, 2.5, 2.5, 0.2])
    a.text(4.7, 1.7, "250 Ω", fontsize=7.6, va="center")
    a.text(5.2, 1.0, T("1–5 V\n→ 模数转换", "1–5 V\n→ A/D"), fontsize=7.4, color=MUTED, ha="center")
    from matplotlib.patches import FancyArrowPatch
    a.add_patch(FancyArrowPatch((1.75, 3.1), (1.75, 2.6), arrowstyle="-|>", mutation_scale=10, color=RED, lw=1.5))
    a.text(1.85, 2.85, "4–20 mA", fontsize=8, color=RED)
    frame(a, (-0.6, 6.6), (-0.2, 3.8)); a.set_aspect("auto")
    a.set_title(T("（a）两线制回路：变送器靠回路电流本身供电", "(a) two-wire loop: the transmitter lives on the loop current"), fontsize=9.4)
    ma = [3.0, 3.6, 4, 20, 20.5, 21.5]
    raw = [(m - 4) / 16 * 27648 for m in ma]
    b.plot([4, 20], [0, 27648], color=ACCENT, lw=1.8)
    b.plot([2.5, 4], [(2.5 - 4) / 16 * 27648, 0], color=MUTED, lw=1.2, ls=(0, (4, 3)))
    b.plot([20, 21.5], [27648, (21.5 - 4) / 16 * 27648], color=MUTED, lw=1.2, ls=(0, (4, 3)))
    b.axvspan(2.5, 3.6, color=RED, alpha=0.08); b.axvspan(20.5, 21.5, color=RED, alpha=0.08)
    b.text(3.05, 21000, T("断线", "broken\nwire"), ha="center", fontsize=8.2, color=RED)
    b.text(21.0, 6000, T("超量程", "over\nrange"), ha="center", fontsize=8.2, color=RED)
    b.set_xlabel(T("回路电流 / mA", "loop current / mA"), fontsize=9)
    b.set_ylabel(T("PLC 读到的数", "value read by the PLC"), fontsize=9)
    bx = b.twinx()
    bx.set_ylim(*[v / 27648 * 2000 for v in b.get_ylim()])
    bx.set_ylabel(T("液位 / mm", "level / mm"), fontsize=9)
    b.set_xticks([4, 8, 12, 16, 20]); b.set_title(T("（b）标定：4 mA ↔ 0，20 mA ↔ 27648 ↔ 2000 mm", "(b) scaling: 4 mA ↔ 0, 20 mA ↔ 27648 ↔ 2000 mm"), fontsize=9.4)
    for s in ("top",):
        b.spines[s].set_visible(False)
    fig.tight_layout()
    return fig


figure(draw(), "fig3_5_1")
# Pt100 (IEC 60751, α = 0.00385), linear approximation R ≈ 100 Ω × (1 + 0.00385 T) (the IEC 60751 table gives 130.90 Ω at 80 °C); type K ≈ 41 µV/°C
A, B = 3.9083e-3, -5.775e-7          # IEC 60751 Callendar–Van Dusen coefficients (T ≥ 0 °C)
out(pt100_80=round(100 * (1 + 0.003850 * 80), 1), pt100_80_cvd=round(100 * (1 + A * 80 + B * 80 * 80), 2), tc_k_400=round(0.041 * 400, 1))
