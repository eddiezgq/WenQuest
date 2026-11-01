"""9.1 梁的挠度：积分法与叠加法。

算例 9.1.1  WQR-105 输出轴 SH-301 B 版在额定转矩下（第 33 章的几何与齿轮力）：把阶梯轴当作等直径的简支梁，用积分法的公式手算
            齿轮处的挠度和两轴承处的转角，取 Ø40（齿轮位）和 Ø35（轴承位）两种直径，与第 33 章的阶梯轴梁单元模型（33.6 节）比较；
算例 9.1.2  UR5e 小臂管（Ø75×2，6061-T6，本书设定，与第 5、8 章相同）伸直水平、末端 5 kg：用叠加法把三种载荷（自重均布、
            腕部和负载的力、负载偏心的力矩）各自引起的末端挠度和转角相加；
图 9.1.1。
"""
import math

import numpy as np

import _ch9 as H
import _shaft as S
from bookout import T, figure, out, style

# ---------------------------------------------------------------- 算例 9.1.1
Ft, Fr = S.gear_forces()
F = math.hypot(Ft, Fr)                        # 两个平面的力作用在同一点，合成后按一个平面算（线性，结果相同）
E = H.mat("40Cr-QT")["E"]                     # SH-301 B 版材料（第 33.8 节）；E 与 45 钢相同
z, y_fe, th_fe = S.deflection(F, E=E)
iA, iB, iG = (int(np.argmin(abs(z - v))) for v in (S.Z_BRG_A, S.Z_BRG_B, S.Z_GEAR))
L = S.Z_BRG_B - S.Z_BRG_A
a = S.Z_GEAR - S.Z_BRG_A
b = L - a


def uniform(d):
    """等直径简支梁，力 F 在 a 处（积分法的结果）：载荷点挠度、两支点转角、挠度曲线"""
    EI = E * math.pi * d ** 4 / 64
    yG = F * a ** 2 * b ** 2 / (3 * EI * L)
    thA = F * b * (L ** 2 - b ** 2) / (6 * EI * L)
    thB = F * a * (L ** 2 - a ** 2) / (6 * EI * L)
    x = np.linspace(0, L, 300)
    yx = np.where(x <= a, F * b * x * (L ** 2 - b ** 2 - x ** 2) / (6 * EI * L),
                  F * a * (L - x) * (L ** 2 - a ** 2 - (L - x) ** 2) / (6 * EI * L))
    return yG, thA, thB, x + S.Z_BRG_A, yx


u40, u35 = uniform(40.0), uniform(35.0)
yG_fe, thA_fe, thB_fe = y_fe[iG], abs(th_fe[iA]), abs(th_fe[iB])

# ---------------------------------------------------------------- 算例 9.1.2
U = H.C7.ur5e()
L2, LW = U["L_fa"] * 1e3, U["L_w"] * 1e3
AL = H.mat("6061-T6")
EI2 = AL["E"] * H.I_tube(*H.TUBE_FA)
w = U["m_fa"] * H.G / L2
P = (U["m_w"] + 5.0) * H.G
Mo = 5.0 * H.G * LW
cases = [(T("自重（均布）", "self-weight (uniform)"), H.cantilever(L2, EI2, w=w)),
         (T("腕部 + 负载的力", "wrist + payload force"), H.cantilever(L2, EI2, P=P)),
         (T("负载偏心的力矩", "payload offset moment"), H.cantilever(L2, EI2, M=Mo))]
y_sum = sum(c[1][0] for c in cases)
th_sum = sum(c[1][1] for c in cases)
y_tip = y_sum + th_sum * LW

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0), gridspec_kw={"width_ratios": [1.25, 1.0]})
m = (z >= S.Z_BRG_A - 1e-9) & (z <= S.Z_BRG_B + 1e-9)
a0.plot(z[m], y_fe[m] * 1e3, color="#d62728", lw=1.6, label=T("阶梯轴（梁单元，33.6 节）", "stepped shaft (beam elements, Sec. 33.6)"))
a0.plot(u40[3], u40[4] * 1e3, color="#1f77b4", lw=1.1, ls="--", label=T("等直径 Ø40（积分法）", "uniform Ø40 (integration)"))
a0.plot(u35[3], u35[4] * 1e3, color="#2ca02c", lw=1.1, ls=":", label=T("等直径 Ø35（积分法）", "uniform Ø35 (integration)"))
for zz in (S.Z_BRG_A, S.Z_BRG_B):
    a0.axvline(zz, color=H.MUTED, lw=0.5, ls="--")
a0.axvline(S.Z_GEAR, color=H.MUTED, lw=0.5)
a0.text(S.Z_GEAR + 1, 0.3, T("齿轮", "gear"), fontsize=6.3, color=H.MUTED)
a0.set_xlabel(T("沿轴线的位置 z / mm", "Position along the axis z / mm"), fontsize=7.2)
a0.set_ylabel(T("挠度 / µm", "Deflection / µm"), fontsize=7.2)
a0.set_ylim(u35[0] * 1e3 * 1.45, -0.3)
a0.legend(fontsize=6.0, frameon=False, loc="lower center")
a0.tick_params(labelsize=6.3)
a0.set_title(T("(a) SH-301 两轴承之间的挠度曲线", "(a) SH-301 deflection between the bearings"), fontsize=7.4)
names = [c[0] for c in cases] + [T("合计", "total")]
ys = [c[1][0] for c in cases] + [y_sum]
a1.barh(range(4), [v * 1e3 for v in ys], color=["#1f77b4", "#ff7f0e", "#2ca02c", "#555555"])
for i, v in enumerate(ys):
    a1.text(v * 1e3 + 1, i, f"{v * 1e3:.1f} µm", va="center", fontsize=6.4)
a1.set_yticks(range(4))
a1.set_yticklabels(names, fontsize=6.5)
a1.invert_yaxis()
a1.set_xlim(0, y_sum * 1e3 * 1.35)
a1.set_xlabel(T("小臂管末端的挠度 / µm", "Forearm-tube end deflection / µm"), fontsize=7.2)
a1.tick_params(labelsize=6.3)
a1.set_title(T("(b) 叠加法：三种载荷分别算再相加", "(b) Superposition of three loads"), fontsize=7.4)
fig.tight_layout()
figure(fig, "fig9_1_1")

out(Ft=Ft, Fr=Fr, F=F, L=L, a=a, b=b, E=E,
    yG_fe=yG_fe * 1e3, thA_fe=thA_fe * 1e3, thB_fe=thB_fe * 1e3,
    yG_40=u40[0] * 1e3, thA_40=u40[1] * 1e3, thB_40=u40[2] * 1e3, yG_35=u35[0] * 1e3, thA_35=u35[1] * 1e3, thB_35=u35[2] * 1e3,
    e40=abs(u40[0] / yG_fe - 1) * 100, eA40=abs(u40[1] / thA_fe - 1) * 100, e35=(u35[0] / yG_fe - 1) * 100,
    L2=L2, LW=LW, m_fa=U["m_fa"], m_w=U["m_w"], EI2=EI2 / 1e9, w=w, P=P, Mo=Mo / 1e3,
    y_w=cases[0][1][0] * 1e3, y_P=cases[1][1][0] * 1e3, y_M=cases[2][1][0] * 1e3, y_sum=y_sum * 1e3, th_sum=th_sum * 1e3,
    y_tip=y_tip * 1e3, pct_P=cases[1][1][0] / y_sum * 100)
