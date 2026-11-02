"""图 20.3.1：左：ω_n = 10 rad/s、x(0) = 1、ẋ(0) = 0 时过阻尼、临界阻尼、欠阻尼的自由响应；
右：特征根在复平面上随阻尼比 ζ 的位置。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

wn = 10.0
t = np.linspace(0, 1.5, 600)


def resp(z):
    if z < 1:
        wd = wn * np.sqrt(1 - z * z)
        return np.exp(-z * wn * t) * (np.cos(wd * t) + z / np.sqrt(1 - z * z) * np.sin(wd * t))
    if z == 1:
        return (1 + wn * t) * np.exp(-wn * t)
    r1, r2 = -z * wn + wn * np.sqrt(z * z - 1), -z * wn - wn * np.sqrt(z * z - 1)
    return (r1 * np.exp(r2 * t) - r2 * np.exp(r1 * t)) / (r1 - r2)


fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
for z, col, lab in ((0.2, BLUE, T("欠阻尼 ζ = 0.2", "underdamped ζ = 0.2")), (1.0, GREEN, T("临界阻尼 ζ = 1", "critical ζ = 1")), (2.0, RED, T("过阻尼 ζ = 2", "overdamped ζ = 2"))):
    a1.plot(t, resp(z), color=col, lw=2, label=lab)
a1.set_xlabel(T("时间 t / s", "time t / s"))
a1.set_ylabel("x(t)")
a1.set_title(T("自由响应的三种情形（ω_n = 10 rad/s）", "Three kinds of free response (ω_n = 10 rad/s)"), fontsize=10)
a1.legend(fontsize=9, frameon=False)
clean(a1)
th = np.linspace(np.pi / 2, 3 * np.pi / 2, 200)
a2.plot(wn * np.cos(th), wn * np.sin(th), color=MUTED, ls=":", lw=1)
zs = np.linspace(0, 1, 60)
a2.plot(-zs * wn, wn * np.sqrt(1 - zs ** 2), color=BLUE, lw=2)
a2.plot(-zs * wn, -wn * np.sqrt(1 - zs ** 2), color=BLUE, lw=2)
zs = np.linspace(1, 3, 80)
a2.plot(-zs * wn + wn * np.sqrt(zs ** 2 - 1), 0 * zs, color=RED, lw=2.5)
a2.plot(-zs * wn - wn * np.sqrt(zs ** 2 - 1), 0 * zs, color=RED, lw=2.5)
for z, col in ((0.2, BLUE), (0.7, BLUE), (1.0, GREEN), (2.0, RED)):
    d = np.sqrt(complex(z * z - 1))
    for r in (-z * wn + wn * d, -z * wn - wn * d):
        a2.plot(r.real, r.imag, "o", color=col, ms=6)
    a2.text(-z * wn + (0.4 if z < 1 else -1.5), wn * abs(d.imag) + (0.8 if z < 1 else 1.2), f"ζ = {z:g}", fontsize=9, color=col)
a2.axhline(0, color=MUTED, lw=0.6)
a2.axvline(0, color=MUTED, lw=0.6)
a2.set_xlim(-40, 4)
a2.set_ylim(-13, 13)

a2.set_xlabel(T("实部", "real part"))
a2.set_ylabel(T("虚部", "imaginary part"))
a2.set_title(T("特征根随 ζ 移动", "Characteristic roots as ζ varies"), fontsize=10)
for s_ in ("top", "right"):
    a2.spines[s_].set_visible(False)
fig.tight_layout()
figure(fig, "fig20_3_1")
