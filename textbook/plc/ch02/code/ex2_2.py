"""2.2 节：图 2.2.1（常用低压电器的图形符号与本书的文字代号），图 2.2.2（热继电器的动作时间曲线）。

热继电器的模型与虚拟设备里的相同（services/gateway/app/production/labkit/plants.js 的 motorPU）：
一阶热惯性，时间常数 290 s，热量达到整定电流对应稳态值的 1.25 倍时动作；电流为整定值的 x 倍时，从冷态起的动作时间
t = −τ·ln(1 − 1.25/x²)。按 IEC 60947-4-1，10 级（class 10）的热继电器在 7.2 倍整定电流下应在 4–10 s 内动作，
1.05 倍时 2 h 内不动作，1.2 倍时 2 h 内动作。"""
import math
from bookout import figure, out, T, style
from _draw02 import (contact, coil, lamp, fuse, group, motor, frame, _l, _lab, INK, MUTED, ACCENT, WARM, RED, P)

TAU, TRIP = 290.0, 1.25


def trip_time(x):
    return math.inf if x * x <= TRIP else -TAU * math.log(1 - TRIP / (x * x))


def symbols():
    plt = style()
    fig, ax = plt.subplots(figsize=(10.5, 6.4))
    cells = [
        (lambda x, y: contact(ax, x, y), T("常开触点", "NO contact"), ""),
        (lambda x, y: contact(ax, x, y, nc=True), T("常闭触点", "NC contact"), ""),
        (lambda x, y: contact(ax, x + 0.2, y, act="push"), T("按钮（常开）", "push-button (NO)"), "S"),
        (lambda x, y: contact(ax, x + 0.2, y, nc=True, act="estop"), T("急停按钮（常闭）", "emergency stop (NC)"), "S"),
        (lambda x, y: contact(ax, x + 0.2, y, act="limit"), T("位置开关（常开）", "position switch (NO)"), "B"),
        (lambda x, y: coil(ax, x, y), T("接触器、继电器线圈", "contactor / relay coil"), "KM、KA"),
        (lambda x, y: coil(ax, x + 0.15, y, kind="on"), T("通电延时时间继电器线圈", "on-delay timer coil"), "KT"),
        (lambda x, y: contact(ax, x, y, delay="on"), T("延时闭合的常开触点", "NO contact, delayed closing"), "KT"),
        (lambda x, y: contact(ax, x, y, nc=True, delay="on"), T("延时断开的常闭触点", "NC contact, delayed opening"), "KT"),
        (lambda x, y: contact(ax, x + 0.2, y, nc=True, act="thermal"), T("热继电器常闭触点", "overload relay NC contact"), "F"),
        (lambda x, y: group(ax, x - P, y, "CB"), T("断路器（三极）", "circuit breaker (3-pole)"), "Q"),
        (lambda x, y: group(ax, x - P, y, "KM"), T("接触器主触点（三极）", "contactor main contacts"), "KM"),
        (lambda x, y: group(ax, x - P, y, "OL"), T("热继电器发热元件", "overload relay heaters"), "F"),
        (lambda x, y: fuse(ax, x, y), T("熔断器", "fuse"), "F"),
        (lambda x, y: lamp(ax, x, y), T("指示灯", "indicator lamp"), "H"),
    ]
    ncol = 5
    for k, (draw, name, code) in enumerate(cells):
        r, c = divmod(k, ncol)
        x, y = 1.0 + c * 2.3, -r * 2.25
        draw(x, y)
        ax.text(x, y - 1.25, name, ha="center", va="top", fontsize=8.4)
        if code:
            ax.text(x, y - 1.6, code, ha="center", va="top", fontsize=8.4, color=ACCENT, family="monospace" if "、" not in code else None)
    frame(ax, (-0.2, 11.6), (-6.6, 0.4))
    return fig


def trip_curve():
    plt = style()
    fig, ax = plt.subplots(figsize=(7.8, 4.4))
    xs = [1.12 + 0.02 * k for k in range(450)]
    ax.plot(xs, [trip_time(x) for x in xs], color=ACCENT, lw=1.7, label=T("虚拟设备的热继电器（冷态起）", "the bench's overload relay (from cold)"))
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.plot([7.2, 7.2], [4, 10], color=RED, lw=6, alpha=0.35, solid_capstyle="butt")
    ax.text(7.5, 18, T("10 级：7.2 倍时 4–10 s 动作", "class 10: 4–10 s at 7.2 ×"), fontsize=8.6, color=RED, va="center")
    ax.axvline(1.05, color=MUTED, lw=0.8, ls=(0, (4, 3)))
    ax.text(1.06, 3, T("1.05 倍：不动作", "1.05 ×: never"), fontsize=8.4, color=MUTED, rotation=90, va="bottom")
    ax.axvline(6.5, color=WARM, lw=0.8, ls=(0, (4, 3)))
    ax.text(6.2, 300, T("启动电流约 6.5 倍", "starting current ≈ 6.5 ×"), fontsize=8.4, color=WARM, ha="right")
    ax.set_xlim(1, 11)
    ax.set_ylim(1, 5000)
    ax.set_xticks([1, 1.2, 1.5, 2, 3, 5, 7.2, 10])
    ax.set_xticklabels(["1", "1.2", "1.5", "2", "3", "5", "7.2", "10"])
    ax.set_xlabel(T("电流 / 整定电流", "current / setting"), fontsize=9.5)
    ax.set_ylabel(T("动作时间 / s", "tripping time / s"), fontsize=9.5)
    ax.grid(True, which="both", color="#e6ebee", lw=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(frameon=False, fontsize=8.6, loc="upper right")
    return fig


figure(symbols(), "fig2_2_1")
figure(trip_curve(), "fig2_2_2")
out(t72=round(trip_time(7.2), 1), t12=round(trip_time(1.2) / 60), t15=round(trip_time(1.5)), t65=round(trip_time(6.5), 1), tau=int(TAU))
