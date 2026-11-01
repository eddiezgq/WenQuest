"""8.10 温度应力：协作机器人关节里，铝合金（7075）壳体的法兰用 M6 钢螺钉固定在钢制的力矩传感器上（本书设定的结构）。
电机发热使关节从 20 °C 升到 60 °C（ΔT = 40 K）：
1. 单向完全约束的钢杆的温度应力 σ = −EαΔT（作为参照）；
2. 铝合金壳体的法兰（厚 12 mm）用 M6 钢螺钉固定在钢制的力矩传感器上：螺钉穿过铝法兰、拧进钢件的螺孔，夹紧长度内只有铝。
   铝比钢胀得多，螺钉被进一步拉长，预紧力增加多少（被夹件的刚度按一个当量圆柱粗估，偏高，第 24 章按 VDI 2230 细讲）；
3. 应变片的“热输出”：自补偿应变片按某种材料的线膨胀系数匹配，若错用了按铝合金匹配的片贴在钢弹性体上，会读出假应变；±45° 全桥里四片同温，假应变互相抵消
   （与 8.1 节的传感器呼应）。线膨胀系数取典型值（_ch8.ALPHA）（算例 8.10.1–8.10.3，图 8.10.1）。"""
import math

import numpy as np

import _ch8 as H
from bookout import T, figure, out, style

ST, AL = H.mat("40Cr-QT"), H.mat("7075-T6")
A_S, A_A = H.ALPHA["steel"], H.ALPHA["al"]
DT = 40.0
sig_full = ST["E"] * A_S * DT
sig_full_al = AL["E"] * A_A * DT
# 2. 螺钉与被夹件
LK = 12.0                                       # 夹紧长度 mm
D_S, AS6 = 6.0, 20.1                            # M6，应力截面积 mm²（ISO 898-1）
DW = 10.0                                       # 螺钉头支承面外径（本书取值）
D_EQ = DW + LK / 2                              # 被夹件当量圆柱外径（锥台的简化，本书取值）
D_HOLE = 6.6
A_P = math.pi / 4 * (D_EQ ** 2 - D_HOLE ** 2)
c_s = ST["E"] * AS6 / LK                        # 螺钉刚度 N/mm（近似：全长按应力截面）
c_p = AL["E"] * A_P / LK
dF = (A_A - A_S) * DT * LK / (1 / c_s + 1 / c_p)
d_sig = dF / AS6
F0 = 8000.0                                     # 预紧力取 8 kN（8.8 级 M6 的常用量级，本书取值；第 24 章计算）
# 3. 应变片热输出：自补偿应变片按某种材料的 α 匹配；若把按铝合金匹配的片贴在钢上，每片的假应变 ≈ (α_片 − α_钢)·ΔT
GAUGE_MISMATCH = A_A - A_S
e_app_single = GAUGE_MISMATCH * DT             # 大小；符号为 (α_钢 − α_片)ΔT，为负
e_app_bridge = 0.0                              # 全桥四片同温、同样的假应变，在电桥里相减抵消
import _rj as R                                 # noqa: E402  8.1 节的传感器：RJ-201 的 Ø50/Ø30 段，起停峰值转矩
e_signal = R.harmonic("25-100")["repeat"] * 1e3 / H.Wp_hollow(R.SEAT, R.BORE) / (2 * ST["G"])

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 2.9))
dts = np.linspace(0, 60, 61)
a0.plot(dts, ST["E"] * A_S * dts, color="#1f77b4", lw=1.3, label=T("完全约束的钢", "fully restrained steel"))
a0.plot(dts, AL["E"] * A_A * dts, color="#ff7f0e", lw=1.3, label=T("完全约束的铝合金", "fully restrained aluminum"))
a0.plot(dts, (A_A - A_S) * dts * LK / (1 / c_s + 1 / c_p) / AS6, color="#d62728", lw=1.3, ls="--", label=T("M6 钢螺钉穿过铝法兰：附加拉应力", "M6 steel screw through an Al flange: added stress"))
a0.axvline(DT, color=H.MUTED, lw=0.6, ls=":")
a0.set_xlabel(T("温升 ΔT / K", "Temperature rise ΔT / K"), fontsize=7.2)
a0.set_ylabel(T("温度应力 / MPa（压或拉）", "Thermal stress / MPa (compressive or tensile)"), fontsize=7.0)
a0.legend(fontsize=6.2, frameon=False, loc="upper left")
a0.tick_params(labelsize=6.3)
a0.set_title(T("(a) 温度应力随温升", "(a) Thermal stress vs temperature rise"), fontsize=7.4)
labs = [T("信号（起停峰值，单片）", "signal (start–stop peak, one gauge)"), T("热输出（单片，40 K）", "thermal output (one gauge, 40 K)"), T("热输出（全桥）", "thermal output (full bridge)")]
vals = [e_signal * 1e6, e_app_single * 1e6, e_app_bridge * 1e6]
a1.barh(range(3), vals, color=["#1f77b4", "#d62728", "#2ca02c"])
for i, v in enumerate(vals):
    a1.text(v + 5, i, f"{v:.0f} µε", va="center", fontsize=6.4)
a1.set_yticks(range(3))
a1.set_yticklabels(labs, fontsize=6.4)
a1.invert_yaxis()
a1.set_xlim(0, max(vals) * 1.35)
a1.set_xlabel(T("应变 / µε", "Strain / µε"), fontsize=7.2)
a1.tick_params(labelsize=6.3)
a1.set_title(T("(b) 力矩传感器：温度造成的假应变", "(b) Torque sensor: apparent strain from temperature"), fontsize=7.4)
fig.tight_layout()
figure(fig, "fig8_10_1")

out(dT=DT, a_s=A_S * 1e6, a_a=A_A * 1e6, sig_full=sig_full, sig_full_al=sig_full_al, Lk=LK, As=AS6, D_eq=D_EQ, Ap=A_P, c_s=c_s / 1000,
    c_p=c_p / 1000, dF=dF, d_sig=d_sig, F0=F0 / 1000, dF_pct=100 * dF / F0, e_app=e_app_single * 1e6, e_sig=e_signal * 1e6,
    app_ratio=e_app_single / e_signal, gm=GAUGE_MISMATCH * 1e6)
