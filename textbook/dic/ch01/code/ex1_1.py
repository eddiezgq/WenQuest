"""1.1 节的计算：MOSFET 开关与 CMOS 反相器。

算例 1.1.1  最小尺寸 NMOS（W = 0.42 μm，L = 0.15 μm）在 VGS = 1.8 V 时的饱和电流与线性区导通电阻。
算例 1.1.2  关节驱动板的光耦输入：芯片输出管脚要吸收 I = 1 mA，输出低电平不超过 0.2 V。由线性区公式求 NMOS 的最小宽度，
            并用二分法解 ID(VDD, VOL) = I 核对；再看负载加到 2 mA 时 VOL 是多少。
图 1.1.1    CMOS 反相器的电路与开关模型（输入为 0、为 1 时各有一个管子导通）。
图 1.1.2    不同宽度的 NMOS 在 VGS = 1.8 V 下的输出特性与 1 mA 负载线：交点就是输出低电平。
"""
import numpy as np

from bookout import T, figure, out, style
from mos import L, VDD, VTn, Wmin, idn, idsat_n, kn, kp, wn_for_vol
import _draw as d

# ---- 算例 1.1.1：最小管
Isat = idsat_n(Wmin)
Ron = 1 / (kn * Wmin / L * (VDD - VTn))               # 线性区、VDS → 0 时的导通电阻
out(W=Wmin, L=L, VT=VTn, kn_ua=kn * 1e6, kp_ua=kp * 1e6, Isat_ua=Isat * 1e6, Isat_per_um=Isat / Wmin * 1e6, Ron_k=Ron / 1e3)

# ---- 算例 1.1.2：光耦输入
I, VOLmax = 1e-3, 0.2
W = wn_for_vol(I, VOLmax)


def vol(Wn, Iload):
    """解 ID(VDD, VOL) = Iload；负载超过饱和电流时返回 None（输出拉不下来）。"""
    if Iload >= idsat_n(Wn):
        return None
    lo, hi = 0.0, VDD - VTn
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if idn(VDD, mid, Wn) > Iload else (mid, hi)
    return (lo + hi) / 2


v1 = vol(W, I)
v2 = vol(W, 2e-3)
assert abs(v1 - VOLmax) < 1e-9
out(I_ma=I * 1e3, VOLmax=VOLmax, Wn=W, WL=W / L, ratio_min=W / Wmin, VOL2=v2, Ron_W=VOLmax / I,
    Isat_W_ma=idsat_n(W) * 1e3, Ron_small_W=Ron * Wmin / W, Ron_gap=(VOLmax / I) / (Ron * Wmin / W) * 100 - 100)

# ---- 图 1.1.1：电路与开关模型
plt = style()


def inverter(ax, x0, vin=None):
    """A CMOS inverter at x0: PMOS above, NMOS below, gates joined; vin = None (circuit), 0 or 1 (switch model)."""
    k = dict(color=d.INK, lw=1.4)
    ax.plot([x0, x0], [3.0, 2.55], **k); ax.text(x0, 3.12, "VDD", ha="center", fontsize=10, color=d.INK)
    ax.plot([x0, x0], [0.45, 0.0], **k); ax.plot([x0 - 0.2, x0 + 0.2], [0.0, 0.0], **k)
    ax.plot([x0 - 0.12, x0 + 0.12], [-0.07, -0.07], **k); ax.plot([x0 - 0.05, x0 + 0.05], [-0.14, -0.14], **k)
    ax.plot([x0, x0], [1.95, 1.05], **k); ax.plot([x0, x0 + 0.9], [1.5, 1.5], **k)
    ax.text(x0 + 0.95, 1.5, "Vout", va="center", fontsize=10, color=d.INK)
    ax.plot([x0 + 0.6, x0 + 0.6], [1.5, 1.2], **k)                 # load capacitor
    ax.plot([x0 + 0.45, x0 + 0.75], [1.2, 1.2], **k); ax.plot([x0 + 0.45, x0 + 0.75], [1.1, 1.1], **k)
    ax.plot([x0 + 0.6, x0 + 0.6], [1.1, 0.85], **k); ax.text(x0 + 0.8, 1.0, "CL", fontsize=9, color=d.MUTED)
    if vin is None:                                                    # transistors
        for y0, y1, col, name in ((2.55, 1.95, d.PMOS, "PMOS"), (1.05, 0.45, d.NMOS, "NMOS")):
            ax.plot([x0, x0], [y0, y1], color=col, lw=3)
            ax.plot([x0 - 0.18, x0 - 0.18], [y0 - 0.05, y1 + 0.05], color=col, lw=1.6)
            ax.text(x0 + 0.12, (y0 + y1) / 2, name, va="center", fontsize=9, color=col)
        ax.plot([x0 - 0.18, x0 - 0.7, x0 - 0.7, x0 - 0.18], [2.25, 2.25, 0.75, 0.75], **k)
        ax.plot([x0 - 0.7, x0 - 1.2], [1.5, 1.5], **k); ax.text(x0 - 1.25, 1.5, "Vin", ha="right", va="center", fontsize=10, color=d.INK)
        ax.plot([x0 - 0.26], [2.25], "o", mfc="white", mec=d.PMOS, ms=5)
        return
    for y0, y1, col, on in ((2.55, 1.95, d.PMOS, vin == 0), (1.05, 0.45, d.NMOS, vin == 1)):
        ax.plot([x0, x0], [y0, y0 - 0.15], color=col, lw=2); ax.plot([x0, x0], [y1, y1 + 0.15], color=col, lw=2)
        ax.plot([x0, x0 + (0 if on else 0.22)], [y0 - 0.15, y1 + 0.15], color=col, lw=2)
    path = [[x0, x0], [3.0, 1.5]] if vin == 0 else [[x0, x0], [1.5, 0.0]]
    ax.plot(*path, color=d.LOAD, lw=5, alpha=0.35)
    ax.text(x0 + 0.3, -0.45, T(f"Vin = {vin}", f"Vin = {vin}"), ha="center", fontsize=9, color=d.INK)
    ax.text(x0 + 0.3, -0.85, T("PMOS 导通，CL 充电" if vin == 0 else "NMOS 导通，CL 放电", "PMOS on, CL charges" if vin == 0 else "NMOS on, CL discharges"),
            ha="center", fontsize=8.5, color=d.MUTED)


fig, ax = plt.subplots(figsize=(7.6, 3.2))
inverter(ax, 1.5)
inverter(ax, 4.5, 0)
inverter(ax, 7.6, 1)
ax.set_xlim(0, 9.4); ax.set_ylim(-1.0, 3.3); ax.set_aspect("equal"); ax.axis("off")
figure(fig, "fig1_1_1")

# ---- 图 1.1.2：输出特性与负载线
fig, ax = plt.subplots(figsize=(5.6, 3.6))
vds = np.linspace(0, VDD, 361)
for Wn, ls in ((2.0, ":"), (4.0, "--"), (W, "-")):
    ax.plot(vds, [idn(VDD, v, Wn) * 1e3 for v in vds], color=d.NMOS, ls=ls, lw=1.6,
            label=T(f"Wn = {Wn:.2f} μm", f"Wn = {Wn:.2f} μm"))
ax.axhline(I * 1e3, color=d.LOAD, lw=1.4, label=T("负载 1 mA", "load 1 mA"))
ax.axvline(VOLmax, color=d.MUTED, lw=1, ls="--")
ax.plot([v1], [I * 1e3], "o", color=d.LOAD)
ax.annotate(T("VOL = 0.2 V", "VOL = 0.2 V"), (v1, I * 1e3), (0.35, 0.55), color=d.INK, fontsize=10,
            arrowprops=dict(arrowstyle="->", color=d.MUTED))
ax.set_xlim(0, 1.0); ax.set_ylim(0, 3.0)
ax.set_xlabel(T("漏源电压 VDS / V", "drain–source voltage VDS / V"))
ax.set_ylabel(T("漏极电流 ID / mA", "drain current ID / mA"))
ax.legend(fontsize=9, frameon=False, loc="upper left")
d.spines(ax)
figure(fig, "fig1_1_2")
