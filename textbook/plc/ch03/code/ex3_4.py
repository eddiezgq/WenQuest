"""3.4 节：图 3.4.1（三种数字量输出：继电器、晶体管、晶闸管），图 3.4.2（晶体管输出断开电磁阀线圈时的电压和电流）。

电磁阀线圈：DC 24 V、0.2 A（4.8 W），电阻 120 Ω，电感取 0.5 H（时间常数 L/R ≈ 4.2 ms）。断开时线圈电流 i 只能经吸收电路续流：
  续流二极管：L di/dt = −(iR + 0.7)；
  二极管串 15 V 稳压管（稳压值要低于输出的钳位余量 23 V，否则内部钳位先导通）：L di/dt = −(iR + 15.7)；
  不加吸收、靠输出晶体管内部 47 V 钳位：线圈两端电压被钳在 −(47 − 24) = −23 V 附近，L di/dt = −(iR + 23)，输出端电压到 −23 V。
电磁阀的衔铁在电流降到吸合电流的约 30 % 时释放（取近似值，以产品样本为准）。"""
import math
from bookout import figure, out, T, style
from _draw03 import _box, _l, _lab, frame, dot, contact, INK, MUTED, ACCENT, GREEN, WARM, RED, SOFT

R, L, I0, VD = 120.0, 0.5, 0.2, 0.7
CASES = [("diode", T("续流二极管", "freewheeling diode"), VD, ACCENT), ("zener", T("二极管 + 15 V 稳压管", "diode + 15 V Zener"), 15.0 + VD, GREEN),
         ("clamp", T("不吸收（晶体管内部 47 V 钳位）", "none (transistor's internal 47 V clamp)"), 23.0, WARM)]
REL = 0.30


def decay(vc, dt=1e-5, t_end=0.03):
    t, i, ts, Is, vs = 0.0, I0, [], [], []
    while t < t_end:
        ts.append(t * 1000); Is.append(i); vs.append(-(vc if i > 0 else 0))
        i = max(0.0, i - (i * R + vc) / L * dt)
        t += dt
    return ts, Is, vs


res = {k: decay(vc) for k, _, vc, _ in CASES}
t_rel = {k: next(t for t, i in zip(res[k][0], res[k][1]) if i <= REL * I0) for k in res}


def outputs():
    """L+ (or L) → the output's switching element → output terminal → load → M (or N)."""
    from matplotlib.patches import Rectangle, Polygon
    plt = style()
    fig, axs = plt.subplots(1, 3, figsize=(11.5, 4.3))
    for ax, title, kind in zip(axs, (T("（a）继电器输出", "(a) relay output"), T("（b）晶体管输出（PNP，源出电流）", "(b) transistor output (PNP, sourcing)"),
                                     T("（c）晶闸管（双向晶闸管）输出", "(c) triac output")), ("relay", "tr", "triac")):
        top, bot = ("L", "N") if kind == "triac" else (("L / L+", "N / M") if kind == "relay" else ("L+", "M"))
        _l(ax, [1.6, 5.0], [3.6, 3.6], lw=1.6); _l(ax, [1.6, 5.0], [0.3, 0.3], lw=1.6)
        ax.text(5.1, 3.6, top, va="center", fontsize=8.4, family="monospace"); ax.text(5.1, 0.3, bot, va="center", fontsize=8.4, family="monospace")
        _box(ax, 0.3, 1.0, 2.6, 2.2, "", fc="#eef4fb", ec=MUTED)
        ax.text(1.0, 2.95, T("PLC 输出", "PLC output"), ha="center", fontsize=8.4)
        x = 2.4
        dot(ax, x, 3.2); ax.text(x + 0.08, 3.32, T("公共端", "COM"), fontsize=7.4)
        _l(ax, [x, x], [3.6, 3.2])
        dot(ax, 2.9, 1.4); ax.text(2.95, 1.55, "Q0.0", fontsize=7.4, family="monospace")
        if kind == "relay":
            _l(ax, [x, x], [3.2, 2.65]); _l(ax, [x, x - 0.25], [1.95, 2.6], lw=1.4); _l(ax, [x, x], [1.95, 1.4])
            ax.add_patch(Rectangle((0.6, 1.95), 0.5, 0.5, fc="white", ec=INK, lw=1.1, zorder=5))
            ax.text(0.85, 1.7, T("线圈", "coil"), ha="center", fontsize=7.2, color=MUTED, zorder=6)
            _l(ax, [1.1, x - 0.12], [2.25, 2.25], lw=0.9, ls=(0, (2, 1.5)))
            note = T("交流、直流都能接；\n约 2 A，寿命有限、动作慢", "AC or DC loads; about 2 A;\nlimited life, slow")
        elif kind == "tr":
            _l(ax, [x, x], [3.2, 2.6]); _l(ax, [x, x], [2.0, 1.4])
            _l(ax, [x - 0.3, x - 0.3], [2.05, 2.55], lw=2.2)                     # base bar
            _l(ax, [x - 0.3, x], [2.45, 2.6]); _l(ax, [x - 0.3, x], [2.15, 2.0])  # emitter (top, to L+), collector (bottom, to the load)
            ax.add_patch(Polygon([[x - 0.27, 2.43], [x - 0.12, 2.43], [x - 0.17, 2.55]], closed=True, fc=INK, ec=INK, zorder=6))   # PNP: arrow into the base
            _l(ax, [x - 0.75, x - 0.3], [2.3, 2.3], lw=0.9)
            note = T("只接直流；约 0.5 A；\n快、无触点", "DC only; about 0.5 A;\nfast, no contacts")
        else:
            _l(ax, [x, x], [3.2, 2.55]); _l(ax, [x, x], [2.05, 1.4])
            ax.add_patch(Polygon([[x - 0.22, 2.5], [x + 0.22, 2.5], [x, 2.3]], closed=True, fc="white", ec=INK, lw=1.1, zorder=5))
            ax.add_patch(Polygon([[x - 0.22, 2.1], [x + 0.22, 2.1], [x, 2.3]], closed=True, fc="white", ec=INK, lw=1.1, zorder=5))
            _l(ax, [x - 0.25, x + 0.25], [2.3, 2.3], lw=1.1, z=6)
            note = T("只接交流；无触点、寿命长；\n关断后有漏电流", "AC only; no contacts, long life;\nleaks when off")
        _l(ax, [x, 2.9, 4.2, 4.2], [1.4, 1.4, 1.4, 1.15]); _l(ax, [4.2, 4.2], [0.55, 0.3])
        ax.add_patch(Rectangle((4.0, 0.55), 0.4, 0.6, fc="white", ec=INK, lw=1.1, zorder=5))
        ax.text(4.5, 0.85, T("负载", "load"), fontsize=8, va="center")
        ax.text(1.6, 0.55, note, ha="center", fontsize=7.8, color=MUTED, va="center")
        frame(ax, (0.1, 5.6), (0.0, 3.9)); ax.set_aspect("auto")
        ax.set_title(title, fontsize=9.6)
    return fig


def transient():
    plt = style()
    fig, (a, b) = plt.subplots(1, 2, figsize=(10.5, 3.8))
    for k, label, vc, color in CASES:
        ts, Is, vs = res[k]
        a.plot([-2, 0] + ts, [0, 0] + [v for v in vs], color=color, lw=1.6, label=label)
        b.plot([-2, 0] + ts, [I0 * 1000, I0 * 1000] + [i * 1000 for i in Is], color=color, lw=1.6)
        b.plot([t_rel[k]], [REL * I0 * 1000], "o", color=color, ms=4)
    a.set_xlabel(T("断开后的时间 / ms", "time after switch-off / ms"), fontsize=9)
    a.set_ylabel(T("线圈两端电压 / V", "coil voltage / V"), fontsize=9)
    a.legend(frameon=False, fontsize=8.2, loc="lower right")
    b.axhline(REL * I0 * 1000, color=MUTED, lw=0.8, ls=(0, (4, 3)))
    b.text(29, REL * I0 * 1000 + 4, T("衔铁释放（约 30 %）", "armature releases (≈30 %)"), ha="right", fontsize=8, color=MUTED)
    b.set_xlabel(T("断开后的时间 / ms", "time after switch-off / ms"), fontsize=9)
    b.set_ylabel(T("线圈电流 / mA", "coil current / mA"), fontsize=9)
    for ax in (a, b):
        ax.set_xlim(-2, 30)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig


figure(outputs(), "fig3_4_1")
figure(transient(), "fig3_4_2")
out(tau=round(L / R * 1000, 1), rel_diode=round(t_rel["diode"], 1), rel_zener=round(t_rel["zener"], 1), rel_clamp=round(t_rel["clamp"], 1),
    ratio=round(t_rel["diode"] / t_rel["zener"], 1))
