"""1.2 节的计算：电压传输特性与噪声容限。

算例 1.2.1  最小 NMOS 配 Wp/Wn = 1 与 Wp/Wn = r（两管饱和电流相等的“对称”尺寸）：开关阈值 VM、VIL、VIH 与噪声容限。
算例 1.2.2  编码器信号经 2 m 电缆进入控制芯片，叠加约 ±0.3 V 干扰：两种尺寸会不会误翻转。
图 1.2.1    两种尺寸的传输特性，标出 VM 与斜率为 −1 的两点。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from mos import VDD, VTn, Wmin, kn, kp, noise_margins, vm, vout
import _draw as d

r = kn / kp                                           # 两管饱和电流相等时 Wp/Wn = k′n/k′p（|VT| 相同）
res = {}
for key, ratio in (("a", 1.0), ("b", r)):
    nm = noise_margins(Wmin, ratio * Wmin)
    res[key] = dict(ratio=ratio, VM=vm(Wmin, ratio * Wmin), **nm)
a, b = res["a"], res["b"]
out(r=r, VMa=a["VM"], VILa=a["VIL"], VIHa=a["VIH"], NMLa=a["NML"], NMHa=a["NMH"],
    VMb=b["VM"], VILb=b["VIL"], VIHb=b["VIH"], NMLb=b["NML"], NMHb=b["NMH"], VOLa=a["VOL"], VOHa=a["VOH"])
noise = 0.3
out(noise=noise, worst_a=min(a["NML"], a["NMH"]), worst_b=min(b["NML"], b["NMH"]),
    margin_a=min(a["NML"], a["NMH"]) - noise, margin_b=min(b["NML"], b["NMH"]) - noise)
# 开关阈值的解析式（两管都饱和时 In = Ip）与二分法结果一致
x = math.sqrt(kp * r * Wmin / (kn * Wmin))
assert abs((VTn + x * (VDD - VTn)) / (1 + x) - b["VM"]) < 1e-12

plt = style()
fig, ax = plt.subplots(figsize=(5.2, 4.0))
vin = np.linspace(0, VDD, 361)
for key, color, name in (("a", d.PMOS, T("Wp/Wn = 1", "Wp/Wn = 1")), ("b", d.NMOS, T(f"Wp/Wn = r = {r:.2f}", f"Wp/Wn = r = {r:.2f}"))):
    q = res[key]
    ax.plot(vin, [vout(v, Wmin, q["ratio"] * Wmin) for v in vin], color=color, lw=1.8, label=name)
    ax.plot([q["VIL"], q["VIH"]], [q["VOH"], q["VOL"]], "o", color=color, ms=4)
ax.plot([0, VDD], [0, VDD], color=d.MUTED, lw=0.8, ls=":")
ax.text(1.55, 1.42, T("Vout = Vin", "Vout = Vin"), color=d.MUTED, fontsize=9)
ax.set_xlim(0, VDD); ax.set_ylim(0, VDD + 0.05)
ax.set_xlabel(T("输入电压 Vin / V", "input voltage Vin / V"))
ax.set_ylabel(T("输出电压 Vout / V", "output voltage Vout / V"))
ax.legend(fontsize=9, frameon=False, loc="lower left")
d.spines(ax)
figure(fig, "fig1_2_1")
